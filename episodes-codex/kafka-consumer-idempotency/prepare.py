#!/usr/bin/env python3
"""Prepare this episode's sentences with the unmodified shared voice tool."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

D = Path(__file__).resolve().parent
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file() and (p / 'site/package.json').is_file())
subprocess.run([sys.executable, str(ROOT / 'episodes/_shared/voice/prep.py'), '--dir', str(D)], check=True)
script = (D / 'script.md').read_bytes()
narration = ''.join(re.findall(r'^旁白：(.*)$', script.decode(), re.M))
sentences = json.loads((D / 'voice/sents.json').read_text())
report = {'scriptSHA256': hashlib.sha256(script).hexdigest(),
          'narrationSHA256': hashlib.sha256(narration.encode()).hexdigest(),
          'sentenceCount': len(sentences),
          'definition': 'Full current script bytes and concatenated exact narration lines; no inferred word timings or voice QA claim.'}
(D / 'voice/script-narration-sha256.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
