# Kafka MQ03 · 日志重放

2026-10-30，制作 [#311](https://github.com/linhongcun/video-studio/issues/311)《Kafka日志重放：消息读过了，为什么还能重读？》，身份为 **EP.43 / Kafka MQ03 / kafka-log-replay**。已完成制作、本地检查、主干合并、Release、Pages及线上完整媒体和实际播放器核验。

沿保留的同一条分区日志，区分当前消费者的读取位置与已提交的下一条恢复位置，再演示停用通知整组后仅回退P0、预览与执行、重启重处理及旧封闭段清理边界。固定Kafka 4.4.0传统消费组与两分区；客户端内存读取位置不画成Broker持久组游标，P1与积分组保持。模型和教学CLI示意不冒充真实集群/adminCLI/保留调度或业务副作用实验。

成片11镜22句、4章，正文3943帧加150帧原题/机构资料页，共4093帧、136.4333秒、7,023,582字节；完整SHA-256为 `0baa057bfa08635e97ce6e19b75fcd198ece292072bc401c23ea971218baa637`。170项输入冻结，137项有限模型、22句声音来源与信号、95动态采样/3段连续片/56张顺序帧、55张正式编码帧及三比例封面按实际范围通过；四幅配图、四处原文、22cue、4章与本地46项动作/20次严格PTS核验通过。

- [成片与图文](https://linhongcun.github.io/video-studio/episodes/kafka-log-replay/)、[制作与发布记录](../../../../episodes-codex/kafka-log-replay/release.md)、[独立质检](../../../../episodes-codex/kafka-log-replay/qa-final-independent.md)。
- [PR #438](https://github.com/linhongcun/video-studio/pull/438)合并 `e21e14570db934af7ede110e95b627d7b4190cdb`；[Release v0.95.0](https://github.com/linhongcun/video-studio/releases/tag/v0.95.0)；[Release后Pages 40991181077](https://github.com/linhongcun/video-studio/actions/runs/40991181077)已成功。首push同SHA重复部署40991042825已主动取消，未诊断为失败或阻塞，本轮未修改工作流。
- [正式编码检查](../../../../episodes-codex/kafka-log-replay/qa/encoded-independent.json)、[本地网站检查](../../../../episodes-codex/kafka-log-replay/qa/site-independent/report.json)。制作中保留上游72b841c1的“其他”分类与4f631ca7的README重写，记录见本期发布页；[线上HTTP核验](../../../../episodes-codex/kafka-log-replay/online-verification.json)14项普通canonical GET通过：完整媒体/海报/VTT及四图SHA一致，4章22cue、三课MQ目录、入口和真实Release更新日志正确；[线上原生Chromium检查](../../../../episodes-codex/kafka-log-replay/qa/site-online-native/report.json)46项动作、20次严格PTS核验通过，无TLS绕过或HTTP回填；实际查看四张线上原图，桌面资料页、手机原文浮层及844×390横屏资料题名/署名清楚，原生暂停控件保留，所看图无等待弧。

本轮仅GitHub与站点，无外部平台新发。没有逐字ASR、全片人工语义听辨、物理手机或学习效果测试，不将技术通过写成用户观看认可。系列当前3/9已交付；#311已在本次线上核验后按completed关闭并同步[#308](https://github.com/linhongcun/video-studio/issues/308)；其余6题未开工、不自动启动，原14题维持取消。
