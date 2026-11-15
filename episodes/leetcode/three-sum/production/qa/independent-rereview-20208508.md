# LC.15 差异复审：20208508

- 复审者：独立 Devin reviewer，session `00e1dcdb7f8d42ffab4a3f90d14a8d50`。
- 日期：2026-11-15（北京时间）。
- 旧提交：`4ba29a5a6a484d50c9a122dedc16d6f9978ce1d7`。
- 本轮固定提交：`202085088ca00326f7e440cbffd41f6fcc02e7db`。
- 仓库：`linhongcun/video-studio`；已 fetch 指定制作分支，未另拉整仓历史。
- 范围：仅复审变化文稿、动作计划和新增 SVG，并逐字节确认算法、保存轨迹、来源与测试不变。未修改仓库文件，未做 TTS、视频渲染、commit/push、PR 或外部评论；结束时工作区干净。
- 下文制作文件路径相对于 `episodes/leetcode/three-sum/production/`；SVG 路径另列。

## 结论

**本轮差异复审通过，无必须修正项。上轮 F1 已解决，三项清晰度建议已落实。新增 SVG 已在 Chrome 实际查看，所示数组、下标、指针、算式与解释正确，观察视图中未见文字裁切或遮挡。**

该通过只覆盖本轮列明的文字、计划和静态 SVG；不包含实际配音起音绑定、动画连续动作、成片及站点页面验收。

## 修订核对

| 项目 | 固定提交中的修订与结论 |
| --- | --- |
| F1：第二次命中后的实际位移 | `script.md:17` 明确“先右移左指针，它与右指针相遇”；`article.mdx:50` 明确 L 到下标 4、右侧循环不再移动。与原有实现及 trace 的 L:3→4、R:4→4 完全一致。通过。 |
| 第 05 镜的三数和 | `script.md:17` 补“加上固定的负一，三数和为零”，避免只听见 0 与 1 相加的歧义。通过。 |
| 第 07 镜去重补例 | `script.md:23` 明确跳过连续两个 0，再让 R 向内至相遇；对应 L:1→3、R:4→3。不再要求跨过会合位置。后句限定“同一个固定值”，去重原因与上下文匹配。通过。 |
| 文章收束 | `article.mdx:101` 将“不可能成功”的排除限定于和偏小或偏大，另述命中后及固定值去重。通过。 |
| 第 05、07 镜 cue | `plan.json:151,159,232,244` 附近已同步改句起始 cue；脚本中的句子索引与 cue/endCue 检查通过。 |
| 第 03 镜先证明再移动 | `plan.json:70–92`：first 仅事件 0（fix）；second 才有事件 1–5（low 扫描至相遇）。静态计划中不再在证明句开头提前移动。通过。 |
| 第 06 镜句内移动 cue | `plan.json:195–208`：second 仅证明，无事件；新增 move 使用同一句中的唯一文本“所以可以安全左移右指针”，承载事件 16–17。文本位置、句子编号 1 与事件次序正确。通过；真实 onset 解析及生效帧尚待制作实现后检查。 |

九镜 actions 的事件列表展开后均与各镜 `traceEvents` 一致，所有 cue 位于标记的句子中；带 endCue 的项均命中下一句。第 06 镜 second 与 move 共享 sentence=1 是有意的句内拆分，不应在下游仅按 sentence 编号合并成一次提前动作。

## SVG 实看

文件：`episodes/leetcode/three-sum/publication/article/01.svg`，1440×720。

本轮以 Chrome 直接打开实际 SVG，在完整图可见的缩放视图中观察（1024×768 桌面截图坐标；浏览器缩放约 60%）。同时核对 SVG 源码与文章 37–39 行：

