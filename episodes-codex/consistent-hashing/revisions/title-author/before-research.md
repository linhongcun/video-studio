# EA01一致性哈希：公开资料与示例边界

访问日期：2026-10-25（北京时间）。本轮通过TinyFish实际提取并阅读下列三个官方页面的相关正文，不以搜索摘要代替原文。动态文档没有明确页面发布日期时如实标注；访问日期不冒充发布日期。

视频讲**缓存路由的单归属简化模型**：固定哈希空间、顺时针首个节点、插入一个新节点、多个虚拟位置。Cassandra资料有多副本、修复和失败域语境，本片只借其明确解释的环与虚拟节点机制，不把简化模型说成完整Cassandra实现，也不把它说成Redis Cluster的分片方式。

## R1 NGINX官方：普通哈希与一致性哈希的重映射区别

- 主张：成员变化会使普通哈希映射大幅改变；`hash ... consistent`使用Ketama一致性哈希，以减少成员变化时重新映射的键，服务于缓存命中。
- 来源：NGINX，Module ngx_http_upstream_module，`hash`指令节。
- 链接：https://nginx.org/en/docs/http/ngx_http_upstream_module.html#hash
- 访问日期：2026-10-25（北京时间）。
- 页面上的日期：未标该节最后更新日期；正文说明`hash`指令自1.7.2出现，这是功能引入版本，不是页面日期。
- 实际读取：工具返回了整个模块正文，实际核对`hash`段从Syntax到`ketama_points`说明；工具final_url锚点显示`#keepalive`，同一返回正文仍完整包含`hash`段，引用使用官方正确`#hash`锚点。
- 用在：01、04–06、11、14镜及文章的工程动机与产品实例。
- 原句短引：普通哈希，“may result in remapping most of the keys”。
- 原句短引：consistent，“only a few keys will be remapped”。
- 原句短引：缓存动机，“a higher cache hit ratio for caching servers”。
- 适用边界：这是NGINX对其实现的说明，不保证任意手选环、任意键分布或任意容量配置都改变固定比例的键；本片0..99环与十键不冒充NGINX Ketama实现或实测。

## R2 Apache Cassandra 5.0官方：固定环与虚拟节点

- 主张：取哈希值对桶数取余时，改变桶数可能改变大量映射；一致性哈希把节点映到环中，以键的哈希位置沿环查找负责节点；一个物理节点可以拥有多个token位置。
- 来源：Apache Cassandra Documentation，Dynamo，Dataset Partitioning: Consistent Hashing；Consistent Hashing using a Token Ring；Multiple Tokens per Physical Node (vnodes)。
- 链接：https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html
- 访问日期：2026-10-25（北京时间）。
- 页面上的日期：正文未标发布日期/最后更新日期；页面元数据`dcterms.identifier`为5.0，作为本次适用文档版本记录，不把latest永久理解为5.0。
- 实际读取：完整提取正文中取余、Token Ring、Multiple Tokens per Physical Node、token数量代价与Multi-master Replication开头；已区分环的单归属教学与原页RF=3示例。
- 用在：02–04、06–14镜；文章的环、虚拟节点与代价。
- 原句短引：取余问题，“adding a single node might invalidate almost all of the mappings”。
- 原句短引：环，“maps every node to one or more tokens on a continuous hash ring”。
- 原句短引：查找方向，“walk the ring in a clockwise fashion”。
- 原句短引：虚拟节点，“assigning multiple tokens in the token ring to each physical node”。
- 原句短引：代价，“Cluster-wide maintenance operations are often slowed”。
- 适用边界：原页讨论持久数据、多副本和token分配器。视频取一个负责节点，省略复制，不套用Cassandra默认token数量或声称每个节点固定必须三个token。虚拟节点缓解分配倾斜，需要合理位置/权重与工作负载前提；额外token也会增加维护成本，不是越多越好。

## R3 Redis官方：固定槽分片与迁移是另一层机制

