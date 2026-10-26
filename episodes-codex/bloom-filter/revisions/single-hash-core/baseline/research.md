# 布隆过滤器：调研与内容边界

访问日期：2026-10-26（北京时间）。按当前AGENTS、RULES、调研模板和新片参考资料流程执行。本期选自既有工程算法候选#300；EA06是策划检索编号，实际为工程算法第二支制作，不由候选编号推断站点EP。

## 核心问题与本片模型

成员查询可以交给权威存储，但不在集合中的编号也可能触发昂贵查询。片中解释如何先用紧凑摘要排除一部分不存在的查询，以及为什么全部相关位为1仍不能确认存在。

本片使用初始全0的固定位数组、稳定的多位置映射和只置1的插入过程。先解释位是0或1，再解释同一编号每次映到相同位置、不同编号可共享位置。仅当相关元素已正确插入且查询配置和位状态保持时，发现0才可以安全排除；“可能存在”继续交给真实集合或权威存储确认。

## 实际来源读取与证据

官网直接访问Redis Bloom文档、Redis博客和Cassandra Bloom页面均被本环境代理403拒绝，未取得官网正文。实际阅读改用官方维护的GitHub仓库，并固定不可变commit；每份原文用GitHub Contents API GET后base64还原原字节，核对Git blob SHA-1和SHA-256。完整访问结果、摘要、证据路径及阅读范围见[核验JSON](research/source-verification.json)，原文在[research/sources](research/sources/)。成功访问官方仓库不写成同时成功访问官网。

### R1 · Redis：Bloom filter

