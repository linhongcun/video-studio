#!/usr/bin/env python3
"""Assemble sentence timing without copying the shared onset/timing algorithm."""
from pathlib import Path
import subprocess
import sys

D = Path(__file__).resolve().parent
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file() and (p / 'site/package.json').is_file())
subprocess.run([sys.executable, str(ROOT / 'episodes-codex/_shared/assemble_sentence_episode.py'), str(D)], check=True)
