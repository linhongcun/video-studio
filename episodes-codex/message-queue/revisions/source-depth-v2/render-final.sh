#!/usr/bin/env bash
set -euo pipefail
MQ01_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 "$MQ01_DIR/render.py" "$MQ01_DIR"
