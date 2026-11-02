#!/usr/bin/env python3
"""Protect current migrated production/publication bytes and file mtimes."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse
import hashlib
import json
import os
import subprocess

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
A = Path(__file__).resolve().parent
BASELINE = A / 'baseline.json'
PUBLICATION = 'episodes/message-queue/kafka-consumer-idempotency/publication/'
REPLACE_FILES = {'article-sources.json', 'article.mdx', 'meta.json', 'pronunciation.md', 'reference-appendix-media-check.json', 'reference-appendix.json', 'references.json', 'script.md', 'storyboard.json', 'video.mp4', 'words.json'}


def identity(path):
    raw = os.fsencode(os.readlink(path)) if path.is_symlink() else path.read_bytes()
    return {'gitBlob': hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest(),
            'sha256': hashlib.sha256(raw).hexdigest(), 'mtimeNs': path.lstat().st_mtime_ns}


def main():
    ap = argparse.ArgumentParser(__doc__)
    ap.add_argument('--snapshot', action='store_true')
    ap.add_argument('--verify', action='store_true')
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    assert args.snapshot != args.verify
    if args.snapshot:
        assert not BASELINE.exists(), 'Never overwrite an initial preservation baseline'
        rows = subprocess.check_output(['git', 'ls-tree', '-rz', 'HEAD', '--', 'episodes', 'site/src',
                                        'site/scripts', '.github', 'AGENTS.md'], cwd=ROOT).split(b'\0')
        files = {}
        for row in filter(None, rows):
            metadata, name = row.split(b'\t', 1)
            mode, kind, blob = metadata.decode().split()
            rel = os.fsdecode(name)
            if rel.startswith(PUBLICATION) and rel[len(PUBLICATION):] in REPLACE_FILES:
                continue  # Authorized replacement of this existing episode only.
            assert kind == 'blob'
            record = identity(ROOT / rel)
            assert record['gitBlob'] == blob, ('Baseline working bytes differ from fetched main', rel)
            files[rel] = {'gitMode': mode, **record}
        result = {'baseSHA': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  'branch': subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip(),
                  'startedAtBeijing': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'),
                  'layout': 'Post-migration current paths; no old-manifest expected hashes reinterpreted.',
                  'authorizedExistingEpisodeChanges': [PUBLICATION + p for p in sorted(REPLACE_FILES)],
                  'files': files}
        BASELINE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'snapshot': True, 'protectedFiles': len(files),
                          'publicationFiles': sum('/publication/' in p for p in files),
                          'baseSHA': result['baseSHA']}))
        return
    baseline = json.loads(BASELINE.read_text())
    failures = []
    for rel, expected in baseline['files'].items():
        p = ROOT / rel
        if not p.exists() and not p.is_symlink():
            failures.append({'path': rel, 'reason': 'missing'})
            continue
        actual = identity(p)
        for field in ['gitBlob', 'sha256', 'mtimeNs']:
            if actual[field] != expected[field]:
                failures.append({'path': rel, 'field': field})
    result = {'passed': not failures, 'readOnly': True, 'baseSHA': baseline['baseSHA'],
              'protectedFiles': len(baseline['files']), 'failures': failures}
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        assert not args.out.exists(), 'Preserve every prior verification attempt'
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result))
    assert not failures, 'Protected pre-existing bytes or mtimes changed'


if __name__ == '__main__':
    main()
