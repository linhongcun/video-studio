# EP.20 权威资料核验

访问日期：R1—R5为2026-10-24，R6—R9为本轮2026-10-25（北京时间）。已实际打开下列官方正文与原始代码，不以issue、旧稿或搜索摘要代替事实来源。

| ID | 来源 | 核验结论与范围 |
|---|---|---|
| R1 | [MySQL 8.4 §5.6.9 Using AUTO_INCREMENT](https://dev.mysql.com/doc/refman/8.4/en/example-auto-increment.html) | 官方示例用AUTO_INCREMENT配合PRIMARY KEY，为本表新记录生成编号；不能据此推断独立表之间全局不重。 |
| R2 | [Apache ShardingSphere 当前Key Generate Algorithm](https://shardingsphere.apache.org/document/current/en/user-manual/common-config/builtin-algorithm/keygen/) | 分片后不同实际表彼此不感知，本地自增会有重复风险；SNOWFLAKE要求唯一worker-id，有时间差处理参数。 |
| R3 | [Twitter原始IdWorker.scala](https://github.com/twitter-archive/snowflake/blob/snowflake-2010/src/main/scala/com/twitter/service/snowflake/IdWorker.scala) | 2010—2012原实现，仅参考历史原理：机房和worker各5位、sequence12位，时间位在上方；同毫秒序号增加，用尽等下一毫秒；回拨拒绝生成。不是现行产品配置默认值。 |
| R4 | [Apache ShardingSphere现行SnowflakeKeyGenerateAlgorithm.java](https://github.com/apache/shardingsphere/blob/master/infra/algorithm/type/key-generator/type/snowflake/src/main/java/org/apache/shardingsphere/infra/algorithm/keygen/snowflake/SnowflakeKeyGenerateAlgorithm.java) | 核验当前实现的机器/序号字段、时间处理与序号耗尽等待；原理并非随意拼十进制文本。master内容会变，本文按本次访问内容说明。 |
| R5 | [MDN Number.MAX_SAFE_INTEGER](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER)与[BigInt](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/BigInt) | Number安全整数范围有限；大整数用BigInt计算、toString显示，不能先损失精度再转BigInt，JSON应按约定用字符串等方式承载。 |
| R6 | [RFC 9562（2024）§5.4](https://www.rfc-editor.org/rfc/rfc9562.html#section-5.4)、[§6.4](https://www.rfc-editor.org/rfc/rfc9562.html#section-6.4)、[§6.8—6.9](https://www.rfc-editor.org/rfc/rfc9562.html#section-6.8) | 2026-10-25实际读取正文：§5.4明确UUIDv4由真随机或伪随机数据生成，版本与变体之外有122个随机位；§6.4支持多节点独立生成，碰撞风险随生成规模变化；§6.8不作无共享知识条件下的绝对全局唯一保证；§6.9要求可靠的密码学随机源并注意进程状态变化。片中仅称“UUID的随机版本”，不把所有版本都说成随机，也不报没有实验依据的概率或性能数字。 |
| R7 | [Redis INCR](https://redis.io/docs/latest/commands/incr/) | 2026-10-25实际读取命令说明及“Pattern: counter”：对同一key的整数值原子加一，key不存在时从0初始化。以多个节点共享同一计数器解释集中发号；不推断多个独立计数器自动互斥，也不承诺没有跳号或故障后永不重复。 |
| R8 | [Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) | 2026-10-25实际读取持久化方式和RDB/AOF优缺点：RDB保存时间点快照，AOF记录写操作；不同策略有不同的数据丢失窗口。用于说明恢复旧状态可能导致计数回退；不将“开启持久化”写成零丢失保证，不在本片展开配置教学。 |
| R9 | [Redis replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/) | 2026-10-25实际读取复制及故障转移正文：默认异步复制，故障转移仍可能丢失已确认写入；WAIT降低风险但不会把系统变成强一致的CP系统。用于限定Redis集中发号的恢复边界，不能只凭INCR原子性推出跨故障唯一。 |

## 本轮方案范围补充

用户指出只讲雪花算法容易让观众把分布式ID等同于雪花。本轮在`16-options`与`17-redis`中先交代多种实现，概述随机UUID本地生成、Redis同一计数器集中取号及其条件，然后回到雪花主线。称“经典方案之一”是选取代表方案的编辑表述，不作为最流行、性能最佳或适用于所有场景的排名结论；不因补总览而在短片中展开全部方案。

## 教学数字

本地自增示例41→42为虚构订单数据。字段示例使用相对毫秒4000000000、生成器编号7或9、序号0或1；按 `(相对毫秒 << 22) | (生成器编号 << 12) | 序号` 的整数规则组合。示意生成器编号概括原版机房号与机器号，总共10位，并非某个实际部署的身份。数值均在对应字段范围内；实际实现的纪元、分配与恢复策略必须统一。

片中不讲各段位数、不提供吞吐实测或无条件安全承诺；重启、身份复用、时钟回拨、序号耗尽都需要实现正确处理。没有宣称所有节点生成顺序等于业务发生顺序，也没有将ID当作安全令牌。
