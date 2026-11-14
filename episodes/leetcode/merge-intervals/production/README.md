# LC56 工程与环境

十镜 Remotion 主体、trace 驱动的数据板、完整代码卡和共享配音/装配/freeze 薄包装已实现。独立复审通过；复审报告原字节保存在 qa/independent-rereview-df13a3e.md。已生成20句MiMo配音并按真实句级时序装配：正文4388帧，代码卡从4238帧开始；voice.wav末个非零样本为140.6448秒，代码卡起点为141.2667秒。附加150帧资料页后的首版为4538帧、151.2667秒，机器媒体检查通过。首版仍待独立审片/听审；当前已知需合并修正：finish状态不能回退，开场映射需在第二句前完成，08结果输出与09分离动作需按对应句内语义定位。修复并复核前不再正式渲染；不擅自合并或发布Release。90帧/镜仅用于静帧布局，不代表真实配音或字幕时序。

## 动画与时间线

plan.json 映射十镜和 trace 事件；05–09 从本期 trace 读取状态。Solution 即时维护 merged 的末段，trace 则在 separate 时把 before 加入 completed、finish 时再加入末 current；只是记录时机不同，结果等价。排序对象保留原 ID 和颜色，数轴使用固定 0–15 同尺度。episode-config.json 将代码卡与资料页各设为 5 秒；代码卡实际起帧由获准配音后的 voice build 推导。代码卡逐行数据由 scripts/build_code_card.py 从 solution.py 生成，采用 31px 字体、43px 行距。

先运行 scripts/check_plan_cues.py，验证 plan.json 中每个配音术语确实匹配对应脚本句首；scripts/build_layout_placeholder.py 也会执行此检查并生成无音频占位 storyboard。占位 storyboard 仅用于 Remotion 静帧 smoke；正式 render/freeze 必须先有实际 voice.wav、words.json 和非 provisional 的 storyboard。静帧样本位于 remotion/out/lc56-*.png，不能作为正式动态或时序验收。

初审和通过的复审报告均按原字节保存在 qa/；两份报告都由 freeze.py 纳入输入清单，不覆盖初审记录。

## 依赖与静帧烟测

~~~sh
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT/episodes/leetcode/merge-intervals/production/remotion"
npm ci
npm run typecheck
CHROME_BIN="$(command -v google-chrome)" npm run smoke:still
~~~

依赖按 LC347 当前 package-lock 的版本集复制并为本期锁定；为类型检查仓库共享 Frame，另按仓库现有工程固定 React 18 类型包版本。npm ci 未安装或替换 Chrome；它报告锁文件依赖有 11 项漏洞（1 moderate、10 high），没有执行自动升级。此环境的 google-chrome 命令解析到 Devin Chrome shim，实际浏览器是 Chrome for Testing 156.0.8078.47。字体使用共享 Frame 的 Noto Sans CJK SC；系统已提供该字体，无需安装。

烟测输出到 remotion/out/setup-smoke.png。它只检查 Remotion bundle、共享 LeetCode Frame、字体和已有 Chrome 能否协作。

## Python runtime

环境置于仓库外，避免把虚拟环境纳入制作输入：

~~~sh
ROOT="$(git rev-parse --show-toplevel)"
python3 -m venv "$HOME/.venv-lc56"
"$HOME/.venv-lc56/bin/python" -m pip install -r "$ROOT/episodes/leetcode/merge-intervals/production/requirements-runtime.txt"
~~~

运行共享 Python 工具或 Remotion render scripts 前，先激活该 venv；runtime 依赖按 LC347 当前 requirements-runtime.txt 的精确版本锁定。

## 正式配音、时序、冻结与渲染

voice/params.json 将末尾停顿设为 5.6 秒：共享构建器原有 0.6 秒自然尾停，加 5 秒完整代码卡；配音不变速、不裁句。

~~~sh
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
source "$HOME/.venv-lc56/bin/activate"
EPDIR=episodes/leetcode/merge-intervals/production
python3 episodes/_shared/voice/prep.py --dir "$EPDIR"
python3 episodes/_shared/voice/gen.py --dir "$EPDIR"
python3 episodes/_shared/voice/build.py --dir "$EPDIR"
python3 "$EPDIR/prepare_code_endcard.py"
python3 episodes/_shared/place_v2.py --dir "$EPDIR" --mode whole
python3 episodes/_shared/label_onset_strict.py --dir "$EPDIR"
python3 episodes/_shared/check_sentence_episode.py "$EPDIR"
python3 "$EPDIR/scripts/sync_storyboard.py"
node site/scripts/check-references.mjs --sources "$EPDIR"
python3 "$EPDIR/freeze.py"
python3 "$EPDIR/render.py"
~~~

gen.py 仅在审读通过后调用；MiMo API Key 仅由进程环境变量 MIMO_API_KEY 提供，不写入文件、命令参数或日志。首句试听取成功后再生成其余句子。Remotion 使用已有 Chrome 时显式设置 CHROME_BIN；不要安装或替换浏览器。

prepare_code_endcard.py 调用共享句级装配包装，不改 script.md，并将 timing source 绑定到真实 voice.wav、words.json 和原脚本 SHA；代码卡帧数来自真实音轨。正式渲染只走 render.py，默认追加共享 title-author 资料页。freeze.py 和 Remotion 的正式 render 脚本拒绝缺少真实 voice/storyboard、草稿或 layout-only placeholder 的输入；smoke:still 仅供布局检查。
