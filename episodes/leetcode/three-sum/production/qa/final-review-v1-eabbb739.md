# LC.15 最终媒体独立复核：旧版 eabbb739

**结论：旧版不作最终验收。除主会话正在修正的两项显示问题外，本轮没有发现其他可确认的算法、动画或媒体阻断项。指定声音已用实际 MP4 音轨交叉识别；09 复杂度与末尾无辅助“好”得到支持，06“右指针”的精确发音仍不能据自动工具确定。不能据此声称完成真人逐字听审。**

主会话已通知会重渲染一次；本报告只记录旧版剩余检查结果，不适用于随后任何新视频 SHA。

- 执行者：独立 reviewer Devin，session `00e1dcdb7f8d42ffab4a3f90d14a8d50`。
- 固定提交：`5798f6e509390afbc560c47aec1eb45588c95c5f`。
- 视频：`episodes/leetcode/three-sum/publication/video.mp4`。
- **视频 SHA-256：`eabbb739623aacce0fce3a60486e13a05fd3a10ea8ee0354ff2a3cd95d46a062`。**
- 实测：1920×1080，30 fps，5798 帧，193.2667 秒；正文 5648 帧，参考资料 150 帧。
- 本轮未编辑仓库文件、未提交/推送、未做 TTS、未重新渲染、未启动站点验收。报告及提取证据置于仓库外。

## 已知必须修正项

| 项目 | 旧版位置与表现 | 修订要求 |
| --- | --- | --- |
| F1：首镜未明确显示题名 | 0–16.467 秒，LC.15 与方法/说明可见，但首镜没有明确写“三数之和”。`production/remotion/src/Main.tsx:114,124`。 | 首镜标题补题名；新片须查看实际画面和裁切。 |
| F2：相遇后说明仍称跳过右端 | 约 89.800–91.400 秒，帧 2694–2742，05 镜 L、R 已同在下标 4，R 没有位移，说明仍为“命中后跳过右端的当前值”。`production/remotion/src/Main.tsx:62`。 | `l >= r` 的无位移状态应说明已相遇、R 不再移动；保留 07 镜仍有 R 位移时的去重说明。 |

以上两项与主会话最新通知一致。F2 是显示文案问题；实际 05 镜指针运动是正确的。

## 实际检查范围与方法

1. 对最终 MP4 做完整视频/音频解码；`ffmpeg -v error -xerror ... -f null -` 正常退出，另一次整轨响度扫描正常完成。
2. 将整片按 1 fps 提取为按时间排列的画面，实际顺序审看全部 10 页，覆盖开头至最后一秒；另看 03/05/06/07 各 16 张密集动作帧，以及代码卡开始前后、末正文帧与资料页的 1920×1080 原尺寸画面。抽样图像检查不等同于逐帧、原速人工观看。
3. 从真实 MP4 连续解码全部 **5798 帧**，按画面中的 L/R 色块位置测量指针轨迹；另连续检查结果区填充状态。该项用于排查证明期间提前移动、R 是否实际保持不动以及结果出现时间，不把源码预期替代成片测量。
4. 对照固定提交的脚本、plan、正式 storyboard、voice cues/picks/shot_frames、实际渲染源码、trace、资料页输入及已有 QA；`freeze.py --verify` 实际输出 **152 LC15 frozen inputs unchanged**。
5. 从最终 MP4 解码出 16 kHz 单声道音频，在 104.000–114.400 秒、168.000–188.2667 秒、179.000–188.2667 秒三个区间独立运行 faster-whisper small；结合本轮 describe_audio、制作方最终 ASR 和原始失败转写交叉判断。small 的初次文件解码因 PyAV 参数兼容失败，改为将解码后的 numpy PCM 输入模型后成功完成；没有改音频内容。

**能力边界：**未完成真人逐字听审；自动语音工具对普通话算法术语存在明显同音误识别。未做发布站点的暂停/全屏、移动端或导航验收，该范围由主会话的浏览器 agent 负责。

## 其余视觉、算法与媒体结果

帧号均从零开始，秒数为帧号除以 30；像素轨迹采用色块中位位置，允许压缩与文字挖空造成约 2 像素波动。

