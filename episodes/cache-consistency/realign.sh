#!/bin/sh
# EP.22 缓存和数据库一致性（Miyazaki）：sh realign.sh [Knoll timing 路径]
# 默认读 /workspace/share/ep22/timeline.json（只读）；不存在 → 字数估算（make_timing.py，provisionalTiming=true）。_audit 用本目录副本，所有写入只在本目录。
set -e; cd "$(dirname "$0")"; export PYTHONDONTWRITEBYTECODE=1
T="${1:-/workspace/share/ep22/timeline.json}"
if [ -f "$T" ] && [ -z "$FORCE_ESTIMATE" ]; then echo "timing: $T"; MAP="python3 -B map_timing.py $T"; else echo "无 Knoll timing（$T），用字数估算（provisionalTiming=true）"; MAP="python3 -B make_timing.py"; fi
for i in 1 2 3 4 5; do
  $MAP >/dev/null && python3 -B asr_words.py >/dev/null && python3 -B gen.py >/dev/null
  rc=0; python3 -B _audit/labelfix.py . || rc=$?
  [ $rc = 3 ] || break
done
[ $rc = 0 ] || [ $rc = 3 ] || exit $rc
python3 -B validate.py && python3 -B _audit/fullshow.py . && python3 -B _audit/cuecheck.py .
python3 -B -c "
import json;m=json.load(open('storyboard.json'))['meta'];print(('PENDING 暂定时间轴（字数估算，不是定稿）' if m.get('pendingAudio') else 'FINAL 时间轴'),m['durationInFrames'])"
