# 单位置主线：参考资料输入

本修订仍使用两项核心官方文档，一页、默认5秒；采用`original-title-quote`，保留原题和连续原文，不显示内部`supports`。此文件记录制作输入，不预记新附录已编码或已通过播放器检查。

| 编号 | 原始题名 | 支持内容 | 原文证据 |
|---|---|---|---|
| R1 · Redis | Bloom filter | 近似成员查询的两种结果；容量、空间与选取次数取舍 | `research/sources/redis-bloom-filter.md` |
| R2 · Apache Cassandra | Bloom Filters | 确定排除/可能存在及内存准确性取舍 | `research/sources/cassandra-bloom-filters.adoc` |

这两份原文及其原始GET回执从既有制作工程按原字节复制，原下载时间、固定commit、Git blob和SHA保留；本次只重新阅读相关段落和核对新路径，不将复制或复读记为新下载。原始回执在`research/previous-retrieval/source-verification.original.json`，新复读/路径对应在`research/source-verification.json`。

Guava的`BloomFilter.java`与`BloomFilterStrategies.java`另作研究和文章源码依据，明确支持最小k=1以及实际置位/查询循环；不增加片尾页数，也不把Java源码语法改写成原文短引。

官网链接和本轮复用的不可变GitHub正文链接均保留。原官网访问被代理403拒绝，不能记作成功；复读固定副本不改变这一历史事实。源题名和短引在新证据路径中逐字匹配。

新片的8位数组、seed22、A/B/C映到3而D映到7，以及seed0的第二位置，均为实际SHA-256可复算的教学参数。官方来源支持基础机制，不提供这些示例数值或生产误判率。正式编码仍需检查实际卡片、字幕结束边界和暂停/全屏可读性。
