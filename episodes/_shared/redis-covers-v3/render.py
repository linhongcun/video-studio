#!/usr/bin/env python3
"""Render Redis covers, check geometry and real fonts, then install checked outputs."""

import sys as _episode_path_sys
from pathlib import Path as _EpisodePath
_episode_path_sys.path.insert(0, str(next(parent for parent in _EpisodePath(__file__).resolve().parents
                                       if (parent / 'episode_paths.py').is_file())))
from episode_paths import repo_root, production_directory, publication_directory, resolve_repo_path, resolve_frozen_path
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
REPO = repo_root()
SIZES = {'16x9': (1920, 1080), '3x4': (1080, 1440), '4x3': (1440, 1080)}
INPUTS = ['template.mjs', 'diagrams.mjs', 'catalog.json', 'style-v1.json',
          'plan-layout.json', 'background.png', 'render.py', 'README.md',
          '../middleware-identity/redis-original.svg', '../middleware-identity/LICENSE.txt',
          '../middleware-identity/source.json', '../middleware-identity/NOTICE.md']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font_inputs():
    bindings = []
    for family in ('Noto Sans CJK SC', 'DejaVu Sans'):
        for weight in ('regular', 'bold'):
            actual = subprocess.check_output(['fc-match', '-f', '%{family}\n%{style}\n%{file}\n', f'{family}:weight={weight}'], text=True).splitlines()
            assert len(actual) == 3 and family.casefold() in [part.strip().casefold() for part in actual[0].split(',')], ('Required font unavailable', family, actual)
            bindings.append({'family': family, 'weight': weight, 'actualFamily': actual[0], 'actualStyle': actual[1], 'file': actual[2], 'sha256': sha(Path(actual[2]))})
    return bindings


def inspect(page, path, size):
    w, h = SIZES[size]
    page.set_viewport_size({'width': w, 'height': h})
    page.set_content('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:#EEF1F5}svg{display:block}</style>' + path.read_text())
    page.evaluate('document.fonts.ready')
    assert page.evaluate('document.fonts.check(\'600 36px "Noto Sans CJK SC"\')'), 'Noto font unavailable'
    bounds = page.evaluate('''() => Array.from(document.querySelectorAll('text')).map(e=>{
      const r=e.getBoundingClientRect();return {id:e.dataset.element,text:e.textContent,x:r.x,y:r.y,width:r.width,height:r.height};
    })''')
    groups = page.evaluate('''() => Array.from(document.querySelectorAll('[data-group]')).map(e=>{
      const r=e.getBoundingClientRect();return {id:e.dataset.group,x:r.x,y:r.y,width:r.width,height:r.height};
    })''')
    ink = page.evaluate('''() => Array.from(document.querySelectorAll('[data-ink]')).map(e=>{
      const r=e.getBoundingClientRect();const s=parseFloat(getComputedStyle(e).strokeWidth)||0;
      const m=e.getScreenCTM();const p=s/2*Math.max(Math.hypot(m.a,m.b),Math.hypot(m.c,m.d));
      return {id:e.dataset.ink,x:r.x-p,y:r.y-p,width:r.width+2*p,height:r.height+2*p};
    })''')
    cards = page.evaluate('''() => Array.from(document.querySelectorAll('[data-card]')).map(e=>{
      const r=e.querySelector('rect').getBoundingClientRect();
      return {id:e.dataset.card,x:r.x,y:r.y,width:r.width,height:r.height,text:Array.from(e.querySelectorAll('text')).map(t=>{
        const b=t.getBoundingClientRect();return {text:t.textContent,x:b.x,y:b.y,width:b.width,height:b.height};
      })};
    })''')
    for card in cards:
        for item in card['text']:
            assert item['x'] >= card['x']+2 and item['x']+item['width'] <= card['x']+card['width']-2, ('Card text horizontal overflow', path, card, item)
            assert item['y'] >= card['y']+1 and item['y']+item['height'] <= card['y']+card['height']-1, ('Card text vertical overflow', path, card, item)
        if len(card['text']) == 2:
            a, b = card['text']
            assert a['y']+a['height']+1 <= b['y'], ('Card label/value collision', path, card)
    for b in bounds:
        assert b['width'] > 0 and b['height'] > 0, ('empty text', path, b)
    for b in bounds + ink + groups:
        assert b['x'] >= 0 and b['y'] >= 0 and b['x']+b['width'] <= w+.1 and b['y']+b['height'] <= h+.1, ('COPYFIT', path, b)
        if size == '16x9':
            assert b['y']+b['height'] < 918, ('horizontal bottom safety', path, b)
        if size == '4x3':
            assert b['x'] >= 315 and b['x']+b['width'] <= 1125 and b['y']+b['height'] < 918, ('4:3 content safety', path, b)
    by_id = {b['id']: b for b in groups}
    gap = 9 if size == '4x3' else 12
    for first, second in [('header', 'identity'), ('identity', 'title'), ('title', 'question')]:
        a, b = by_id[first], by_id[second]
        assert a['y']+a['height']+gap <= b['y'], ('group vertical spacing', path, first, second, a, b)
    if size != '16x9':
        a, b = by_id['question'], by_id['diagram']
        assert a['y']+a['height']+gap <= b['y'], ('question/diagram spacing', path)
    else:
        right = max(by_id[k]['x']+by_id[k]['width'] for k in ['identity', 'title', 'question'])
        assert right+24 <= by_id['diagram']['x'], ('text/diagram spacing', path)
    return bounds, groups, ink


