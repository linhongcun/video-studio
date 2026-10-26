# 数据库身份标识优化（#230）

2026-10-25，用户确认数据库圆柱、中文库名与内部记录分层的画法，并明确要求使用MySQL icon。按16片只读盘点，本轮接入10片；原脚本、音轨、字幕、分镜、数值和相机不改。

| 视频 | 接入位置 | 保留对象 |
|---|---|---|
| 服务端缓存 | 数据库角色标题 | 应用、缓存、价格及读取统计 |
| 缓存一致性 | 数据库角色标题 | 读写路径、缓存副本、价格与失效状态 |
| 主从复制 | 主库、从库及首次角色标题 | 同一用户的昵称记录与接收/应用状态 |
| 2PC | 订单库、库存库参与者标题 | 协调者、已保存值、待确认修改和占用 |
| 负载均衡 | 第11镜的共同数据库节点 | 三个应用、查询路径与瓶颈说明 |
| 分布式事务入门 | 同库共同范围、独立库范围 | 订单/库存字段、调用方、知识地图 |
| Saga | 账户库、库存库的本地边界 | 扣款、退款流水、请求、流程记录 |
| Outbox | 订单库/库存库边界和结尾库整体标题 | 订单、待办、唯一标记及队列 |
| 本地事务 | 第02/15镜同一数据库边界 | 两个账户及事务括线 |
| 分库分表 | 单库及A/B/C库标题 | 订单表、字段、行与路由落点 |

标记40–44像素，保持原色，以小型二维圆柱承载MySQL海豚图标。库内记录不变成独立数据库；应用、协调者、缓存、消息、统计和TCC资源不误贴。标记随原Scene变焦与淡出，总览知识节点继续表达步骤与判断。

## 素材与来源

使用[Devicon的MySQL SVG](https://github.com/devicons/devicon/blob/master/icons/mysql/mysql-original.svg)，Git blob `207170c1103aba5d26a3de34ed0735e5f32ea619`；原始SVG、离线data URI、MIT notice及来源摘要保存在[共享身份组件](../../../episodes-codex/_shared/database-identity/source.json)。原色及图形比例保持，没有外链图片请求。图标用于用户要求的技术对象识别，不宣称官方授权或品牌背书；品牌素材说明已实际查阅[MySQL官网](https://www.mysql.com/about/legal/logos.html)。

## 实际验证范围

- 33张预演代表帧：事务组16张实际为960×540，其余17张为1920×1080；包括库角色、调用方不误标、缩放中间态和回图。历史早期负载均衡检查由最终[独立预检](../../mysql-database-identity/load-balancing-preflight.json)取代，旧源/图指纹不改写为新版。
- 993条冻结声明对应866个唯一输入。fresh复制逐项SHA一致，全新依赖安装后10片类型检查通过；负载均衡2835帧与事务入门1848帧按实际相同比例复现，PNG字节和解码像素一致。纠正比例共输出3张图、仅2个代表时点，见[干净构建](../../mysql-database-identity/clean-build.json)。
- 画面正式编码，原混合AAC流直接复制；每片完整解码、格式/帧数和输入检查。负载均衡与本地事务只重新渲染涉及图标的镜头，未改镜头复用原画面，再统一编码；新源片段采用高质量CRF1中间编码，完整过程与基线指纹单列，不伪称整片均重新渲染。
- 正式MP4另由未制作该片的执行者逐片查看关键编码帧；这些抽查不等于全片实时人工听看或逐字ASR。用户随后明确反馈数据库内容更清晰，具体观看片目未逐一确认。

## 复现入口

已有本期freeze.py或句级episode-config的工程使用`episodes-codex/_shared/freeze_database_identity.py EPDIR`；旧的复制/本地事务/分库工程使用`freeze_database_identity_legacy.py EPDIR`。后者先保护旧清单中的所有未修改输入，再收录审核过的单一源文件、实际渲染依赖与共享图标。两者都不修改其他已发布工程的冻结器或共享相机。

源码常规渲染仍使用各期Remotion入口；本轮精确交付另保留原AAC及部分原画面的复用记录。历史原片/源/QA由各片`revisions/mysql-identity-before.json`指向Git基线，不把旧媒体复制回仓库。

## 当前状态

[PR #235](https://github.com/linhongcun/video-studio/pull/235)已合并，随[v0.58.1](https://github.com/linhongcun/video-studio/releases/tag/v0.58.1)发布；[Release后Pages部署](https://github.com/linhongcun/video-studio/actions/runs/40147968820)成功。线上10支完整视频SHA、字幕、章节、封面、源链接与实际更新日志核验通过，#230已以completed关闭。仅更新GitHub站点。2026-10-25用户反馈“现在这个关于数据库的内容看着就清晰多了”，已补入S019与项目记忆；不记为十片均获逐项认可。

[线上核验](../../mysql-database-identity/online-verification.json)与[发布身份](../../mysql-database-identity/release-binding.json)保存实际结果。
