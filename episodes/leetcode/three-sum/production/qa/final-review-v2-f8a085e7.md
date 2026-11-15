# LC.15 修订版成片独立复审

**结论：本轮复审通过，无阻断项。首屏题名和 05 相遇提示均已修正；07 的实际 R 移动提示正确，完整代码卡与资料页保留。沿用下述已经核实身份的既有检查范围，并保留音频听辨能力边界。**

- 独立复核者：Devin，session `00e1dcdb7f8d42ffab4a3f90d14a8d50`。
- 固定提交：`858c94a1b845fe9467ce7f8e143c602c0fcf2ee1`，`visualRevision=2`。
- 媒体：`episodes/leetcode/three-sum/publication/video.mp4`。
- **最终视频 SHA-256：`f8a085e7b49265e25cb39970f39e1f1fed77e071eff12493ad9dbbbad61dd5b5`。**
- 实测格式：1920×1080，H.264/AAC，30 fps，5798 帧，193.2667 秒。正文 5648 帧，资料页 150 帧。

## 本轮实际检查

从新 SHA 的 MP4 提取实际画面，查看原尺寸画面和 05/07 各 12 张按时间排列的密集帧；同时完整解码新旧视频逐帧比较，核对新冻结输入。没有重渲染，也没有把预检截图当作最终媒体截图。

| 检查点 | 实际证据与结果 |
| --- | --- |
| 首屏题名 | 帧 0 已清楚显示“三数之和：找全组合，怎样不重复？”，题名完整，无文字裁切或遮挡。通过。 |
| 05 相遇提示 | 查看帧 2680–2861 的关键状态；帧 2694–2742（89.800–91.400 秒）显示“两端已相遇，右指针不再移动”。L/R 同在下标 4，随后转为“L 与 R 相遇 → 结束本轮”。通过。 |
| 07 仍移动 R | 查看帧 3570–4214 的关键状态；帧 3621、3630、3640（120.700、121.000、121.333 秒）可见 R 从下标 4 向 3 移动，提示仍是“命中后跳过右端的当前值”，没有误套“右指针不再移动”；相遇后停止。通过。 |
| 完整代码卡 | 5498–5647 帧（183.2667–188.2667 秒）完整保留 150 帧；实际查看首、末画面，23 行 Python 代码可暂停阅读，无字幕覆盖。全部 150 帧与旧版解码像素相同。通过。 |
| 资料页与衔接 | 5648–5797 帧（188.2667–193.2667 秒），实际查看首、中、末画面；《3Sum》—LeetCode、《Sorting Techniques》—Python Software Foundation 清楚完整。代码卡到资料页边界正确，无正文字幕残留。全部 150 帧与旧版解码像素相同。通过。 |
| 媒体与冻结 | 新视频完整解码正常退出；ffprobe 帧数、帧率与音轨时长正确；本轮实际运行冻结验证，152 项通过。最终工作区干净。通过。 |

## 复用范围及身份依据

对照旧提交 `5798f6e509390afbc560c47aec1eb45588c95c5f` 和旧视频 SHA `eabbb739623aacce0fce3a60486e13a05fd3a10ea8ee0354ff2a3cd95d46a062`，没有将旧报告直接改名作为新版通过：

- 新旧 152 项冻结清单中，145 项相同；6 个共同路径更新，另一个是带内容哈希的 storyboard 快照换名。实际动画源码仅改首镜标题与相遇时的提示分支；其他更新为 revision 元数据、预检和渲染并发配置。
- 脚本、文章、plan、voice.wav、words、cues、picks、shot_frames、算法/trace、资料来源、timeline、CodeCard、data 均逐字节相同。正式 storyboard 仅 `meta.visualRevision: 1→2`，其他 JSON 内容相同。
- 对两版真实 MP4 的全部 **5798 帧**比较解码帧校验值，**5223 帧像素完全相同**；差异只在帧 **0–493** 和 **2663–2743**。03、06、07、08、09 及代码卡、资料页全部帧相同。因此沿用旧报告相应的完整算法流程、证明期间不提前移动、结果出现时机和边界示例结论。
- 两版实际 MP4 的 AAC 包校验值及时间戳记录完全一致；其 framemd5 输出 SHA-256 均为 `39f376655c11acc1b036a1e5118a1b7aa95645f4aa4d6df531751fa610902f11`。所以沿用旧版实际音轨复核范围，本轮没有重复 ASR。

## 保留的能力边界

旧报告中的 **06“右指针”自动同音识别冲突仍保留**：不能直接判定为 TTS 错误，也没有签为真人逐字听审通过。09 复杂度及结尾无辅助“好”的既有交叉识别证据沿用。自动识别和代理复核不等于真人听审。

本轮为受影响范围的成片复审，没有重复全片原速人工观看，也没有进行站点浏览器、手机全屏、发布副本或线上 SHA 验收。这些不属于本次只读复审范围。

## 关键文件 SHA-256

下列路径相对 `episodes/leetcode/three-sum/`。未变文件的完整身份同时与旧报告核对。

| 文件 | SHA-256 |
| --- | --- |
| `publication/video.mp4` | `f8a085e7b49265e25cb39970f39e1f1fed77e071eff12493ad9dbbbad61dd5b5` |
| `production/storyboard.json` | `a9808829a520c40edf6be9db938227a869fa3f187c30638d9b9effa69c4036f7` |
| `production/source-sha256.json` | `a9f05f5bda6ec20d26ac572635b37e40d13f21dca11202d453135d149c52b94a` |
| `production/remotion/src/Main.tsx` | `49b9672aae4e85d35c66f216877c389570a7ad9168c6e36724ca264ad2315660` |
| `production/script.md` | `456c5a4dbfb282fac836e40181b8e3180a3e47b217a4f4eb1d55a073c6dabdde` |
| `production/voice.wav` | `27642ce43c0119ca099adc77a6ec8998e6f053a62d1c468831ed8598aa86f4ef` |
| `production/voice/cues.json` | `1a96326479be5a558266ce56ae259d74b7ddd929c521c96cb108a71280533354` |
| `production/voice/picks.json` | `85fbfd14ca0bbaad78713e409b3956e5efa6b218acc29681fe14dc1c7e9d4ff7` |
| `production/voice/shot_frames.json` | `557ee31557e6a71f57989be6e158d0786ed717a8e7bf8bc8d3bdb380d4d7dacf` |
| `production/words.json` | `339ec6d84d5dde5185a301bbf6a1b4582d795cf26d57ab0a3b39518e67d67bbf` |
| `production/trace/main-example.json` | `4666429b57cef74cc1db8e033d01f7d896ef0dfe21a83d09e41f42e202c7c02c` |
| `production/solution.py` | `c682c9a28e05e5e5856526a10af53951a393a90c318a41dd70c16538ec556daa` |
| `production/references.json` | `daeb60f5dd9afe5df5b5caa1413880148f65a64df04a31db28534c6035ac06a2` |
| `production/reference-appendix.json` | `df3079438ef9d54c3299de35893d5d3a66a3aae17ef1a2a53aed9b5c72944e7f` |
| `production/reference-appendix-media-check.json` | `decfb39acdeb209edc6ef9fcb843c809accb4e23141577aaa0b5035ff8b41f47` |

全程未编辑制作文件、未 commit/push、未建 PR、未重新生成配音或视频。
