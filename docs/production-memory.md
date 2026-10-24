# 项目制作记忆

更新于2026-10-24（北京时间）。本文件保留用户偏好、案例状态与阅读入口；具体错误及有效做法分别积累到下面两份文件，避免多处复制后互相冲突。

## 开工阅读入口

1. [教训](lessons-learned.md)：发生过什么、下次如何避免、如何验证已修复。
2. [成功经验](successful-practices.md)：实际有效的做法、适用场景和证据。
3. [现行规范](RULES.md)与[制作流程](pipeline.md)：规范和流程的真源；案例参数不自动变成新规定。

新问题和成功做法使用稳定编号追加，已有条目若发现局限，补充适用范围和证据。每期制作、返工和收到用户指导时都检查是否有值得更新的记录；没有新发现时不凑条目。不要只记录口号，也不要把尚未验证的建议写成成功经验。

## 用户明确的质量偏好

- “一定要去查阅一些核心的权威资料。”
- “制作动画的时候一定要通俗易懂，并且尽可能好看吧。”
- EP.16第一版被指出信息持续密集、主要变化是字幕；第二版通过逐步揭示、焦点移动和因果动作重做后，用户表示“这次就符合预期了”。详见教训L001至L004、成功经验S003至S005。
- EP.21 方案分章后，用户进一步要求新增独立的“什么是分布式事务”前置视频，现片作为深入讲解：先概念、再方案，循序渐进、层次分明。制作每集时还要根据指导适时积累经验，详见L009。
- 动画要引导观众知道看什么、发生了什么。静帧整齐、文字不溢出、渲染成功，不等于讲解效果合格。

## GitHub 自主发布授权

2026-10-24 用户在认可EP.17后明确说：“代码可以提交合并了，视频可以布置上线了。以后做好后就可以自己这样做了……要是有问题，我会跟你说的。大不了你再重新改，再上个线就行。”

