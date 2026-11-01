#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/remotion"
export PATH="/workspace/.venvs/video-studio/bin:$PATH"
python ../../../../episodes-codex/freeze.py --verify
npx tsc --noEmit
npm run render
python ../../../../episodes-codex/freeze.py --verify
python ../../../../episodes-codex/verify.py --final
