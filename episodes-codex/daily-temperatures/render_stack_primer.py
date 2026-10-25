"""Assemble reviewed new intervals and old pictures with the shared splice tool."""
from pathlib import Path
import json,subprocess,sys,shutil
EP=Path(__file__).resolve().parent;ROOT=EP.parents[1]
subprocess.run([sys.executable,str(EP/'freeze.py'),'--verify'],check=True)
subprocess.run([sys.executable,str(ROOT/'episodes-codex/_shared/remix_approach.py'),str(EP),'--run','--plan',str(EP/'stack-primer-remix-plan.json'),'--overwrite-output'],check=True)
subprocess.run(['npm','run','render:mix'],cwd=EP/'remotion',check=True)
shutil.copy2(EP/'remotion/out/mix-report.json',EP/'mix-report.json')
