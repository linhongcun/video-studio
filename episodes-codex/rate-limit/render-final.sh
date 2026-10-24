#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/remotion"
export PATH="/workspace/.venvs/video-studio/bin:$PATH"
python ../freeze.py --verify
npx tsc --noEmit
npm run render
python ../freeze.py --verify
python ../verify.py --final
