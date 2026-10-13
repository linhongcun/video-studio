#!/bin/sh
# 一键重跑（第十三期）：sh run.sh [timing 路径]（默认 /workspace/share/ep13-timing.json）；文件不存在则回退暂定 timing（make_timing.py）
set -e; cd "$(dirname "$0")"; export PYTHONDONTWRITEBYTECODE=1
T="${1:-/workspace/share/ep13-timing.json}"
if [ -f "$T" ]; then cp "$T" timing.mimo.json && python3 -B map_timing.py
else echo "timing 不存在：$T → 用暂定 timing"; rm -f timing.mimo.json; python3 -B make_timing.py; fi
python3 -B gen.py && python3 -B validate.py
