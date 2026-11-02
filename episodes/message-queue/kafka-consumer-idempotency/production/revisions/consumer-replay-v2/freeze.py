#!/usr/bin/env python3
"""Freeze this episode's current measured inputs; --verify never rewrites them."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import runpy
import subprocess
import sys

D = Path(__file__).resolve().parent
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file() and (p / 'site/package.json').is_file())
sys.path.insert(0, str(ROOT / 'episodes/_shared'))
from episode_paths import resolve_repo_path, resolve_frozen_path, episode_slug

MANIFEST = D / 'source-sha256.json'
PIPELINE = ROOT / 'episodes/_shared/render_with_references.py'
A = ROOT / 'docs/archive/2026-11/mq05-consumer-replay'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_files(directory):
    """Current research/example inputs, never generated code caches or media."""
    excluded = {'node_modules', 'out', '__pycache__', '.git', 'target', 'build'}
    return [p for p in directory.rglob('*') if p.is_file()
            and not excluded.intersection(p.relative_to(directory).parts)
            and p.suffix not in {'.mp4', '.pyc', '.class'}]


def extras():
    paths = [D / name for name in ['prepare.py', 'assemble.py', 'freeze.py', 'verify.py',
        'render.py', 'render-final.sh', 'references-renderer.py', 'check-references.mjs',
        'pipeline-tools.py', 'normalize-color.py', 'references.json', 'article.mdx',
        'article-figure-plan.json']]
    paths += [PIPELINE, ROOT / 'episodes/_shared/episode_paths.py',
        ROOT / 'site/scripts/episode-paths.mjs', ROOT / 'site/scripts/check-references.mjs',
        ROOT / 'episodes/_shared/kafka-video/references.py',
        ROOT / 'episodes/_shared/kafka-covers/style-v1.json',
        ROOT / 'episodes/_shared/append_references_bibliography.py',
        ROOT / 'episodes/_shared/append_references_original.py',
        ROOT / 'episodes/_shared/append_references.py',
        ROOT / 'episodes/_shared/requirements-reference-appendix.txt',
        ROOT / 'episodes/_shared/theme/pageTheme.ts', A / 'font-environment.json', A / 'fonts.py']
    for name in ['article-sources.json', 'model.py', 'build_model.py', 'model.mjs', 'model.json',
                 'voice/input-provenance.json', 'voice/schema-adaptation.json',
                 'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg', 'poster.jpg', 'cover-style.json']:
        if (D / name).is_file():
            paths.append(D / name)
    for name in ['sources', 'examples', 'remotion/scripts']:
        paths += source_files(D / name)
    paths += list((D / 'voice').glob('jobs*.json'))
    for catalog in ['references.json', 'article-sources.json']:
        if (D / catalog).is_file():
            for source in json.loads((D / catalog).read_text())['sources']:
                for field in ['verification', 'titleEvidence', 'quotation']:
                    evidence = source.get(field, {}).get('evidence')
                    if evidence:
                        paths.append(resolve_repo_path(evidence, root=ROOT))
    imports = '\n'.join(p.read_text() for p in (D / 'remotion/src').rglob('*')
                        if p.is_file() and p.suffix in {'.ts', '.tsx'})
    for component in ['branch-map', 'middleware-identity']:
        if f'_shared/{component}' in imports:
            paths += source_files(ROOT / 'episodes/_shared' / component)
    declaration = D / 'freeze-inputs.json'
    assert declaration.is_file(), 'Root must finalize the actual extra-input declaration before freeze'
    paths.append(declaration)
    for entry in json.loads(declaration.read_text()):
        relative = Path(entry)
        assert relative.parts and not relative.is_absolute(), 'Use portable input paths'
        paths.append(resolve_repo_path(relative, root=ROOT) if relative.parts[0] in {'episodes', 'site', 'docs', 'scripts'}
                     else (D / relative).resolve())
    resolved = sorted(set(p.resolve() for p in paths))
    forbidden = {'video.mp4', 'render-result.json', 'reference-appendix.json', 'reference-appendix-media-check.json'}
    for path in resolved:
        assert path.is_relative_to(ROOT) and path.is_file(), f'Missing or external input: {path}'
        assert path.suffix != '.mp4' and path.name not in forbidden, f'Output is not an input: {path}'
    return resolved


def verify():
    spec = importlib.util.spec_from_file_location('current_reference_pipeline', PIPELINE)
    pipeline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pipeline)
    pipeline.verify_freeze(D)
    manifest = json.loads(MANIFEST.read_text())
    required = extras() + [p for p in (D / 'remotion/src').rglob('*') if p.is_file()]
    absent = [os.path.relpath(p, D) for p in required if os.path.relpath(p, D) not in manifest]
    assert not absent, f'Actual inputs not declared: {absent}'
    print(json.dumps({'passed': True, 'readOnly': True, 'inputs': len(manifest),
                      'manifestSHA256': digest(MANIFEST)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    config = json.loads((D / 'episode-config.json').read_text())
    assert config['slug'] == episode_slug(D)
    board = json.loads((D / 'storyboard.json').read_text())
    assert not board['meta'].get('pendingAudio') and not board['meta'].get('provisionalTiming')
    fps = board['meta']['fps']
    figures = json.loads((D / 'article-figure-plan.json').read_text())['figures']
    assert figures and all(type(f.get('frame')) is int and 0 <= f['frame'] < board['meta']['durationInFrames']
        and isinstance(f.get('seconds'), (float, int)) and abs(f['seconds'] - f['frame'] / fps) < 1e-9
        for f in figures), 'Finalize actual integer-frame article positions before freezing'
    subprocess.run(['node', str(D / 'check-references.mjs'), '--sources', str(D)], cwd=ROOT, check=True)
    if args.verify:
        verify()
        return
    assert not MANIFEST.exists(), 'Preserve the previous freeze identity; root must explicitly choose a new revision'
    paths = extras()
    canonical = ROOT / 'episodes/_shared/freeze_sentence_episode.py'
    sys.argv = [str(canonical), str(D)]
    runpy.run_path(str(canonical), run_name='__main__')
    manifest = json.loads(MANIFEST.read_text())
    manifest.update({os.path.relpath(p, D): digest(p) for p in paths})
    MANIFEST.write_text(json.dumps(dict(sorted(manifest.items())), ensure_ascii=False, indent=2) + '\n')
    verify()


if __name__ == '__main__':
    main()
