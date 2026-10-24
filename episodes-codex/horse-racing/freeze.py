#!/usr/bin/env python3
"""Use the shared freezer, then include P01 mathematical and rendering-script inputs."""
from pathlib import Path
import hashlib
import json
import os
import runpy
import sys

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1:] == ['--verify']:
    manifest = json.loads((D/'source-sha256.json').read_text())
    mismatches = [rel for rel, sha in manifest.items()
                  if not (D/rel).is_file() or digest(D/rel) != sha]
    assert not mismatches, mismatches
    print(json.dumps({'inputs': len(manifest), 'status': 'passed'}, ensure_ascii=False))
else:
    assert not sys.argv[1:], 'Usage: freeze.py [--verify]'
    sys.argv = [str(ROOT/'episodes-codex/_shared/freeze_sentence_episode.py'), str(D)]
    runpy.run_path(sys.argv[0], run_name='__main__')
    manifest = json.loads((D/'source-sha256.json').read_text())
    extra = [Path(__file__).resolve(), D/'research-math.md', D/'verify_math.py']
    extra += [p for p in (D/'remotion/scripts').rglob('*') if p.is_file()]
    for p in extra:
        manifest[os.path.relpath(p, D)] = digest(p)
    (D/'source-sha256.json').write_text(json.dumps(dict(sorted(manifest.items())),
                                                ensure_ascii=False, indent=2)+'\n')
    print(f'{len(manifest)} P01 production inputs frozen')

