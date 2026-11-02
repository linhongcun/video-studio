# Redis Cluster 自动故障转移：本轮研究

本轮实际读取日期：2026-11-02（北京时间）。适用固定 Redis 8.4.0 commit `60ba86f3c8b4e1ec96451171753a0a38e5c45a0c`。制作基线 `01cd181caf24d4a8ce846c0eb8faeeab8f0054e2`。正式视频、配音与产品实验尚未完成，不能把本记录视为交付通过。

官方资料通过 GitHub Contents API 实际GET保存原响应及解码字节。本机未安装 requests，首次Python尝试在联网前因缺模块终止，随后使用标准库urllib完成。未因此绕过网络代理。官方文档目录当前文件blob为 `2b03f5d63c83e9b293a6c9e98cd42faafa15ff46`，最近触及该文档的commit为 `eeff9cc955632aa199d1b1eabccd096d69b57878`；`sources/docs-file.json`与`cluster-spec.response.json`保存响应。版本文档与8.4固定源码交叉核对，不将动态文档页访问成功替代产品实验。

## R1：Redis cluster specification

- 机构：Redis。机构归属依据官方redis/docs仓库及对应redis.io发布路径；未发现此文明确公开个人署名，不推定Git提交者为作者，省略author。
- 实际原题：`Redis cluster specification`。`sources/cluster-spec.md` frontmatter `title:`是原题证据；不将linkTitle或自拟中文摘要当原题。
- 公开链接：https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/
- 固定仓库文档：https://github.com/redis/docs/blob/eeff9cc955632aa199d1b1eabccd096d69b57878/content/operate/oss_and_stack/reference/cluster-spec.md
- 页面发布日期：未标。本轮核对文档的Failure detection、Cluster current epoch、Configuration epoch、Replica election and promotion、Replica rank、Masters reply to replica vote request、Hash slots configuration propagation及Write safety上下文。
- 连续原句：`Once the replica receives ACKs from the majority of masters, it wins the election.`
- 原句位置：Replica election and promotion，第833行；本轮保存`source/cluster-spec.md`实际文件名为`sources/cluster-spec.md`。
- 用在：01–12；片尾入选。
- 重点：PFAIL是本地视图，FAIL依赖有效期内多数主节点的故障判断；这部分是弱聚合，不说成同步原子投票。正常自动路径中，合格副本提高currentEpoch并请求主节点授权；迟到的旧轮次回复不计入本轮。多数授权后提升并以更高configEpoch传播槽归属。
- 边界：角色与Sentinel不同；投票分母不是全部进程或当前在线进程。Redis Cluster的槽映射不是经典一致性哈希环。复制异步，授权不保证零写入丢失。手动FORCE/TAKEOVER路径不在本片。

## R2：cluster_legacy.c

- 机构：Redis；官方redis/redis仓库固定源码，无本文件明确个人署名，不从版权或提交者自动推定个人作者。
- 原题：`cluster_legacy.c`，由Contents API响应`name`证实。响应`sources/redis-cluster-legacy.response.json`；字节`sources/redis-cluster-legacy.c`。
- 版本：Redis 8.4.0，固定commit `60ba86f3c8b4e1ec96451171753a0a38e5c45a0c`。tag原响应`sources/redis-tag.json`。
- 公开链接：https://github.com/redis/redis/blob/60ba86f3c8b4e1ec96451171753a0a38e5c45a0c/src/cluster_legacy.c
- 阅读执行段：`clusterSendFailoverAuthIfNeeded`(4042–4145)、`clusterHandleSlaveFailover`(4292–4455)、AUTH_ACK接收(3280–3295)、`clusterFailoverReplaceYourMaster`及故障报告/标记函数。
- 连续原句（源码）：`int needed_quorum = (server.cluster->size / 2) + 1;`，第4295行。
- 确认：有槽主节点才有票；同轮只投一次，投票信息存储并安排fsync配置；自动授权要求候选为副本且旧主FAIL；配置不能落后于已知槽。副本新鲜度检查、固定+随机+排名延迟在先，提高currentEpoch和请求授权在后；满足计数门槛才晋升。
- 用在：03–10及图文；片尾入选。
- 注意源码注释中的“quorum is the cluster size + 1”不是实际计算公式，不能照搬；实际公式如上为整除2加1。演示以执行代码和规范对应。

## 文章独有摘录

A1从同一官方规范摘取PFAIL/FAIL完整定义段，支持故障判断阶段；A2摘取Write safety开头，支持异步复制数据丢失边界；A3为参选前置段；A4为更高configEpoch传播槽归属段。均保存到`article-sources.json`，逐字与`sources/cluster-spec.md`核对。不是额外独立文献，不为片尾凑条目。

## 教学模型与产品实验分界

动画使用三主三副本、固定槽范围与轮次5→6的有限模型。轮次、节点名、固定消息先后及预设数据差一条是教学输入，不是Redis运行日志。模型检查资格、报告有效期、投票资格/去重、轮次有效性、多数门槛、晋升后的槽归属和不可凭授权补数据。

真实产品实验拟使用同一8.4.0固定源码构建的redis-server/redis-cli，六个隔离本地进程，端口16600–16605，观察正常自动晋升与无法获得多数的对照。真实日志与结果另存；当前尚未执行，不预写通过。
