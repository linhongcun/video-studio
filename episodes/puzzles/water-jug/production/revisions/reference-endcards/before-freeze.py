#!/usr/bin/env python3
"""Delegate to the shared sentence freezer and pin P03-specific inputs."""
from pathlib import Path
import hashlib
import json
import os
import runpy
import sys
D = Path(__file__).resolve().parent
ROOT = D.parents[1]
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
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
    extra = [Path(__file__).resolve(), D/'assemble.py', D/'research-math.md', D/'verify_math.py']
    extra += [p for p in (D/'remotion/scripts').rglob('*')
              if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    for p in extra:
        manifest[os.path.relpath(p, D)] = digest(p)
    (D/'source-sha256.json').write_text(json.dumps(dict(sorted(manifest.items())),
                                                ensure_ascii=False, indent=2)+'\n')
    print(f'{len(manifest)} P03 production inputs frozen')