- 原始题名：`Bloom filter`，原文Markdown front matter的`title`，没有用中文概括替代题名。
- 本轮实读：[官方文档固定正文](https://github.com/redis/docs/blob/4fe762f8dab40f0b661207374378ed52113c9fe3/content/develop/data-types/probabilistic/bloom-filter.md)。
- 官网对应页：[Bloom filter](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/)，本轮直连403。
- 版本与日期：固定commit`4fe762f8dab40f0b661207374378ed52113c9fe3`；文档未标发布日期，访问日不是发布日期，也不推断某个Redis正式版本。
- 原文证据：`research/sources/redis-bloom-filter.md`；本轮阅读完整文档184行。
- 支持主张：紧凑成员摘要，阴性/阳性不对称，可能是假阳性，预期容量和目标误判率的空间取舍。Redis多层可扩展过滤器与本片单个位数组分开。
- 原文摘录：A Bloom filter can guarantee the absence of an item from a set, but it can only give an estimation about its presence.
- 定位：Overview第三段第一句，原文行33；列入片尾R1。
- 采用边界：概述后续关于阳性答案中有多少错误的口语描述容易混淆条件概率，本稿不采用。标准假阳性概率以实际未插入元素为条件，不是阳性答案中错误所占比例。文档的`NONSCALING`和容量行为不在本片作产品命令保证。

### R2 · Apache Cassandra：Bloom Filters

- 原始题名：`Bloom Filters`，AsciiDoc首行`= Bloom Filters`。
- 本轮实读：[官方文档固定正文](https://github.com/apache/cassandra/blob/05853eaeab006bd1e834331ac8b1dfdc464d1f31/doc/modules/cassandra/pages/managing/operating/bloom_filters.adoc)。
- 官网对应页：[Bloom Filters](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/bloom_filters.html)，本轮直连403。
- 版本与日期：固定trunk commit`05853eaeab006bd1e834331ac8b1dfdc464d1f31`；原文未标发布日期，不据此冒称特定正式产品版本已实测。
- 原文证据：`research/sources/cassandra-bloom-filters.adoc`；本轮阅读完整短页。
- 支持主张：Cassandra在读路径利用摘要排除不含目标分区的SSTable文件；存在可能性仍需进一步检查；准确性与内存存在取舍。
- 原文摘录（保持原始换行）：

  ```text
  bloom filters can be made more accurate by allowing them to
  consume more RAM.
  ```

- 定位：开头第三段，原文行14–15；列入片尾R2。
- 采用边界：SSTable是本条来源的真实系统语境，不把本片简化模型说成完整Cassandra读路径；不采用该页具体默认参数和内存倍数作为通用Bloom定律，本轮未运行产品验证。

### R3 · Google Guava：BloomFilter.java及BloomFilterStrategies.java

- 原始文件题名：`BloomFilter.java`、`BloomFilterStrategies.java`，仅作源码引用，不自拟成正式文档题名。
- 本轮实读：[BloomFilter.java](https://github.com/google/guava/blob/5ae56d77e64305752b919ff2c96713f47ac0c94c/guava/src/com/google/common/hash/BloomFilter.java)、[BloomFilterStrategies.java](https://github.com/google/guava/blob/5ae56d77e64305752b919ff2c96713f47ac0c94c/guava/src/com/google/common/hash/BloomFilterStrategies.java)。
- 版本与日期：固定commit`5ae56d77e64305752b919ff2c96713f47ac0c94c`；源码copyright年份不冒充本轮维护日期。
- 原文证据：`research/sources/guava-BloomFilter.java`、`research/sources/guava-BloomFilterStrategies.java`。
- 实际阅读范围：类型Javadoc，Strategy的置位/查询契约，`put`/`mightContain`、`expectedFpp`、容量/尺寸相关方法和`readFrom`中funnel一致性要求；实际32/64位策略的置位与查询循环。未编译运行Guava，也不宣称逐行审计完整库。
- 支持主张：插入把多个选中位置置1；查询仅在所有选中位均为1时返回可能存在；正确插入的同一元素后续应返回true；容量超预期会恶化假阳性；查询映射必须与构造时一致。
- 结构边界：实际实现可以从两个哈希值派生多个位置，不能说每个位置都必须重跑独立哈希函数。基础结构的删除问题由共享位模型直接推导，不将Cuckoo或Counting的删除能力套到普通位数组。
- 用在：研究、文章和机制核验；不增加片尾第二页。

## 自设教学输入及可复算结论

以下不是Redis、Guava或Cassandra产品参数或实测。教学模型使用16位、索引0–15；三路位置为`SHA256(f'{seed}:{sku}')`前8字节按big-endian整数对16取模，seed为0、1、2。

| 身份/操作 | 编号 | 映射位置 | 结论 |
|---|---|---|---|
| 插入A | sku101 | 3、14、15 | 对应位置置1 |
| 插入B | sku205 | 0、3、12 | 共享3，置位后1位为0、3、12、14、15 |
| 未插入D，查询 | sku001 | 12、2、15 | 2为0，可确定未插入 |
| 未插入C，查询 | sku067 | 14、0、15 | 14/15来自A、0来自B，全部为1但C未插入，构成假阳性 |
| 错误删除反例 | 清零A所占位 | 3与B共享 | 将3清零会令B出现错误阴性，普通过滤器不能据元素直接清零删除 |

四个编号和共享位结果已用Python标准库实际复算，尚不代表独立模型大样本、正式动画或成片检查通过。一个合成假阳性不能推出普遍误判率；不在片中用该样本估算请求减少比例。

## 事实、编辑选择与后续检查分开

- 公开资料支持机制与边界；采用编号查询、16位三路演示、镜头组织和解释顺序属于编辑设计。
- 无假阴性有正确插入、稳定配置和状态维护前提。过滤器漏同步、损坏或错误清零时不能替数据库给出可靠不存在判断；并发注册还需要权威存储的唯一性约束，不靠一次Bloom查询保证。
- 基础过滤器只置1，额外元素不会把已置位变成0；更多元素和固定空间通常让误判风险上升，但具体概率依赖模型/配置，不给无来源的通用百分比。
- 位数组记录摘要，不保存原始对象，不直接返回对象内容；“可能存在”并非数据库实际命中。
- 本轮只完成源阅读和确定性例子复算。资料卡布局、脚本编辑、真实配音、术语时序、动态、正式媒体和线上交付由后续真实检查分别记录。
