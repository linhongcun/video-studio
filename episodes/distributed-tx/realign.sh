#!/bin/sh
# EP.21 分布式事务（Miyazaki）：sh realign.sh [Knoll timing 路径]
# 默认读 Knoll 的 /workspace/share/ep21/timeline.json（只读）；不存在 → 用暂定估算 timing（make_timing.py，provisionalTiming=true）；words.json 没到时 asr_words.json 为空，术语按字数插值。
set -e; cd "$(dirname "$0")"; export PYTHONDONTWRITEBYTECODE=1
T="${1:-/workspace/share/ep21/timeline.json}"
# FORCE_ESTIMATE=1：即使 Knoll 文件已在，也按字数估算跑（配音还没过 QA 时用）
if [ -f "$T" ] && [ -z "$FORCE_ESTIMATE" ]; then echo "timing: $T"; MAP="python3 -B map_timing.py $T"; else echo "无 Knoll timing（$T），用字数估算（provisionalTiming=true）"; MAP="python3 -B make_timing.py"; fi
# fullshow / labelfix：distributed-tx 用新定义（完整显示 = 可见 − 12 帧 pop-in − 转场淡出），由 _audit/terms.json fullShowExcludesFadeOut 打开
# 标签修正可能加 hold（label_holds.json）→ 退出码 3 时重跑，最多 4 轮
for i in 1 2 3 4; do
  $MAP >/dev/null && python3 -B asr_words.py /dev/null/none >/dev/null && python3 -B gen.py >/dev/null && python3 -B cue_words.py >/dev/null
  rc=0; python3 -B ../_audit/labelfix.py . || rc=$?
  [ $rc = 3 ] || break
done
[ $rc = 0 ] || [ $rc = 3 ] || exit $rc
python3 -B gen.py | tail -1 && python3 -B cue_words.py && python3 -B ../_audit/labelfix.py . >/dev/null; python3 -B validate.py && python3 -B ../_audit/fullshow.py . && (cd .. && python3 -B _audit/cuecheck.py distributed-tx)
# 配音状态：没有 Knoll timeline → pendingAudio（暂定，不是定稿）；有 → 核对 narration.wav 在不在、打印 sha256
python3 -B -c "
import json,os,hashlib
m=json.load(open('storyboard.json'))['meta'];W='/workspace/share/ep21/narration.wav'
if m.get('pendingAudio'): print('PENDING 暂定时间轴（字数估算，不是定稿）：'+('Knoll 文件已在 /workspace/share/ep21/，去掉 FORCE_ESTIMATE 重跑即定稿' if os.path.isfile('/workspace/share/ep21/timeline.json') else '等 /workspace/share/ep21/ narration.wav + timeline.json + words.json'))
else: print('FINAL 时间轴：Knoll timeline', ('narration.wav sha256 '+hashlib.sha256(open(W,'rb').read()).hexdigest()) if os.path.isfile(W) else '（缺 narration.wav！）', '| words.json', 'OK' if os.path.isfile('/workspace/share/ep21/words.json') else '缺')
"
