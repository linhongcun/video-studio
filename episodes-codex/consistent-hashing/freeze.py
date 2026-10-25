#!/usr/bin/env python3
"""Freeze the actual current episode inputs through the shared freezer."""
from pathlib import Path
import hashlib, json, os, runpy, sys
D = Path(__file__).resolve().parent
ROOT = D.parents[1]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
if sys.argv[1:] == ['--verify']:
    manifest = json.loads((D/'source-sha256.json').read_text())
    failures = [rel for rel, digest in manifest.items() if not (D/rel).is_file() or sha(D/rel) != digest]
    assert not failures, failures
    print(json.dumps({'status':'passed','inputs':len(manifest)}))
else:
    assert not sys.argv[1:], 'Usage: freeze.py [--verify]'
    sys.argv = [str(ROOT/'episodes-codex/_shared/freeze_sentence_episode.py'), str(D)]
    runpy.run_path(sys.argv[0],run_name='__main__')
    manifest = json.loads((D/'source-sha256.json').read_text())
    extras = [Path(__file__).resolve(), D/'assemble.py', D/'voice/input-provenance.json', D/'model.json', D/'voice/audit_takes.py']
    extras += [p for p in (D/'remotion/scripts').rglob('*') if p.is_file()]
    extras += list((D/'voice').glob('jobs*.json'))
    extras += [p for p in D.glob('*.py') if p.name != 'freeze.py']
    for path in extras:
        if path.is_file(): manifest[os.path.relpath(path,D)] = sha(path)
    (D/'source-sha256.json').write_text(json.dumps(dict(sorted(manifest.items())),ensure_ascii=False,indent=2)+'\n')
    print(f'{len(manifest)} current production inputs frozen')
