#!/usr/bin/env python3
"""Generate only the two finalized04 sentence jobs with the unmodified shared TTS tool."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
from voice_reuse import validate_reuse

D = Path(__file__).resolve().parent
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file())
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--jobs', type=Path, default=D / 'voice/jobs-motivation.json')
args = parser.parse_args()
jobs = args.jobs.resolve()
validate_reuse()
rows = json.loads(jobs.read_text())
assert len(rows) == 2 and {row[0] for row in rows} == {'04-backwards-1', '04-backwards-2'}, 'Only04 replacement jobs are authorized in this revision'
subprocess.run([sys.executable, str(ROOT / 'episodes/_shared/voice/gen.py'),
                '--dir', str(D), '--jobs', str(jobs)], check=True)
validate_reuse(require_new_takes=True)