| 检查点 | 实际成片证据 | 结论 |
| --- | --- | --- |
| 03：证明期间 L 不提前走 | 36.833–48.767 秒，帧 1105–1463，359 个连续帧中的 L 色块位置保持不变，R 也保持最右。第二句之后才开始向内；首次超过基线 2 像素的 L 位移在帧 1498，49.933 秒。 | 通过。固定 -4 的候选查完，结果区保持空。 |
| 04：第一组答案 | 主例排序数组、i/L/R、和等于 0 与第一组 `[-1,-1,2]` 一致；随后左右端点各自跳过当前值，再到第二次命中。 | 通过。 |
| 05：只有 L 3→4，R 不动 | 全镜 77.000–95.400 秒，帧 2310–2861，共 552 帧，R 色块始终在 x=1300；L 从下标 3 向下标 4 移动，约帧 2684 / 89.467 秒起保持与 R 相遇。 | 运动通过；相遇后的说明须按 F2 修正。 |
| 06：重复固定值与偏大证明 | 先跳过重复 -1，再固定 0、L=4、R=5、和=3。第二句开始帧 3134 / 104.467 秒至帧 3287 / 109.567 秒，154 个连续帧的 R 位置全为 x=1550。 | 证明期间没有提前移动 R。 |
| 06：内部 move cue 后再移动 | 正式 cue 为帧 3287.45 / 109.582 秒；画面中 R 首次显著位移在帧 3313 / 110.433 秒，向左到下标 4 并与 L 相遇。cue 是动作段起点，不是首个像素变化时刻。 | 通过，无提前移动。 |
| 07：重复值与相遇即停 | 114.400–140.500 秒切换为 `[-2,0,0,2,2]`；先命中 `[-2,0,2]`，L 从下标 1 越过两个 0 到下标 3，随后 R 从 4 到 3。约 120.133 秒 L 已稳定在下标 3，121.600 秒 R 相遇后保持稳定至镜尾。结果始终仅一组。 | 通过；未越过相遇位置继续移动。 |
| 结果区不提前输出 | 以真实像素逐帧检查主例结果区：第一行首次出现为帧 1891 / 63.033 秒，第二行首次出现为帧 2400 / 80.000 秒；均在各自命中镜中。07 开头帧 3432 清空主例答案，补例结果在帧 3537 / 117.900 秒出现。 | 通过。01 题意镜在解释官方输出时展示答案属于输入/输出说明；进入推导后未携带未来答案。 |
| 08：允许重复数值、不同位置 | 140.500–159.833 秒，三个 0 分属 i、L、R 三个下标，输出 `[[0,0,0]]`；后续 `[0,1,1] → []`，没有把相同数值误当成同一位置。 | 通过。 |
| 09：复杂度 | 画面显示 O(n²)、每轮 O(n)×最多 n 轮、除输出外 O(n)，并注明有序副本与排序工作空间。与实现相符。 | 通过。 |
| 完整代码卡 | 183.2667–188.2667 秒，帧 5498–5647，共 150 帧；实际查看首帧和末帧，完整 23 行可见。包括 `l < r`、两端 while 去重以及最后 `return ans`，没有字幕覆盖代码，字形和缩进可暂停读。最终 article 的代码段与 solution.py 字节一致。 | 通过。 |
| 资料页 | 188.2667–193.2667 秒，帧 5648–5797；实际查看原尺寸画面，显示《3Sum》—LeetCode、《Sorting Techniques》—Python Software Foundation。字清楚，标题及机构无裁切，无虚构个人作者。 | 通过。 |
| 媒体与冻结身份 | 完整解码通过；重新计算视频 SHA 与要求一致；152 项冻结输入通过。整轨实测 -16.02 LUFS、-3.21 dBTP，与制作报告 -16.0 / -3.2 的取整一致。 | 通过。响度数值不等同于听感验收。 |

## 指定音频的交叉核查

以下全部涉及真实最终 MP4 音轨，不只读取脚本或旧 QA。

| 区间 | 本轮获得的证据 | 判断与限制 |
| --- | --- | --- |
| 06：约 104.5–111.5 秒，“右指针”两处 | 制作方 medium 整轨 ASR 正确识别“对这个右指针……所以可以安全左移右指针”。本轮 small 独立识别成“对这个幼稚针……所以可以安全左移幼稚针”，本轮 describe_audio 也有“柚子针”等明显错误；其余“最小候选/换更大的数只会更大/左移”语义可对应。 | **精确发音未能确定。**这些结果是同音/近音识别冲突，不能直接证明 TTS 说错，也不能签为真人听辨通过。本轮未确认需要重配。 |
| 09：168–182.5 秒，复杂度 | small 从实际片段识别到“每轮两个指针只向内走……总时间是平方级……额外空间是线性级，完整代码请暂停阅读”；夹有“线性部数/便利/排须人组/出书出外”等术语误字。最终 medium 整轨同样保留平方级、线性级和暂停阅读语义。 | 自动复核支持复杂度语义正确，没有平方/线性互换的证据；不声称普通话每字发音已获真人验收。 |
| 09：179–188.2667 秒，尾部辅助“好” | small 对实际尾部独立识别为“额外空间是线性级，完整代码请暂停阅读。”，未识别出“好”；完整 09 片段同样终止于“阅读”。voice/picks.json 选定 `09-close-2=b`，最终 medium 整轨尾部也无“好”。 | 多路证据支持旧 a take 的辅助“好”已去除；未发现残留。不会将 describe_audio 的“无异常”当作真人确认。 |

## 新 SHA 到达后的聚焦复核范围

