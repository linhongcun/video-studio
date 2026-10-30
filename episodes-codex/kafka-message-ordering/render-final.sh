#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/remotion"
flock /tmp/video-studio-render.lock npm run render
