# Kafka规划issue更新草稿

9份JSON：#308总览、#310–316、#323，每份仅number/title/body，未创建#309草稿。原始issue JSON在上级目录保持原字节。所有工作只在work，未联网写入GitHub。

- #308重写为统一Kafka的9题总览；明确旧MQ01是此前RabbitMQ交付、本轮Kafka改造进行中，未来8题未开工。稳定MQ01–08/MQ15和14取消条目保留。
- #310、312、313、316分别重写订阅分工、发送确认、消费幂等、应用重试/死信，移除RabbitMQ Exchange/quorum/ACK删除/DLX的适用模型。
- #311仅改为“Kafka日志重放”题名并补一段与MQ02的范围划分，旧技术和验收正文保留。
- #314、315、323保留原题和主体，只各补一段范围或计数边界，不整篇重写。

每份草稿保留独立问题、机制/示例、边界、专项验收和资料。Kafka官方固定commit来自kafka_research已核验集合1156b2752aaa28eafc0b4c4d387e63356793268d；原现有Kafka canonical链接继续保留，不冒称本任务重新GET过这些网页。PostgreSQL与Chris Richardson的幂等来源保留。MQ04固定生产确认条件、MQ15解释副本条件，避免重复；MQ08显式写出死信发送与位点提交非天然原子、重试计数恢复须定稿。

root应用前可对照draft-manifest.json中的原title/body SHA再读一次当前issue，若上游已改则先合并差异，避免覆盖其他修改。草稿是待审查输入，不代表已应用、未来8期已开工或媒体已完成。
