#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/workspace/.venvs/video-studio/bin:$PATH"
flock /tmp/video-studio-render.lock python3 render.py .