查看首镜实际题名与布局、05 相遇后的新说明，以及 07 真实右指针移动时的说明是否仍正确；同时确认新旧脚本/音频/trace/cue 字节未变，视频帧数、完整代码卡和资料页保留。新的 MP4 必须重新绑定完整 SHA；本报告不得直接改写为新版通过。

## 本轮输入与证据 SHA-256

仓库路径以下均相对 `episodes/leetcode/three-sum/`。`review/` 为本 reviewer 在仓库外从最终媒体产生的测量/识别证据，列出身份以便追溯，不属于制作输入。

| 文件 | SHA-256 |
| --- | --- |
| `publication/video.mp4` | `eabbb739623aacce0fce3a60486e13a05fd3a10ea8ee0354ff2a3cd95d46a062` |
| `production/script.md` | `456c5a4dbfb282fac836e40181b8e3180a3e47b217a4f4eb1d55a073c6dabdde` |
| `production/article.mdx` | `1f65d8e2d6b41cde5242c5bdf55ac164e7ddedc72d1938a2398d658859213803` |
| `production/plan.json` | `bd5ee38d59bce1e6ae9fbe34bf88f76f3522b4aba08e267c59811a5b7d158cc2` |
| `production/storyboard.json` | `dea4482f52fafdb9b0b1bc3632718e1c094a364b2d9725e768aece7b3761a3fc` |
| `production/solution.py` | `c682c9a28e05e5e5856526a10af53951a393a90c318a41dd70c16538ec556daa` |
| `production/solution.json` | `54a5e3a17e1559ed0cd1d7d7f3e841a3d3f807bf09a6dadd36951bb8cbf736ea` |
| `production/trace/main-example.json` | `4666429b57cef74cc1db8e033d01f7d896ef0dfe21a83d09e41f42e202c7c02c` |
| `production/source-sha256.json` | `cb741c34be4948ec08d745b7538e75c926dafc3a861105037766c95dbf8a7049` |
| `production/voice/cues.json` | `1a96326479be5a558266ce56ae259d74b7ddd929c521c96cb108a71280533354` |
| `production/voice/picks.json` | `85fbfd14ca0bbaad78713e409b3956e5efa6b218acc29681fe14dc1c7e9d4ff7` |
| `production/voice/shot_frames.json` | `557ee31557e6a71f57989be6e158d0786ed717a8e7bf8bc8d3bdb380d4d7dacf` |
| `production/voice/asr_full.json` | `a08d84bd0db8821543c307006b8216598b4cf24c5b60f87976d22d24cd8b07e5` |
| `production/voice.wav` | `27642ce43c0119ca099adc77a6ec8998e6f053a62d1c468831ed8598aa86f4ef` |
| `production/mix-report.json` | `c270a85080843478ff066071c744a60797c5f3b9657346f72f1963b49c7c90fc` |
| `production/qa/tts-listen-results.json` | `0631060bac26a5e9e5835168d4cae6ac79a21698c2dacef34592ad8fdd2c49d5` |
| `production/qa/tts-review.md` | `60ac2900ef7251549a420282874f26691bcaf5e4b37b7af6a252fb140960e498` |
| `production/qa/preflight/report.json` | `b6909e11727ccc8567e49063770a3b16e05a96a612c8ee109051a9b5325717d3` |
| `production/references.json` | `daeb60f5dd9afe5df5b5caa1413880148f65a64df04a31db28534c6035ac06a2` |
| `production/reference-appendix.json` | `e67204cdccd6ff08442a5eaa722fd74466d89c7df38cc4b8bdfc98af16041cf9` |
| `production/reference-appendix-media-check.json` | `571d0e731466cb6ac29020e3826b0d7080b8578b049d604a6db6e2ea860acf53` |
| `production/remotion/src/Main.tsx` | `93d88c196a463a2494022b9d7ad8ed1c5e42e42496ce6f328513f87f62bf6be0` |
| `production/remotion/src/timeline.ts` | `14773a8d2affbb3570a72c7dea6e6f869fde53aacca001fb2582ca4e779962ec` |
| `production/remotion/src/CodeCard.tsx` | `cb56f98a6c1a5bb624dd98d434632914721691f68ae4165ffc36cf829340ee2d` |
| `review/06-audio-small-asr.json` | `b667b3f308095e6eaf9ee7fd9d930653279b4b3b8a5c93fb16eec48495098475` |
| `review/09-audio-small-asr.json` | `874645cbbd581392db238d6a8a79595de9829803a07cad95736b37087c63ee98` |
| `review/tail-audio-small-asr.json` | `f9c50d477711284a195ccc431ca1dc265312dadff98d2d018ac92db15c47782d` |
| `review/pill-tracks.json` | `6583b23f6d1fde18d0eab8362cbc621f8e674e75d9468453d8d45295f1abe2ce` |
| `review/result-visibility.json` | `d613abd9614e133b0c4aaad228469e5d2ccb8b4a538453df9d4f7f47bd298edc` |

最终工作区状态检查为空，HEAD 仍为上述固定提交。
