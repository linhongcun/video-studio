#!/usr/bin/env python3
"""Generate only the three finalized03/04 sentence jobs with the unmodified shared TTS tool."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
from voice_reuse import validate_reuse

D = Path(__file__).resolve().parent
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file())
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--jobs', type=Path, default=D / 'voice/jobs-logic.json')
args = parser.parse_args()
jobs = args.jobs.resolve()
validate_reuse()
rows = json.loads(jobs.read_text())
assert len(rows) == 3 and {row[0] for row in rows} == {'03-assign-roles-1', '04-send-once-1', '04-send-once-2'}, 'Only the three declared03/04 replacement jobs are authorized in this revision'
picks = json.loads((D / 'voice/picks.json').read_text())
assert all(row[1] == picks[row[0]] and row[2] is None for row in rows), 'Generate the selected replacement labels from prepared text only'
subprocess.run([sys.executable, str(ROOT / 'episodes/_shared/voice/gen.py'),
                '--dir', str(D), '--jobs', str(jobs)], check=True)
validate_reuse(require_new_takes=True)
