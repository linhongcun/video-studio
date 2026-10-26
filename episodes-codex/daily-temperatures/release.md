# 每日温度：还要等几天，才会更暖？ 发布记录

首次发布v0.69.0；[内容PR #306](https://github.com/linhongcun/video-studio/pull/306)合并`6b1c3705b229cef18e0823f350518dda6143199c`，Release后Pages 40198237161成功。线上核验2026-10-25T21:39:05.600725+08:00通过，issue #80已completed关闭。

4538帧/151.267秒，最后150帧完整Python暂停卡。正式视频完整SHA256：`11f6bbfae10e05670285f7c5733369268b07d4d89ef5a25ec2821b8745a66df4`。制作与发布副本、附注tag及线上完整文件一致，声音/程序/真实预演/实际MP4的检查范围见qa-final.md与qa-media-independent.md。

网站实际3build/2日期/2历史检查，失败与修后记录保留；精确首卡原生字幕无cue。文章派生与全站VTT边界范围、最新主干保持、所有HTTP响应、发布及关闭issue证据统一见[批次](../../docs/leetcode-batch-next/README.md)。首次交付时未发外部平台、尚无观看反馈；用户随后指出基础概念跳步，以下修订记录取代“尚无反馈”状态，不声称ASR或全片人工听辨。

## 单调栈前置修订

用户已观看旧版并指出默认观众懂单调栈。现先演栈的同端存取、后放先取、栈底/顶，再演温度不升与维护，最后合称单调栈。4句新增、28句take复用；Python仍5秒，新增默认5秒参考资料卡，最终5472帧/182.4秒。完整SHA256：`f3aa4f315770896ef3b3d15d8ad3d38ed5602d07528d9fcc20300bad3d6b3a3b`。190项生产输入、实际预演、独立最终MP4视觉/媒体与音源检查通过，原片/原QA在revisions/stack-primer-before。

内容PR #335合并d6b7e61b52d6ea06f4976786df34097235250cf0，附注tag/Release v0.70.1后manual Pages40207127313成功，15:34:17Z首轮10次完整HTTPS核验通过；视频/海报全文SHA、32字幕/四章、完整Python/两卡边界、参考资料/日期及本Release自身关联均一致，45其他课849文件保持。发布、线上和真实检查范围见[本轮修订](../../docs/daily-temperatures-stack-primer/README.md)。首发v0.69.0、slug/标题、createdAt/publishedAt保持，修后用户观看与学习效果尚未取得。

## v0.70.3 · 原始题名与原文摘录

参考资料卡改为实际原题、逐字原文短引和位置，原讲解/声音/代码卡保持；当前发布5472帧，完整SHA-256：`67907fdb572b7fe681c69050936f5d20bc10c45e72fce07a95d3146bce98c343`。[PR #338](https://github.com/linhongcun/video-studio/pull/338)、[Release](https://github.com/linhongcun/video-studio/releases/tag/v0.70.3)与[Release后Pages](https://github.com/linhongcun/video-studio/actions/runs/40210425589)已完成，41次canonical GET覆盖本片完整视频/海报SHA、VTT、原章节/日期/引用和更新日志通过。实际来源、媒体保真与播放器范围见[本批记录](../../docs/reference-endcards/original-titles/README.md)。仅GitHub站点，无平台重发；不表示用户已观看认可。

## v0.71.2 · 题名与署名简表

资料片尾统一只显示完整原始题名和作者/机构，一页5秒；原引文/定位等保留文章研究，正文、声音、代码卡不变。当前5472帧，完整SHA-256：`60e3192f057f70bb11c6ebd60ea6a971a7c0258ed1e7e86da46d502637f4224e`。[PR #345](https://github.com/linhongcun/video-studio/pull/345)、[Release](https://github.com/linhongcun/video-studio/releases/tag/v0.71.2)与[Release后Pages](https://github.com/linhongcun/video-studio/actions/runs/40284847950)完成，69次canonical完整GET覆盖本片媒体/海报SHA、字幕、章节/日期、引用及更新日志通过。实际检查与限制见仓库docs/reference-endcards/title-author。仅GitHub站点，无平台重发或本版观看认可。
