#!/usr/bin/env python3
"""Freeze this Skills episode after all writers have stopped; verify is read-only."""
from pathlib import Path
import hashlib,json,os,runpy,sys
D=Path(__file__).resolve().parent
ROOT=D.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1:]==['--verify']:
    manifest=json.loads((D/'source-sha256.json').read_text())
    bad=[rel for rel,digest in manifest.items() if not (D/rel).is_file() or sha(D/rel)!=digest]
    assert not bad,bad
    print(json.dumps({'status':'passed','productionInputs':len(manifest)},ensure_ascii=False))
else:
    assert not sys.argv[1:],'Usage: freeze.py [--verify]'
    sys.argv=[str(ROOT/'episodes-codex/_shared/freeze_sentence_episode.py'),str(D)]
    runpy.run_path(sys.argv[0],run_name='__main__')
    manifest=json.loads((D/'source-sha256.json').read_text())
    extra=[Path(__file__).resolve(),D/'assemble.py']
    extra += [D/name for name in ['startup.json','research-demo.md'] if (D/name).is_file()]
    for directory in [D/'remotion/scripts',D/'demo']:
        extra += [p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    for p in extra:manifest[os.path.relpath(p,D)]=sha(p)
    (D/'source-sha256.json').write_text(json.dumps(dict(sorted(manifest.items())),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'productionInputs':len(manifest),'demoEvidence':'Skill package, fixtures, real script outputs and agent review are frozen','excluded':'Mutable QA, deployment records, README and encoded output'},ensure_ascii=False))