- 从左到右为 `[-4,-1,-1,0,1,2]`，下标 0–5；固定 i 指向下标 0 的 -4，L 指向下标 1 的 -1，R 指向下标 5 的 2。
- 算式 `−4 + (−1) + 2 = −3 < 0` 正确；右值 2 已为候选最大值，因此不能靠换更小右数将当前总和升至零。
- 青色箭头向右，从当前 L 列朝下一列，配文“排除当前 L，向右移动”；方向与算法一致。
- 标题、来源语境说明、全部格内值及下标、角色名、算式、长解释句和底部箭头说明均完整可见；未见相互遮挡、越出 SVG 画布或文字截断。文章 alt/caption 与所见图意一致。

本次是单张静态机制图实看，不能替代站点桌面/手机中的实际显示、亮暗主题、原图入口或动画检查。没有生成或检查视频。

## 验证与一个非阻断排版建议

- 修改后的制作 MDX 经仓库指定 `parseArticle` 直接解析：PASS。
- 九镜 cue/sentence/endCue 与事件展开检查：PASS。
- `solution.py`、`three_sum_trace.py`、`trace/main-example.json`、`references.json`、`research/source-evidence.json`、`tests/test_solution.py` 与上轮提交逐字节相同；上轮算法 oracle 及原文审查证据可复用。本轮没有重复运行未变化的 6,399 多重集穷举，也没有再次访问来源。
- 文章 Python 代码块能被 Python AST 正常解析，AST 与 `solution.py` 完全一致。
- `git diff --exit-code` 返回 0，`git status --porcelain` 为空，HEAD 为本轮固定提交。

**非阻断建议：** `article.mdx:84` 的 `r -= 1` 意外比原稿多缩进 4 个空格。它仍是合法的 elif 单语句代码块，AST 与实现一致，未改变语义；建议整理回与第 82 行 `l += 1` 相同缩进，以恢复代码卡的统一风格。本轮不能再声称文章代码与 `solution.py`“字节完全一致”，应表述为“语义一致”。

后续待验：共享 voice/cues 实际输出中第 06 镜 move 的独立起音、03/06 证明期间指针保持、05 无位移的 skip-right 不被误画成移动、07 相遇即停，以及最终 MP4 的独立复核。本 reviewer 交付后等待下一次通知。

## 本轮已审及用于复用判定的文件完整 SHA-256

| 文件（仓库相对路径） | SHA-256 |
| --- | --- |
| `episodes/leetcode/three-sum/production/script.md` | `456c5a4dbfb282fac836e40181b8e3180a3e47b217a4f4eb1d55a073c6dabdde` |
| `episodes/leetcode/three-sum/production/article.mdx` | `df845fc9fb2a3667525282e755afc03b1954b7fddab4d430093d7c3bfc0524c7` |
| `episodes/leetcode/three-sum/production/plan.json` | `bd5ee38d59bce1e6ae9fbe34bf88f76f3522b4aba08e267c59811a5b7d158cc2` |
| `episodes/leetcode/three-sum/publication/article/01.svg` | `d71cb7501a7ec63c39e83ab56e2e7f1c3e853256e3f6fe9f3e42c5f8d3ccea14` |
| `episodes/leetcode/three-sum/production/solution.py` | `c682c9a28e05e5e5856526a10af53951a393a90c318a41dd70c16538ec556daa` |
| `episodes/leetcode/three-sum/production/three_sum_trace.py` | `15f0e14b32e3149717e42d8718a5f832ab66f159749d30654556c8e770ccc186` |
| `episodes/leetcode/three-sum/production/trace/main-example.json` | `4666429b57cef74cc1db8e033d01f7d896ef0dfe21a83d09e41f42e202c7c02c` |
| `episodes/leetcode/three-sum/production/references.json` | `daeb60f5dd9afe5df5b5caa1413880148f65a64df04a31db28534c6035ac06a2` |
| `episodes/leetcode/three-sum/production/research/source-evidence.json` | `90ab6a8276fc48d004bab6878ef9b06241337686e804fc38283dace4b480e4a7` |
| `episodes/leetcode/three-sum/production/tests/test_solution.py` | `4e8a36ad9d7a29dffe0acae908e385801b49793563bec7af38d7be1d781c0f7d` |
