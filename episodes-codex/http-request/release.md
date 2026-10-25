# EP.01 本次站点交付

北京时间2026-10-25 19:53:15完成线上核验。当前内容通过[PR #288](https://github.com/linhongcun/video-studio/pull/288)合并，提交f1fe833c70ee0a6c9e3296ba2710b77f05a34823；附注tag及[Release v0.68.2](https://github.com/linhongcun/video-studio/releases/tag/v0.68.2)已发布，Release后[Pages部署](https://github.com/linhongcun/video-studio/actions/runs/40190399664)成功，head与tag一致。

原标题、URL、创建与首发时间、历史平台链接保持；实际内容修改时间为2026-10-25T19:38:59+08:00。当前成片5406帧/180.2秒，9,161,920字节，完整SHA-256 `593c528daae0aca8540d9daa34e53455fce6776fcdc330ff3ff705564234a1c6`。

- 114生产输入、14句首cue、完整解码、−16.0LUFS/−3.8dBTP，以及独立真实动态和31个正式MP4时点通过；范围见qa-final.md。
- 最新站点构建、42条日期与课程路径检查通过。双视口34条原生字幕和28次章节/正文seek、播放ended、海报与日期标识通过；整合EP20时通过严格SHA证明复用不变检查，定向验证最终v0.68.2页面。
- 正式首轮9次完整HTTPS GET共9,691,106字节，线上MP4/海报完整SHA、34条字幕逐句时序、七章精确起点/锚点、源入口、日期版、RSS首发、目录/库/首页及本Release自己的更新日志条目一致。实际报告见[线上证据](../../docs/http-request-depth/online-verification.json)。

[#283](https://github.com/linhongcun/video-studio/issues/283)已在上述核验后以completed关闭。只上GitHub站点，平台未新发。未执行逐字ASR、完整人工听辨或初学者实验，不把独立检查和上线写成用户已经观看认可本次修改。修前v0.48.0交付记录保存在revisions/technical-depth-v2/release.md。

## v0.69.3 · 第二批片尾参考资料

2026-10-25补充可暂停的片尾参考资料，并在文章提供完整出处和对应知识点；默认制作入口已接入参考资料流程。原正文全部解码帧/时间戳、AAC包/时间戳与PCM保持，不重新配音或整条渲染。

[PR #333](https://github.com/linhongcun/video-studio/pull/333)、[Release v0.69.3](https://github.com/linhongcun/video-studio/releases/tag/v0.69.3)及Release后Pages40205865861均完成，完整线上媒体/海报SHA、VTT、原章节与来源链接核验通过；完整记录见[第二批](../../docs/reference-endcards/batch-2/README.md)。原正文基线及追加回执见revisions/reference-endcards。只上GitHub站点，无平台重发。

## v0.70.3 · 原始题名与原文摘录

参考资料卡改为实际原题、逐字原文短引和位置，原讲解/声音/代码卡保持；当前发布5706帧，完整SHA-256：`0ed555a69ba3413bcccad4cb31c8340d739e5a7a38535a5b0a06c6e0345fe68f`。[PR #338](https://github.com/linhongcun/video-studio/pull/338)、[Release](https://github.com/linhongcun/video-studio/releases/tag/v0.70.3)与[Release后Pages](https://github.com/linhongcun/video-studio/actions/runs/40210425589)已完成，41次canonical GET覆盖本片完整视频/海报SHA、VTT、原章节/日期/引用和更新日志通过。实际来源、媒体保真与播放器范围见[本批记录](../../docs/reference-endcards/original-titles/README.md)。仅GitHub站点，无平台重发；不表示用户已观看认可。
