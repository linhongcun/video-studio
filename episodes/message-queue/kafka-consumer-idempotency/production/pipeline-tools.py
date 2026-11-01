#!/usr/bin/env python3
"""Resolve shared production dependencies from this episode root."""
from pathlib import Path
import subprocess,sys
D=Path(__file__).resolve().parent
ROOT=next(p for p in D.parents if (p/'AGENTS.md').is_file() and (p/'site/package.json').is_file())
if sys.argv[1]=='references':
 subprocess.run(['node',str(D/'check-references.mjs'),'--sources',str(D)],cwd=ROOT,check=True)
elif sys.argv[1]=='mix':
 subprocess.run([sys.executable,str(ROOT/'episodes/_shared/music/mix_bgm.py'),'--in',str(D/'remotion/out/voice-bt709.mp4'),'--bgm',str(ROOT/'episodes/_shared/music/Wallpaper.mp3'),'--mode','constant','--below','12','--out',str(D/'remotion/out/body.mp4'),'--report',str(D/'remotion/out/mix-report.json')],check=True)
else:raise SystemExit('Choose references or mix')
