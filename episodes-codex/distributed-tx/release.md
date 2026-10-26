# EP.21 分章修订版发布记录

2026-10-24，用户观看v0.45.4后要求主流方案分章、有条序，并各自讲清边界。本次v0.45.5按GitHub持续授权制作、检查、合并与部署；没有记为用户已观看认可。只上站点，不重发平台。

视频完整SHA256：`ef17294435f00901ffcdc7c3711501102ffea9db8e7c0160b5001cbb6b19eb91`，20,427,234 bytes，11675帧，389.184秒，1080p/30fps，−16.0LUFS、TP−3.7dBTP。直接复制通过检查的冻结媒体到episodes/distributed-tx/，发布时不再生成配音或画面。

新版覆盖2PC/XA、Seata AT、TCC、Saga、可靠消息，并分别演示Outbox与RocketMQ事务消息。更新七章文章、公开研究、脚本、三尺寸封面、76句字幕与真实章节起点，保留原发布日期、首发版本和平台链接。194项冻结输入、完整媒体解码、185个实际编码/预演状态采样对比与首尾、关键帧逐图复核、声学时序及站点构建核验均有记录。

详见qa-motion.md、qa-final.md、qa-media-samples.json和render-result.json。没有可用官方ASR权重，不声称逐字ASR或全片人工听辨；图像一致性不代替动画教学检查。关键资料均为实际阅读的官方/原作者公开正文。

发布闭环：本地构建与76句VTT/七章/海报/完整SHA核验 → PR合并 → 附注tag与Release → Release后Pages部署 → 实际线上文件及更新日志核验 → #73以completed关闭。#73已因本次反馈重新打开，未执行的平台事项不勾选完成。在线证据以对应Release、Actions运行及issue状态为准。

---

## 历史：v0.45.4可靠消息单线版

# EP.21 站点发布记录

2026-10-24，按用户已授权的旧版重制任务及GitHub持续发布流程，将本期纳入v0.45.4的EP.18–21批次。只上站点，不重发平台。本期按制作和独立检查结果发布，没有将其记为用户已经观看认可。

视频SHA-256：`4f01d09aceeab441d82b162caf90337b99faff4388b015978d29469a506c4356`，规格1920×1080、30fps、3791帧、126.378秒。`episodes/distributed-tx/video.mp4` 使用同一份冻结成片，不在发布阶段重新生成音频或画面。

站点同步文章、研究、脚本、封面、海报、冻结分镜 `storyboard.2a871098.json` 与28句字幕，设置实际 `finalVideoFrames`，移除旧时序与旧版标记。保留原发布日期、首发版本和平台链接。当前入口见 [README.md](README.md)。

制作检查证据见 [qa-motion.md](qa-motion.md)、[qa-final.md](qa-final.md)、[source-sha256.json](source-sha256.json) 与 [render-result.json](render-result.json)。检查包括真实编码抽帧、全部字幕/冻结输入核对及完整媒体解码；没有可用官方ASR权重，不声称已做逐字ASR或全片人工听辨。

发布顺序：本地站点构建与逐项核验 → PR合并 → 附注tag及Release → Release后再次部署Pages → 核验线上完整视频SHA、海报、全部VTT、章节、时长及更新日志 → 将对应 [#73](https://github.com/linhongcun/video-studio/issues/73) 以 `completed` 关闭。未执行的平台新发事项不勾选完成。

<!-- batch-12-publication-archive:start -->
## 存量片尾参考资料第十二批 · v0.77.2

[PR #366](https://github.com/linhongcun/video-studio/pull/366)已合并，发布[v0.77.2](https://github.com/linhongcun/video-studio/releases/tag/v0.77.2)，[Pages 40354381553](https://github.com/linhongcun/video-studio/actions/runs/40354381553)成功；合并提交945791d8f8843f076b6ce2ef73ffe7cb2a0e26ea。2026-10-27T00:04:23+08:00完成21项规范URL完整GET和5次公开GitHub身份读取，五片完整MP4、海报、全文字幕、资料页面、原章节/首发日期、更新日志与tag/Release/Pages身份一致。固定原47期全部补齐，当前48期发布视频均有参考资料附录；两项口径分别记数。

本期8项、2页，原body11675帧→最终11975帧，完整SHA256 e7c5a5941084ed9299f0483cba1b11f2b6a0118c4061d23c7d89a9059915a88c。原制作MP4与固定Git原片完整SHA一致。

各项实际技术阅读日期：R1 XA Transactions：2026-10-24；R2 Seata AT mode：2026-10-24；R3 Seata TCC Mode：2026-10-24；R4 SEATA Saga Pattern：2026-10-24；R5 Compensating Transaction pattern：2026-10-24；R6 Transactional outbox pattern：2026-10-24；R7 Transaction Message：2026-10-24；R8 Handling duplicate messages using the Idempotent consumer pattern：2026-10-24。逐项保留24/25日实际技术阅读和原有题名/署名记录；本轮新增或复用metadata的真实日期和范围按references.json及各来源证据单列，不统一伪造为新技术重读。未读论文/书目不补为已读，不从Git或维护账号猜个人作者。

本批18项6页，每页5秒；当前真实冻结输入1020项由最终production-entry-check、独立QA与当前清单一致确认，原927项全部实核且0缺件。适配器/策略的完整Java卡、所有原正文/音轨和历史收尾保留，Skills原制作MP4缺失事实保留，未重建正文。历史事务合集继续archived，replacedBy与学习导航保持。字幕派生变化逐项沿真实QA记录，不改源分镜或words。

完整证据见[第十二批归档](../../docs/archive/2026-10/reference-endcards-batch-12/README.md)。旧首发身份与归档/替代路径保持；未执行议题或平台操作。
<!-- batch-12-publication-archive:end -->
