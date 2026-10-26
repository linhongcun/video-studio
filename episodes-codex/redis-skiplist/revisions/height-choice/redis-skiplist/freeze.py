#!/usr/bin/env python3
"""Freeze this height-choice revision's mixed voice and title-author inputs.

Run only after narration, timing, source evidence, artwork and all production
writers are final. Verification is read-only. Rendered media and generated
receipts are outputs, never encoding inputs. Original research may be explicitly
reused at its frozen path; the original production and manifest remain read-only.
"""
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
ROOT = next(parent for parent in D.parents
            if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
MANIFEST = D / 'source-sha256.json'
WRAPPER = ROOT / 'episodes-codex/_shared/render_with_references.py'
ORIGINAL = ROOT / 'episodes-codex/redis-skiplist'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def production_extras():
    references = json.loads((D / 'references.json').read_text())
    paths = [Path(__file__).resolve(), D / 'references.json', D / 'article.mdx',
             D / 'voice/input-provenance.json',
             WRAPPER,
             ROOT / 'episodes-codex/_shared/append_references_bibliography.py',
             ROOT / 'episodes-codex/_shared/append_references_original.py',
             ROOT / 'episodes-codex/_shared/append_references.py',
             ROOT / 'episodes-codex/_shared/requirements-reference-appendix.txt',
             ROOT / 'site/scripts/check-references.mjs',
             ROOT / 'episodes/_shared/theme/pageTheme.ts']
    for source in references['sources']:
        paths += [ROOT / source['verification']['evidence'],
                  ROOT / source['titleEvidence']['evidence']]
        if source.get('quotation'):
            paths.append(ROOT / source['quotation']['evidence'])
    # Explicit optional producer/provenance inputs. Additional actual production
    # helpers can be declared in freeze-inputs.json rather than freezing later QA
    # outputs merely because they share an extension or directory.
    # Voice audits are later QA outputs, not inputs to the fresh mixed-source
    # build. Its actual source provenance is mandatory above; no historical
    # all-exact reuse report is treated as approval for these new takes.
    for relative in ['assemble.py', 'model.json', 'build_model.py', 'make_model.py',
                     'prepare_voice.py', 'voice/schema-adaptation.json']:
        if (D / relative).is_file():
            paths.append(D / relative)
    paths += [p for p in (D / 'remotion/scripts').rglob('*')
              if p.is_file() and p.suffix in {'.mjs', '.js', '.ts', '.json'}]
    paths += list((D / 'voice').glob('jobs*.json'))
    declaration = D / 'freeze-inputs.json'
    if declaration.is_file():
        paths.append(declaration)
        declared = json.loads(declaration.read_text())
        assert isinstance(declared, list), 'freeze-inputs.json must be a list of paths'
        for relative in declared:
            assert isinstance(relative, str) and relative.strip(), 'freeze-inputs.json must be a list of paths'
            relative = Path(relative)
            assert not relative.is_absolute(), 'Declare portable production-input paths'
            base = ROOT if relative.parts[0] in {'episodes-codex', 'episodes', 'site', 'docs'} else D
            paths.append(base / relative)
    paths = [path.resolve() for path in paths]
    original_manifest = None
    for path in paths:
        assert path.is_relative_to(ROOT), f'Input outside repository: {path}'
        assert path.is_file(), f'Missing production input: {path}'
        if path.is_relative_to(ORIGINAL / 'research'):
            if original_manifest is None:
                original_manifest = json.loads((ORIGINAL / 'source-sha256.json').read_text())
            relative = str(path.relative_to(ORIGINAL))
            assert original_manifest.get(relative) == digest(path), f'Original frozen research changed: {relative}'
    return sorted(set(paths))


def verify():
    manifest = json.loads(MANIFEST.read_text())
    spec = importlib.util.spec_from_file_location('skiplist_reference_entry', WRAPPER)
    wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wrapper)
    wrapper.verify_freeze(D)
    required = production_extras()
    required += [p for p in (D / 'remotion/src').rglob('*') if p.is_file()]
    absent = [os.path.relpath(path, D) for path in required
              if os.path.relpath(path, D) not in manifest]
    assert not absent, f'Unfrozen production inputs: {absent}'
    print(json.dumps({'status': 'passed', 'inputs': len(manifest),
                      'manifestSHA256': digest(MANIFEST), 'readOnly': True}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    subprocess.run(['node', str(ROOT / 'site/scripts/check-references.mjs'),
                    '--sources', str(D)], cwd=ROOT, check=True)
    if args.verify:
        verify()
        return
    # Validate additional evidence before the canonical freezer writes snapshots.
    extras = production_extras()
    freezer = ROOT / 'episodes-codex/_shared/freeze_sentence_episode.py'
    sys.argv = [str(freezer), str(D)]
    runpy.run_path(str(freezer), run_name='__main__')
    manifest = json.loads(MANIFEST.read_text())
    for path in extras:
        manifest[os.path.relpath(path, D)] = digest(path)
    forbidden = {'video.mp4', 'body.mp4', 'render-result.json',
                 'reference-appendix.json', 'reference-appendix-media-check.json'}
    assert all(Path(relative).suffix != '.mp4' and Path(relative).name not in forbidden
               for relative in manifest), 'Rendered outputs cannot be frozen as inputs'
    MANIFEST.write_text(json.dumps(dict(sorted(manifest.items())), ensure_ascii=False, indent=2) + '\n')
    verify()


if __name__ == '__main__':
    main()