def frozen_paths(repo, targets, slugs):
    """Scan every tracked freeze; keep unresolved copied-path evidence explicit.

    The bounded fallback is valid only for absent, untracked destinations in new
    episode directories. Any reference to a target episode in an unresolved
    manifest is ambiguous and blocks installation rather than bypassing it.
    """
    names = subprocess.check_output(['git', '-C', str(repo), 'ls-files', '-z', '**/source-sha256.json']).decode().split('\0')
    result = set()
    unresolved = []
    ambiguous = []
    raw_entries = 0
    needles = {slug.casefold() for slug in slugs}
    needles.update(p.relative_to(repo).as_posix().casefold() for p in targets)
    def resolve(manifest, name):
        path = Path(name)
        if path.is_absolute(): return path.resolve()
        if name.startswith(('episodes/', 'episodes-codex/', 'docs/', 'site/', 'design/')): return resolve_repo_path(path, root=repo)
        return resolve_frozen_path(manifest, str(path))
    def add(manifest, name):
        nonlocal raw_entries
        raw_entries += 1
        try:
            result.add(resolve(manifest, name))
        except ValueError as error:
            unresolved.append({'manifest': manifest.relative_to(repo).as_posix(),
                               'entry': name, 'error': str(error),
                               'manifestSha256': sha(manifest)})
    def visit(manifest, value):
        if isinstance(value, dict):
            for key, child in value.items():
                if isinstance(child, str) and len(child) == 64 and all(c in '0123456789abcdefABCDEF' for c in child):
                    add(manifest, key)
                if key == 'path' and isinstance(child, str) and any(isinstance(value.get(k), str) and len(value[k]) == 64 for k in ('sha256','SHA256')):
                    add(manifest, child)
                if isinstance(child, (dict,list)): visit(manifest, child)
        elif isinstance(value, list):
            for child in value: visit(manifest, child)
    for name in filter(None, names):
        manifest = resolve_repo_path(name, root=repo)
        value = json.loads(manifest.read_text())
        before = len(unresolved)
        visit(manifest, value)
        if len(unresolved) != before:
            raw = (name+'\n'+json.dumps(value, ensure_ascii=False)).replace('\\', '/').casefold()
            matches = sorted(needle for needle in needles if needle in raw)
            if matches:
                ambiguous.append({'manifest': name, 'targetReferences': matches,
                                  'manifestSha256': sha(manifest)})
    return result, {'trackedManifests': len(list(filter(None, names))),
                    'rawPathEntries': raw_entries, 'resolvedUniquePaths': len(result),
                    'unresolvedEntries': unresolved,
                    'unresolvedManifests': sorted({i['manifest'] for i in unresolved}),
                    'ambiguousTargetReferences': ambiguous,
                    'unresolvedRawManifestGuard': 'entire decoded JSON and manifest path scanned for every new target slug and complete target path'}


