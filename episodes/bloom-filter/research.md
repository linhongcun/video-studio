# 布隆过滤器：单位置主线的研究依据

复读日期：2026-10-26（北京时间）。本修订以8位、一次位置计算讲清加入、共享、确定排除和可能存在，移除商品业务与三路并行计算；仅在结尾用同一集合的两位置重建对照说明增加检查的作用。

## 来源身份与本次读取范围

本次没有重新下载官网或仓库正文。四份既有固定官方原文与原GET核验JSON按原字节复制，并重新核对SHA；原始下载时间和失败的官网访问保持历史身份。原始回执见`research/previous-retrieval/source-verification.original.json`，新文件路径、摘要与复读范围见`research/source-verification.json`。

### R1 · Redis：Bloom filter

- 原始题名：`Bloom filter`，原文front matter的`title`。
- 固定官方正文：https://github.com/redis/docs/blob/4fe762f8dab40f0b661207374378ed52113c9fe3/content/develop/data-types/probabilistic/bloom-filter.md
- 官网对应页：https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/ 。原直接访问403，本次未重新访问。
- 固定commit：`4fe762f8dab40f0b661207374378ed52113c9fe3`；未标发布日期，不以复读日冒充文档发布日期。
- 原文字节SHA-256：`0e72ec0308ce57807ff8012465455c7d5bc37df78cecffe99e23e8f1e3ecfc59`；证据`research/sources/redis-bloom-filter.md`。
- 本次复读：Overview的不对称错误、Reserving Bloom filters及Total size的容量、选k和空间相关段。它支持通用成员摘要与取舍，不据此声称Redis默认只选一个位置。
- 入卡连续原句：A Bloom filter can guarantee the absence of an item from a set, but it can only give an estimation about its presence.
- 原句定位：Overview第三段第一句，行33；未拼接、翻译或增加省略号。
- 采用边界：概述中阳性回答错误比例的口语化表述不采用，避免混淆P(返回阳性|未加入)与P(未加入|返回阳性)。不把NONSCALING简述当作本轮已审核的内部实现。

### R2 · Apache Cassandra：Bloom Filters

- 原始题名：`Bloom Filters`，AsciiDoc首行`= Bloom Filters`。
- 固定官方正文：https://github.com/apache/cassandra/blob/05853eaeab006bd1e834331ac8b1dfdc464d1f31/doc/modules/cassandra/pages/managing/operating/bloom_filters.adoc
- 官网对应页：https://cassandra.apache.org/doc/latest/cassandra/managing/operating/bloom_filters.html 。原直接访问403，本次未重新访问。
- 固定trunk commit：`05853eaeab006bd1e834331ac8b1dfdc464d1f31`；未标发布日期，不写成特定正式版本已经实测。
- 原文字节SHA-256：`8582c28aba3e3ec34c01aeb2dcd8463995d443a5280ae624fbbf2894b3c0c357`；证据`research/sources/cassandra-bloom-filters.adoc`。
- 本次复读：开头的确定不存在/可能存在，以及准确性与内存的取舍。这份短页不规定k的最小值。
- 入卡连续原句，保持原始换行：

  ```text
  bloom filters can be made more accurate by allowing them to
  consume more RAM.
  ```

- 定位：开头第三段，行14–15；不采用该页产品默认参数或内存倍数作为通用Bloom定律。

### R3 · Google Guava：实际k=1依据

- 原始文件题名：`BloomFilter.java`、`BloomFilterStrategies.java`。
- 固定正文：https://github.com/google/guava/blob/5ae56d77e64305752b919ff2c96713f47ac0c94c/guava/src/com/google/common/hash/BloomFilter.java
- 策略正文：https://github.com/google/guava/blob/5ae56d77e64305752b919ff2c96713f47ac0c94c/guava/src/com/google/common/hash/BloomFilterStrategies.java
- 两份证据：`research/sources/guava-BloomFilter.java`和`research/sources/guava-BloomFilterStrategies.java`，SHA分别为`c72a38abb4a0963ed026b5b56d1e265ab9ebd1805a20227d290c371f19849143`、`4d643bea3fcf55540b8d39343b89ccccecc707daf1593fb503c1d7d4b299b5c2`。
- 实际复读：类Javadoc、构造器、put契约、选k方法，以及实际置位/查询策略循环；不宣称逐行审计整个Guava库或运行了Java产品。
- `BloomFilter.java`行134–140要求`numHashFunctions > 0`且不超过255；合法最小整数为1。
- 行565–567返回`max(1, (int) round(-log(p) / LOG_TWO))`，明确把最小k钳到1。按该源码p=0.5时取k=1，这是源码推导而非本轮产品运行。
- `BloomFilterStrategies.java`约116–124、138–148的实际循环均为`i < numHashFunctions`，k=1正常执行一次。插入置位，查询遇到0返回false。
- 类Javadoc保留单边错误定义，put保证正确插入的同一对象后续返回可能存在；普通过滤器不保存每个已置位的所有者。
- 实现可由少量基础哈希派生多个位置，不能把k次位置选择一概说成必须运行k次完整SHA。

## 新教学模型与完整因果

主规则是`SHA256(f"22:{key}".encode("utf-8"))`前8字节按big-endian非负整数对8取模。真实输入就是A、B、C、D，数字来自实际计算；这些参数刻意选择来展示碰撞，不是产品配置或概率样本。

| 元素 | 第一位置（seed22） | 对照第二位置（seed0） | 初始是否加入 |
|---|---|---|---|
| A | 3 | 2 | 是 |
| B | 3 | 1 | 是 |
| C | 3 | 5 | 否 |
| D | 7 | 5 | 否 |

- 初始8位全0；加入A使3号0→1，加入B也到3号但保持1。位值不是计数，不保存元素或所有权。
- D在7见0，可确定未加入：若正确加入，它当时必把7置1；结论要求固定规则和标记正确保留。
- C在3见1，但从未加入；这个1来自A/B，只能表示可能存在。
- 错误删除A并清3后，仍在集合内的B会被错误排除。它是无效操作反例，不是普通Bloom支持的删除方法。

## 两位置对照须重新构造

另外从全0开始，使用同一集合A/B构造两位置摘要：A写3/2，B写3/1，得到1、2、3为1。再查C的3/5，5为0，排除原先C这次误判。不能用未补齐第二位置的旧单位置数组直接执行新查询。

这个对照只能证明本次C被排除，不证明所有查询或全局误判率单调改善。真实保护性反例H映到[1,1]：单位置时1号为0，H被排除；两位置重建后1号被B置1，H反而成为假阳性。该反例留作技术审查，不把第五个元素扩进主片。

增加位置会增加选取/检查与置位工作，也会使固定数组更拥挤；位数、预计元素数和k要联合选择。更多位消耗空间，不能把单个合成例子用来估算线上误判率、请求减少比例或吞吐。

## 验证范围

本修订的可运行教学代码负责复算A/B/C/D、共享位错误删除及独立重建的两位置对照；执行结果另存`research/`。源阅读、模型复算与后续真实配音/动态/正式成片检查分开记录，不预记未执行的阶段通过。
