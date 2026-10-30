#!/usr/bin/env python3
"""Read-only verification of old production inputs and published identities."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--installed', action='store_true')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    baseline = json.loads((HERE / 'baseline.json').read_text())
    errors = []
    allowed = {}
    if args.installed:
        publication = json.loads((HERE / 'publication-files.json').read_text())
        for episode in publication['episodes']:
            for name, expected in episode['files'].items():
                assert not Path(name).name.startswith('cover-') and name != 'cover-style.json'
                allowed[f"episodes/{episode['slug']}/{name}"] = expected
    for rel, expected in baseline['frozenPhysicalInputs'].items():
        p = ROOT / rel
        if not p.is_file():
            errors.append({'path': rel, 'failure': 'missing frozen input'})
            continue
        if hashlib.sha256(p.read_bytes()).hexdigest() != expected['sha256']:
            errors.append({'path': rel, 'failure': 'frozen input bytes changed'})
        if p.stat().st_mtime_ns != expected['mtimeNs']:
            errors.append({'path': rel, 'failure': 'frozen input mtime changed'})
    publication_changes = []
    for rel, expected in baseline['protectedGitBlobs'].items():
        p = ROOT / rel
        actual = subprocess.check_output(['git', 'hash-object', str(p)], cwd=ROOT, text=True).strip() if p.is_file() else None
        if actual != expected:
            if args.installed and rel in allowed and p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == allowed[rel]:
                publication_changes.append(rel)
            else:
                errors.append({'path': rel, 'failure': 'old protected Git blob changed'})
    before = json.loads((HERE / 'publication-before.json').read_text())
    for slug, old in before.items():
        current = json.loads((ROOT / 'episodes' / slug / 'meta.json').read_text())
        for key in ['ep', 'slug', 'title', 'createdAt', 'publishedAt', 'firstRelease', 'platforms', 'poster']:
            if current.get(key) != old.get(key):
                errors.append({'path': f'episodes/{slug}/meta.json', 'failure': 'identity changed', 'key': key})
    report = {'passed': not errors, 'readOnly': True, 'baseline': baseline['base'],
              'physicalFrozenInputs': len(baseline['frozenPhysicalInputs']),
              'protectedGitBlobs': len(baseline['protectedGitBlobs']),
              'intentionalPublicationChanges': publication_changes, 'errors': errors}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    assert not errors, errors[:10]
    print(json.dumps({'passed': True, 'frozenInputs': report['physicalFrozenInputs'],
                      'oldGitBlobs': report['protectedGitBlobs'],
                      'intentionalPublicationChanges': len(publication_changes)}))


if __name__ == '__main__':
    main()
