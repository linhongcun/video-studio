#!/usr/bin/env python3
"""Run the current binary-opening site check, writing only revision evidence.

Use after the approved revised media is synced and the new site build passes:
python episodes-codex/egg-drop/revisions/binary-opening/verify_site.py \
  --release vX.Y.Z --base http://127.0.0.1:4398/video-studio/
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from verify_site import main


if __name__ == '__main__':
    main()
