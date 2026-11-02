# EP52 Redis近似LRU：来源与实现研究

日期：2026-11-02（北京时间）。状态：本轮实际读取官方固定源码与官方文档；脚本待独立叙事审读；未配音、未编码。制作基线 `01cd181caf24d4a8ce846c0eb8faeeab8f0054e2`，只创建本期实体目录，不改任何历史冻结输入。

## 固定版本与实读证据

- 产品：Redis 8.4.0，官方 tag API 解析为 commit `60ba86f3c8b4e1ec96451171753a0a38e5c45a0c`。实际API响应保存 `sources/redis-tag.json`。
- 官方文档：`redis/docs` 的 `content/develop/reference/eviction/index.md`，固定提交 `8e40c52452233daad74a303d3714586f53640a36`，blob `4046af13e35ec800e694ce3010bd4b78edd55458`。将内容API解码为 `sources/key-eviction.md`，后续固定提交API再次下载并验证逐字节相同。网页未标发布日期；当前文档还含8.6的LRM章节，本期只核对LRU/LFU与maxmemory章节，不把LRM写成8.4功能。
- 实现：固定8.4.0的 `src/evict.c`，blob `5509bdf034e51a039979a79a701e6bc32593ca78`，保存官方Contents API与原文 `sources/evict.c`。实际读取本片相关结构、时钟估算、抽样填池、遍历数据库、池选择及删除调用。
- GET URL、HTTP200、访问时刻、响应字节数与SHA见 `sources/fetch-manifest.json`。官方维护机构为Redis；没有把copyright、Git提交者或维护账号推定为文献个人作者。

## R1 · Key eviction

- 机构：Redis。原始题名 **Key eviction**，题名依据为官方源文档frontmatter `title: Key eviction`（`sources/key-eviction.md` 第15行）。
- 公开网页：https://redis.io/docs/latest/develop/reference/eviction/ 。实际本轮读取官方源码的固定版本：https://github.com/redis/docs/blob/8e40c52452233daad74a303d3714586f53640a36/content/develop/reference/eviction/index.md 。
- 版本：本轮固定文档提交；网页未标日期，不凭仓库提交日期猜测文档发布日期。
- 实读章节：Using maxmemory / Eviction policies / Approximated LRU algorithm / LFU eviction。
- 连续原文：`The Redis LRU algorithm uses an approximation of the least recently used\nkeys rather than calculating them exactly. It samples a small number of keys\nat random and then evicts the ones with the longest time since last access.`
- 定位：Approximated LRU algorithm 段首，原始换行保留于证据。支持片中近似而非全局精确顺序、随机抽样和较长空闲候选；不支持任意固定抽样必能找全局最旧。
- 第二段：`From Redis 3.0 onwards, the algorithm also tracks a pool of good\ncandidates for eviction.`（正文完整句在证据中）支持跨样本候选机制，具体持久、排序和存在检查以R2实现为依据。
- 配置与成本：`maxmemory-samples 5`为文档示例配置；提高采样到10会增加CPU。文档内存成本说明不等同于本片已测量内存或CPU百分比。
- LFU：文章只说明概率计数与衰减，不当精确频率、永久热点保护或视频并行主线。
- 片尾：入选R1；片尾只显示原始题名与机构。

## R2 · evict.c

- 机构：Redis；原始题名为官方源码文件名 **evict.c**，依据 `sources/redis-evict-api.json` 的 `name` 与 `path`。代码文件不另拟中文名冒充原题。
- 版本：Redis8.4.0 / commit `60ba86f3c8b4e1ec96451171753a0a38e5c45a0c`。
- 永久链接：https://github.com/redis/redis/blob/60ba86f3c8b4e1ec96451171753a0a38e5c45a0c/src/evict.c 。
- 第24–46行：EvictionPoolLRU为静态池，`EVPOOL_SIZE 16`；每项存idle、key、dbid、slot。注释明确保留跨performEvictions调用的候选，池内idle升序、右端较旧。
- 第75–83行：`estimateObjectIdleTime` 使用压缩LRU时钟估计空闲毫秒，不是维护链表全局名次。
- 第90–110行：算法注释声明N个随机样本、固定M池、保留不存在的候选可能成为ghost。
- 第134–224行：`evictionPoolPopulate` 通过字典采样取得候选，根据策略计算idle；按排序位置插入，满池时更差样本不加入或挤掉较差项。它没有逐键维护精确全局顺序，也没有去重同名候选的显式步骤；动画采用互不重叠样本，文章注明可能重复。
- 第575–645行：`performEvictions` 在需要腾空间的循环里先按符合策略的数据集填池，再从池最大端往回找。先移除该候选记录，并查询实际键；存在则选它，不存在则继续。候选池中的idle是采样时记录，不是每轮统一刷新历史分数，存在检查也不等于重新计算该键当前idle。
- 第680–693行：为选择的实际键调用 `deleteEvictedKeyAndPropagate`，累计释放内存；是否需要继续按实际字节判断，不是固定“每写一个键就删一个键”。
- 连续原句：`To improve the quality of the LRU approximation we take a set of keys\n * that are good candidate for eviction across performEvictions() calls.` 保存换行/注释符号的原始证据用于核对；文章采用不含注释符号、位于连续同一行的短引：`#define EVPOOL_SIZE 16`。
- 片尾：入选R2，题名evict.c与机构Redis。

## 本片原创教学实例与限制

当前示意时刻100，最近访问时间 A10/B20/C30/D40/E50/F60/G70/H80，空闲90/80/70/60/50/40/30/20。八个等大键只是展示容量，不作为Redis内存账本。全部无TTL；allkeys-lru单DB，无Cluster迁移和并行访问。

第一轮固定样本C/D/E，空池进入E50/D60/C70，取C；原键C删除，写I。D/E候选不清空。第二轮固定样本F/G/H，加入后H20/G30/F40/E50/D60，取D；写J。两轮置于同一粗粒度时钟内、期间无其他读取；此条件使所示分数保持，不用动画的停止时钟冒充真实系统自动刷新旧候选。A始终未被抽到，说明局部候选胜出不保证全局最旧。

另设独立ghost条件：应用先删E，而旧池记录还在；使用它时发现键不存在并跳过，不重复释放内存。图上必须将原始键与候选记录画成不同对象，采样不表示数据移动。

采样数3为教学配置，不冒充默认值。样本序列为预设，不能说实测Redis随机数恰好如此；实际产品运行单独保留自己的日志和结果，不用教学模型代替。扩大样本只提高发现旧键的机会，不承诺所有负载/每个随机序列的命中率单调改善。
