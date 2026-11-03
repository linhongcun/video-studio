#!/usr/bin/env python3
"""Delegate measured sentence assembly, then declare the actual purple canvas."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

D = Path(__file__).resolve().parent
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file() and (p / 'site/package.json').is_file())
subprocess.run([sys.executable, str(ROOT / 'episodes/_shared/assemble_sentence_episode.py'), str(D)], check=True)
board = D / 'storyboard.json'
original = board.read_bytes()
value = json.loads(original)
palette = json.loads((ROOT / 'episodes/_shared/puzzles-covers/catalog.json').read_text())['palette']
value['meta']['palette'] = {'bg': palette['background'], 'text': palette['text']}
value['meta']['styleContract'] = 'episodes/_shared/puzzles-video/theme.ts'
board.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
(D / 'storyboard-metadata-adaptation.json').write_text(json.dumps({
    'sharedAssemblySHA256': hashlib.sha256(original).hexdigest(),
    'adaptedSHA256': hashlib.sha256(board.read_bytes()).hexdigest(),
    'changedFields': ['meta.palette', 'meta.styleContract'],
    'timingOrNarrationChanged': False,
}, ensure_ascii=False, indent=2) + '\n')
