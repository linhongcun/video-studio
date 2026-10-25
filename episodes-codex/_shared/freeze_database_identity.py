"""Extend this batch's existing freezer with the database identity artwork."""
from pathlib import Path
import hashlib
import json
import os
import runpy
import sys

assert len(sys.argv) == 2, 'Usage: freeze_database_identity.py EPDIR'
D = Path(sys.argv[1]).resolve()
ROOT = Path(__file__).resolve().parents[2]
if (D / 'freeze.py').is_file():
    freezer = D / 'freeze.py'
    delegate_argv = [str(freezer)]
elif (D / 'remotion/src/branch-map.ts').is_file():
    freezer = ROOT / 'episodes-codex/_shared/freeze_navigation_episode.py'
    delegate_argv = [str(freezer), str(D)]
else:
    freezer = ROOT / 'episodes-codex/_shared/freeze_sentence_episode.py'
    delegate_argv = [str(freezer), str(D)]
sys.argv = delegate_argv
runpy.run_path(str(freezer), run_name='__main__')
manifest = json.loads((D / 'source-sha256.json').read_text())
extra = [Path(__file__).resolve()]
extra += [p for p in (ROOT / 'episodes-codex/_shared/database-identity').iterdir() if p.is_file()]
for p in extra:
    manifest[os.path.relpath(p, D)] = hashlib.sha256(p.read_bytes()).hexdigest()
(D / 'source-sha256.json').write_text(json.dumps(dict(sorted(manifest.items())), ensure_ascii=False, indent=2) + '\n')
print(f'{len(manifest)} frozen inputs including MySQL artwork and identity component')
