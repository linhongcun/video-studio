#!/usr/bin/env python3
"""Freeze this logic revision; preserve28 retained take identities and old evidence."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import re
import runpy
import subprocess
import sys

D = Path(__file__).resolve().parent
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file() and (p / 'site/package.json').is_file())
sys.path.insert(0, str(ROOT / 'episodes/_shared'))
from episode_paths import resolve_repo_path
sys.path.insert(0, str(D))
from voice_reuse import validate_reuse

MANIFEST = D / 'source-sha256.json'
WRAPPER = ROOT / 'episodes/_shared/render_with_references.py'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imported_local_files(path):
    if path.suffix not in {'.ts', '.tsx', '.js', '.mjs', '.jsx'}:
        return []
    names = re.findall(r'''(?:from\s*|import\s*)['"]([^'"]+)['"]''', path.read_text())
    found = []
    for name in names:
        if not name.startswith('.'):
            continue
        candidate = path.parent / name
        options = [candidate] if candidate.suffix else [candidate, *[Path(str(candidate) + ext) for ext in ('.ts', '.tsx', '.js', '.json')], candidate / 'index.ts', candidate / 'index.tsx']
        matches = [p.resolve() for p in options if p.is_file()]
        if not matches:
            raise ValueError(f'Missing local production import: {path}: {name}')
        found.append(matches[0])
    return found


def extras():
    paths = [WRAPPER, ROOT / 'episodes/_shared/append_references_bibliography.py',
             ROOT / 'episodes/_shared/append_references_original.py',
             ROOT / 'episodes/_shared/append_references.py',
             ROOT / 'episodes/_shared/requirements-reference-appendix.txt',
             ROOT / 'site/scripts/check-references.mjs',
             ROOT / 'site/scripts/episode-paths.mjs',
             ROOT / 'episodes/_shared/theme/pageTheme.ts',
             ROOT / 'episodes/_shared/episode_paths.py',
             ROOT / 'episodes/_shared/puzzles-video/references.py',
             ROOT / 'episodes/_shared/puzzles-covers/catalog.json',
             D / 'references.json', D / 'article.mdx']
    paths += list(D.glob('*.py')) + list(D.glob('*.sh')) + list(D.glob('*.mjs')) + list(D.glob('*.cjs'))
    cover_style = D / 'cover-style.json'
    if cover_style.is_file():
        paths.append(cover_style)
        # Covers are reused verbatim. The retained style map records their
        # historical generator; today's expanded shared catalog is not replayed.
        paths += list(D.glob('cover-*.png')) + list(D.glob('cover-*.jpg')) + list(D.glob('cover-*.svg'))
        if (D / 'poster.jpg').is_file():
            paths.append(D / 'poster.jpg')
    paths += [p for p in (D / 'remotion/src').rglob('*') if p.is_file()]
    paths += [p for p in (D / 'remotion/scripts').rglob('*') if p.is_file()]
    paths += list((D / 'voice').glob('jobs*.json'))
    paths.append(D / 'input-provenance.json')
    provenance = json.loads((D / 'input-provenance.json').read_text())
    historical = ROOT / provenance['historicalFreeze']
    assert digest(historical) == provenance['historicalFreezeSha256']
    paths.append(historical)
    validate_reuse(require_new_takes=True)
    for relative, expected in provenance['copiedInputs'].items():
        if relative.startswith('cover-') and relative.endswith('.jpg') or relative == 'poster.jpg':
            assert digest(D / relative) == expected, f'Reused cover differs: {relative}'
    for name in ['article-sources.json', 'model.json', 'voice/input-provenance.json', 'voice/schema-adaptation.json', 'voice/reuse-check.json', 'voice/runtime-provenance.json']:
        if (D / name).is_file():
            paths.append(D / name)
    for catalog in ['references.json', 'article-sources.json']:
        if not (D / catalog).is_file():
            continue
        for source in json.loads((D / catalog).read_text())['sources']:
            for field in ['verification', 'titleEvidence', 'quotation']:
                evidence = source.get(field, {}).get('evidence')
                if evidence:
                    paths.append(resolve_repo_path(evidence, root=ROOT))
    declaration = D / 'freeze-inputs.json'
    if declaration.is_file():
        paths.append(declaration)
        for relative in json.loads(declaration.read_text()):
            relative = Path(relative)
            assert not relative.is_absolute(), 'Use repository or episode relative production inputs'
            paths.append(ROOT / relative if relative.parts[0] in {'episodes', 'site', 'docs'} else D / relative)
    pending, closure = list(paths), set()
    while pending:
        path = pending.pop().resolve()
        if path in closure:
            continue
        assert path.is_relative_to(ROOT), f'Input outside repository: {path}'
        assert path.is_file(), f'Missing production input: {path}'
        assert path.suffix != '.mp4', f'Rendered media is an output: {path}'
        closure.add(path)
        pending += imported_local_files(path)
    return sorted(closure)


def verify():
    spec = importlib.util.spec_from_file_location('balls_reference_pipeline', WRAPPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.verify_freeze(D)
    manifest = json.loads(MANIFEST.read_text())
    absent = [os.path.relpath(p, D) for p in extras() if os.path.relpath(p, D) not in manifest]
    assert not absent, f'Unfrozen production inputs: {absent}'
    print(json.dumps({'status': 'passed', 'frozenInputs': len(manifest),
                      'manifestSHA256': digest(MANIFEST), 'readOnly': True}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.verify:
        verify()
        return
    assert not (D / 'video.mp4').exists(), 'Preserve rendered production and choose a new revision before changing its freeze'
    subprocess.run(['node', str(ROOT / 'site/scripts/check-references.mjs'), '--sources', str(D)], cwd=ROOT, check=True)
    canonical = ROOT / 'episodes/_shared/freeze_sentence_episode.py'
    sys.argv = [str(canonical), str(D)]
    runpy.run_path(str(canonical), run_name='__main__')
    manifest = json.loads(MANIFEST.read_text())
    manifest.update({os.path.relpath(p, D): digest(p) for p in extras()})
    forbidden = {'video.mp4', 'render-result.json', 'reference-appendix.json', 'reference-appendix-media-check.json'}
    assert all(Path(p).suffix != '.mp4' and Path(p).name not in forbidden for p in manifest)
    MANIFEST.write_text(json.dumps(dict(sorted(manifest.items())), ensure_ascii=False, indent=2) + '\n')
    verify()


if __name__ == '__main__':
    main()
