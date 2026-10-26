# EP.18 官方资料核验

访问日期2026-10-24（北京时间）。逐页实际打开正文，技术背景选MySQL 8.4长期支持系列，示例版本写作8.4.0所属系列；不是声称该小版本为当日最新版。旧issue与旧稿只作需求背景，不当作事实出处。

| ID | 官方正文 | 已核验内容与边界 |
|---|---|---|
| R1 | [§19.2 Replication Implementation](https://dev.mysql.com/doc/refman/8.4/en/replication-implementation.html) | 源记录更改，副本请求日志并各自重放；动画路径表示更改流向，不冒称源无条件主动推送 |
| R2 | [§19.2.3 Replication Threads](https://dev.mysql.com/doc/refman/8.4/en/replication-threads.html) | 接收线程与应用线程是不同阶段；收到更改不等于数据已经可读到新值 |
| R3 | [§19.4.5 Using Replication for Scale-Out](https://dev.mysql.com/doc/refman/8.4/en/replication-solutions-scaleout.html) | 一种读多写少场景可让写入走源、读取按需求选源或副本；片中本次刚改后查询定向主库是教学方案选择，不是万能一致性保证 |
| R4 | [§19.4.10 Semisynchronous Replication](https://dev.mysql.com/doc/refman/8.4/en/replication-semisync.html) | 默认异步；主库提交不保证副本已经取得、应用，半同步确认也不等于在副本已执行完成 |
| R5 | [§15.7.7.35 SHOW REPLICA STATUS](https://dev.mysql.com/doc/refman/8.4/en/show-replica-status.html) | Seconds_Behind_Source是有条件的滞后指标，网络慢时0不代表已经追上源；故视频不展示假精确延迟秒数 |
| R6 | [§17.7.2.3 Consistent Nonlocking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html) | RR一致性读可沿用既有快照，RC每次快照不同；“直接读主库”必须结合新查询/事务、缓存和路由边界讨论 |

主线仅一种可能原因：用户7042昵称阿青改青禾、异步复制尚未应用，刷新恰读旧副本。不是对真实网站故障原因的诊断，不声称刷新旧值都由主从延迟造成。教学昵称与编号无真实用户关联。无性能实测、固定传播时间或必定最终追上的承诺。主库成功后可能从库已经更新，也可能还未更新；本例选择后一时间序列。

## 2026-10-26 片尾资料清单整理

本轮只整理已验收视频的title-author片尾，选四项原题：Replication Implementation、Replication Threads、Using Replication for Scale-Out、Semisynchronous Replication，分别对应更改复制、接收与应用、读写路由及默认异步的完成边界；四项同页5秒。监控指标与一致性快照的旧来源继续保留在原文及脚注，不扩展成本轮新调研。

官方实读日期保持2026-10-24，本轮未新GET或捏造官网正文SHA。基线`278f69a71151cada63e7068b4cfc0d5222501ac7`研究Git blob为`f12ee2821b958f5c78b4e46adb7c0908c916f69b`，完整SHA-256为`3013581e3f768c71cf683756539f3a75e1a329a740808a40c6bdc444a8217439`。[清单证据](../../docs/reference-endcards/batch-6/sources-db-replication.json)保存原题、原始行与逐论点旧记录。发布机构为Oracle / MySQL，未推断个人作者。原全文、frontmatter、锚点、旁白、分镜、冻结与媒体均不改。
