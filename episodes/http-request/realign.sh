#!/bin/sh
# 2026-10-14 内容核对重配音对齐（Miyazaki）：sh realign.sh [timing 路径]
# 默认读 Knoll 冰糖重配音（pad10 已转正）/workspace/knoll-audit-revoice/ep1/ep1-timing.json（只读）；不会回退到 /workspace/share。
set -e; cd "$(dirname "$0")"; export PYTHONDONTWRITEBYTECODE=1
T="${1:-/workspace/knoll-audit-revoice/ep1/ep1-timing.json}"; [ -f "$T" ] || { echo "timing 不存在：$T" >&2; exit 1; }
echo "timing: $T"
# 标签修正可能加 hold（label_holds.json，align.py 在镜头末尾加静音）→ 退出码 3 时重跑，最多 4 轮
for i in 1 2 3 4; do
  cp "$T" timing.json && python3 -B gen.py >/dev/null
  rc=0; python3 -B ../_audit/labelfix.py . || rc=$?
  [ $rc = 3 ] || break
done
[ $rc = 0 ] || [ $rc = 3 ] || exit $rc
python3 -B gen.py | tail -1 && python3 -B ../_audit/labelfix.py . >/dev/null; python3 -B validate.py && python3 -B ../_audit/fullshow.py .
