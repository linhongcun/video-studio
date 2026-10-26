# Redis跳表：资料核验与主张范围

本期为工程算法03候选实现，实际身份由root记录。只讲一条因果链：有序链表找55要逐项看；加一层稀疏远链接，按下一节点的大小决定前进或在当前位置下降，取得各层插入前驱，再把新55接进去。用户对上一期简化后的清晰度给出正向反馈，本片据此保留机制主线，避免将业务查找、改分、排名、区间四条路径同时开讲；这不是对本片新成片的预先认可。

## 已实际读取的固定第一方来源

|原题/原文件名|版本或提交|支持主张|
|---|---|---|
|Redis sorted sets|docs `fcc15c76a48baeb0dc08fc839242a7799c077080`|score排序、同分member字典序、普通编码下跳表/字典分工|
|t_zset.c|Redis8.4.0 GA `60ba86f3c8b4e1ec96451171753a0a38e5c45a0c`|真实比较/前进/下降、随机层高、记录各层前驱、前向链接接入；编码分支与改分边界|
|Memory optimization|同一docs提交|小集合listpack与超阈值转换，不将教学8节点当默认实际编码|

实际获取方法为官方GitHub Contents API GET，base64解码原始UTF-8字节，逐一核SHA-256及Git blobSHA1；题名用实际frontmatter及GitHub文件名元数据。官网URL仅作对应入口，本轮未把官网记为成功访问。原文与元数据在research/sources，获取台账在research/source-verification.json。

## 原文位置与技术结论

- `sorted-sets.md`第20行原题`Redis sorted sets`，不是旧策划概括的`Sorted sets`。第25–27/44–47行给出score及相同score下member字典序；第69–73行为普通跳表编码下的结构说明。引用的连续原文为`Sorted sets are implemented via a\ndual-ported data structure containing both a skip list and a hash table`，references.json保存真实换行。该段不能单独证明所有小ZSET都使用跳表，必须结合编码分支。
- `t_zset.c`第1行实际文件名，GitHub元数据`name: t_zset.c`可逐字定位。第125–136行说明随机层高且较高层更少；第140–160行从高层开始，比较后继的score、同分时再以`sdscmp`比较成员，仅后继小于插入目标时前进；否则记录当前前驱，再在同一当前位置降到下一层。不能画成先走到过大的70，再退回40。
- 第164–179行给新节点随机层高，再令新节点前向链接接原后继、旧前驱指向新节点。第181–191行还维护span、backward、tail等，本片仅画前向链接机制，不能称为完整Redis内存布局。
- 第267–309行`zslUpdateScore`：若分数变化后仍处邻居之间，可能只更新score；否则删除旧节点再插入。不是每次改分都全量重排，也不是每次都必然移动节点。此支线留图文，不进入主片。
- 第1259–1280及ZADD编码分支说明listpack与skiplist编码。小集合的默认紧凑编码不应被片中8项图覆盖；图统一标“跳表编码示意”。真实产品演示若要强制8项跳表，应明确配置并核`OBJECT ENCODING`，不能伪造本例随机层高是实际Redis抽样轨迹。
- `memory-optimization.md`第37–43行列出Redis>=7的listpack阈值配置；第55–56行连续原文`If a specially encoded value overflows the configured max size,
Redis will automatically convert it into normal encoding.`。本片不把配置示例值当所有部署的固定规则。

## 最简可复算例子

底层节点分数依次10、20、30、40、50、60、70、80，只有40和70在上层也有链接。节点在上下层是同一个元素的不同前向链接，不是额外保存一批成员。分数互不相同以免同分分支抢主线；真实比较仍以(score,member字节序)排序。

查55：上层看40，小于55，前进到40；后继70过大，游标留在40下降。底层看50，小于55，前进到50；后继60过大，确定插入前驱为底50/上40。插入55，本次示例固定层高为2：新55的底层后继为60、上层后继为70，再令底50与上40分别指向55。其余前向链接保持。

40/70的上层位置是不规则的合法示例高度，不是每隔固定几个选一个；新增55取2层是为动画固定的一个合法结果，不是实际Redis RNG回放。固定两层只展示前进/下降机制，不能宣称永远两层对任意规模均有O(logN)保证；完整随机多层跳表的期望效率与最坏退化另行说明。

本例比较4个后继分数，逐项底层对照比较6个；这只是单一构造，不是吞吐/延迟/命中率实验，也不证明每个查询都减少同样次数。

## 模型与实际执行范围

/tmp候选builder曾在`before.nodes`用浅拷贝，活动链条插入后污染了“插入前”序列化快照。独立复核发现此问题后保留原候选，并改为deepcopy；新增按forward实际遍历before/after、无悬空/环、before无55、原40上→70/50底→60保持的断言，两次完整生成逐字一致。原11,269断言只覆盖活动结构的查询、插入、同分排序，不能证明旧序列化快照正确。正式model由root另写builder，不直接把旧候选当生产数据。

本文代码单独实际运行，输出及断言见research/article-snippet-verification.json与article-demo-result.json。查找、插入及字节比较教学模型与真实Redis产品实验分开；本调研未运行Redis服务端，也未报告生产性能。

## 主片取舍

- 保留一个游标、一种向前动作、一个下降点、各层两个插入前驱；先让观众看清规则和因果，再命名跳表。
- 字典按member定位、span求排名、同分成员比较、改分/删除、更多层与概率公式留图文；不把省略机制说成Redis不存在这些结构。
- 参考资料卡保留Redis sorted sets与t_zset.c两个实际原题/原文件名。Memory optimization作为图文补充，不因“只上两项卡”删掉编码边界或源码依据。
- 只有来源与模型通过不能推出新片已经清晰。最终仍需实际配音窗口、无字幕连续动画、成片与播放器检查。

## 完整出处

- Redis，**Redis sorted sets**：https://github.com/redis/docs/blob/fcc15c76a48baeb0dc08fc839242a7799c077080/content/develop/data-types/sorted-sets.md；官网入口https://redis.io/docs/latest/develop/data-types/sorted-sets/。
- Redis，**t_zset.c**：https://github.com/redis/redis/blob/60ba86f3c8b4e1ec96451171753a0a38e5c45a0c/src/t_zset.c，Redis Open Source8.4.0 GA，提交日期2025-11-18。
- Redis，**Memory optimization**：https://github.com/redis/docs/blob/fcc15c76a48baeb0dc08fc839242a7799c077080/content/operate/oss_and_stack/management/optimization/memory-optimization.md；官网入口https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/memory-optimization/。