- 主张：Redis Cluster把键空间分为16384个槽，键到槽使用CRC16后取余，扩容迁移槽及槽内键；这与本片节点直接放入环、沿环找节点的模型不同。
- 来源：Redis cluster specification，Key distribution model；Live reconfiguration。
- 链接：https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/
- 访问日期：2026-10-25（北京时间）。
- 页面上的日期：正文未标最后更新日期；工具返回页面`article.modified_time`为2026-09-21T15:59:03+01:00，仅记录其元数据，不推出所有章节该日重写。
- 实际读取：Key distribution model中的16384槽和`HASH_SLOT = CRC16(key) mod 16384`、hash-tag例外；Live reconfiguration中新增空节点、移动槽和移动槽内键；MOVED/ASK仅识别职责，未把全协议当作本期内容。
- 用在：仅文章的产品边界；支持把“负责位置变化”与“搬迁键”区分，不将Redis操作细节推广为所有缓存的迁移协议。
- 原句短引：固定槽，“The cluster's key space is split into 16384 slots”。
- 原句短引：迁移，“moving a hash slot from one node to another”。
- 原句短引：数据，“move keys from an instance to another instance”。
- 适用边界：hash-tag可能改变参与CRC16的子串；文章的简式不是无例外完整规范。16384是固定槽数，与当前节点数量无关，所以不能看见mod就误判它有本片直接对节点数取余的同一问题。

## 本期自设示例与推导，不作为公开来源数字

| 项目 | 输入与结论 | 证据性质 |
|---|---|---|
| 取余扩容 | 哈希值[5,13,27,34,46,56,64,78,86,95]；编号A0/B1/C2，新增D3；`h % 3`到`h % 4`有8项改变 | 预设教学输入，按规则直接计算；进入片前由制作侧与独立侧复核 |
| 单环扩容 | 固定空间0..99，A20/B50/C85，新增D70；首个位置不小于h的节点，否则回绕；只有56/64改归D | 预设教学输入，非哈希产品实测 |
| 局部区间 | 保留旧token，只插入D70，受影响区间(50,70]，长度20；50仍B，70归D | 顺时针首个节点规则的直接推导；不推成一般20%保证 |
| 虚拟节点 | A5/38/72、B15/48/82、C28/60/94；另例插入D10/34/88 | 预先配置示例，不是随机生成、最优分配或性能测试 |
| 多处分担 | D分别接管(5,10]、(28,34]、(82,88]，原负责节点依次B、A、C | 由同一查找规则推导；不口播17%或作为均衡收益结论 |
| 单热点限制 | 同一键、同一哈希与同一成员视图仍找到同一负责节点；重复请求因此仍可能集中 | 确定性单归属模型的直接推论，不推广为所有带复制/热点拆分策略的系统 |
| 缓存未命中 | 原值在C，新的取余路由去A；A可能无此键，须迁移或按该缓存策略回源重建 | 本片自设数据库回源场景；不是每种缓存固定有此数据库路径 |

经典1997一致性哈希论文和2007 Dynamo论文是历史背景，本稿没有获取并通读其全文，故不把它们记作本轮已读材料或主论证。算法历史年份、作者归属和旧文参数不进本期脚本。

## 事实、编辑判断与待验证项

- 公开资料支持机制和产品边界；选择缓存扩容作为贯穿示例、14镜组织和本期样本是编辑判断。
- 文稿中的计算表是可复算的教学内容，不等于TTS、程序运行、真实动态、成片或初学者理解已经通过。
- 视频不声称提升多少吞吐、节省多少内存、迁移多少字节；键数、数据大小、请求频率与机器容量是不同指标。
- 不讨论共识、主节点选举或强一致协议；名称中的“一致性”不能解释成自动的数据副本一致性。

## 原题名与引用语段校订（2026-10-25）

本轮只校订参考资料的题名与显示原句，未重写技术讲解。实际重新GET四项中属于本片的官方固定正文，完整响应SHA、题名原文和逐字短引见[核验记录](../../docs/reference-endcards/original-titles/sources-extra.json)。旧资料读取记录保留，不追改为新访问。

- R1 原题：Module ngx_http_upstream_module；定位：hash directive, consistent parameter paragraph；实际固定正文：https://github.com/nginx/nginx.org/blob/34f63eb329ff52623cec453cd8f7539f9a5f8606/xml/en/docs/http/ngx_http_upstream_module.xml。
  - 原句（130字符）：The method ensures that only a few keys will be remapped to different servers when a server is added to or removed from the group.

- R2 原题：Dynamo；定位：Multiple Tokens per Physical Node (vnodes), paragraph 2；实际固定正文：https://github.com/apache/cassandra/blob/76550e931481e965ae3283d8cf4a59c320d74c55/doc/modules/cassandra/pages/architecture/dynamo.adoc。
  - 原句（101字符）：Virtual nodes solve the problem by assigning multiple tokens in the token ring to each physical node.

- 已核实R2是Apache Cassandra 5.0文档的AsciiDoc首题`= Dynamo`，不是Amazon论文。历史关于未通读Amazon原论文的记录仍成立；没有为本次片尾替换资料身份。
