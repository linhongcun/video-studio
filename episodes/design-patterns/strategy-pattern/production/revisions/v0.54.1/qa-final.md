# D01章节口头衔接修订：最终检查

2026-10-24（北京时间）。用户实际观看v0.52.0后认为整体问题不大，指出章节切换缺少简短承接，听众容易把新内容当作上一模块的延续。本次按反馈集中修订04、11、15，第一句交代下一段方向，第二句才开始本节的新动作。

## 本次范围与结果

- 保持16镜32句，改录六句；其余十三镜的原PCM、局部字幕/cue、局部语音时间和镜长严格一致。
- 新片5292帧、30fps，画面176.4秒；相较原版5198帧只增加94帧，约3.13秒。
- 仅三镜由Remotion局部重渲，其余十三镜从已发布画面精确取帧后快速H.264编码。十三镜同局部代表帧最大平均RGB差0.318/255，不声称像素或码流字节相同。
- 实际1080p H.264/30fps、48kHz AAC，−16.0LUFS/−3.7dBTP；所有5292帧PTS连续，完整解码与163项冻结核对通过。
- 新视频完整SHA-256：`7f5606a875198472c7f8f052c6e0f14f180a1c9c4b21b0055cb8e9ab8da68726`，9,542,813字节。来源、映射、编码与复用证据见本期`chapter-bridge-baseline.json`、`chapter-bridge-assembly.json`、`chapter-bridge-render.json`及`chapter-bridge-picture-reuse.json`。

## 实际局部复核

独立编辑先审04/11/15与相邻文本，随后实际查看12张真实时序无字幕预演；正式编码后独立抽看18张实际帧，覆盖03尾→04、10尾→11、14尾→15。根任务另从正式MP4抽11张，实际查看其中4张章节承接/取舍帧。

三处第一句均保留承接状态和新的方向标题，第二句后才拆规则、修改75%与返回75元、展示适用条件；未发现已查看的新旧字幕串位或金额叠盖。具体文件、帧与范围在`revisions/chapter-bridges/editorial.md`、`revisions/chapter-bridges/qa-independent.md`、`revisions/chapter-bridges/root-encoded-index.json`。三个有声边界片段保留在忽略输出目录，索引为`chapter-bridge-transition-clips.json`。

本次是实际关键帧序列、句边界与字幕/旁白源核对，未称为全片人工听辨或逐字ASR。用户尚未观看修订版，不将检查通过写成其已认可。

## 站点本地检查

只同步video、script、storyboard、words四项变化；文章和封面SHA保持。两个视口各实际测试delegate、change、boundary三个入口，共六次seek，最大误差约0.000000667秒；32条VTT载入正常，视频无播放错误。

四章精确帧为0、907、3188、4541。历史firstRelease保留v0.52.0，补丁版本与线上结果见本期`release.md`和站点`online-verification.json`。本地证据为站点目录`site-bridge-copy-manifest.json`、`site-bridge-static-check.json`、`site-bridge-browser-check.json`。

## 沿用的既有验证

本次未增加技术事实或更改示例代码，沿用原六份资料、完整代码和最小差异实跑证据。原版完整交付报告归档在`revisions/v0.52.0/`，其结果与当前修订范围分开，不将旧媒体报告当作新片结果。
