# EP.05 CDN 地图与术语返工发布记录

2026-10-24 22:24:22（北京时间），[v0.50.3](https://github.com/linhongcun/video-studio/releases/tag/v0.50.3)已按持续授权完成GitHub站点发布与线上文件核验，历史平台投稿保留。

- [媒体PR](https://github.com/linhongcun/video-studio/pull/162)，合并提交`123ff03407351419fd69da303a568fd4185c9f74`；Release后[再次部署](https://github.com/linhongcun/video-studio/actions/runs/40102166946)。
- 成片3989帧，完整SHA-256：`3715e0514c8ec1cef02a8b32027910de16fd18b04ef5b1b0191f9596f277d9e6`。
- 真实大陆轮廓与节点路径、CDN/边缘节点/回源的名称解释、过期后的接收状态已按本期QA完成检查。
- 线上canonical视频/海报完整SHA及字节数、VTT逐字节、HTML标题/章节/当前源码入口，以及首页版本与Release更新日志全部通过。见[实际GET证据](https://github.com/linhongcun/video-studio/blob/main/docs/cdn-map-terms/online.json)。
- 冻结生产输入在发布记录写入前后逐项全文SHA一致。未执行逐字ASR或完整人工听辨，文件核验不冒充完整观看或听辨。

本次按用户观看旧版后的反馈返工，自主上线不表示用户已观看或认可新版。旧v0.48.0资料见[历史快照](revisions/v0.48.0/README.md)。

## v0.69.3 · 第二批片尾参考资料

2026-10-25补充可暂停的片尾参考资料，并在文章提供完整出处和对应知识点；默认制作入口已接入参考资料流程。原正文全部解码帧/时间戳、AAC包/时间戳与PCM保持，不重新配音或整条渲染。

[PR #333](https://github.com/linhongcun/video-studio/pull/333)、[Release v0.69.3](https://github.com/linhongcun/video-studio/releases/tag/v0.69.3)及Release后Pages40205865861均完成，完整线上媒体/海报SHA、VTT、原章节与来源链接核验通过；完整记录见[第二批](../../docs/reference-endcards/batch-2/README.md)。原正文基线及追加回执见revisions/reference-endcards。只上GitHub站点，无平台重发。

## v0.70.3 · 原始题名与原文摘录

参考资料卡改为实际原题、逐字原文短引和位置，原讲解/声音/代码卡保持；当前发布4289帧，完整SHA-256：`55dac48af13a3d8e49bb8070223d5340af2239654b5f2e30361d1a478146ac2a`。[PR #338](https://github.com/linhongcun/video-studio/pull/338)、[Release](https://github.com/linhongcun/video-studio/releases/tag/v0.70.3)与[Release后Pages](https://github.com/linhongcun/video-studio/actions/runs/40210425589)已完成，41次canonical GET覆盖本片完整视频/海报SHA、VTT、原章节/日期/引用和更新日志通过。实际来源、媒体保真与播放器范围见[本批记录](../../docs/reference-endcards/original-titles/README.md)。仅GitHub站点，无平台重发；不表示用户已观看认可。

## v0.71.2 · 题名与署名简表

资料片尾统一只显示完整原始题名和作者/机构，一页5秒；原引文/定位等保留文章研究，正文、声音、代码卡不变。当前4139帧，完整SHA-256：`22307927f9fc084aac1df1e07d91c6e24578ac7bc028b3b5b27af88fe6f78d37`。[PR #345](https://github.com/linhongcun/video-studio/pull/345)、[Release](https://github.com/linhongcun/video-studio/releases/tag/v0.71.2)与[Release后Pages](https://github.com/linhongcun/video-studio/actions/runs/40284847950)完成，69次canonical完整GET覆盖本片媒体/海报SHA、字幕、章节/日期、引用及更新日志通过。实际检查与限制见仓库docs/reference-endcards/title-author。仅GitHub站点，无平台重发或本版观看认可。
