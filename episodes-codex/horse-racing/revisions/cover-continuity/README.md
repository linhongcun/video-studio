# horse-racing · 正文与封面视觉统一

2026-10-28，状态：高清成片与音频身份检查完成，独立视觉与站点发布状态见批次报告。

当前视觉入口：[../../remotion/src/cover-continuity/index.ts](../../remotion/src/cover-continuity/index.ts)。共用[系列主题与制作入口](../../../_shared/puzzles-video/README.md)。原题、脚本、旁白、字幕、时序和模型继续使用原文件；旧Remotion入口和旧冻结只保留历史身份。

本修订的`source-sha256.json`是独立新输入清单，`baseline-publication.json`绑定旧发布MP4、提交与原元数据。声音从旧发布MP4完整流拷贝；`baseline-audio-check.json`记录全部AAC包及解码PCM比较。`render-result.json`与两份reference receipt只在真实制作后生成，不列入编码前输入。

仓根命令：

```bash
python3 episodes-codex/_shared/puzzles-video/render.py horse-racing --freeze
python3 episodes-codex/_shared/puzzles-video/render.py horse-racing --render
python3 episodes-codex/_shared/puzzles-video/render.py horse-racing --verify
```

输入改动须保留本目录并选择新`--revision`；不要重写清单追认。正文与资料页、最终媒体及站点验证见[本批记录](../../../../docs/archive/2026-10/puzzles-video-style/README.md)。不把本轮视觉/技术复核当作新技术调研、逐字ASR、全片人工听辨或用户观看认可。