据此，后续视频制作和质量检查完成后，可自主合并主干、发Release、部署GitHub Pages并核验线上文件，不再逐期要求观看确认或widget。收到反馈后修正、检查并重新上线。资料与动态表达要求继续，检查能力不足须如实记录。平台新发不包含在本次持续授权中。真源见[RULES的STATUS](RULES.md#status)。

同日用户补充：“以后制作完将对应的那个issue也进行关闭吧。”后续制作、合并上线及核验完成后，以`completed`关闭对应制作issue，作为发布收尾，不再另问。未执行的平台事项仍如实保留，不扩大平台发布授权。

## 已验证案例与当前状态

### EP.15 数据库索引

- 对应 [#66](https://github.com/linhongcun/video-studio/issues/66)，已按用户指令标记完成并关闭。
- [PR #112](https://github.com/linhongcun/video-studio/pull/112)已合并；[v0.45.1](https://github.com/linhongcun/video-studio/releases/tag/v0.45.1)只上站点，不重发平台。[部署运行40054122723](https://github.com/linhongcun/video-studio/actions/runs/40054122723)成功。
- [线上页面](https://linhongcun.github.io/video-studio/episodes/db-index/)的视频与用户批准版完整SHA一致，前缀为`1b903ab2`；海报、外挂字幕和更新日志也已核验。
- [制作工程](../episodes-codex/db-index/README.md)、[权威资料核验](../episodes-codex/db-index/research.md)、[媒体指标](../episodes-codex/db-index/render-result.json)已入库。

### EP.16 数据库事务

- 对应 [#67](https://github.com/linhongcun/video-studio/issues/67)。第一版SHA前缀`3085d678`；重做后的第二版`6aa379dd`，4066帧、约135.5秒。
- 用户已观看并认可第二版，随后明确批准合并主干并部署 GitHub；本次发布版本为[v0.45.2](https://github.com/linhongcun/video-studio/releases/tag/v0.45.2)，只上站点，不重发平台。
- [制作工程](../episodes-codex/db-transaction/README.md)、[连续动画检查](../episodes-codex/db-transaction/qa-motion-v2.md)、[媒体指标](../episodes-codex/db-transaction/render-result.json)与[发布记录](../episodes-codex/db-transaction/release.md)随本期入库；[站点页面](https://linhongcun.github.io/video-studio/episodes/db-transaction/)使用批准版的原样副本。
- EP.16当时按单期明确指令合并和部署；后续GitHub持续授权及完成后关闭制作issue的约定见上节。

### EP.17 数据库锁

- 用户明确要求选择并开始制作下一期，选定 [#69](https://github.com/linhongcun/video-studio/issues/69)，接上EP.16片尾的最后一件库存问题。
- [制作工程](../episodes-codex/db-lock/README.md)成片为14镜、28句、3457帧、约115.2秒；用户观看认可后批准[PR #119](https://github.com/linhongcun/video-studio/pull/119)合并，发布版本为[v0.45.3](https://github.com/linhongcun/video-studio/releases/tag/v0.45.3)。视频SHA前缀`93804b48`。
- [权威资料核验](../episodes-codex/db-lock/research.md)、[动态预检](../episodes-codex/db-lock/qa-motion.md)与[成片核验](../episodes-codex/db-lock/qa-final.md)及[发布记录](../episodes-codex/db-lock/release.md)随本期入库。重点是乙等待后加锁读取新库存0，再由程序判定缺货，不把行锁当成业务检查。
- [站点页面](https://linhongcun.github.io/video-studio/episodes/db-lock/)使用本期通过的同一份视频；平台历史投稿保留。#69 已按用户后续指令以`completed`关闭。

### EP.18–21 旧版重制批次

2026-10-24 接续EP.17，完成其余四期已上线旧版的重制，本站版本v0.45.4。按持续授权自主发布，制作检查通过不记为用户已经观看认可。四期保留同一示例逐步展示因果动作，复杂技术分支放在配套文章。

| 期 | 制作与检查入口 | 主要动画 | 实际帧数 | 视频SHA前缀 | 对应issue |
|---|---|---|---|---|---|
| EP.18 | [db-replication](../episodes-codex/db-replication/README.md) · [成片检查](../episodes-codex/db-replication/qa-final.md) | 昵称从主库提交，经接收再应用到从库 | 3560 | `f149b8ad` | [#70](https://github.com/linhongcun/video-studio/issues/70) |
| EP.19 | [db-sharding](../episodes-codex/db-sharding/README.md) · [成片检查](../episodes-codex/db-sharding/qa-final.md) | 提取用户键，再将订单路由到固定分片 | 3760 | `ff3d0ba1` | [#71](https://github.com/linhongcun/video-studio/issues/71) |
| EP.20 | [global-id](../episodes-codex/global-id/README.md) · [成片检查](../episodes-codex/global-id/qa-final.md) | 本地号码碰撞，再逐字段生成与核对完整ID | 4419 | `14bd428e` | [#72](https://github.com/linhongcun/video-studio/issues/72) |
| EP.21 | [distributed-tx](../episodes-codex/distributed-tx/README.md) · [成片检查](../episodes-codex/distributed-tx/qa-final.md) | 订单和待办共同落盘，重试送达，去重后扣库存 | 3791 | `4f01d09a` | [#73](https://github.com/linhongcun/video-studio/issues/73) |

- 官方MySQL、Vitess、Apache、AWS等正文及历史原始实现按主张记录在各期research中。Snowflake示例使用BigInt并验证字段计算；历史Twitter源码明确标为原理参考，不当成当前运维建议。
- 动态复核拦截并修复文字被路径穿过、提取值重复及查询结果交叉叠写；修订后重新冻结和完整编码。具体案例补入L003–L005。
- 站点复制完成检查的同一文件，使用实际最终帧数和字幕边界；GitHub上线核验通过后关闭四个对应制作issue。平台历史投稿保留。
- 官方ASR模型权重在当前网络下不可用，已保留选定takes、声学起音、信号与响度检查；未声称完成逐字ASR或全片人工听辨。

### EP.21 按用户反馈改为方案分章版

- 用户观看v0.45.4后指出只讲可靠消息不够全面、缺少章节条序，要求主流方案各自有清楚边界。本版为v0.45.5，38镜76句、11675帧、约389.2秒，视频SHA前缀`ef172944`，按GitHub持续授权检查后发布，不记为用户已观看认可。
- 章节依次为跨系统协作边界、2PC/XA、Seata AT、TCC、Saga、可靠消息、按业务约束选择。可靠消息分别演示Outbox与RocketMQ事务消息，不混淆待发表、半消息和消费端事务。
- [制作工程](../episodes-codex/distributed-tx/README.md)、[公开资料](../episodes-codex/distributed-tx/research.md)、[逐镜设计](../episodes-codex/distributed-tx/visual-direction.md)与[动态检查](../episodes-codex/distributed-tx/qa-motion.md)保留每种提交/补偿/隔离边界。音轨采用69b+6c+1d，不加速压缩内容；没有逐字ASR或全片人工听辨的结论。
- #73因本次返工重新打开；v0.45.5 新版上线并核验后已以 `completed` 关闭，平台历史投稿保持原样。具体问题和有效做法见L008、S009。

### EP.21 新增前置入门篇

- 用户要求新增《什么是分布式事务》，现有五类方案视频保留为深入讲解；新制作目录与站点 slug 为 `distributed-tx-intro`。
- 两片共用历史期号21，以“入门”“方案详解”区分，学习路径为EP.20 → 入门 → 方案详解；新片独立首发，不改现片冻结视频及制作快照。
- 重点是先理解同一业务目标、本地事务边界、部分成功、超时结果未知，再建立恢复与最终业务结果的要求；详细方案机制继续看原片。
- 新片20镜40句、5章、5155帧，约171.8秒；成片完整SHA为`933bbac04b7a9d656156edca4cc0d0c9218d856e6ec303063d93771993012fd5`。本次站点发布版本v0.46.0，对应[#123](https://github.com/linhongcun/video-studio/issues/123)。
- [制作工程](../episodes-codex/distributed-tx-intro/README.md)、[独立检查](../episodes-codex/distributed-tx-intro/qa-independent.md)与[成片报告](../episodes-codex/distributed-tx-intro/qa-final.md)已记录权威资料、156个最终预演采样点、六段无字幕序列、独立28张与主任务12张实际编码查看。166冻结输入编码后匹配，媒体−16.0LUFS；未执行逐字ASR/全片人工听辨。
- 教学顺序、双向入口、草稿隐藏与Release映射有实际检查。用户尚未观看新增片，不将制作/独立检查或上线写成用户认可。新指导及验证经验见L009、L010、S010；Release后部署及线上核验按发布流程收尾。

## 复用边界

- EP.21 在 v0.45.4 上线后，用户反馈只讲可靠消息缺少全面、有条序的梳理，要求列举主流分布式事务方案，且每种边界清楚。本次返工改为分章总览：2PC/XA、AT、TCC、Saga、可靠消息（Outbox/事务消息）；一章一个当前焦点，最后统一比较。不能用旧的“一条主线、2–3术语”限制抵消用户本次明确范围。详见L008。

- 14或16镜、具体时长、字号、滚动位移及坐标都是单期实现，不照搬成后续硬规则。
- 官方ASR模型下载在当时环境被拒绝，后续重新检查能力。既有句级音频边界和声学起音不能冒充逐字识别或完整人工听辨。
- 授权范围和系列状态以最新用户指令及RULES的STATUS判断；GitHub站点已有持续授权，平台新发仍未授权。
