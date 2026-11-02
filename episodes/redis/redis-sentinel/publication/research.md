# Sentinel：故障确认、执行授权与副本选择

2026-11-02（北京时间）实际重新读取官方文档与Redis8.4.0固定源码。本轮公开GET原字节保存在sources/，每次状态、日期与SHA见sources/fetch-log.json；失败响应也原样保留，不能作为成功阅读证据。开工基线01cd181caf24d4a8ce846c0eb8faeeab8f0054e2。

## R1：High availability with Redis Sentinel

- 机构：Redis。未见明确个人署名，不从仓库提交者推断作者。
- 原始题名：High availability with Redis Sentinel；证据为sources/sentinel-fixed.md前置title字段第12行。
- 官方页面：https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/ 。本轮通过官方redis/docs仓库读取固定正文，未把页面可访问性等同于真实浏览器访问。
- 固定正文：https://github.com/redis/docs/blob/c0f4f836b44de0041ddd63e88fdd843e5f4f0dfb/content/operate/oss_and_stack/management/sentinel.md 。固定提交由GitHub API的sources/docs-main.json解析，GET日期2026-11-02；文档未标发布日期。
- 署名/许可：官方redis/docs仓库及sources/docs-LICENSE明确Redis Ltd.。保存原文作为内部核验输入；文章只引用支持核心论点的短句，保留来源与原语言，不声称Redis官方背书。该文档许可原文保留。
- 支持主张：故障quorum与多数授权不同；五个Sentinel/quorum2仍至少三票；SDOWN/ODOWN条件；筛选与priority0；异步复制的数据损失边界。
- 实读位置：第126–141、930–979、1021–1067、1074–1108、1189行上下文。
- 连续短引（Quorum节，第1090行）：“The difference may seem subtle but is actually quite simple to understand and use.  For example if you have 5 Sentinel instances, and the quorum is set to 2, a failover will be triggered as soon as 2 Sentinels believe that the master is not reachable, however one of the two Sentinels will be able to failover only if it gets authorization at least from 3 Sentinels.”
- 连续短引（Replica selection and priority节，第1061–1062行）：“A Redis instance can be configured with a special `replica-priority` of zero\nin order to be **never selected** by Sentinels as the new master.”
- 片尾入选：R1。片尾仅显示原题和机构。

## R2：sentinel.c

- 机构：Redis，未指定单个作者。源码完整版权头与三许可原文分别保留sources/sentinel-fixed.c及sources/redis-LICENSE.txt。
- 原始题名采用实际文件名sentinel.c，不自拟论文/文档标题；文件路径与公开固定URL为题名依据，源码第一段声明为Redis Sentinel implementation。
- 版本：Redis8.4.0，tag固定commit60ba86f3c8b4e1ec96451171753a0a38e5c45a0c；tag API回应保留sources/redis-tag.json。实际原字节GET：https://raw.githubusercontent.com/redis/redis/60ba86f3c8b4e1ec96451171753a0a38e5c45a0c/src/sentinel.c 。访问日期2026-11-02。
- 实读执行路径：sentinelVoteLeader第4738–4762行只在更新轮次时记录投票；sentinelGetLeader第4794–4866行按已知sentinels字典+自己计数，并同时要求绝对多数及master->quorum；sentinelFailoverWaitStart第5097–5128行未当选且非强制路径则不继续。
- 副本选择：sentinelSelectSlave第5051–5094行先排除SDOWN/ODOWN、disconnected、近期不可用、priority0、过期INFO和过长断连；compareSlavesForPromotion第5023–5049行按priority小者、offset大者、runid字典序小者排序。
- 晋升及确认：sentinelFailoverSendSlaveOfNoOne第5148–5175行发SLAVEOF NO ONE但不依赖命令reply，实际通过INFO观测角色；WaitPromotion及INFO处理负责继续状态转移。脚本用“晋升命令/角色报告”而非让观众背旧命令名。
- 连续短引（sentinelGetLeader）：“voters = dictSize(master->sentinels)+1; /* All the other sentinels and me.*/”
- 核验范围：已实际阅读上述执行段及文档上下文；有限教学模型与运行实测分别留证，不把模型断言称为产品容错证明。片尾入选R2。

## 本片边界

正常自动故障转移、五个已互相发现的Sentinel、quorum2、epoch示例7；强制SENTINEL FAILOVER与Redis Cluster不套用本文授权结论。演示省略发现、TILT、认证及配置持久化细节；文章列出必要筛选和排序，但不堆进视频。客户端必须支持Sentinel发现或由应用另行重连，Sentinel不转发业务流量。

所有进度900/800、轮次7和写入w42是原创教学数字。异步复制窗口图只解释可能性，不把它称作已执行的数据丢失实验。
