"""Reviewed body splice; the default shared wrapper adds the bibliography."""
from pathlib import Path
import json
import shutil
import subprocess
import sys

EP = Path(__file__).resolve().parent
ROOT = EP.parents[1]
subprocess.run([sys.executable, str(EP / 'freeze.py'), '--verify'], check=True)
subprocess.run([sys.executable, str(ROOT / 'episodes-codex/_shared/remix_approach.py'),
                str(EP), '--run', '--plan', str(EP / 'problem-fit-remix-plan.json'),
                '--overwrite-output'], check=True)
subprocess.run(['npm', 'run', 'render:mix'], cwd=EP / 'remotion', check=True)
shutil.copy2(EP / 'remotion/out/mix-report.json', EP / 'mix-report.json')
publication = EP / 'video.mp4'
previous = EP / 'remotion/out/prior-problem-fit-publication.mp4'
has_receipt = (EP / 'revisions/reference-endcards/reference-appendix.json').is_file()
if has_receipt and publication.is_file():
    shutil.copy2(publication, previous)
shutil.copy2(EP / 'remotion/out/body.mp4', publication)
subprocess.run([sys.executable, str(ROOT / 'episodes-codex/_shared/check_encoded_episode.py'), str(EP)], check=True)
shutil.copy2(EP / 'render-result.json', EP / 'body-render-result.json')
if has_receipt:
    shutil.copy2(previous, publication)
