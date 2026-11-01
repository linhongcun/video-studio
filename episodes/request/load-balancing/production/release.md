# 数据库身份修订（#230）

一台服务器忙不过来，怎么办？：保留原配音、字幕与3186帧时长，给真实库角色增加MySQL识别标记，内部记录与提交范围保持。

当前视频完整SHA-256：`3a6e0bc31c9d51c49412af3d2d17d03f418528d8ece057e7079ea05261389163`；原混合AAC逐字节保持。正式媒体/预演/fresh复现的实际范围见[本轮QA](qa-mysql-identity.json)。图标来源为Devicon，原始SVG、MIT notice和品牌说明见[共享素材](../_shared/database-identity/source.json)，不称官方授权素材。

[PR #235](https://github.com/linhongcun/video-studio/pull/235)已合并，随[v0.58.1](https://github.com/linhongcun/video-studio/releases/tag/v0.58.1)发布；[Release后Pages部署](https://github.com/linhongcun/video-studio/actions/runs/40147968820)成功。线上10支完整视频SHA、字幕、章节、封面、源链接与实际更新日志核验通过，#230已以completed关闭。仅更新GitHub站点，用户对新版的观看反馈后续另记。

[实际线上证据](../../docs/mysql-database-identity/online-verification.json)。

## 历史发布记录

# EP.06 站点发布记录

2026-10-24 19:53:36（北京时间），按用户持续授权发布[v0.48.0](https://github.com/linhongcun/video-studio/releases/tag/v0.48.0)，只上GitHub站点，保留历史平台投稿。

- 媒体[PR](https://github.com/linhongcun/video-studio/pull/151)，合并提交 `81ced01a028827ddff1c66138e2d718031ddfdc1`；Release后再次[部署](https://github.com/linhongcun/video-studio/actions/runs/40091595906)。
- 成片3186帧，完整SHA-256：`c2f9274453d1e816f0b44fcd3ed52d0a59a56699b88a40c4638c4f8b998debcd`。
- 本地制作检查、冻结输入、实际编码抽帧、站点构建及浏览器验证见本期QA和批次记录。
- 线上canonical视频、海报完整SHA与字节数、VTT逐字节、HTML章节/标题/源码入口，以及首页版本、更新日志实际Release链接均已核验。
- [完整线上证明](../../docs/codex-remake-ep01-14/online.json)保留逐项GET结果；检查不冒充完整人工播放、逐字ASR或独立完整听辨。

按持续授权自主发布不表示用户已经观看认可。后续反馈应重新冻结受影响输入并检查、发布。

## v0.70.4 · 第三批片尾参考资料

本片补充一页5秒可暂停资料卡，保留实际原题、连续原文摘录和位置；原正文/音轨/分镜与视觉保持，最终3336帧，完整SHA-256：`4975964050b2944001c23d40828879bbc04479366fa55889d02db8283c24580e`。[PR #339](https://github.com/linhongcun/video-studio/pull/339)、[Release](https://github.com/linhongcun/video-studio/releases/tag/v0.70.4)和[Release后Pages](https://github.com/linhongcun/video-studio/actions/runs/40242724829)完成。13次canonical完整GET覆盖本片视频/海报SHA、字幕、章节、出处和更新日志通过，见[本批记录](../../docs/reference-endcards/batch-3/README.md)。仅GitHub站点，无平台重发或本版用户观看结论。

## v0.71.2 · 题名与署名简表

资料片尾统一只显示完整原始题名和作者/机构，一页5秒；原引文/定位等保留文章研究，正文、声音、代码卡不变。当前3336帧，完整SHA-256：`95fbf079d44373439a70f3be3eab230c3352d2224c490e2d22b88552788446bc`。[PR #345](https://github.com/linhongcun/video-studio/pull/345)、[Release](https://github.com/linhongcun/video-studio/releases/tag/v0.71.2)与[Release后Pages](https://github.com/linhongcun/video-studio/actions/runs/40284847950)完成，69次canonical完整GET覆盖本片媒体/海报SHA、字幕、章节/日期、引用及更新日志通过。实际检查与限制见仓库docs/reference-endcards/title-author。仅GitHub站点，无平台重发或本版观看认可。
