"""Thin entry point for this checked pattern-flow revision and Java tail."""
from pathlib import Path
import runpy
import sys
D = Path(__file__).resolve().parent
ROOT = D.parents[1]
verify = '--verify' in sys.argv
helper = ROOT / 'episodes-codex/_shared/freeze_pattern_flow_episode.py'
sys.argv = [str(helper), str(D)] + (['--verify'] if verify else [])
runpy.run_path(str(helper), run_name='__main__')
