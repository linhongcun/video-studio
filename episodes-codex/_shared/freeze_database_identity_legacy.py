"""Freeze reviewed identity edits in older projects without sentence episode configs."""
from pathlib import Path
import hashlib
import json
import os
import sys

assert len(sys.argv) == 2, 'Usage: freeze_database_identity_legacy.py EPDIR'
D = Path(sys.argv[1]).resolve()
ROOT = Path(__file__).resolve().parents[2]
allowed = {'db-replication': 'remotion/src/Main.tsx',
           'db-transaction': 'remotion/src/MotionParts.tsx',
           'db-sharding': 'remotion/src/Main.tsx'}
assert D.name in allowed
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
old = json.loads((D / 'source-sha256.json').read_text())
for rel, expected in old.items():
    assert (D / rel).is_file(), rel
    if rel != allowed[D.name]:
        assert sha(D / rel) == expected, f'Unreviewed input change: {rel}'
sb = json.loads((D / 'storyboard.json').read_text())
words = json.loads((D / 'words.json').read_text())
assert words['scriptSha256'] == sha(D / 'script.md')
assert words['audioSha256'] == sha(D / 'voice.wav')
assert sb['meta']['durationInFrames'] == words['durationFrames']
files = [D / rel for rel in old]
files += [p for p in (D / 'remotion/src').rglob('*') if p.is_file()]
files += [D / 'remotion' / name for name in ['package.json', 'package-lock.json', 'tsconfig.json', 'remotion.config.ts', 'public/audio/voice.wav']]
files += [p for p in (ROOT / 'episodes-codex/_shared/database-identity').iterdir() if p.is_file()]
files += [Path(__file__).resolve()]
manifest = {os.path.relpath(p, D): sha(p) for p in sorted(set(files))}
(D / 'source-sha256.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(f'{len(manifest)} legacy inputs frozen with reviewed identity source and MySQL artwork')
