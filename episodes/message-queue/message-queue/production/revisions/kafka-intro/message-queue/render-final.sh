#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/workspace/.venvs/video-studio/bin:$PATH"
python3 freeze.py --verify
npm --prefix remotion run check:types
flock /tmp/video-studio-render.lock npm --prefix remotion run render
python3 freeze.py --verify
python3 verify.py --final
