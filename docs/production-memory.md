# 项目制作记忆

更新于2026-10-24（北京时间）。本文件保留用户偏好、案例状态与阅读入口；具体错误及有效做法分别积累到下面两份文件，避免多处复制后互相冲突。

## 开工阅读入口

1. [教训](lessons-learned.md)：发生过什么、下次如何避免、如何验证已修复。
2. [成功经验](successful-practices.md)：实际有效的做法、适用场景和证据。
3. [现行规范](RULES.md)与[制作流程](pipeline.md)：规范和流程的真源；案例参数不自动变成新规定。

新问题和成功做法使用稳定编号追加，已有条目若发现局限，补充适用范围和证据。每期制作、返工和收到用户指导时都检查是否有值得更新的记录；没有新发现时不凑条目。不要只记录口号，也不要把尚未验证的建议写成成功经验。

## 用户明确的质量偏好

- “一定要去查阅一些核心的权威资料。”
- 2026-10-24 用户强调：讨论当下流行、前沿技术及后续视频选题时，联网调研是重要环节。选题讨论阶段就应查阅近期一手资料，核对发布/更新日期并提供可核验链接；区分已核实事实、热度信号和选题判断，不把已有知识或项目资料当作当下趋势的联网证据。本次此前的 Agent 选题建议未联网，已向用户明确说明并开始补充调研。
- 同日用户要求根据权威、实际资料重新规划 Agent 开发系列，供后续制作参考。已联网核验官方规范、文档和工程总结，整理为 [16 期主线与 4 个深入方向](agent-development-topics.md)，含前置、拟演示、来源日期和适用边界；这是选题参考，尚无示例实测或成片结论。
- 同日用户认可全部选题，要求“先提 issue 到 GitHub 上，后面我会分批来做”。已创建[系列总览 #130](https://github.com/linhongcun/video-studio/issues/130)，以及 A01–A16（#131–#146）和 B01–B04（#147–#150）共 20 个选题 issue，均待排期；具体链接见选题文档。后续按用户安排分批启动制作，建单不表示已开工。
- 用户随后要求先选择一期制作视频查看效果，本次选定 A01 / [#131](https://github.com/linhongcun/video-studio/issues/131)，拟为 EP.22《AI 能回答问题，怎么才能真正帮你办事？》，制作与站点 slug 为 agent-intro；其余选题仍按后续批次安排。制作/发布检查不代表用户已经观看认可。
- “制作动画的时候一定要通俗易懂，并且尽可能好看吧。”
- EP.16第一版被指出信息持续密集、主要变化是字幕；第二版通过逐步揭示、焦点移动和因果动作重做后，用户表示“这次就符合预期了”。详见教训L001至L004、成功经验S003至S005。
- EP.21 方案分章后，用户进一步要求新增独立的“什么是分布式事务”前置视频，现片作为深入讲解：先概念、再方案，循序渐进、层次分明。制作每集时还要根据指导适时积累经验，详见L009。
- 用户观看EP.21约6分29秒方案合集后明确反馈：视频太长、内容太复杂、动画表达不清楚，每种实现讲得不够详细；现在要求常见实现一集一个，少见/框架特例不单独展开。缩短靠拆分范围，不靠加速。机器检查通过与用户观看结论分开记录，见L012。
- 用户观看EP.05 CDN的v0.48.0后要求增加地图，直观看到从临近边缘节点取数据，并在合适时机点出CDN等重要术语。讲解应让观众轻松理解，也能学到正式名称；先动作后命名，避免术语堆积。地图应说明示意性质，区分地理接近与实际网络调度。返工检查不预写为用户已认可，见L019和[本次记录](cdn-map-terms-revision.md)。
- 动画要引导观众知道看什么、发生了什么。静帧整齐、文字不溢出、渲染成功，不等于讲解效果合格。
- 用户观看LC.11 v0.49.0后明确指出，成片下方持续增长的装饰进度条会影响注意力，要求去掉并避免以后重犯。新视频不添加与讲解无关的持续动态进度条；保留播放器原生进度控件，参与讲解因果的状态动画仍按内容需要设计，见L018。
- 用户随后进一步要求，算法题解视频最后贴出本题完整Python程序，供感兴趣观众暂停查看，让思路与具体实现直接在视频内闭环，不必再回头查完整解法。正文继续渐进解释关键行，片尾独立静态完整代码卡按本条明确要求另计；代码须与讲解、文章和执行源一致，保留无装饰进度条的规范。这是用户明确指导，不是尚未完成的新卡片验证结论。
- 用户后续明确修正：供暂停查看的代码卡5秒加暂停提示即可，不应按完整阅读时长延长；同时要求小改动缩短处理时间。小修先划定影响范围，复用已验收的不变部分，优先可证实的无损剪短；必要修后和上线检查保留，不重复无关检查，见L020。

## GitHub 自主发布授权

2026-10-24 用户在认可EP.17后明确说：“代码可以提交合并了，视频可以布置上线了。以后做好后就可以自己这样做了……要是有问题，我会跟你说的。大不了你再重新改，再上个线就行。”

据此，后续视频制作和质量检查完成后，可自主合并主干、发Release、部署GitHub Pages并核验线上文件，不再逐期要求观看确认或widget。收到反馈后修正、检查并重新上线。资料与动态表达要求继续，检查能力不足须如实记录。平台新发不包含在本次持续授权中。真源见[RULES的STATUS](RULES.md#status)。

同日用户补充：“以后制作完将对应的那个issue也进行关闭吧。”后续制作、合并上线及核验完成后，以`completed`关闭对应制作issue，作为发布收尾，不再另问。未执行的平台事项仍如实保留，不扩大平台发布授权。

## 已验证案例与当前状态

### EP.22 Agent 概念入门

- 用户要求先选一期制作看效果，选定 A01 / [#131](https://github.com/linhongcun/video-studio/issues/131)《AI 能回答问题，怎么才能真正帮你办事？》，制作与站点 slug 为 agent-intro，新系列键 agent。
- [制作工程](../episodes-codex/agent-intro/README.md)为20镜40句、5章、5420帧，约180.7秒；通过同一合成退款咨询解释模型请求、程序执行、结果回传和动态选择，只查询并给申请建议，退款始终未执行。
- 实际媒体SHA-256为44b21f36f6b99b4106141548a6bbc70c7556a394e4f1e819949b0e2af9be9b9c，−16.0LUFS；171冻结输入、完整解码、73预演/74实际帧比对、18张独立实际成片图及干净构建已检查。未执行逐字ASR或全片人工听辨，详见[最终报告](../episodes-codex/agent-intro/qa-final.md)。
- 站点正式构建、40条VTT、5章精确跳转、桌面/手机布局和完整媒体SHA已有本地证据；[发布记录](../episodes-codex/agent-intro/release.md)、GitHub [v0.50.0](https://github.com/linhongcun/video-studio/releases/tag/v0.50.0)及制作issue保留最终发布与线上核验状态。用户尚未观看，不记为用户认可。

### EP.05 CDN 地图与术语返工

- 用户实际观看v0.48.0后要求加入地图及CDN等核心名称，本次按反馈返工。用同一公开图片演示临近边缘节点服务、未命中回源与命中短返，地图交代网络路径/时延调度的边界；09镜同时修正接收图片与等待文字的时序。
- 对应[#57](https://github.com/linhongcun/video-studio/issues/57)已为本次返工重开。本地制作、独立过程片、正式编码及35帧独立图审与网页检查已完成，线上发布结果按实际完成写入[返工记录](cdn-map-terms-revision.md)，不将用户对旧片的修改意见写成已认可新版。

### EP.01–14 新一轮 Codex 重制

- 2026-10-24 用户确认：将 EP.01–14 的上一轮 Cursor 重制版，全部按照今天 Codex 重制版的规格和经验进行 Codex 重制。
- 本轮覆盖 HTTP、HTTPS、DNS、登录状态、CDN、负载均衡、浏览器缓存、服务端缓存、缓存一致性、消息队列、限流、幂等、熔断和降级。未将 EP.18–21 或已下架的隔离级别加入本次范围。
- 制作目录为 `episodes-codex/<slug>/`，逐期执行资料、动态表达、配音时序、冻结、成片及线上核验；按既有持续授权发布 GitHub 站点。平台投稿不在本次范围。
- [批次记录](codex-remake-ep01-14.md)区分制作中、检查通过、接入站点和线上核验完成，不将旧轮次已关闭的 issue 当成本轮已完成。
- 本轮v0.48.0：160镜、320句新配音、45667帧，合计约25分22秒。各期本地完整解码、动态及独立实际帧复核完成；统一构建、浏览器与线上核验结果分别记录，不将已发布等同用户已观看认可。
- [v0.48.0](https://github.com/linhongcun/video-studio/releases/tag/v0.48.0)已由[媒体PR](https://github.com/linhongcun/video-studio/pull/151)合并并[部署](https://github.com/linhongcun/video-studio/actions/runs/40091595906)，2026-10-24 19:53:36（北京时间）线上14期视频/海报完整SHA、字幕逐字节、章节与源码入口、首页和更新日志核验通过；完整证据见[online.json](codex-remake-ep01-14/online.json)。各期release.md与来源SHA可追溯，平台投稿保留。

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

- 用户观看v0.45.4后指出只讲可靠消息不够全面、缺少章节条序，要求主流方案各自有清楚边界。本版为v0.45.5，38镜76句、11675帧、约389.2秒，视频SHA前缀`ef172944`，按GitHub持续授权检查后发布。用户随后已观看本版并明确指出时长、复杂度、动画清晰度与单方案深度不足，要求拆为常见实现独立短片；不能继续把“尚未观看”当作当前状态。
- 章节依次为跨系统协作边界、2PC/XA、Seata AT、TCC、Saga、可靠消息、按业务约束选择。可靠消息分别演示Outbox与RocketMQ事务消息，不混淆待发表、半消息和消费端事务。
- [制作工程](../episodes-codex/distributed-tx/README.md)、[公开资料](../episodes-codex/distributed-tx/research.md)、[逐镜设计](../episodes-codex/distributed-tx/visual-direction.md)与[动态检查](../episodes-codex/distributed-tx/qa-motion.md)保留每种提交/补偿/隔离边界。音轨采用69b+6c+1d，不加速压缩内容；没有逐字ASR或全片人工听辨的结论。
- #73因本次返工重新打开；v0.45.5 新版上线并核验后已以 `completed` 关闭，平台历史投稿保持原样。具体问题和有效做法见L008、S009。

### EP.21 新增前置入门篇

- 用户要求新增《什么是分布式事务》，现有五类方案视频保留为深入讲解；新制作目录与站点 slug 为 `distributed-tx-intro`。
- 两片共用历史期号21，以“入门”“方案详解”区分，学习路径为EP.20 → 入门 → 方案详解；新片独立首发，不改现片冻结视频及制作快照。
- 重点是先理解同一业务目标、本地事务边界、部分成功、超时结果未知，再建立恢复与最终业务结果的要求；详细方案机制继续看原片。
- 新片20镜40句、5章、5155帧，约171.8秒；成片完整SHA为`933bbac04b7a9d656156edca4cc0d0c9218d856e6ec303063d93771993012fd5`。本次站点发布版本v0.46.0，对应[#123](https://github.com/linhongcun/video-studio/issues/123)。
- [制作工程](../episodes-codex/distributed-tx-intro/README.md)、[独立检查](../episodes-codex/distributed-tx-intro/qa-independent.md)与[成片报告](../episodes-codex/distributed-tx-intro/qa-final.md)已记录权威资料、156个最终预演采样点、六段无字幕序列、独立28张与主任务12张实际编码查看。166冻结输入编码后匹配，媒体−16.0LUFS；未执行逐字ASR/全片人工听辨。
- [PR #124](https://github.com/linhongcun/video-studio/pull/124)已合并，v0.46.0主干/标签提交为`c1da2a1eef696d8bd08c9b078d7b833d75308498`；[Release后部署40080409097](https://github.com/linhongcun/video-studio/actions/runs/40080409097)成功。线上完整媒体933bbac0…、40句字幕、5章、海报、教学顺序、双向入口和更新日志核验后，#123已以`completed`关闭。
- 用户尚未明确观看认可新增入门片，不将制作/独立检查或上线写成用户认可。新指导及验证经验见L009、L010、S010；本次新四片的制作状态与此历史完成状态分开。

### EP.21 按观看反馈拆为单机制短片（当前方向）

- 保留`distributed-tx-intro`作为概念前置；依次制作`tx-2pc`（两阶段提交）、`tx-tcc`、`tx-saga`、`tx-outbox`（可靠消息，以Outbox展开），四片独立URL/媒体/章节，历史整数期号仍为21，用part及lessonOrder区分。
- 本批制作目标每集约90–150秒，不是全局绝对上限。每片一机制、一成功过程、一关键失败收尾和清楚边界；AT等具体框架模式先放文章拓展，不声称市场份额或冷门结论。
- 旧`distributed-tx`归档，原URL/媒体/字幕仍可回看，页面解释已经拆片并引向独立课程；从首页、系列、相关推荐和搜索中移出，不再作为当前学习路径终点。旧输入与成片保持可追溯。
- 对应制作issue依次为[#125](https://github.com/linhongcun/video-studio/issues/125)、[#126](https://github.com/linhongcun/video-studio/issues/126)、[#127](https://github.com/linhongcun/video-studio/issues/127)、[#128](https://github.com/linhongcun/video-studio/issues/128)。本条是用户最新指导与当前制作安排；逐片质量、上线与用户观看结论后续按实际证据补齐，不提前写为成功。具体教训见L012，S009/S010已注明旧检查结论的适用限制。

### EP.21 常见实现独立短片（v0.47.0）

- 用户已实际观看原约6分29秒合集，并指出太长、内容复杂/动画不清、每种讲得不够详细；最新要求以常见实现各自独立短片取代单个深入合集。概念前置保留，AT等框架扩展不列首批，不据此断言市场冷门。
- 本批四片均为14镜28句，不变速。制作目录与站点slug一致，制作入口在episodes-codex；旧合集保留原URL/媒体/194冻结输入，退出推荐和搜索。入门保留原媒体/166输入，站点文章改接四片路径。

| 独立片 | 真实画面秒数 | 帧数 | 成片SHA前缀 | 制作issue |
|---|---:|---:|---|---|
| [2PC](../episodes-codex/tx-2pc/README.md) | 113.267 | 3398 | `f6980821` | [#125](https://github.com/linhongcun/video-studio/issues/125) |
| [TCC](../episodes-codex/tx-tcc/README.md) | 120.600 | 3618 | `170a4fcc` | [#126](https://github.com/linhongcun/video-studio/issues/126) |
| [Saga](../episodes-codex/tx-saga/README.md) | 115.933 | 3478 | `9cc5b7a5` | [#127](https://github.com/linhongcun/video-studio/issues/127) |
| [可靠消息](../episodes-codex/tx-outbox/README.md) | 116.633 | 3499 | `e9353f98` | [#128](https://github.com/linhongcun/video-studio/issues/128) |

- 四片分别冻结131/129/131/131项输入；真实媒体H.264/1080p/30fps、−16LUFS，完整解码通过。独立80张/主任务37张编码查看及438点预演保真闭合；无逐字ASR、句内词级对齐或全片人工听辨结论。
- 公开资料、过程边界和实际查看范围见[批次独立审查](transaction-split-editorial-review.md)，干净构建证据见[报告](transaction-split-clean-build.json)。L012/S011记录拆题，L013记录计数歧义，L014记录独立临时盘耗尽与完整重新编码，不将机器成功当成用户认可。
- 发布版本v0.47.0，GitHub合并/Release/部署及线上核验按持续授权执行；四个制作issue在线上核验后completed关闭，最终状态见Release与issue。用户尚未观看四片，平台新发未授权。

## LeetCode 首期：LC.11 盛最多水的容器

- 2026-10-24，用户从本仓12条LeetCode选题中采纳[#78](https://github.com/linhongcun/video-studio/issues/78)，明确授权开始制作《盛最多水的容器：为什么每次都移动短边？》，完成后合并项目并发布网站。未授权外部平台投稿。
- 制作目录`episodes-codex/container-most-water/`，站点`episodes/container-most-water/`。独立算法系列展示LC.11，内部ep22仅用于排序/Release，不将网络或事务课程当作先修。
- v0.49.0初版为22镜44句、4章、6544帧，约3分38秒，冰糖原速。用同一输入`[2,3,10,5,7,8,9]`解释面积、固定短边的整组排除与正式扫描，保留36而非最后面积5。初版完整视频SHA为`624c2fa8dec7c8f96caad8b25d5890ae83c1854f4c16443617b32685002f18e0`。
- 初版真实时序/声学起音、186项冻结输入、全解码、114个预演记录与114个实际MP4帧的保真、独立目视和干净依赖首帧复现已按实际范围记录。未执行逐字ASR或全片人工听辨；这些是发布前检查，与后续用户观看结论分开保留。
- 本期发现QA传参不能保证实际隐藏字幕，修正后重出并查看真无字幕过程，见L016；安全排除的算法叙事做法与独立证据见S012。已由[PR #154](https://github.com/linhongcun/video-studio/pull/154)合并并发布v0.49.0，Release后部署40093925916成功；线上视频/海报完整SHA、44句VTT、四章、独立系列/RSS和更新日志实际GET通过，#78已以completed关闭。完整证据见[发布记录](../episodes-codex/container-most-water/release.md)与online-verification.json，平台未投稿。
- 同日用户已实际观看初版，明确表示“这个视频做得真不错”，认可主体讲解；唯一修改意见是去掉成片内底部装饰进度条，以免分散注意力，并要求更新教训。新版仅删除两个SVG矩形，主体预演像素、解码音频及全部时序保持；全6544帧底带扫描、独立正式成片与390/1440网页原生进度控件/章节/字幕复验通过。v0.50.1已由PR #157合并并经Release后部署40097496603上线，实际GET核验新版视频6d1e3b4c…8adb、海报、44句VTT、四章及更新日志通过，不预写为用户已观看认可新版。对应教训L018，S012已补认可范围，证据见本期qa-progress-removal-*。
- 用户进一步要求片尾展示完整Python解法并更新经验。本轮在原6544帧之后追加450帧、15秒静态代码卡，供暂停阅读；保留前面讲解与配音，旧字幕在6543结束，不新增口播。本期停留参数不作为全系列固定要求。16行程序与文章/显示源逐字相同，独立8代表用例执行通过；真实预演3个原段同帧PNG与旧版字节相同，代码卡首/中/末3帧相同，独立查看字号/缩进/最长行/返回值可读。原44句及人声PCM前缀保持，卡区人声全零；190输入冻结核对、6994帧正式编码、完整解码及−16.0LUFS/−3.7dBTP通过；独立实际查看硬切和最终return，全部450卡帧稳定且return可见；网站73页构建、旧课程/Agent回归、390/1440的3:53时长/四章/原生控件/44句VTT及片尾零cue/暂停阅读复验通过，v0.50.2已由PR #159合并，Release后部署40100807342成功；线上完整视频SHA为072ae1db…535b，海报/44句VTT/四章/系列/RSS/更新日志实际GET通过，证据见本期release.md和online-verification.json。S013记录用户指导和独立预演支持，不将此写成用户已观看认可新卡片或已测量学习收益。

- 用户随后要求把15秒代码卡缩为5秒，并质疑小改动耗时。本轮按5秒静态卡加暂停提示修正，原完整程序与正文继续保留；已复用旧编码画面快速转码，6694帧/连续PTS/末return/人声前缀/190输入及1440单页3:43时长和字幕检查通过，发布结果待线上补齐，不声称用户已观看认可新版。v0.50.2的15秒技术证据属于历史，当前方向见L020及S013后续修正。

## 复用边界

- EP.21的范围按最新用户反馈推进：先前从可靠消息改为分章合集解决覆盖要求，后续观看又暴露长片密度与深度问题，现改为常见实现独立短片。历史取舍与检查记录不删除，但不能把旧的总览方向当作当前授权目标。详见L008、L009、L012。

- 14或16镜、具体时长、字号、滚动位移及坐标都是单期实现，不照搬成后续硬规则。
- 官方ASR模型下载在当时环境被拒绝，后续重新检查能力。既有句级音频边界和声学起音不能冒充逐字识别或完整人工听辨。
- 授权范围和系列状态以最新用户指令及RULES的STATUS判断；GitHub站点已有持续授权，平台新发仍未授权。
