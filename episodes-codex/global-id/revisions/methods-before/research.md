# EP.20 权威资料核验

访问日期：2026-10-24（北京时间）。已实际打开下列官方正文与原始代码，不以issue、旧稿或搜索摘要代替事实来源。

| ID | 来源 | 核验结论与范围 |
|---|---|---|
| R1 | [MySQL 8.4 §5.6.9 Using AUTO_INCREMENT](https://dev.mysql.com/doc/refman/8.4/en/example-auto-increment.html) | 官方示例用AUTO_INCREMENT配合PRIMARY KEY，为本表新记录生成编号；不能据此推断独立表之间全局不重。 |
| R2 | [Apache ShardingSphere 当前Key Generate Algorithm](https://shardingsphere.apache.org/document/current/en/user-manual/common-config/builtin-algorithm/keygen/) | 分片后不同实际表彼此不感知，本地自增会有重复风险；SNOWFLAKE要求唯一worker-id，有时间差处理参数。 |
| R3 | [Twitter原始IdWorker.scala](https://github.com/twitter-archive/snowflake/blob/snowflake-2010/src/main/scala/com/twitter/service/snowflake/IdWorker.scala) | 2010—2012原实现，仅参考历史原理：机房和worker各5位、sequence12位，时间位在上方；同毫秒序号增加，用尽等下一毫秒；回拨拒绝生成。不是现行产品配置默认值。 |
| R4 | [Apache ShardingSphere现行SnowflakeKeyGenerateAlgorithm.java](https://github.com/apache/shardingsphere/blob/master/infra/algorithm/type/key-generator/type/snowflake/src/main/java/org/apache/shardingsphere/infra/algorithm/keygen/snowflake/SnowflakeKeyGenerateAlgorithm.java) | 核验当前实现的机器/序号字段、时间处理与序号耗尽等待；原理并非随意拼十进制文本。master内容会变，本文按本次访问内容说明。 |
| R5 | [MDN Number.MAX_SAFE_INTEGER](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER)与[BigInt](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/BigInt) | Number安全整数范围有限；大整数用BigInt计算、toString显示，不能先损失精度再转BigInt，JSON应按约定用字符串等方式承载。 |

## 教学数字

本地自增示例41→42为虚构订单数据。字段示例使用相对毫秒4000000000、生成器编号7或9、序号0或1；按 `(相对毫秒 << 22) | (生成器编号 << 12) | 序号` 的整数规则组合。示意生成器编号概括原版机房号与机器号，总共10位，并非某个实际部署的身份。数值均在对应字段范围内；实际实现的纪元、分配与恢复策略必须统一。

片中不讲各段位数、不提供吞吐实测或无条件安全承诺；重启、身份复用、时钟回拨、序号耗尽都需要实现正确处理。没有宣称所有节点生成顺序等于业务发生顺序，也没有将ID当作安全令牌。
