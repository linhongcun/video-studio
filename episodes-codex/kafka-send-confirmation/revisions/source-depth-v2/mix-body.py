from pathlib import Path
import subprocess,sys
D=Path(__file__).resolve().parent
ROOT=next(p for p in D.parents if (p/'AGENTS.md').is_file())
subprocess.run([sys.executable,str(ROOT/'episodes/_shared/music/mix_bgm.py'),'--in',str(D/'remotion/out/voice-bt709.mp4'),'--bgm',str(ROOT/'episodes/_shared/music/Wallpaper.mp3'),'--mode','constant','--below','12','--out',str(D/'remotion/out/body.mp4'),'--report',str(D/'remotion/out/mix-report.json')],cwd=ROOT,check=True)
