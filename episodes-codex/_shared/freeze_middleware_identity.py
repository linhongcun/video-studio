"""Extend an episode's current freezer with the middleware identity assets.

Existing freezers and already released shared inputs stay unchanged. Preserve
the database identity wrapper where the episode already uses that component.
"""
from pathlib import Path
import hashlib
import json
import os
import runpy
import sys

assert len(sys.argv) == 2, 'Usage: freeze_middleware_identity.py EPDIR'
D = Path(sys.argv[1]).resolve()
ROOT = Path(__file__).resolve().parents[2]
previous = json.loads((D / 'source-sha256.json').read_text())
if any('database-identity/' in rel for rel in previous):
    freezer = ROOT / 'episodes-codex/_shared/freeze_database_identity.py'
    delegate_argv = [str(freezer), str(D)]
elif (D / 'freeze.py').is_file():
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
extra += [p for p in (ROOT / 'episodes-codex/_shared/middleware-identity').iterdir()
          if p.is_file()]
for p in extra:
    manifest[os.path.relpath(p, D)] = hashlib.sha256(p.read_bytes()).hexdigest()
(D / 'source-sha256.json').write_text(json.dumps(
    dict(sorted(manifest.items())), ensure_ascii=False, indent=2) + '\n')
print(f'{len(manifest)} inputs frozen including middleware identity and original artwork')
