#!/usr/bin/env python3
"""Read-only current input checks; final media verification is explicitly separate."""
from pathlib import Path
import argparse,json,subprocess,sys
D=Path(__file__).resolve().parent
ROOT=next(p for p in D.parents if (p/'AGENTS.md').is_file())
p=argparse.ArgumentParser(__doc__);p.add_argument('--final',action='store_true');a=p.parse_args()
subprocess.run([sys.executable,str(D/'fonts.py'),'--verify'],check=True)
subprocess.run(['node',str(D/'check-references.mjs'),'--sources',str(D)],check=True)
subprocess.run([sys.executable,str(ROOT/'episodes/_shared/check_sentence_episode.py'),str(D)],cwd=ROOT,check=True)
if (D/'source-sha256.json').exists():subprocess.run([sys.executable,str(D/'freeze.py'),'--verify'],cwd=ROOT,check=True)
if a.final:
    subprocess.run([sys.executable,str(D/'render.py'),str(D),'--verify'],cwd=ROOT,check=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(D/'video.mp4'),'-f','null','-'],check=True)
print(json.dumps(dict(passed=True,scope='references/current sentence inputs/fonts'+('/final appendix identity and complete decode' if a.final else ''),limits='Not semantic ASR, full human listening, independent visual or website acceptance.')))
