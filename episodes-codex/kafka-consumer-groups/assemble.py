#!/usr/bin/env python3
"""Assemble sentence timing without copying the shared onset/timing algorithm."""
from pathlib import Path
import subprocess
import sys

D = Path(__file__).resolve().parent
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file() and (p / 'site/package.json').is_file())
subprocess.run([sys.executable, str(ROOT / 'episodes-codex/_shared/assemble_sentence_episode.py'), str(D)], check=True)

import json
import hashlib
board = D / 'storyboard.json'
original = board.read_bytes()
value = json.loads(original)
config = json.loads((D / 'episode-config.json').read_text())
style = json.loads((ROOT / 'episodes-codex/_shared/kafka-covers/style-v1.json').read_text())
value['meta']['palette'] = {'bg': style['palette']['background'], 'text': style['palette']['text']}
value['meta']['sampleDataLabel'] = config['sampleDataLabel']
value['meta']['styleContract'] = 'episodes-codex/_shared/kafka-covers/style-v1.json'
board.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
(D / 'storyboard-metadata-adaptation.json').write_text(json.dumps({'sharedAssemblySHA256': hashlib.sha256(original).hexdigest(), 'adaptedSHA256': hashlib.sha256(board.read_bytes()).hexdigest(), 'changedFields': ['meta.palette', 'meta.sampleDataLabel', 'meta.styleContract'], 'timingOrNarrationChanged': False}, ensure_ascii=False, indent=2)+'\n')
