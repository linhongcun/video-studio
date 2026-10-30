#!/usr/bin/env python3
"""Freeze this episode's real production inputs without changing older episodes."""
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
MANIFEST = D / 'source-sha256.json'
WRAPPER = ROOT / 'episodes-codex/_shared/render_with_references.py'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extras():
    paths = [Path(__file__).resolve(), D / 'prepare.py', D / 'assemble.py',
             D / 'verify.py', D / 'render-final.sh', D / 'references.json',
             D / 'article.mdx', WRAPPER,
             ROOT / 'episodes-codex/_shared/append_references_bibliography.py',
             ROOT / 'episodes-codex/_shared/append_references_original.py',
             ROOT / 'episodes-codex/_shared/append_references.py',
             ROOT / 'episodes-codex/_shared/requirements-reference-appendix.txt',
             ROOT / 'site/scripts/check-references.mjs',
             ROOT / 'episodes/_shared/theme/pageTheme.ts']
    for name in ['voice/input-provenance.json', 'voice/reused-source-baseline.json',
                 'voice/schema-adaptation.json', 'article-sources.json',
                 'build_model.py', 'model.json']:
        if (D / name).is_file():
            paths.append(D / name)
    paths += [p for p in (D / 'remotion/scripts').rglob('*') if p.is_file()]
    paths += list((D / 'voice').glob('jobs*.json'))
    for catalog in ['references.json', 'article-sources.json']:
        if not (D / catalog).is_file():
            continue
        for source in json.loads((D / catalog).read_text())['sources']:
            for field in ['verification', 'titleEvidence', 'quotation']:
                if source.get(field, {}).get('evidence'):
                    paths.append(ROOT / source[field]['evidence'])
    # Freeze the exact shared components actually imported by this revision.
    imports = '\n'.join(p.read_text() for p in (D / 'remotion/src').rglob('*')
                        if p.is_file() and p.suffix in {'.ts', '.tsx'})
    for component in ['branch-map', 'middleware-identity']:
        if f'_shared/{component}' in imports:
            paths += [p for p in (ROOT / 'episodes-codex/_shared' / component).rglob('*') if p.is_file()]
    declaration = D / 'freeze-inputs.json'
    if declaration.is_file():
        paths.append(declaration)
        for relative in json.loads(declaration.read_text()):
            relative = Path(relative)
            assert not relative.is_absolute(), 'Use portable production-input paths'
            base = ROOT if relative.parts[0] in {'episodes-codex', 'episodes', 'site', 'docs'} else D
            paths.append(base / relative)
    resolved = sorted(set(p.resolve() for p in paths))
    for path in resolved:
        assert path.is_relative_to(ROOT), f'Input outside repository: {path}'
        assert path.is_file(), f'Missing production input: {path}'
        assert path.suffix != '.mp4', f'Rendered media is an output: {path}'
    return resolved


def verify():
    spec = importlib.util.spec_from_file_location('kafka_reference_entry', WRAPPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.verify_freeze(D)
    manifest = json.loads(MANIFEST.read_text())
    required = extras() + [p for p in (D / 'remotion/src').rglob('*') if p.is_file()]
    absent = [os.path.relpath(p, D) for p in required if os.path.relpath(p, D) not in manifest]
    assert not absent, f'Unfrozen production inputs: {absent}'
    print(json.dumps({'status': 'passed', 'frozenInputs': len(manifest),
                      'manifestSHA256': digest(MANIFEST), 'readOnly': True}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    subprocess.run(['node', str(ROOT / 'site/scripts/check-references.mjs'), '--sources', str(D)], cwd=ROOT, check=True)
    if args.verify:
        verify()
        return
    paths = extras()
    canonical = ROOT / 'episodes-codex/_shared/freeze_sentence_episode.py'
    sys.argv = [str(canonical), str(D)]
    runpy.run_path(str(canonical), run_name='__main__')
    manifest = json.loads(MANIFEST.read_text())
    manifest.update({os.path.relpath(p, D): digest(p) for p in paths})
    forbidden = {'video.mp4', 'render-result.json', 'reference-appendix.json', 'reference-appendix-media-check.json'}
    assert all(Path(p).suffix != '.mp4' and Path(p).name not in forbidden for p in manifest)
    MANIFEST.write_text(json.dumps(dict(sorted(manifest.items())), ensure_ascii=False, indent=2) + '\n')
    verify()


if __name__ == '__main__':
    main()
