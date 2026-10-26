#!/usr/bin/env python3
"""Freeze EA01's current reference orchestration without rewriting body history.

The retained 5881-frame body was rendered at c80faaef using the archived146
inputs. Its original package, article and research are verified at relocated,
byte-identical snapshots. The new source-sha256.json describes the current
reference appending and future renders; it never claims that later citation
edits or the current package produced the retained body. Videos and generated
receipts are outputs, not frozen inputs.

Usage: freeze_with_references.py [--verify | --check-body]
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
ARCHIVE = D / 'revisions/reference-endcards'
BODY_MANIFEST = ARCHIVE / 'body-source-sha256.json'
BODY_MANIFEST_SHA256 = 'f5380a8b01cf9b8a2badcfe38a108cfa6f76ba9a682c50c7c7860448ddc5060c'
BODY_PACKAGE = ARCHIVE / 'body-remotion-package.json'
BODY_DOCUMENTS = {
    'article.mdx': D / 'revisions/original-titles/before-article.mdx',
    'research.md': D / 'revisions/original-titles/before-research.md',
}
MANIFEST = D / 'source-sha256.json'


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def body_inputs() -> dict[str, str]:
    assert sha(BODY_MANIFEST) == BODY_MANIFEST_SHA256, 'Original146 body manifest changed'
    original = read(BODY_MANIFEST)
    assert isinstance(original, dict) and len(original) == 146
    failures = []
    relocated = {'remotion/package.json': BODY_PACKAGE, **BODY_DOCUMENTS}
    for relative, expected in original.items():
        target = relocated.get(relative, D / relative)
        resolved = target.resolve()
        assert resolved.is_relative_to(ROOT), f'Body input outside repository: {relative}'
        if not resolved.is_file() or sha(resolved) != expected:
            failures.append(relative)
    assert not failures, f'Original body inputs changed, using archived package/document mappings: {failures}'
    return original


def compose_manifest() -> dict[str, str]:
    original = body_inputs()
    # Current citation documents/package govern the new appendix and future
    # full renders; their original body-era bytes remain independently checked.
    result = dict(original)
    result['remotion/package.json'] = sha(D / 'remotion/package.json')
    for relative in BODY_DOCUMENTS:
        result[relative] = sha(D / relative)
    refs = read(D / 'references.json')
    extras = [
        Path(__file__).resolve(),
        BODY_MANIFEST,
        BODY_PACKAGE,
        *BODY_DOCUMENTS.values(),
        ARCHIVE / 'body-provenance.json',
        D / 'references.json',
        D / 'references.md',
        ROOT / 'episodes-codex/_shared/render_with_references.py',
        ROOT / 'episodes-codex/_shared/append_references_bibliography.py',
        ROOT / 'episodes-codex/_shared/append_references_original.py',
        ROOT / 'episodes-codex/_shared/append_references.py',
        ROOT / 'episodes-codex/_shared/requirements-reference-appendix.txt',
        ROOT / 'site/scripts/check-references.mjs',
        ROOT / 'episodes-codex/_template/reference-scripts.json',
    ]
    for source in refs['sources']:
        records = [source['verification'], source['titleEvidence']]
        if 'quotation' in source:
            records.append(source['quotation'])
        for record in records:
            evidence = record['evidence']
            assert isinstance(evidence, str) and not Path(evidence).is_absolute()
            extras.append(ROOT / evidence)
    for path in extras:
        path = path.resolve()
        assert path.is_relative_to(ROOT) and path.is_file(), f'Missing/outside input: {path}'
        result[os.path.relpath(path, D)] = sha(path)
    result = dict(sorted(result.items()))
    forbidden_names = {
        'video.mp4', 'body.mp4', 'voice.mp4', 'render-result.json',
        'reference-appendix.json', 'reference-appendix-media-check.json',
        'reference-inputs-sha256.json',
    }
    assert all(Path(relative).suffix != '.mp4' and Path(relative).name not in forbidden_names
               for relative in result), 'Rendered media/receipts must not be encoding inputs'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--verify', action='store_true', help='Read-only verify the current combination freeze')
    action.add_argument('--check-body', action='store_true', help='Read-only verify the original146 relocated body inputs')
    args = parser.parse_args()
    original = body_inputs()
    if args.check_body:
        print(json.dumps({'status': 'passed', 'originalBodyInputs': len(original),
                          'packageCheckedAt': str(BODY_PACKAGE.relative_to(D)),
                          'documentsCheckedAt': {name: str(path.relative_to(D))
                                                 for name, path in BODY_DOCUMENTS.items()},
                          'originalBodyManifestSHA256': BODY_MANIFEST_SHA256,
                          'bodyRenderRepeated': False}, ensure_ascii=False))
        return
    subprocess.run(['node', str(ROOT / 'site/scripts/check-references.mjs'),
                    '--sources', str(D)], cwd=ROOT, check=True)
    expected = compose_manifest()
    if args.verify:
        actual = read(MANIFEST)
        assert actual == expected, 'Current reference-orchestration manifest differs from its inputs'
    else:
        MANIFEST.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({
        'checkedAtUTC': datetime.now(timezone.utc).isoformat(),
        'status': 'passed' if args.verify else 'frozen',
        'scope': 'Reference appending/future default render orchestration; retained body uses archived146 inputs.',
        'inputs': len(expected),
        'originalBodyInputsVerified': len(original),
        'originalBodyManifestSHA256': BODY_MANIFEST_SHA256,
        'currentPackageSHA256': expected['remotion/package.json'],
        'oldPackageSnapshotSHA256': sha(BODY_PACKAGE),
        'oldDocumentSnapshotSHA256': {name: sha(path) for name, path in BODY_DOCUMENTS.items()},
        'manifestSHA256': sha(MANIFEST),
        'bodyRenderRepeated': False,
        'renderedOutputsIncluded': False,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