def installation_preflight(repo, targets, slugs):
    """Read-only safety check; never permit replacement, including symlinks."""
    repo = repo.resolve()
    raw_targets = {p.absolute() for p in targets}
    assert all(p.is_relative_to(repo) for p in raw_targets), 'Installation target outside repository'
    aliases = sorted(p.relative_to(repo).as_posix() for p in raw_targets if p != p.resolve())
    targets = {p.resolve() for p in raw_targets}
    assert all(p.is_relative_to(repo) for p in targets), 'Resolved installation target outside repository'
    tracked = set(filter(None, subprocess.check_output(
        ['git', '-C', str(repo), 'ls-files', '-z']).decode().split('\0')))
    existing = sorted(p.relative_to(repo).as_posix() for p in raw_targets if os.path.lexists(p))
    tracked_targets = sorted(p.relative_to(repo).as_posix() for p in raw_targets
                             if p.relative_to(repo).as_posix() in tracked)
    protected, diagnosis = frozen_paths(repo, targets, slugs)
    intersection = sorted(p.relative_to(repo).as_posix() for p in targets.intersection(protected))
    return {'schemaVersion': 1, 'mode': 'new-target-only',
            'checkedAt': datetime.now(timezone.utc).isoformat(),
            'targets': sorted(p.relative_to(repo).as_posix() for p in targets),
            'targetCount': len(targets), 'existingTargets': existing,
            'trackedTargets': tracked_targets, 'symlinkOrAliasTargets': aliases,
            'frozenTargetIntersection': intersection,
            'freezeScan': diagnosis,
            'passed': not (existing or tracked_targets or aliases or intersection or diagnosis['ambiguousTargetReferences'])}


def verify_artifacts(out, prior, fonts, episodes):
    assert prior['passed'] and not prior.get('installed'), 'Expected uninstalled checked candidates'
    assert prior['fontInputs'] == fonts, 'Checked actual fonts changed'
    assert {(i['slug'], i['size']) for i in prior['images']} == {(e['slug'], s) for e in episodes for s in SIZES}
    for item in prior['images']:
        for ext in ['svg', 'png', 'jpg']:
            assert sha(out/item['slug']/f"cover-{item['size']}.{ext}") == item[ext+'Sha256'], 'Checked artifact changed'


