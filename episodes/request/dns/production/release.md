# 输入网址后，怎么找到服务器？：全流程与局部定位重制

对应[#199](https://github.com/linhongcun/video-studio/issues/199)，本批设计ID与实际站点发布号分别追溯。保留原配音、字幕与3200帧时长，增加适合本片机制的稀疏全局图、局部聚焦、情景重置与结尾回收。

完整视频SHA-256：`832b2aa74fd3d9a84fb11b9fd602e04804bba61fc45e00c1d11ac8b051e74ca7`。具体动态、独立编辑与正式媒体证据见[最终检查](qa-final.md)。历史媒体与源见[原版索引](revisions/pre-flow-map.json)。

已由[PR #224](https://github.com/linhongcun/video-studio/pull/224)合并，随[v0.56.2](https://github.com/linhongcun/video-studio/releases/tag/v0.56.2)上线，并经[Release后Pages部署](https://github.com/linhongcun/video-studio/actions/runs/40118710238)成功。线上视频完整SHA与上述本地成片一致，字幕、章节、海报和更新日志已核验；#199已以completed关闭，见[线上证据](../../docs/flow-navigation-audit/online-verification.json)。本轮仅更新GitHub站点，用户对新版的观看反馈后续另记。

## v0.69.1 · 片尾参考资料

2026-10-25为原正文追加5秒可暂停参考资料卡，配套文章提供完整来源及对应知识点。原正文全量解码帧/时间戳、原AAC包/时间戳和PCM保持；新片尾、原生字幕结束、播放器暂停与手机全屏按实际范围复核。

[PR #330](https://github.com/linhongcun/video-studio/pull/330)、[Release v0.69.1](https://github.com/linhongcun/video-studio/releases/tag/v0.69.1)及Release后Pages40200401923已完成；完整线上媒体/海报SHA、VTT、原章节和来源链接核验通过。实际证据见[首批记录](../../docs/reference-endcards/batch-1/README.md)，本期追加输入与原正文基线在revisions/reference-endcards。仅GitHub站点，无平台重发。

## v0.70.3 · 原始题名与原文摘录

参考资料卡改为实际原题、逐字原文短引和位置，原讲解/声音/代码卡保持；当前发布3350帧，完整SHA-256：`7b4c4af1490a8c19bcc5436ed9510255daa76f81021e59b4a8f9f8884a71375c`。[PR #338](https://github.com/linhongcun/video-studio/pull/338)、[Release](https://github.com/linhongcun/video-studio/releases/tag/v0.70.3)与[Release后Pages](https://github.com/linhongcun/video-studio/actions/runs/40210425589)已完成，41次canonical GET覆盖本片完整视频/海报SHA、VTT、原章节/日期/引用和更新日志通过。实际来源、媒体保真与播放器范围见[本批记录](../../docs/reference-endcards/original-titles/README.md)。仅GitHub站点，无平台重发；不表示用户已观看认可。

## v0.71.2 · 题名与署名简表

资料片尾统一只显示完整原始题名和作者/机构，一页5秒；原引文/定位等保留文章研究，正文、声音、代码卡不变。当前3350帧，完整SHA-256：`ad3835685fc98d460602cfc0766bc586154d6441fce50b82fe66280909e552af`。[PR #345](https://github.com/linhongcun/video-studio/pull/345)、[Release](https://github.com/linhongcun/video-studio/releases/tag/v0.71.2)与[Release后Pages](https://github.com/linhongcun/video-studio/actions/runs/40284847950)完成，69次canonical完整GET覆盖本片媒体/海报SHA、字幕、章节/日期、引用及更新日志通过。实际检查与限制见仓库docs/reference-endcards/title-author。仅GitHub站点，无平台重发或本版观看认可。
