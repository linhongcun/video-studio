# LC20 工程与环境

九镜 Remotion 主体、trace 驱动的字符行与栈、完整代码卡和共享配音/装配/freeze 薄包装沿 LC56 工程结构建立。`plan.json` 每镜两个动作，首句动作以第二句 cue 为 `endCue`，保证动作在本句内完成；带 `events` 的动作按顺序驱动 `trace/main-example.json` 的事件（push/pop/mismatch/empty/leftover/finish）。字符按类型着色，配对成功变青、失败变红；栈画在字符行右侧，自底向上。

依赖：Python 用 `~/.venv-lc56`（numpy/scipy/soundfile/faster-whisper/parselmouth/playwright），Remotion 渲染设置 `CHROME_BIN=/home/ubuntu/.local/bin/google-chrome`。流程：`scripts/build_trace.py` → `tests/` → `scripts/check_plan_cues.py` → 共享 voice prep/gen/run.sh → `prepare_code_endcard.py`（装配、代码卡起帧）→ `freeze.py` → `npm run render:body` → `render.py`（资料附录与最终媒体）。90 帧/镜占位 storyboard 仅用于静帧布局，不代表真实配音或字幕时序。
