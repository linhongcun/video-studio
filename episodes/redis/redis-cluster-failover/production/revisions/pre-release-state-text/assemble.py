#!/usr/bin/env python3
"""Thin local entry; use the current shared sentence assembly/placement/onset tools."""
from pathlib import Path
import subprocess,sys,json
D=Path(__file__).resolve().parent
ROOT=next(p for p in D.parents if (p/'AGENTS.md').is_file())
subprocess.run([sys.executable,str(ROOT/'episodes/_shared/assemble_sentence_episode.py'),str(D)],cwd=ROOT,check=True)
board=json.loads((D/'storyboard.json').read_text());board['meta']['palette']=json.loads((ROOT/'episodes/_shared/redis-video/style-v1.json').read_text())['palette'];(D/'storyboard.json').write_text(json.dumps(board,ensure_ascii=False,indent=2)+'\n')
for file,args in [('place_v2.py',['--dir',str(D),'--mode','whole']),('label_onset_strict.py',['--dir',str(D)])]:
    subprocess.run([sys.executable,str(ROOT/'episodes/_shared'/file),*args],cwd=ROOT,check=True)
