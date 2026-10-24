# EP.11《抢票时，为什么总提示系统繁忙？》

2026-10-24用户授权EP01–14按今天Codex规格重制，本期为全新制作工程。只在本目录产出，不改线上旧文件；站点接入和发布由root统一完成。

- research.md记录实际读取的官方正文、日期与边界。
- script.md、article.mdx、pronunciation.md和visual-direction.md记录同一主线与逐镜因果。
- 已完成本地成片与核验，见delivery.json和qa-final.md。全片12镜、24句、3271帧、约109.0秒，1920×1080、30fps。
- 配音冰糖，使用仓内共享prep/gen/build；一条短尾候选保留a/b对比，选段见voice/picks.json、tail-comparison.json和substitutions.md。
- words.json是句级时序和声学句首起音，不是逐字ASR；能力边界如实保留。
- 冻结清单source-sha256.json包含实际脚本、选定takes、共享实现和全部Remotion输入。
- 动态小样、成片和媒体核验分别记录在qa-motion.md、qa-final.md和render-result.json。

复现：在remotion目录npm ci、npx tsc --noEmit、npm run covers、npm run render。工作区可使用EP01的集中node_modules软链；它不入库。运行渲染时Python需要numpy（使用/workspace/.venvs/video-studio/bin加入PATH），系统需要FFmpeg、Chromium和Noto Sans CJK SC。

配音复现保留原takes避免重复调用非确定性TTS：共享voice/build.py --dir episodes-codex/rate-limit，再运行本期assemble.py、共享selfcheck.py、place_v2.py --mode whole、label_onset_strict.py，然后本期freeze.py与verify.py。

最终视频video.mp4、三种封面、captions.srt供root接入同名站点slug。平台历史投稿不自动重发。

独立实际编码图审结果见qa-independent-encoded.md；所有能力限制如实记在qa-final.md。

## 站点发布

[v0.48.0](https://github.com/linhongcun/video-studio/releases/tag/v0.48.0)已完成站点部署与线上文件核验，见[发布记录](release.md)。
