# global-id 片尾参考资料

以下列出实际视频主线采用的8项核心资料。技术正文和代码的既有实读日期分别为2026-10-24、2026-10-25（北京时间）；本轮整理保留原日期。RFC 9562 的完整题名、明确作者及 Sentinel 的完整题名于2026-10-26另补官方仓库证据；该补证不等于重新核验技术正文。原有参考资料与脚注全部保留。

视频采用`title-author`，只显示完整原题与明确作者或机构；8项分2页、每页最多4项、5秒。版本、日期、链接、支持论点和边界仅供文章与内部核验，不上视频。

**[R1] Universally Unique IDentifiers (UUIDs)**

K. Davis, B. Peabody, P. Leach · RFC 9562 · May 2024：[官方资料](https://www.rfc-editor.org/rfc/rfc9562.html)；[既有实读记录（2026-10-25）](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/global-id/research.md#L12)。 [完整题名与署名补证（2026-10-26，官方书目）](https://github.com/ietf-tools/relaton-data-rfcs/blob/04b9eaa000f02f4a35d08c8e17ee3b3d00faf523/data/RFC9562.yaml)。

定位：§2.1；§5.4；§5.7；§6.4、§6.8—6.11

支持范围：随机UUIDv4支持节点本地生成，但依赖可靠随机源，碰撞风险低不等于绝对不碰撞。；UUIDv4缺少时间排序造成数据库索引局部性问题；UUIDv7时间字段和排序目的不能扩为严格的跨机器业务全序。

边界：讨论随机、不递增限于UUIDv4，不扩展到所有UUID。；不提供统一性能倍数或跨节点严格业务先后承诺。

**[R2] Clustered and Secondary Indexes**

Oracle / MySQL · MySQL 8.4 Reference Manual：[官方资料](https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html)；[既有实读记录（2026-10-25）](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/global-id/research.md#L16)。

定位：§17.6.2.1 · 既有实读正文371—382行

支持范围：InnoDB主键通常就是存放行数据的聚簇索引，二级索引也携带主键。；随机UUIDv4直接作主键的页局部性讨论限定于本片InnoDB语境。

边界：不泛化为所有MySQL存储引擎，不称随机主键导致索引失效。

**[R3] The Physical Structure of an InnoDB Index**

Oracle / MySQL · MySQL 8.4 Reference Manual：[官方资料](https://dev.mysql.com/doc/refman/8.4/en/innodb-physical-structure.html)；[既有实读记录（2026-10-25）](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/global-id/research.md#L17)。

定位：§17.6.2.2 · 既有实读正文370—374行；原记录另列Glossary fill factor

支持范围：除空间索引外，InnoDB索引采用B-tree；顺序和随机插入的索引页利用情况不同。；结合UUIDv4非顺序落点和原有fill-factor补充来源，说明空间不足时可能页分裂与额外维护。

边界：动画为机制教学示意，不是磁盘布局实测，不说每次插入都页分裂。；原文章的Glossary、Bulk Data Loading等独立脚注仍保留，未冒充本条标题。

**[R4] INCR**

Redis · Redis command documentation · 实读2026-10-25：[官方资料](https://redis.io/docs/latest/commands/incr/)；[既有实读记录（2026-10-25）](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/global-id/research.md#L13)。

定位：命令说明；Pattern: counter

支持范围：同一key整数值原子加一，key不存在时从0初始化。；多节点共享同一计数器可集中取号；原子递增的运行区间和异步复制故障后的状态保留是不同条件。

边界：不承诺独立计数器自动互斥、绝不跳号或故障后永不重复。；计数器不得被不当重置、过期或与其他业务复用。

**[R5] Redis replication**

Redis · Redis replication documentation · 实读2026-10-25：[官方资料](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)；[既有实读记录（2026-10-25）](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/global-id/research.md#L15)。

定位：异步复制；故障转移丢写；WAIT一致性边界

支持范围：默认异步复制下故障转移可能丢失已经确认的写入，旧主已返回计数可能尚未到副本。；WAIT可降低部分风险，但不能据此把Redis变为强一致CP系统或推出INCR跨故障唯一。

边界：可靠预留号段及切换跳号是本文根据风险推导的设计条件，不是Redis复制自动提供的功能或保证。

**[R6] High availability with Redis Sentinel**

Redis · Redis Sentinel documentation · 实读2026-10-25：[官方资料](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/)；[既有实读记录（2026-10-25）](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/global-id/research.md#L19)。 [完整题名补证（2026-10-26，官方仓库）](https://github.com/redis/docs/blob/d1b865f6dd93274757e28dad7fb02d4ccd7d39d4/content/operate/oss_and_stack/management/sentinel.md)。

定位：既有实读正文102—103、139、852—862行；本轮仅补官方源title行12

支持范围：副本可在故障后提升为主，默认异步复制仍可丢失已确认的写入，旧主可被新主状态覆盖。；落后副本接管共同计数器后，计数状态可能回退而重复发号。

边界：1001—1200号段必须在使用前由独立可靠记录原子预留；隔离旧主、恢复与重新预留互斥，无法确认边界就停号。；这些号段安全条件是教学推导，不声称Sentinel自动跳号、固定加N或只看落库ID就能安全。

**[R7] IdWorker.scala**

Twitter · snowflake-2010 · 2010—2012历史原始实现，仅参考：[官方资料](https://github.com/twitter-archive/snowflake/blob/snowflake-2010/src/main/scala/com/twitter/service/snowflake/IdWorker.scala)；[既有实读记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/global-id/research.md#L9)。 仅参考：2010—2012历史原始实现，不作为现行默认配置指南。

定位：源码中的datacenterId、workerId、sequence、nextId、tilNextMillis

支持范围：历史原实现将时间、机房/worker身份、同毫秒序号放在不同位字段。；同毫秒序号用尽会等待下一毫秒，时钟回拨有拒绝生成分支；身份冲突会破坏不重复前提。

边界：2010—2012历史原始实现仅参考，不作为现行产品默认值或当前部署指南。；片中的10位生成器身份概括历史机房与worker组合，不把两个进程共用身份当作不同生成器。

**[R8] SnowflakeKeyGenerateAlgorithm.java**

Apache ShardingSphere · Apache ShardingSphere master · 按2026-10-24实读内容：[官方资料](https://github.com/apache/shardingsphere/blob/master/infra/algorithm/type/key-generator/type/snowflake/src/main/java/org/apache/shardingsphere/infra/algorithm/keygen/snowflake/SnowflakeKeyGenerateAlgorithm.java)；[既有实读记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/global-id/research.md#L10)。

定位：当前实现的worker/sequence字段、时间处理、序号耗尽等待

支持范围：现行ShardingSphere实现用于对照时间、worker及序号的整数位组合，而非拼接十进制文本。；机器身份、时钟处理与序号状态需按所用实现正确维护，不能只凭“用了雪花”宣称无条件不重复。

边界：原始访问链接为可变master，本次只复用2026-10-24所记录的实际读取，不伪造该日未保存的上游commit或代码全文SHA。；当前配置说明Key Generate Algorithm仍保留旧脚注；本条源码不替代各版本部署配置核验。

内部核验凭据：`docs/reference-endcards/batch-6/sources-global-id.json`。旧研究blob `a424fd10e55813281e6c8ae38b11e1481dc1c222`；完整SHA-256 `51f698626af14fe8a51b9e31f5d1b80c4a0d719867f446122e43f90d5003ee37`。