def revalidate_existing(out, prior, inputs, fonts, episodes):
    """Revalidate the same approved bytes after an installer-only code change."""
    verify_artifacts(out, prior, fonts, episodes)
    assert set(prior['inputs']) == set(inputs), 'Unexpected input-set change'
    changed = [name for name in inputs if inputs[name] != prior['inputs'][name]]
    assert changed == ['render.py'], ('Only installer code may change for same-artifact revalidation', changed)
    script = '''import fs from 'node:fs';import {pathToFileURL} from 'node:url';
const here=process.argv[1];const {cover}=await import(pathToFileURL(here+'/template.mjs'));
const c=JSON.parse(fs.readFileSync(here+'/catalog.json','utf8'));
const proofs=JSON.parse(fs.readFileSync(here+'/plan-layout.json','utf8')).entries;
const result={};for(const e of c.episodes)for(const s of ['16x9','3x4','4x3'])result[e.slug+'/cover-'+s+'.svg']=cover(e,s);
for(const e of proofs)for(const s of ['16x9','3x4','4x3'])result['typography-only/'+e.slug+'-'+s+'.svg']=cover(e,s,true);
process.stdout.write(JSON.stringify(result));'''
    generated = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', script, str(HERE)], text=True))
    for name, source in generated.items():
        assert (out/name).read_bytes() == source.encode(), ('Artwork source no longer reproduces approved SVG', name)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
        assert browser.version == prior['runtime']['chromium'], 'Checked browser changed'
        assert importlib.metadata.version('playwright') == prior['runtime']['playwright'], 'Checked browser driver changed'
        page = browser.new_page(device_scale_factor=1)
        for item in prior['images']:
            path = out/item['slug']/f"cover-{item['size']}.svg"
            bounds, groups, ink = inspect(page, path, item['size'])
            assert (bounds, groups, ink) == (item['textBounds'], item['groupBounds'], item['inkBounds']), ('Approved layout changed', path)
            for ext, options in [('png', {'type':'png'}), ('jpg', {'type':'jpeg','quality':94})]:
                assert hashlib.sha256(page.screenshot(**options)).hexdigest() == item[ext+'Sha256'], ('In-memory pixel revalidation differs', path, ext)
        for item in prior['plannedTypography']:
            path = out/'typography-only'/item['name']
            bounds, groups, ink = inspect(page, path, item['size'])
            assert (bounds, groups, ink) == (item['textBounds'], item['groupBounds'], item['inkBounds']), ('Approved stress layout changed', path)
        browser.close()
    report_path = out/'render-report.json'
    old_bytes = report_path.read_bytes()
    old_sha = hashlib.sha256(old_bytes).hexdigest()
    backup = out/f'render-report.before-installer-fix.{old_sha[:16]}.json'
    if backup.exists():
        assert backup.read_bytes() == old_bytes, 'Previous report backup differs'
    else:
        with backup.open('xb') as stream:
            stream.write(old_bytes)
    evidence = {'schemaVersion': 1, 'checkedAt': datetime.now(timezone.utc).isoformat(),
                'scope': 'installer-only code change; original SVG/PNG/JPEG files never rewritten',
                'previousReport': backup.name, 'previousReportSha256': old_sha,
                'changedInput': 'render.py', 'oldInputSha256': prior['inputs']['render.py'],
                'newInputSha256': inputs['render.py'], 'fontInputsUnchanged': True,
                'artworkSourceInputsUnchanged': True, 'svgReproductionMatched': len(generated),
                'unchangedImageArtifacts': len(prior['images'])*3,
                'inMemoryPixelComparisons': len(prior['images'])*2,
                'layoutComparisons': len(prior['images'])+len(prior['plannedTypography']),
                'passed': True}
    evidence_path = out/'artifact-revalidation.json'
    assert not evidence_path.exists(), 'Preserve the previous revalidation identity; choose another revision'
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n')
    updated = dict(prior)
    updated['inputs'] = inputs
    updated['artifactRevalidation'] = {'file': evidence_path.name, 'sha256': sha(evidence_path)}
    report_path.write_text(json.dumps(updated, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(evidence, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--check-install', action='store_true', help='Read-only new-target installation preflight; never copy assets')
    parser.add_argument('--revalidate-existing', action='store_true', help='Revalidate unchanged approved artifacts after installer-only code change')
    parser.add_argument('--repo', type=Path, default=REPO)
    args = parser.parse_args()
    assert sum([args.install, args.check_install, args.revalidate_existing]) <= 1, 'Choose one operation'
    out, repo = args.out_dir.resolve(), args.repo.resolve()
    catalog = json.loads((HERE/'catalog.json').read_text())
    catalog_episodes = catalog['episodes']
    preserved = set(catalog.get('preservedEpisodes', []))
    episodes = [ep for ep in catalog_episodes if ep['slug'] not in preserved]
    actual = {}
    for p in (repo/'episodes').glob('*/*/publication/meta.json'):
        m = json.loads(p.read_text())
        if m.get('series') == catalog['series']:
            actual[m['slug']] = m
    identity_checks = []
    for ep in catalog_episodes:
        assert ep['number'] == f"EP.{ep['ep']:02d}", 'Use actual EP number'
        production = (resolve_repo_path(ep['productionRoot'], root=repo)).resolve()
        assert production.is_relative_to(repo/'episodes'/'redis'/ep['slug']/'production'), 'Invalid production root'
        m = actual.get(ep['slug'])
        if m is None:
            assert not (args.install or args.check_install), 'Install requires the real episode metadata'
            identity_checks.append({'slug': ep['slug'], 'status': 'catalog-only-candidate', 'ep': ep['ep'], 'sourceTitle': ep['sourceTitle']})
            continue
        assert m['ep'] == ep['ep'] and m['title'] == ep['sourceTitle'], 'EP/title mismatch'
        assert resolve_repo_path(m['sourcePath'], root=repo) == production / 'remotion', 'Catalog must bind exact current sourcePath'
        assert m.get('poster', 'cover-16x9.jpg') == 'cover-16x9.jpg', 'Review another site poster convention before installing'
        identity_checks.append({'slug': ep['slug'], 'status': 'matched-real-metadata', 'ep': m['ep'], 'sourceTitle': m['title'], 'draft': m.get('draft')})
    inputs = {name: sha(HERE/name) for name in INPUTS}
    fonts = font_inputs()
    if args.revalidate_existing:
        prior = json.loads((out/'render-report.json').read_text())
        revalidate_existing(out, prior, inputs, fonts, episodes)
        return
    if args.install or args.check_install:
        prior = json.loads((out/'render-report.json').read_text())
        assert prior['inputs'] == inputs, 'Checked render inputs changed; explicitly revalidate installer-only changes'
        verify_artifacts(out, prior, fonts, episodes)
        operations = []
        sidecars = []
        for ep in episodes:
            source = out/ep['slug']
            production_covers = repo/'episodes'/'redis'/ep['slug']/'production'/'covers'
            publication = repo/'episodes'/'redis'/ep['slug']/'publication'
            assert (repo/ep['installationRoot']).absolute() == production_covers, 'Only the new episode production/covers destination is allowed'
            for dest, exts in [(production_covers, ['png', 'jpg']), (publication, ['jpg'])]:
                for size in SIZES:
                    for ext in exts:
                        operations.append((source/f'cover-{size}.{ext}', dest/f'cover-{size}.{ext}'))
                operations.append((source/'cover-3x4.jpg', dest/'poster.jpg'))
                sidecars.append(dest/'cover-style.json')
        targets = {p for _, p in operations}.union(sidecars)
        assert len(targets) == len(operations)+len(sidecars), 'Duplicate planned installation targets'
        safety = installation_preflight(repo, targets, [ep['slug'] for ep in episodes])
        safety_path = out/'install-preflight.json'
        safety_path.write_text(json.dumps(safety, ensure_ascii=False, indent=2)+'\n')
        assert safety['passed'], f'New-target installation safety check failed; inspect {safety_path}'
        if args.check_install:
            print(json.dumps({'passed': True, 'readOnly': True, 'targetCount': len(targets),
                              'unresolvedHistoricalEntries': len(safety['freezeScan']['unresolvedEntries']),
                              'diagnosis': str(safety_path)}, ensure_ascii=False))
            return
        for source, dest in operations:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with source.open('rb') as stream, dest.open('xb') as target:
                shutil.copyfileobj(stream, target)
        for ep in episodes:
            images = [i for i in prior['images'] if i['slug'] == ep['slug']]
            manifest = {'style': catalog['version'], 'ep': ep['ep'], 'number': ep['number'],
                        'productionRoot': ep['installationRoot'], 'currentRemotionRoot': ep['productionRoot'], 'seriesSource': 'episodes/_shared/redis-covers-v3',
                        'sourceSha256': inputs, 'fontInputs': fonts, 'sitePoster': 'cover-16x9.jpg', 'portraitPoster': 'poster.jpg',
                        'covers': {i['size']: {'dimensions': i['dimensions'], 'jpgSha256': i['jpgSha256'], 'pngSha256': i['pngSha256']} for i in images}}
            for dest in [repo/'episodes'/'redis'/ep['slug']/'production'/'covers', repo/'episodes'/'redis'/ep['slug']/'publication']:
                with (dest/'cover-style.json').open('x') as stream:
                    stream.write(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
        prior.update(installed=True, installedAt=datetime.now(timezone.utc).isoformat(), installedImages=len(operations),
                     frozenTargetIntersection=0, installationPreflight={'file': safety_path.name, 'sha256': sha(safety_path)})
        (out/'render-report.json').write_text(json.dumps(prior, ensure_ascii=False, indent=2)+'\n')
        print(f'Installed {len(operations)} checked cover images and {len(episodes)*2} manifests')
        return
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(['node', str(HERE/'template.mjs'), '--out-dir', str(out)], check=True)
    report = {'schemaVersion': 1, 'style': catalog['version'], 'checkedAt': datetime.now(timezone.utc).isoformat(),
              'inputs': inputs, 'fontInputs': fonts, 'episodeIdentityChecks': identity_checks, 'images': [], 'plannedTypography': [], 'preservedEpisodes': sorted(preserved), 'installed': False}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
        report['runtime'] = {'chromium': browser.version, 'playwright': importlib.metadata.version('playwright')}
        page = browser.new_page(device_scale_factor=1)
        for ep in episodes:
            for size, dimensions in SIZES.items():
                p = out/ep['slug']/f'cover-{size}'
                bounds, groups, ink = inspect(page, p.with_suffix('.svg'), size)
                page.screenshot(path=str(p.with_suffix('.png')), type='png')
                page.screenshot(path=str(p.with_suffix('.jpg')), type='jpeg', quality=94)
                for ext in ['png', 'jpg']:
                    with Image.open(p.with_suffix('.'+ext)) as im:
                        assert im.size == dimensions, 'Unexpected image dimensions'
                report['images'].append({'slug': ep['slug'], 'number': ep['number'], 'size': size, 'dimensions': list(dimensions),
                                         **{ext+'Sha256': sha(p.with_suffix('.'+ext)) for ext in ['svg', 'png', 'jpg']},
                                         'textBounds': bounds, 'groupBounds': groups, 'inkBounds': ink})
                print(f'Candidate image ready: {p.with_suffix(".png")}', flush=True)
        for p in sorted((out/'typography-only').glob('*.svg')):
            size = p.stem.rsplit('-', 1)[1]
            bounds, groups, ink = inspect(page, p, size)
            report['plannedTypography'].append({'name': p.name, 'size': size, 'passed': True,
                                                 'textBounds': bounds, 'groupBounds': groups, 'inkBounds': ink,
                                                 'scope': 'Typography only, not a future episode or mechanism illustration'})
        browser.close()
    ep = episodes[0]
    with Image.open(out/ep['slug']/'cover-16x9.jpg') as im:
        preview = Image.new('RGB', (1024, 660), '#EEF1F5')
        preview.paste(im.resize((960, 540), Image.Resampling.LANCZOS), (32, 88))
        font = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 30)
        ImageDraw.Draw(preview).text((32, 24), 'Redis · '+ep['number']+' / 系列统一封面', font=font, fill='#182737')
        preview.save(out/'preview.png')
        preview.save(out/'preview.jpg', quality=95)
    sheet = Image.new('RGB', (1800, len(episodes)*560), '#EEF1F5')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 24)
    for row, ep in enumerate(episodes):
        for col, size in enumerate(SIZES):
            with Image.open(out/ep['slug']/f'cover-{size}.jpg') as im:
                im.thumbnail((570, 490), Image.Resampling.LANCZOS)
                x = col*600 + (600-im.width)//2
                y = row*560 + 56 + (490-im.height)//2
                sheet.paste(im, (x, y))
            draw.text((col*600+20, row*560+14), ep['number']+' · '+size, font=font, fill='#182737')
    sheet.save(out/'contact-sheet.png')
    sheet.save(out/'contact-sheet.jpg', quality=95)
    report['contactSheet'] = {'file': 'contact-sheet.png', 'sha256': sha(out/'contact-sheet.png')}
    report['passed'] = True
    (out/'render-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(f"Checked {len(report['images'])} covers and {len(report['plannedTypography'])} typography-only layouts")


if __name__ == '__main__':
    main()
