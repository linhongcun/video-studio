"""Render the frozen voice and pictures; shared wrapper adds bibliography."""
from pathlib import Path
import shutil,subprocess,sys
EP=Path(__file__).resolve().parent;ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
subprocess.run([sys.executable,str(EP/'freeze.py'),'--verify'],check=True)
subprocess.run(['npm','run','render:voice'],cwd=EP/'remotion',check=True)
subprocess.run(['npm','run','render:mix'],cwd=EP/'remotion',check=True)
shutil.copy2(EP/'remotion/out/mix-report.json',EP/'mix-report.json')
publication=EP/'video.mp4';prior=EP/'remotion/out/prior-publication.mp4'
has_receipt=(EP/'revisions/reference-endcards/reference-appendix.json').is_file()
if has_receipt and publication.is_file():shutil.copy2(publication,prior)
shutil.copy2(EP/'remotion/out/body.mp4',publication)
subprocess.run([sys.executable,str(ROOT/'episodes/_shared/check_encoded_episode.py'),str(EP)],check=True)
shutil.copy2(EP/'render-result.json',EP/'body-render-result.json')
if has_receipt:shutil.copy2(prior,publication)
