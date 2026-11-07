#!/usr/bin/env python3
"""Delegate all trimming, normalization and assembly to the existing shared voice builder."""
from pathlib import Path
import json
import subprocess
import sys
from voice_reuse import validate_reuse

D = Path(__file__).resolve().parent
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file())
validate_reuse(require_new_takes=True)
subprocess.run([sys.executable, str(ROOT / 'episodes/_shared/voice/build.py'), '--dir', str(D)], check=True)
report = validate_reuse(require_new_takes=True)
(D / 'voice/reuse-check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
