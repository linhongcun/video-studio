# LC.15 三数之和：独立文稿、算法与图文结构审读

- 审读日期：2026-11-15（北京时间）。
- 审读者：独立 Devin reviewer，session `00e1dcdb7f8d42ffab4a3f90d14a8d50`。
- 仓库：`linhongcun/video-studio`。
- 已 fetch 指定分支：`devin/1794721619-leetcode-3sum`。
- 固定审读提交：`4ba29a5a6a484d50c9a122dedc16d6f9978ce1d7`。报告不覆盖分支后续提交。
- 执行范围：只读审查；未修改制作文件，未 commit/push、建 PR 或发外部评论。测试禁写 Python 字节码；结束时工作区干净。
- 下文制作文件路径均相对于 `episodes/leetcode/three-sum/production/`。

## 结论与必须修正项

**发现 1 项需要在文稿冻结、批量定稿配音前修正的动作表述不一致。算法、官方主例计算、去重依据、复杂度及引文支持关系未发现其他必须修正的问题。** 文章结构基本成立。图像、动画、声音及站点均未作实际验收。

### F1 · P2：第二次命中后，实际只有左指针移动，稿件却说“两端向内推进”

- 位置：`script.md:17`（第 05 镜）；`article.mdx:50` 有相同的“两端继续向内”表述。
- 原句：旁白“记录后两端向内推进并相遇”；文章“两端继续向内，L 与 R 相遇”。
- 复核依据：第二组 `[-1,0,1]` 命中时 `i=1,L=3,R=4`。`solution.py:18–22` 首先跳左值，使 `L:3→4`；此时 `L=R`，右侧 while 条件已经为假，`R` 仍为 4。`three_sum_trace.py:25–30` 与保存轨迹 `trace/main-example.json:158–198` 一致：`skip-left.nextL=4`，随后 `skip-right.nextR=4`，后者没有发生位移。
- 影响：若动画忠实按当前 trace 播放，口播中的“两端推进”没有相应动作；若为迁就旁白再移动 R，则会与本期完整实现及轨迹不同。“两端都动并相遇”也无法对应此处相邻两个下标。
- 建议旁白第二句改为：“记录后左指针右移，与右指针相遇，这个负一作为固定值的所有可能就找完了。”文章对应改为：“记录第二组后，L 从 3 右移到 4，与仍在 4 的 R 相遇，结束本轮。”
- 联动：如采用该改法，同步 `plan.json:151,159` 的 `endCue` / `cue`（当前均以“记录后两端向内推”起头），保留第二句的 sentence 编号 1。事件 11、12、13 可保留，但事件 12 是无位移检查，不应画成一次实际右移。
- 复验范围：第 05 镜两句文稿、文章该段、cue 匹配与第二次命中的连续动作；不需要改算法以迎合错误描述。

## 非阻断的听觉与措辞建议

1. `script.md:17`：“左指针是零，右指针是一，相加得到第二个答案”依赖观众记住固定的 -1，单听容易接成“零加一等于零”。建议第一句改为“现在左指针是零，右指针是一，加上固定的负一，三数和为零，得到第二个答案：负一、零、一。”原句并未明确断言 `0+1=0`，这里列为听觉清晰度建议。
2. `script.md:23`：补例中左侧 0 从下标 1 跳至 3，右侧 2 从 4 移至 3 即相遇，算法不会继续把会合位置也跳过去。可说“左边跳过两个零，右边向内跳过重复的二；一旦相遇就停止”，避免“全部等值格都必须跨过去”的印象。`article.mdx:63` 已准确写出终点，无须改变补例或结果。
3. `article.mdx:101`：“每次移动都排除一个确定不可能成功的端点”建议收窄成“和偏小或偏大时，每次移动都排除一个不可能成功的端点”。命中后的移动排除的是已经输出的数值组合，并非不可能成功；后半句已有去重解释，补条件即可让收束更严谨。

以上建议不构成算法实现失败；没有进行 TTS，不能把文字风险判断记为实际发音失败或听辨通过。

## 官方主例与去重补例逐项核对

主例排序后为 `[-4,-1,-1,0,1,2]`。保存轨迹的 `main` 与当前 trace 函数再生成的对象完全一致。

