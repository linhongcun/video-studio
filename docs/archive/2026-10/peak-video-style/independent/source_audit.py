#!/usr/bin/env python3
"""Independent, read-only preservation checks for the peak-style derivatives."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent/'.git').exists())
BASE = 'eea5d8fab1037cb9630a14647cbada564082a74b'
SLUGS = ['rate-limit', 'idempotency', 'circuit-breaker', 'degradation']
OUT = ROOT / 'work/peak-video-style/independent'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def section(text, start, end):
    return text[text.index(start):text.index(end, text.index(start))]


def check(name, ok, **extra):
    return {'name': name, 'pass': bool(ok), **extra}


def audit():
    checks, episodes = [], {}
    checks.append(check('base_exists', subprocess.run(['git', 'cat-file', '-e', BASE], cwd=ROOT).returncode == 0, base=BASE))
    cover = json.loads((ROOT/'episodes-codex/_shared/peak-covers/style-v1.json').read_text())
    style_path = ROOT/'episodes-codex/_shared/peak-video/style-v1.json'
    if style_path.exists():
        style = json.loads(style_path.read_text())
        checks.append(check('cover_palette_identical', style['palette'] == cover['palette'], palette=style['palette']))
    tree = subprocess.check_output(['git', 'ls-tree', '-r', BASE, '--', *[f'episodes-codex/{s}' for s in SLUGS]], cwd=ROOT, text=True).splitlines()
    startup=json.loads((ROOT/'work/peak-video-style/preservation-baseline.json').read_text())['productionFiles']
    old_files = []
    for row in tree:
        entry,name=row.split('\t',1)
        mode,kind,blob=entry.split()
        path = ROOT/name
        current = path.read_bytes() if path.is_file() else None
        actual = sha(current) if current is not None else None
        actual_blob=hashlib.sha1(f'blob {len(current)}\0'.encode()+current).hexdigest() if current is not None else None
        prior=startup[name]
        same=actual_blob==blob and (not prior.get('sha256') or prior['sha256']==actual) if current is not None else not prior['presentAtAudit']
        old_files.append({'path': name, 'baselineGitBlob':blob, 'currentGitBlob':actual_blob,
            'startupSHA256':prior.get('sha256'), 'currentSHA256':actual,
            'presentAtStartup':prior['presentAtAudit'],'presentNow':current is not None,
            'state':'materialized-bytes-checked' if current is not None else 'sparse-absent-not-read', 'same':same})
    doc_paths = [f'episodes-codex/{s}/README.md' for s in SLUGS]
    changed = [x['path'] for x in old_files if not x['same']]
    checks.append(check('original_production_tracked_bytes_preserved_except_unfrozen_README_links',
        all(path in doc_paths for path in changed), count=len(old_files), materializedCount=sum(x['presentNow'] for x in old_files), sparseAbsentCount=sum(not x['presentNow'] for x in old_files), changed=changed,
        allowedDocumentationOnly=doc_paths))
    freeze_rows=[]
    for slug in SLUGS:
        episode=ROOT/f'episodes-codex/{slug}'
        frozen=json.loads((episode/'source-sha256.json').read_text())
        for name,expected in frozen.items():
            path=(episode/name).resolve()
            actual=sha(path.read_bytes()) if path.is_file() else None
            freeze_rows.append({'episode':slug,'path':str(path.relative_to(ROOT)), 'expectedSHA256':expected,'actualSHA256':actual,'present':actual is not None,'same':actual==expected if actual is not None else None})
    checks.append(check('all_materialized_original_frozen_inputs_SHA256_match_old_manifests',all(x['same'] for x in freeze_rows if x['present']), count=len(freeze_rows), materializedCount=sum(x['present'] for x in freeze_rows), sparseAbsentCount=sum(not x['present'] for x in freeze_rows), changed=[x['path'] for x in freeze_rows if x['present'] and not x['same']] ))
    checks.append(check('README_links_not_frozen_inputs',not any(x['path'] in doc_paths for x in freeze_rows)))

    branch_original=(ROOT/'episodes-codex/_shared/branch-map/index.ts').read_text()
    branch_derivative=(ROOT/'episodes-codex/_shared/peak-video/branch-map.ts').read_text()
    render_original=branch_original[branch_original.index('export function createBranchNavigator'):]
    render_derivative=branch_derivative[branch_derivative.index('export function createBranchNavigator'):]
    expected=render_original.replace("(edge.color ?? nodeColor(to)) : '#536C85'", "(edge.color ? mapColor(edge.color) : nodeColor(to)) : C.edge")
    expected=expected.replace("on ? color : '#536C85'", 'on ? color : C.edge').replace("on ? '#172A40' : C.bg", 'on ? C.surface : C.bg').replace("on ? color : '#B5C5D6'", 'on ? color : C.muted')
    checks.append(check('branch_renderer_exact_except_four_palette_substitutions',expected==render_derivative))
    checks.append(check('branch_camera_and_state_use_frozen_original',"import {actualNavState} from '../branch-map';" in branch_derivative and 'function actualNavState' not in branch_derivative))

    for slug in SLUGS:
        episode = ROOT/f'episodes-codex/{slug}'
        original = (episode/'remotion/src/Main.tsx').read_text()
        copied_path = episode/'remotion/src/peak-style/Main.tsx'
        items = []
        if not copied_path.exists():
            items.append(check('derivative_exists', False))
            episodes[slug] = {'status': 'waiting', 'checks': items}
            continue
        copied = copied_path.read_text()
        # This includes all animation helpers, Scene branches, states, numeric
        # motion/geometry and in-scene copy; header/ShotView is audited separately.
        original_core = section(original, 'const clamp=', 'export type MainProps=')
        copied_core = section(copied, 'const clamp=', 'export type MainProps=')
        items.append(check('all_helpers_and_Scene_exact_bytes', original_core == copied_core,
            originalSHA256=sha(original_core.encode()), copiedSHA256=sha(copied_core.encode())))
        # The complete composition tail includes audio, Sequence start/duration,
        # and burned subtitle props; every frame continues to use the same data.
        original_main = original[original.index('export const Main:'):]
        copied_main = copied[copied.index('export const Main:'):]
        items.append(check('Main_audio_and_Sequence_exact_bytes', original_main == copied_main))
        items.append(check('uses_original_shot_data', re.search(r"import\s*\{Shot,shots\}\s*from ['\"]\.\./data['\"]", copied) is not None))
        original_sub = re.search(r'\{captions&&sub&&.*?\{sub.text\}</div>\}', original, re.S).group()
        copied_sub = re.search(r'\{captions&&sub&&.*?\{sub.text\}</div>\}', copied, re.S).group()
        items.append(check('burned_subtitle_expression_exact_bytes', original_sub == copied_sub))
        storyboard = json.loads((episode/'storyboard.json').read_text())
        shots = [shot for scene in storyboard['scenes'] for shot in scene['shots']]
        terms = json.loads((episode/'episode.json').read_text()).get('terms', [])
        cumulative = 0
        summary = []
        for shot in shots:
            summary.append({'id':str(shot['id']).zfill(2), 'from':cumulative, 'durationInFrames':shot['durationInFrames'], 'subtitleCount':len(shot.get('subtitles', [])), 'cueFrames':shot.get('cueFrames')})
            cumulative += shot['durationInFrames']
        episodes[slug] = {'status':'pass' if all(x['pass'] for x in items) else 'fail', 'checks':items,
            'MainSHA256':sha(copied_path.read_bytes()), 'bodyFrames':cumulative, 'fps':30, 'shots':summary, 'terms':terms}
    result = {'schemaVersion':1, 'base':BASE, 'scope':'Static preservation of materialized bytes; sparse-absent historical media retains its Git blob and startup absent state without being hydrated or consumed. This does not claim PNG visibility, encoded output, audio listening or browser decode validation.',
        'status':'pass' if all(c['pass'] for c in checks) and all(e['status']=='pass' for e in episodes.values()) else 'fail_or_waiting',
        'checks':checks, 'episodes':episodes}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'original-production-byte-manifest.json').write_text(json.dumps(old_files, indent=2)+'\n')
    (OUT/'original-frozen-input-audit.json').write_text(json.dumps(freeze_rows, indent=2)+'\n')
    (OUT/'source-audit.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({'status':result['status'], 'checks':checks, 'episodes':{s:{'status':v['status'], 'checks':v['checks']} for s,v in episodes.items()}}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    audit()
