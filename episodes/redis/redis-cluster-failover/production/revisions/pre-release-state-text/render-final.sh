#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/workspace/.venvs/video-studio/bin:$PATH"
python3 fonts.py --verify
python3 freeze.py --verify
flock /tmp/video-studio-render.lock bash -c 'cd remotion && npm run render'
python3 freeze.py --verify