| 阶段 | 核对的实际状态与结果 | 对应稿件与计划 |
| --- | --- | --- |
| 固定 -4 | `(L,R)=(1,5),(2,5),(3,5),(4,5)`，总和依次 `-3,-3,-2,-1`；L 到 5 相遇，无答案 | 脚本 03；文章 35–48 行；plan 的事件 0–5 |
| 第一个 -1 首次命中 | `i=1,L=2,R=5`，`-1-1+2=0`，结果加入 `[-1,-1,2]`；跳到 L=3、R=4 | 脚本 04；文章 50 行；事件 6–9 |
| 同一 -1 二次命中 | `-1+0+1=0`，加入 `[-1,0,1]`；L 从 3 到 4，R 停在 4 | 脚本 05；文章 50 行；事件 10–13；动作措辞见 F1 |
| 跳过下一个 -1 | i=2 的固定值与前一值相同，跳过整轮 | 脚本 06；文章 52 行；事件 14 |
| 固定 0 偏大 | `i=3,L=4,R=5`，总和 3；R 从 5 到 4，相遇，外层合法固定位置遍历完毕 | 脚本 06；文章 52–54 行；事件 15–17 |
| 去重补例 | `[-2,0,0,2,2]`，首次命中后 L 从 1 到 3，R 从 4 到 3，本轮结束，只输出一次 `[-2,0,2]` | 脚本 07、文章 63 行均明确换例；plan 07 使用补例事件 0–4 |

补例 `duplicates` 保存的是完整运行：固定 -2 的一轮后还会检查固定 0。第 07 镜只展示该固定值下的两端去重，未宣称展示补例全程，选取事件 0–4 符合这段用途。保存的 `duplicates`、`zeros`、`none` 均与重新生成完全一致。

## 算法、边界与安全排除

- **不同下标与重复数值：** 排序保留每个元素及其重数，只改变次序；返回值不要求原下标。每次求和均满足 `i < L < R`，既防止复用位置，也允许用两个 -1 或三个 0。不能先对整个输入做集合去重。文章 27、60、67、95 行已交代。
- **偏小排除左端：** 固定 i 与 L，对于剩余区间任意右端 k≤R，`a[i]+a[L]+a[k] ≤ 当前和 < 0`，故当前 L 的所有剩余配对都失败，可以右移 L。脚本 03 给出“右边已经取了最大的数”的具体依据；文章 37 行及表格接上状态。
- **偏大排除右端：** 固定 i 与 R，对于剩余区间任意左端 k≥L，`a[i]+a[k]+a[R] ≥ 当前和 > 0`，故可以左移 R。脚本 06 与文章 54 行对应。
- **覆盖与终止：** 初始候选从 `i+1` 到 `n-1`，每次只删除不可能成功的端点，或在命中后删除同值重复配对；L、R 相遇后没有两个不同位置可选。外层覆盖所有可作最左元素的位置，重复固定值的早一轮拥有后一轮右侧候选的超集。
- **两层去重：** 固定值重复时跳过该轮；命中后固定值及一端值已经唯一确定另一端值，因此同值端点只会重复同一数值组合。`article.mdx:60–61` 说明了两层各自依据。脚本 04、06、07 对应具体操作，没有把题意引文冒充解法证明。
- **边界：** `[0,0,0]` 合法；`[0,0,0,0]` 也只输出一组；`[0,1,1]` 无解。提前停止必须是 `a[i] > 0`，不能写 `>= 0`，文章 95 行已解释。全负、全正、重复固定值、重复两端及最大绝对值实例均在现有测试内。
- **复杂度：** `solution.py` 的排序 O(n log n)，每轮双指针合计 O(n)，外层 O(n)，总时间 O(n²)。`sorted(nums)` 新建列表，连同 Python 排序工作空间，除输出额外空间 O(n)；结果另占 O(k)。脚本 09、文章 97 行口径一致。本结论针对解题实现，不把保存所有事件的教学 trace 当作 O(n) 空间实现。

## 脚本四问定位（依据仅列脚本与草分镜）

| 问题 | 片中已建立的依据及用途 | 审读判断 |
| --- | --- | --- |
| 要判断什么？ | 01 镜明确整数数组、三个不同位置、和为零、返回所有不重复数值组合；用两个 -1 对比“位置不同但组合相同” | 题意五项齐全 |
| 为什么从这里、按此顺序？ | 02 镜从任意三位置枚举的重复检查引出排序大小关系；固定一个位置，在其右侧从近端与最远端开始，保证三个位置不同 | 选择理由在指针扫描前建立；03 镜继续兑现最大右端的用途 |
| 每步为何成立？ | 03 镜以最大右数证明偏小可排除左端；04 镜以方程唯一配对说明命中后去重；06 镜以最小左候选证明偏大可排除右端 | 关键理由可直接定位，无须借文章补推理；05 镜实际位移需按 F1 修正 |
| 如何支持下一步及结尾？ | 03→04 在 -4 候选穷尽后更换固定值；04→05 保留同一固定值继续搜；06 完成主例；07 明示切补例；08 区分数值与位置；09 回收移动规则及复杂度 | 主例、补例和边界不串成同一条轨迹；收束回答如何找全且去重 |

