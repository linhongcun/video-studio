# EP.63 · LC.994 `rotting-oranges` 最终质检与验收报告

- **期数与标识**：EP.63 / `LC.994` / `rotting-oranges` / `series: leetcode` / Issue [#515](https://github.com/linhongcun/video-studio/issues/515)
- **基线与分支**：`origin/main` 实际完整提交 `860180740cea3c44bd60f568bc3d0ceb6353717d`（注：冻结前 `production/README.md` 第 3 行曾手误转录后 32 位哈希，按冻结规则保留原文件字节并在此勘误）；制作分支 `feat/lc994-rotting-oranges`
- **最终成片完整 SHA-256**：`967ad12db0b8a60158087088b4af46f56f8b4bf659cff3bb71c785294dc854ec`
- **正文成片完整 SHA-256**：`4326d42d0d7fd8a57269ac8ba6a1f57c7bb0f5aa6de40c3a7081de19937744fb`
- **画面与音频规格**：`1920×1080` H.264 `yuv420p` limited `bt709`（`color_range=tv`, `color_space/transfer/primaries=bt709`），`30/1 fps`，共 `7992` 帧（`266.40s` = 正文 `7692` 帧 + 完整 Python 代码卡 `150` 帧 `[7692..7841]` + `title-author` 参考资料页 `150` 帧 `[7842..7991]`）；AAC `48000 Hz` 立体声 `12255` 包，`-16.0 LUFS`，`-3.1 dBTP`。

## 1. 各阶段检查汇总

| 阶段 | 执行者 | 结果 | 关键证据与指标 |
| --- | --- | --- | --- |
| 原文调研与来源预检 | 统筹/制作 | PASS | 3 项一手来源实读存证（`research/source-evidence.json`、`references.json`）；`check-references.mjs --sources` 通过 |
| 算法正确性与独立 Oracle 对拍 | 制作 | PASS | `tests/test_solution.py` 5/5 通过（官方三例 + 边界 + 8 种 `m,n≤3` 小网格共 1,614 组穷举 + 3,000 组至 `6×6` 随机网格，与独立逐源 BFS oracle 一致） |
| 配音前独立逻辑与图文结构审读 | 独立只读 `research` 子代理 `60129680` | 第 1 轮 `REVISE` → 第 2 轮 `PASS` | `qa/independent-review-round1.md`、`qa/independent-review-round2.md`；全部阻塞项清零后再批量合成配音 |
| 真实配音、听辨与整轨装配 | 制作 | PASS | MiMo TTS 音色「冰糖」48 候选 → 全部 24 句逐句音频听辨，检出并替换 9 句多音字/断句（`voice/substitutions.md`），复听全部清晰无错；整轨 `-16.0 LUFS`、`-1.4 dBTP`、相邻句响度差 `0.2 dB`、0 丢音、`place_v2 --mode whole` 偏移 `0.0` 帧、`label_onset_strict` 0 失败 |
| 三比例封面生成与安全区核验 | 制作 | PASS | `qa/covers-report.json`；`cover-16x9.jpg` (`db456f97…`)、`cover-4x3.jpg` (`f0f06e27…`)、`cover-3x4.jpg` (`6d103841…`)，仅安装本期，旧期 `cover-style.json` 未受影响 |
| 渲染前 Remotion DOM 预检 | 制作 | PASS | `qa/preflight/report.json`；87 帧 0 越界、0 字幕遮挡、首屏题名/越界跳过/碰撞去重/停止守卫/完整 27 行代码卡边界全通过 |
| 生产输入冻结与一次性全片编码 | 制作 | PASS | `source-sha256.json` 143 项冻结；单次 `render.py` 与 `render.py --verify` 通过，全片 `ffmpeg -f null -` 0 错误，正文解码帧 MD5 与 12,255 包 AAC/PCM 完整一致 |
| 独立成片与片尾附录复核 | 独立只读 `research` 子代理 `324930f1` | PASS | `qa/encoded-review.json`；14 帧成片抽帧（含代码卡与参考资料首/中/末交界）、2 张配套图与 4 份回执全通过；正文/代码卡/资料页底色实测 `(14,24,42)` / `(15,22,41)`，相对 `#0F172A` 偏差 ≤1 |
| 站点构建与双视口真实浏览器验收 | 制作（真实 Chrome + Playwright） | PASS | `check-layout.py`、`check:dates`、`check:references`、`check:articles`、`site build`（189 页）通过；桌面 `1440×900` 与手机 `390×844` 亮暗 4 组合 0 横向溢出、0 控制台错误；视频播放 Canvas 取色 `[14,24,42]`/`[15,22,41]`；原生 VTT 默认关闭（`burnedInCaptions: true`）、24 条字幕于 `256.399s` 结束且代码卡/资料页 0 活动字幕；2 张 `1920×1080` 配图加载及 `147s`/`184s` 回看、原图 200、章节跳转 `189.10s`、目录不改变播放时间、`SourceQuote` 浮层单开与排版均通过 |

## 2. 配套图文站点派生记录（成片后）

为严格保留已编码视频的冻结输入清单（`production/source-sha256.json` 143 项不变），真实浏览器截图复核发现 `SourceQuote` 共享组件会自动输出「译文」标签后，仅在站点发布副本中去掉 3 处 `translation` 属性中重复的 `译文：` 前缀：

- 冻结制作稿 `production/article.mdx` SHA-256：`29d71cfa9030955868818a4e15b61fe50b6bc8f51f7747bde28560ffb3261d98`（未改动，`freeze.py --verify` 通过）
- 站点发布稿 `publication/article.mdx` SHA-256：`7b7ea87bd24eb7e67ce20d2713aa7acf49480a6b388b3ab25687e9e8edf64912`
- 配套关键帧（从最终 `video.mp4` 按 limited BT.709 → full BT.601 转换导出，L059）：
  - `publication/article/01.jpg`（帧 `4404` / `seekTo={147}`，第 2 分钟碰撞去重）：SHA-256 `a5a11d7f997fdbb2e051cc16d35036d761ecd281011beb68a74dc387175ade64`
  - `publication/article/02.jpg`（帧 `5520` / `seekTo={184}`，第 3 分钟停止守卫）：SHA-256 `479d7f4c4b9b17b2d8a3403e65817e69a8f474765248ddff92f63492275180f3`

## 3. 核验范围与能力边界（如实记录）

- **音频与时序**：已完成全部 24 条入选 WAV 的多模态音频逐句听辨与声学包络句级装配（`asrModel: "none"`, `wordAlignment: false`）；未运行本地 `faster-whisper` 逐字 ASR，未引入外部人类听审员复听。
- **动态与成片**：已完成 87 帧 Remotion DOM 预检、14 帧最终编码帧独立逐图复核与 2 张配套关键帧实看；未进行 4 分 26 秒全片实时连续观看。
- **浏览器与设备**：已完成桌面 `1440×900` 与 Chromium 手机模拟 `390×844` 亮暗主题验证；未在物理 iOS/Android 手机真机上测试。
- **发布范围与认可**：本次仅覆盖 GitHub PR、Release `v0.111.0` 与 GitHub Pages 站点（按 `docs/RULES.md` STATUS 持续授权），不涉及外部视频平台投稿，也不代表已获用户观看认可或教学效果量化结论。
