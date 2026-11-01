from pathlib import Path
import subprocess
D=Path(__file__).resolve().parent
ROOT=next(p for p in D.parents if (p/'AGENTS.md').is_file())
subprocess.run(['node',str(D/'check-references.mjs'),'--sources',str(D)],cwd=ROOT,check=True)
