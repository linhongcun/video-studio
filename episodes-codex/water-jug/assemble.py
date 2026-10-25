#!/usr/bin/env python3
"""P03 wrapper around the shared sentence assembler; no timing algorithms."""
from pathlib import Path
import runpy
import sys


EPISODE = Path(__file__).resolve().parent
SHARED = EPISODE.parents[1] / 'episodes-codex/_shared/assemble_sentence_episode.py'

if __name__ == '__main__':
    previous_argv = sys.argv[:]
    try:
        sys.argv = [str(SHARED), str(EPISODE)]
        runpy.run_path(str(SHARED), run_name='__main__')
    finally:
        sys.argv = previous_argv
    # Keep the shared output and the site-facing name byte-identical.
    (EPISODE / 'subtitles.srt').write_bytes((EPISODE / 'captions.srt').read_bytes())
