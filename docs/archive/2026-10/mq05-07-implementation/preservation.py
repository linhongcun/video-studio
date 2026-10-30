#!/usr/bin/env python3
"""Snapshot or verify existing publication and previous MQ frozen inputs."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse
import hashlib
import json
import subprocess

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
HERE = Path(__file__).resolve().parent
BASELINE = HERE / 'baseline.json'
OLD_SLUGS = ['message-queue', 'kafka-consumer-groups', 'kafka-log-replay', 'kafka-send-confirmation']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', action='store_true')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    assert args.snapshot != args.verify
    if args.snapshot:
        assert not BASELINE.exists(), 'Do not overwrite startup evidence'
        old = json.loads((HERE.parent / 'mq-source-depth-remake/baseline.json').read_text())
        paths = {ROOT / p for p in old['frozenPhysicalInputs']}
        for slug in OLD_SLUGS:
            d = ROOT / 'episodes-codex' / slug / 'revisions/source-depth-v2'
            paths.update((d / rel).resolve() for rel in json.loads((d / 'source-sha256.json').read_text()))
        physical = {str(p.relative_to(ROOT)): {'sha256': sha(p), 'mtimeNs': p.stat().st_mtime_ns} for p in sorted(paths)}
        blobs = {}
        for row in subprocess.check_output(['git', 'ls-files', '-s', '--', 'episodes'], cwd=ROOT, text=True).splitlines():
            mode, digest, stage, relative = row.split(maxsplit=3)
            assert stage == '0'
            blobs[relative] = digest
        data = {'base': subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True).strip(),
                'branch': 'codex/mq05-07-implementation-20261030',
                'createdAtBeijing': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
                'scope': 'Existing publication files and prior MQ production remain unchanged; new episodes are additional paths.',
                'protectedGitBlobs': blobs, 'frozenPhysicalInputs': physical}
        BASELINE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'baseline': data['base'], 'publishedFiles': len(blobs), 'oldFrozenPhysicalInputs': len(physical),
                          'oldCoverRendererFrozen': 'episodes-codex/_shared/kafka-covers/render.py' in physical,
                          'growingCatalogFrozen': 'episodes-codex/_shared/kafka-covers/catalog.json' in physical}))
        return
    assert args.out, 'Write verification evidence to an explicit new path'
    baseline = json.loads(BASELINE.read_text())
    errors = []
    for rel, expected in baseline['frozenPhysicalInputs'].items():
        p = ROOT / rel
        if not p.is_file() or sha(p) != expected['sha256']:
            errors.append({'file': rel, 'failure': 'old frozen bytes changed or missing'})
        elif p.stat().st_mtime_ns != expected['mtimeNs']:
            errors.append({'file': rel, 'failure': 'old frozen mtime changed'})
    paths = list(baseline['protectedGitBlobs'])
    actual = subprocess.check_output(['git', 'hash-object', '--stdin-paths'], input='\n'.join(paths) + '\n', cwd=ROOT, text=True).splitlines()
    assert len(actual) == len(paths)
    for rel, digest in zip(paths, actual):
        if digest != baseline['protectedGitBlobs'][rel]:
            errors.append({'file': rel, 'failure': 'existing publication bytes changed'})
    report = {'passed': not errors, 'readOnly': True, 'baseline': baseline['base'],
              'oldFrozenPhysicalInputs': len(baseline['frozenPhysicalInputs']),
              'existingPublicationFiles': len(paths), 'errors': errors}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    assert not errors, errors[:10]
    print(json.dumps({k: v for k, v in report.items() if k != 'errors'}))


if __name__ == '__main__':
    main()
