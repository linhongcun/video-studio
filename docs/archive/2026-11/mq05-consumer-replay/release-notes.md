第45期《消费幂等：已经处理过，为什么还会再来一遍？》内容修订，保留原链接、期号、首发身份与封面。

通过同一 E01@P0offset0，解释读取位置前移、外部数据库成功、Kafka恢复位点尚未提交时的故障窗口，以及重启后为何再次交付原记录。对照提前提交导致的漏处理，最后用同事务业务键说明如何避免重复生效；数据库实现细节留文章。

- 新版167.8秒，含5秒参考资料；四幅成片图支持准确回看。
- Kafka4.4.0/PG18.0三个真实分支、独立源稿/动态/正式媒体与图文检查、本地86动作/22严格PTS和实际图审通过；准确RGB参考复核保持原标准。
- GitHub与本站内容更新，不重发平台。

观看：https://linhongcun.github.io/video-studio/episodes/kafka-consumer-idempotency/
制作与验收：https://github.com/linhongcun/video-studio/tree/main/docs/archive/2026-11/mq05-consumer-replay
