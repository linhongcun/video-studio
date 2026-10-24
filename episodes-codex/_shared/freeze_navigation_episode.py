"""Freeze navigation dependencies without changing other episodes' freezer.

The canonical freezer is itself pinned by already released episodes. Delegate
to it, then record only this navigation production's additional dependencies.
"""
from pathlib import Path
import hashlib
import json
import os
import runpy
import sys

assert len(sys.argv) == 2, 'Usage: freeze_navigation_episode.py EPDIR'
D = Path(sys.argv[1]).resolve()
ROOT = Path(__file__).resolve().parents[2]
assert (D/'remotion/src/branch-map.ts').is_file(), 'Use the canonical freezer for episodes without this navigator'
runpy.run_path(str(ROOT/'episodes-codex/_shared/freeze_sentence_episode.py'), run_name='__main__')
manifest = json.loads((D/'source-sha256.json').read_text())
extra = [Path(__file__).resolve()]
extra += [p for p in (ROOT/'episodes-codex/_shared/branch-map').rglob('*')
          if p.is_file() and p.suffix in {'.ts', '.tsx', '.json'}]
for p in extra:
    manifest[os.path.relpath(p, D)] = hashlib.sha256(p.read_bytes()).hexdigest()
(D/'source-sha256.json').write_text(json.dumps(dict(sorted(manifest.items())), ensure_ascii=False, indent=2)+'\n')
print(f'{len(manifest)} inputs frozen with navigation dependencies')
