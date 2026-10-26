# EP.20 权威资料核验

访问日期：R1—R5为2026-10-24，R6—R13为本轮2026-10-25（北京时间）。已实际打开下列官方正文与原始代码，不以issue、旧稿或搜索摘要代替事实来源。

| ID | 来源 | 核验结论与范围 |
|---|---|---|
| R1 | [MySQL 8.4 §5.6.9 Using AUTO_INCREMENT](https://dev.mysql.com/doc/refman/8.4/en/example-auto-increment.html) | 官方示例用AUTO_INCREMENT配合PRIMARY KEY，为本表新记录生成编号；不能据此推断独立表之间全局不重。 |
| R2 | [Apache ShardingSphere 当前Key Generate Algorithm](https://shardingsphere.apache.org/document/current/en/user-manual/common-config/builtin-algorithm/keygen/) | 分片后不同实际表彼此不感知，本地自增会有重复风险；SNOWFLAKE要求唯一worker-id，有时间差处理参数。 |
| R3 | [Twitter原始IdWorker.scala](https://github.com/twitter-archive/snowflake/blob/snowflake-2010/src/main/scala/com/twitter/service/snowflake/IdWorker.scala) | 2010—2012原实现，仅参考历史原理：机房和worker各5位、sequence12位，时间位在上方；同毫秒序号增加，用尽等下一毫秒；回拨拒绝生成。不是现行产品配置默认值。 |
| R4 | [Apache ShardingSphere现行SnowflakeKeyGenerateAlgorithm.java](https://github.com/apache/shardingsphere/blob/master/infra/algorithm/type/key-generator/type/snowflake/src/main/java/org/apache/shardingsphere/infra/algorithm/keygen/snowflake/SnowflakeKeyGenerateAlgorithm.java) | 核验当前实现的机器/序号字段、时间处理与序号耗尽等待；原理并非随意拼十进制文本。master内容会变，本文按本次访问内容说明。 |
| R5 | [MDN Number.MAX_SAFE_INTEGER](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER)与[BigInt](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/BigInt) | Number安全整数范围有限；大整数用BigInt计算、toString显示，不能先损失精度再转BigInt，JSON应按约定用字符串等方式承载。 |
| R6 | [RFC 9562（2024）§2.1](https://www.rfc-editor.org/rfc/rfc9562.html#section-2.1)、[§5.4 UUIDv4](https://www.rfc-editor.org/rfc/rfc9562.html#section-5.4)、[§5.7 UUIDv7](https://www.rfc-editor.org/rfc/rfc9562.html#section-5.7)、[§6.4](https://www.rfc-editor.org/rfc/rfc9562.html#section-6.4)、[§6.8—6.11](https://www.rfc-editor.org/rfc/rfc9562.html#section-6.8) | 2026-10-25实际读取正文：§5.4明确UUIDv4随机生成；§2.1说明非时间有序UUIDv4的数据库索引局部性较差，连续新值会落到不同索引位置；§5.7与§6.11说明UUIDv7的时间有序字段和排序/局部性目的。§6.4、6.8—6.9保留独立生成、碰撞风险与可靠随机源边界。不把所有UUID都说成随机、不递增或严格全局有序，不报没有测量依据的性能倍数。 |
| R7 | [Redis INCR](https://redis.io/docs/latest/commands/incr/) | 2026-10-25实际读取命令说明及“Pattern: counter”：对同一key的整数值原子加一，key不存在时从0初始化。以多个节点共享同一计数器解释集中发号；不推断多个独立计数器自动互斥，也不承诺没有跳号或故障后永不重复。 |
| R8 | [Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) | 2026-10-25实际读取持久化方式和RDB/AOF优缺点：RDB保存时间点快照，AOF记录写操作；不同策略有不同的数据丢失窗口。用于说明恢复旧状态可能导致计数回退；不将“开启持久化”写成零丢失保证，不在本片展开配置教学。 |
| R9 | [Redis replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/) | 2026-10-25实际读取复制及故障转移正文：默认异步复制，故障转移仍可能丢失已确认写入；WAIT降低风险但不会把系统变成强一致的CP系统。用于限定Redis集中发号的恢复边界，不能只凭INCR原子性推出跨故障唯一。 |
| R10 | [MySQL 8.4 §17.6.2.1 Clustered and Secondary Indexes](https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html) | 2026-10-25实际读取正文371—382行：InnoDB主键通常就是存放行数据的聚簇索引；二级索引记录也携带主键。用于限定随机UUIDv4直接作为InnoDB主键的讨论，不能泛化为所有MySQL存储引擎或索引失效。 |
| R11 | [MySQL 8.4 §17.6.2.2 The Physical Structure of an InnoDB Index](https://dev.mysql.com/doc/refman/8.4/en/innodb-physical-structure.html)、[Glossary：fill factor](https://dev.mysql.com/doc/refman/8.4/en/glossary.html#glos_fill_factor) | 2026-10-25实际读取物理结构370—374行与词汇表998—1000行：除空间索引外采用B-tree；顺序与随机插入的索引页利用情况不同，fill factor定义涉及页分裂前的空间占用及维护开销。结合R6随机落点说明页维护代价；动画页空间不足时可能分裂为机制教学示意，不是每条插入必然分裂或真实磁盘布局实测。 |
| R12 | [MySQL 8.4 §10.5.5 Bulk Data Loading for InnoDB Tables](https://dev.mysql.com/doc/refman/8.4/en/optimizing-innodb-bulk-data-loading.html) | 2026-10-25实际读取445行：批量按PRIMARY KEY顺序插入更快，尤其在表不能全部容纳于缓冲池时。用于支持主键顺序与写入局部性的关系，不把批量加载建议扩成任何负载下固定性能结论。 |
| R13 | [Redis Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/) | 2026-10-25实际读取102—103、139、852—862行：副本可在故障后被提升，异步复制下已确认写入仍可能丢失，旧主数据会被新主状态覆盖。用于说明落后副本切换后计数回退与重复发号。可靠预留号段、停号/隔离旧主和越过安全上界属于本文根据风险推导的设计条件，不声称Sentinel自动跳号或固定加N即可安全。 |

## 本轮方案范围与叙事修订

用户指出，上来先说“雪花只是一种”很突兀，要求依次讲UUID、Redis再详细讲雪花，并补每种方法的取舍。本轮取消该开场，先说明随机UUIDv4的本地生成和不递增对InnoDB主键插入位置的影响，再说明Redis共同计数器、异步复制与切换回退，最后自然进入雪花三字段。

Redis演示沿用1001/1002：旧主已返回两个号码、副本只保留1000，提升后若直接INCR就会重发1001。另一种事先可靠预留号段的治理方案，假设已在旧主使用1001—1200前可靠、原子地预留上界1200；先停号、隔离旧主，放弃整个旧号段后从1201继续。可靠记录必须不会随本次故障回退，恢复和再次预留必须互斥；不能在事故后凭空选1200，不能只看已落库记录而漏掉已发未落库号码，无法确认边界则暂停核对。这是安全条件的教学推导，不是Redis默认功能或一组已被实测验证的生产配置。

随机UUIDv4的非递增性质不延伸为所有UUID；UUIDv7在文章给出时间有序边界。各方案收益与成本在逐项讲述后的回顾表并列，不把任何方案写成普遍优于其他方案。

## 教学数字

本地自增示例41→42为虚构订单数据。字段示例使用相对毫秒4000000000、生成器编号7或9、序号0或1；按 `(相对毫秒 << 22) | (生成器编号 << 12) | 序号` 的整数规则组合。示意生成器编号概括原版机房号与机器号，总共10位，并非某个实际部署的身份。数值均在对应字段范围内；实际实现的纪元、分配与恢复策略必须统一。

UUID示例和索引页分布为教学示意；Redis计数器、1001/1002及预留上界1200、下一号1201均为教学数字，不代表默认配置、自动故障切换行为或真实事故。

片中不讲各段位数、不提供吞吐实测或无条件安全承诺；重启、身份复用、时钟回拨、序号耗尽都需要实现正确处理。没有宣称所有节点生成顺序等于业务发生顺序，也没有将ID当作安全令牌。