第 09 镜“每轮两个指针只向内走”指单调方向，不要求每轮每支都实际移动，未作为 F1 的同类问题处理。

## 文章结构与引用支持关系

- **读者与入口：** 正文 12 行可见地限定会遍历数组、理解下标的读者，建立“找全、下标不同、数值组合去重”问题，并预告排序、移动与去重的因果；不依赖 frontmatter 摘要代替导读。
- **推导顺序：** 16–31 行建立题意、主例、排序为何不损失题目信息与副本语义；35–54 行按同一主例走完排除与命中；60–63 行给去重依据与补例；67–99 行给边界、完整代码、停止条件及代价；101 行回收“不漏且不重”。前提与例子可独立读懂。完整代码与 `solution.py` 字节一致。
- **详略与收束：** 主线保留两个排除依据和两层去重理由；代码紧接其所实现的规则。没有强行增加无关背景或多解。末段已回答开头，不必为凑模板另加一章；措辞精度建议见上文。
- **图位：** 39 行 Figure 紧邻偏小排除解释，alt 给出了数组、指针、总和与观察方向，caption 说明排除的配对范围，明确是自制机制图。固定提交中尚无该实际 SVG，本轮仅审图位及图文语义，**未看图、未验收有效配图**。主会话正在制作图，不能将这一正常阶段待办误报成成片缺陷，也不能据此写“配图通过”。
- **R1：** 已重新读取 [LeetCode 官方题面](https://leetcode.cn/problems/3sum/description/)，核对题意、三例与引文“注意：答案中不可以包含重复的三元组。”。文章 18 行的 supports 只将原文用于去重要求，不将其当成双指针正确性依据。`source-evidence.json` 的题号、英文题名、示例和中文连续引文与清单匹配。
- **R2：** 已重新读取 [Python 官方 Sorting Techniques](https://docs.python.org/3/howto/sorting.html)，确认原题及连续句“There is also a sorted() built-in function that builds a new sorted list from an iterable.”。本次读取页面标题确为 `Python 3.15.2 documentation`，与证据、清单和文章版本一致。文章 31 行仅据此支持 `sorted()` 的副本语义，译文另标，未扩大支持范围。
- **来源格式：** 两来源均使用机构、无虚构个人 author；`presentation: title-author` 与两项片尾清单符合要求。来源检查通过只能证明记录/链接关系，不能证明片尾已经显示正确；本轮未检查实际资料卡或引用浮层交互。

## 实际执行的验证

| 验证 | 结果与范围 |
| --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s episodes/leetcode/three-sum/production/tests -v` | PASS，2 个测试方法；其中穷举值域 -3..3、长度 3..8 的 6,399 个多重集，另有 9 个官方/边界实例；耗时 0.308s |
| 现有 oracle 的独立性 | 暴力枚举来自 `itertools.combinations(a,3)`，不复用双指针判断；检查结果集合、无重复和 trace/solution 一致；low/high 还检查所排除范围确无解 |
| 四组保存 trace 与函数重生成比较 | `main` / `duplicates` / `zeros` / `none` 全部完全一致；主例事件序号 0–17 与计划吻合 |
| 九镜 plan 校验 | action 事件展开与镜级 `traceEvents` 一致；所有事件号有效；cue 在所标 sentence，endCue 在下一句；PASS。F1 改句后需重跑该匹配 |
| 文章代码与解题文件比较 | 文章 Python 代码块与 `solution.py` 完全一致；调用后原输入未修改 |
| 仓库指定 `parseArticle` 直接解析制作 MDX | PASS；只证明语法，未验证图片、引用交互或阅读版式 |
| `node site/scripts/check-references.mjs --sources episodes/leetcode/three-sum/production` | PASS，2 条来源；同时另行完成上述原文阅读 |
| 工作区身份 | `git diff --exit-code` 为 0；`git status --porcelain` 空；HEAD 为指定完整提交 |

测试没有穷举所有整数数组，也未运行 n=3000 性能基准；复杂度结论来自实现推导。未运行会生成制作产物的 trace 构建器、冻结、TTS 或渲染命令。

## 未完成的验收与交接

本报告不覆盖任何真实音频听辨、逐字 ASR、定稿时间轴、实际 SVG/视频画面、连续动画、最长字幕/代码卡版式、参考资料成片、播放器或站点桌面/手机交互。报告中的通过均限于固定提交的文字、源码、证据及实际列明的自动检查。

请主会话修正 F1；如采用听觉建议，同步对应句级 cue。修订提交不自动继承本报告的文稿通过结论，可只交回变化段及联动 plan 复审。本 reviewer 交付后停止，等待主会话通知。

## 已审文件完整 SHA-256

以下为本次实际读取并据以审查的文件字节 SHA-256，均来自固定提交；不是短 blob ID，也不是用提交号代替文件 SHA。

| 文件（仓库相对路径） | SHA-256 |
| --- | --- |
| `AGENTS.md` | `ee733023d7cd66dd1d0260202f17fbbb4057609c108ef095c91155e79fefd67f` |
| `docs/qa.md` | `bdf82ff3bcd372bc42771999a88d47d59c430d0ee922dc9fc6b93121b8ae398b` |
| `docs/article-style.md` | `81e98a86d551df619f51c56ad0d8cec7fedb9b9cdb9ee8809c00f6ab23419812` |
| `docs/research-template.md` | `1a94cdd19aa83fff986b0914f8ac38522754a0ea694bb8e0f66a1bdc0b9cc0df` |
| `docs/pipeline.md` | `d66006015bc2d6a75e96443f33a4fd06a240ee9efa01732c1fde8dd9d766ff03` |
| `docs/RULES.md`（相关规范节） | `6c63a410c9c187a62cf9bf96c00a2a97a42229bacd792f768d6af5f03dbd152b` |
| `episodes/leetcode/three-sum/production/script.md` | `d99c7e236cd325eff6db6570cbda58c79ff00bdf2e59dde7a61b51c977dfdbc3` |
| `episodes/leetcode/three-sum/production/article.mdx` | `3d27cbfc287c4b5ff6257c474612276712401d03d23ed101a1e5297a6ac73443` |
| `episodes/leetcode/three-sum/production/plan.json` | `4dbe3c2e14878eae9437d30e302b490de8812e59306de7df654d8c205964ee65` |
| `episodes/leetcode/three-sum/production/solution.py` | `c682c9a28e05e5e5856526a10af53951a393a90c318a41dd70c16538ec556daa` |
| `episodes/leetcode/three-sum/production/three_sum_trace.py` | `15f0e14b32e3149717e42d8718a5f832ab66f159749d30654556c8e770ccc186` |
| `episodes/leetcode/three-sum/production/research/source-evidence.json` | `90ab6a8276fc48d004bab6878ef9b06241337686e804fc38283dace4b480e4a7` |
| `episodes/leetcode/three-sum/production/references.json` | `daeb60f5dd9afe5df5b5caa1413880148f65a64df04a31db28534c6035ac06a2` |
| `episodes/leetcode/three-sum/production/tests/test_solution.py` | `4e8a36ad9d7a29dffe0acae908e385801b49793563bec7af38d7be1d781c0f7d` |
| `episodes/leetcode/three-sum/production/trace/main-example.json` | `4666429b57cef74cc1db8e033d01f7d896ef0dfe21a83d09e41f42e202c7c02c` |
| `episodes/leetcode/three-sum/production/storyboard-design.md` | `aa1f54f4c6e9cabb9037791bb241f166157f672bd3822e2d8728730661b489af` |
| `episodes/leetcode/three-sum/production/research.md` | `a764bc5b38c808107a3f38d96346c2ce3def90b9b5e842a0b68df85de4c1f1b8` |
| `episodes/leetcode/three-sum/production/README.md` | `bd48bc1d45dde146612228b0a0f5a02e479341c80825499bea81d71e80ef78da` |
| `episodes/leetcode/three-sum/production/pronunciation.md` | `760053c38b39f296067443e72e74c38ea1edd79632c31a736ad9843b7ada13ad` |
| `episodes/leetcode/three-sum/production/episode-config.json` | `acdccccc43dd71245b16adcd762637b23208f05760a90ac429513cf4b1186de1` |
| `episodes/leetcode/three-sum/production/visual-direction.md` | `274ade57b6d6145e2bc55cba91d44948809ae16c53e831b82f9824ec6ec0f68a` |
