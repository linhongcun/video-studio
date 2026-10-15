#!/bin/sh
# EP.17 数据库锁（Miyazaki）：sh realign.sh [Knoll timing 路径]
# 默认读 Knoll 的 /workspace/share/ep17/timeline.json（只读）；不存在 → 用暂定估算 timing（make_timing.py，provisionalTiming=true）；words.json 没到时 asr_words.json 为空，术语按字数插值。
set -e; cd "$(dirname "$0")"; export PYTHONDONTWRITEBYTECODE=1
T="${1:-/workspace/share/ep17/timeline.json}"
if [ -f "$T" ]; then echo "timing: $T"; MAP="python3 -B map_timing.py $T"; else echo "无 Knoll timing（$T），用字数估算（provisionalTiming=true）"; MAP="python3 -B make_timing.py"; fi
# 标签修正可能加 hold（label_holds.json）→ 退出码 3 时重跑，最多 4 轮
for i in 1 2 3 4; do
  $MAP >/dev/null && python3 -B asr_words.py >/dev/null && python3 -B gen.py >/dev/null
  rc=0; python3 -B ../_audit/labelfix.py . || rc=$?
  [ $rc = 3 ] || break
done
[ $rc = 0 ] || [ $rc = 3 ] || exit $rc
python3 -B gen.py | tail -1 && python3 -B ../_audit/labelfix.py . >/dev/null; python3 -B validate.py && python3 -B ../_audit/fullshow.py . && (cd .. && python3 -B _audit/cuecheck.py db-lock)
