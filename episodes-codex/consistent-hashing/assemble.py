#!/usr/bin/env python3
"""Forward this episode to the shared sentence assembler; no timing algorithms."""
from pathlib import Path
import runpy
import sys
D = Path(__file__).resolve().parent
SHARED = D.parents[1] / 'episodes-codex/_shared/assemble_sentence_episode.py'
if __name__ == '__main__':
    sys.argv = [str(SHARED), str(D)]
    runpy.run_path(str(SHARED), run_name='__main__')
    (D / 'subtitles.srt').write_bytes((D / 'captions.srt').read_bytes())
