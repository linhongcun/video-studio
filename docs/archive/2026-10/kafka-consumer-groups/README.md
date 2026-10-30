# Kafka MQ02 · 消费组

2026-10-30，制作 [#310](https://github.com/linhongcun/video-studio/issues/310)《多个消费者：分工处理，还是每人一份？》，身份为 **EP.42 / Kafka MQ02 / kafka-consumer-groups**。已完成制作、本地检查、主干合并、Release、Pages部署及线上完整媒体和实际播放器核验。

同一组 E01–E04 订单事件贯穿两个分区，对照误放同组时各收一半、不同业务各用独立消费组时各读全部，以及通知组增加实例后的组内分工。三个情景明确使用相同保留输入并从开头对照，不把扩实例画成自动重放；固定 Kafka 4.4.0 传统消费组及稳定分配，模型验证与真实集群实验分开记录。

成片10镜20句、4章，正文3445帧加150帧原题/机构资料页，共3595帧、119.8333秒、6,092,144字节；完整 SHA-256 为 `6476246b240a58f5c9904a6606aec5501b66fe00e945169f127f5187258d33af`。159项生产输入冻结，正式编码、三比例封面、文章配图与本地双视口播放器/原文交互已按实际范围检查。

- [成片与图文](https://linhongcun.github.io/video-studio/episodes/kafka-consumer-groups/)、[制作与发布记录](../../../../episodes-codex/kafka-consumer-groups/release.md)、[独立质检](../../../../episodes-codex/kafka-consumer-groups/qa-final-independent.md)。
- [PR #434](https://github.com/linhongcun/video-studio/pull/434) 合并 `c9a8a6e97f82b5bdef140f86e797eff8cc0748ee`；[Release v0.93.0](https://github.com/linhongcun/video-studio/releases/tag/v0.93.0)；[Release后Pages 40980598757](https://github.com/linhongcun/video-studio/actions/runs/40980598757) 已成功；首次push运行40980541655在checkout阻塞后取消，未记作媒体或构建失败。
- [正式编码检查](../../../../episodes-codex/kafka-consumer-groups/qa/encoded-independent/report.json)、[本地网站检查](../../../../episodes-codex/kafka-consumer-groups/qa/site-independent/report.json)；[线上HTTP核验](../../../../episodes-codex/kafka-consumer-groups/online-verification.json)13项普通canonical GET通过，完整媒体/海报/VTT及三幅图字节一致，4章20cue、系列/内容库/首页/旧learn入口与真实Release更新日志正确；[线上原生Chromium检查](../../../../episodes-codex/kafka-consumer-groups/qa/site-online-native/report.json)39项动作、18次严格PTS核验通过，实际查看5张线上图；844横屏资料题名/署名与控件分离，中心原生等待弧的实际状态保留，不称界面完全无等待标记。

本轮仅 GitHub 与站点，无外部平台新发。没有逐字ASR、全片人工语义听辨、真实Kafka集群、物理手机或学习效果测试，不将技术通过写成用户观看认可。系列已交付2/9，其余7题未开工、不自动启动，原14题维持取消；#310已在本次线上核验后按completed关闭，关闭与总览收尾已完成，见[实际发布回执](../../../../episodes-codex/kafka-consumer-groups/publication.json)，总览状态以 [#308](https://github.com/linhongcun/video-studio/issues/308) 为准。
