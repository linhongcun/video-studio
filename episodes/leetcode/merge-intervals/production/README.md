# LC56 工程与环境

十镜 Remotion 主体、trace 驱动的数据板、完整代码卡和共享配音/装配/freeze 薄包装已实现。独立审读期间不改 script/article/solution，不生成配音、不冻结输入、不进行正式编码。当前 storyboard 标记为 layout-only placeholder；90 帧/镜仅用于静帧布局，不代表配音或字幕时序。

## 动画与时间线

plan.json 映射十镜和 trace 事件；05–09 从本期 trace 读取状态。Solution 即时维护 merged 的末段，trace 则在 separate 时把 before 加入 completed、finish 时再加入末 current；只是记录时机不同，结果等价。排序对象保留原 ID 和颜色，数轴使用固定 0–15 同尺度。episode-config.json 将代码卡与资料页各设为 5 秒；代码卡实际起帧由获准配音后的 voice build 推导。代码卡逐行数据由 scripts/build_code_card.py 从 solution.py 生成，采用 31px 字体、43px 行距。

scripts/build_layout_placeholder.py 生成无音频占位 storyboard。静帧样本位于 remotion/out/lc56-*.png，不能作为正式动态或时序验收。

独立初审报告按原字节保存在 qa/independent-review-6967f6a.md；后续复审应基于本次修订提交，不覆盖初审记录。

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

## 审读通过后的共享入口

以下命令是后续流水线入口，本阶段不执行；先完成独立脚本/文章审读及获准的配音、分镜数据：

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
node site/scripts/check-references.mjs --sources "$EPDIR"
~~~

gen.py 只有在审读通过后才可调用；密钥仅通过环境变量 MIMO_API_KEY 提供，不写入文件或 README。

assemble.py 临时提供共享 sentence assembler 所需的画面行，不改审读中的 script.md，并将 timing source 绑定回原脚本 SHA。freeze.py 仅为后续正式冻结入口，本阶段没有运行。Remotion 入口使用共享 title-author 资料页渲染器；本阶段没有 TTS、真实时序、冻结清单或正式编码，因此现在不要运行 npm run render、render:voice 或 render:body。
