# 项目制作记忆

## EP.01技术深度返工（2026-10-25，#283）

用户实际观看现版HTTP请求全流程后认为过于简单，明确希望增加TCP三次握手等常见技术细节。本轮保留同一商品页，将“建连接”展开为三报文、初始序号与确认、为什么需要第三次，再区分TCP/TLS/HTTP并显示HTTP/1.1请求响应字段；缓存、复用、HTTP/3与渐进渲染保持准确边界。当前用户要求优先于旧2–3术语限制，术语逐步绑定对象与动作，不把更多标签当作深度。开工已同步最新40adfbf4，保留修前文稿和QA历史，制作/检查/上线及用户新观看结论按阶段补充。见[基线](../episodes-codex/http-request/revisions/technical-depth-v2/startup.json)与L040。

本轮17镜34句、5406帧/180.2秒，114项冻结、14句首cue、独立真实动态/31成片时点和双视口网站检查通过；在保留v0.68.0日期功能及最新EP20之后，按v0.68.2由PR #288合并f1fe833c，Release后部署40190399664成功。北京时间19:53:15首轮9次完整HTTPS核验通过，视频完整SHA593c528d…34a1c6、34字幕/七章/海报/日期版与本Release条目一致，#283已completed关闭。详见[发布记录](../episodes-codex/http-request/release.md)及[线上证据](http-request-depth/online-verification.json)。新版尚无用户观看反馈，平台未新发，不将旧版技术检查或本轮发布当作教学深度已获认可。

更新于2026-10-25（北京时间）。本文件保留用户偏好、案例状态与阅读入口；具体错误及有效做法分别积累到下面两份文件，避免多处复制后互相冲突。

## 开工阅读入口

1. [教训](lessons-learned.md)：发生过什么、下次如何避免、如何验证已修复。
2. [成功经验](successful-practices.md)：实际有效的做法、适用场景和证据。
3. [现行规范](RULES.md)与[制作流程](pipeline.md)：规范和流程的真源；案例参数不自动变成新规定。

新问题和成功做法使用稳定编号追加，已有条目若发现局限，补充适用范围和证据。每期制作、返工和收到用户指导时都检查是否有值得更新的记录；没有新发现时不凑条目。不要只记录口号，也不要把尚未验证的建议写成成功经验。

## 用户明确的质量偏好

- **EP.20顺序与算法取舍反馈（2026-10-25）：**用户实际观看上一轮后指出，先说“雪花只是一种”突兀，要求UUID→Redis自增→雪花逐项讲、前两项简要但讲出实际优缺点。补随机UUIDv4不递增对MySQL InnoDB主键随机插入的影响，以及Redis异步复制下主从切换回退、重复发号与跳号条件。当前替换补充段为3句UUID/索引+5句Redis/切换/可靠号段/过渡，共1227帧40.9秒；全片5646帧188.2秒，原15镜30句复用。号段跳号用事先可靠预留1001—1200、隔离停发旧主后从1201继续作条件示意，不写成任意固定加N或Redis默认保证；UUIDv7边界放文章。用户反馈、资料与实际检查见[本期记录](../episodes-codex/global-id/README.md)及L008，尚无本轮修后观看结论。

- **EP.20方案定位补充（2026-10-25）：**用户指出只讲雪花容易让观众把分布式ID等同于雪花，要求先交代多种实现，再简单提UUID和Redis自增。本轮在原雪花讲解前加入两镜5句24.7秒，随机UUID说明本地生成及低碰撞，Redis说明同一计数器原子递增与防止故障恢复回退，最后聚焦经典方案之一的雪花。原15镜局部数据与30句人声PCM复用，当前全片5160帧172秒；当时定向预检与发布检查通过；用户随后观看的叙事与取舍反馈已由上方最新条目取代“尚未观看”状态。历史结果以[本期记录](../episodes-codex/global-id/README.md)及对应QA为准。经验补入L008，稳定标题、slug、创建/首发时间继续保留。

- **视频持续打磨与时间版本（2026-10-25）：**用户强调每期视频应有创建时间和修改时间，后续持续完善同一期，以某个时间的版本区分，类似 MacBook Pro 按年份区分；不希望不断累加“重制版”名字。落实口径为稳定期次、标题和链接，`createdAt` 固定、实质内容修改更新 `updatedAt`，对外显示北京时间版本日期；站点发布版本与历史证据继续保留。字段与发布步骤见 [RULES](RULES.md#发布) 和 [publish](publish.md#视频时间与版本)。这是用户指导与维护口径，不预记实现完成或显示效果已获认可。

- **EP.20主题命名（2026-10-25）：**用户认为“全局ID”命名不佳，明确偏好“分布式ID”。本轮从最新`40adfbf4f6a266a8b2a189e89dc5496146f0b199`整合，网站标题改为《分布式 ID：两个订单，怎么撞成同一个号了？》，同步标签、系列介绍及两份文章；文章区分分布式ID主题与全局唯一性要求。保留`global-id`地址、旧标签跳转及旧筛选参数兼容。网站构建、生成页面与实际筛选脚本检查通过，字幕与线上原版字节相同；视频和封面未改。本轮为站点命名小修，不代表用户已认可新版观看效果，不扩展为外平台重发或通用命名规则。

- **LC.200边界反馈修订（2026-10-25）：**用户实际观看v0.66.0后指出第一行第一列为何不向左/上未解释，可能误认为搜索只向右下；要求简单处也提一嘴。原程序和trace已做bounds检查，缺口在表达，原技术通过不抹去本次反馈。本轮仅新录06第二句，明确四向及越界直接跳过；06新增两次边框落点，27原take及其他13镜局部时序/程序/trace/封面保持，只增加62帧约2.07秒。修前v66媒体、脚本与QA已保存，修后定向预检/成片及一次网站构建/两视口检查通过，已由PR #282合并40adfbf4并发布附注tag/Release v0.67.1；Release后Pages40187760204成功，10次完整HTTPS线上核验通过，原#82保持completed。实际状态见[本轮记录](number-of-islands-boundaries/README.md)；尚无修后用户观看结论。经验L045，范围收敛延续L020。

- **LC.200新片制作（2026-10-25）：**用户在认可LC.70真实楼梯后要求自选下一道有把握的题。本次从最新主干选既有[#82](https://github.com/linhongcun/video-studio/issues/82)《岛屿数量：怎样保证一座岛只数一次？》，内部EP34、slug number-of-islands；以同一海陆地图先讲题意，再推导整岛归属、保留分支、DFS与迭代栈。14镜28句4章、5783帧约3分13秒，末150帧完整26行Python卡供暂停。独立并查集65,852例、实计时120动态点、实际MP4独立40点及94比较、全部PTS/150卡/声音/封面均通过；发布前另发现并局部修正原生字幕在精确首卡暂停仍残留末句的毫秒取整，视频SHA4c2389be…bb44d保持。开工与编码/网站前持续同步并保留最新中间件、Skills、适配器和P05草稿，实际首发v0.66.0，PR #277合并2da29e20，附注tag/Release后Pages40179672105成功；线上39次完整HTTPS核验通过，#82已completed关闭。实际结果、首轮检查误判与能力范围见[交付记录](number-of-islands/README.md)，尚无新片用户观看认可。经验见L010/L020/L041/S004。

- 2026-10-25用户在撤下两期旧Agent视频后，授权自选最有把握的一期努力做好。本次选择[Agent Skills / #139](https://github.com/linhongcun/video-studio/issues/139)，制作与站点slug为agent-skills、内部EP.31。以团队API兼容审查贯穿，讲发现/渐进加载、参考资料读取与脚本工具执行双路径、索引开销和宿主保留边界；不把基础接线撑成一期，也不伪造无Skill失败/有Skill成功对照。12镜24句4章、5648帧约3分8秒，正常配音；原定EP30遇主干并行使用，先停止编码、仅同步身份后以同一声音/句界/画面重新冻结。新成片制作侧与独立实际MP4复核已通过，本地站点验证通过，已通过PR #263按v0.62.0合并发布，Release后部署40157863039成功；20个普通canonical GET完整媒体/字幕/章节/入口与更新日志核验通过，原两期旧页和视频仍404，尚无用户观看结论。完整依据、预检修订和能力范围见[本期记录](../episodes-codex/agent-skills/README.md)。

- **LC.70楼梯场景修后认可（v0.61.1）：**2026-10-25，用户实际观看v0.61.1后表示“这次看着就对味了”，认可楼梯“生动形象”，并表示前两阶走法数相加的关系“看得清清楚楚”。这支持本片用原题楼梯、实际脚步和对应位置的计数呈现推导；记录为对场景表达与递推关系清晰度的定性认可，不扩写为完整Python卡、全部数学细节、其他题目均被认可或量化学习效果。后续类似题目优先让已有场景的对象、动作和结果参与推导，按题目设计，不机械照搬楼梯画面。见S004、L041及[本轮记录](climbing-stairs-scene/README.md)。

- 2026-10-25用户观看LC.70爬楼梯后明确指出，原题自带楼梯场景，视频却用数字节点代替真实走法，缺少生动形象的空间与动作，要求必须修改并更新经验教训。楼梯是题目本体，应演出人物上一阶/两阶、三种顺序和最后一步来源，再绑定方法数与滚动变量；旧“不画人物/拟真楼梯”约束撤回。此前保留LC.70只说明推导链已完整，不代表场景得到认可。本轮保留原24句/4779帧和5秒Python卡重做视觉，独立动态、正式成片、媒体、三尺寸封面和一次网站构建/两视口检查均通过，已由PR #260合并3da47c21并发布附注tag/Release v0.61.1，Release后手动部署40156242220成功；28次实际HTTPS核验首次通过，完整媒体/字幕/章节及本轮更新日志身份一致，见L041及[本轮记录](climbing-stairs-scene/README.md)。

- 2026-10-25用户进一步明确“之前的那两期视频可以删除”，评价两期制作效果不佳。A01/EP.22（agent-intro）与A02/EP.28（agent-tool-execution）的发布内容、媒体和相关制作工程在本轮移除；前一轮保留旧媒体的编辑决定被此最新指令取代。#131的completed仅保留历史制作完成事实，不能继续视为在线课程；#132维持not_planned，不再重制。当前11项Skills/MCP/Subagent/Goal等研究候选不变，无新视频制作。已通过[PR #252](https://github.com/linhongcun/video-studio/pull/252)按v0.60.3合并发布，Release后部署40152148732成功；18个普通canonical GET核验通过，8个旧页面/媒体/字幕地址均404，保留课程代表媒体完整SHA及新更新日志正常。具体范围与实际证据见[撤下记录](agent-video-retirement.md)。历史工程与QA链接固定到删除前Git提交。

- 2026-10-25用户进一步明确Agent系列方向：围绕Skills、MCP、Subagent、Goal等热门AI名词解释机制、设计原因、区别与取舍，认为基础接线、入门编码流程缺少观看价值；授权关闭过于简单、缺少深度的旧issue。Goal已确认指“目标驱动的Agent”。此前六个API/工单实战单元为未实施草案，现撤回；不要继续把可运行产物或关键接线作为所有概念片的硬性要求。已关闭9项`not_planned`（#132、#133、#134、#136、#141、#143、#145、#148、#150），重构原10项，并新建[Goal #248](https://github.com/linhongcun/video-studio/issues/248)。当前11项开放研究池优先研究[Skills #139](https://github.com/linhongcun/video-studio/issues/139)、[MCP #138](https://github.com/linhongcun/video-studio/issues/138)、[Subagent #146](https://github.com/linhongcun/video-studio/issues/146)、Goal #248；Harness #149、Context Engineering #135后续，其余5项储备。具体处置见[系列总览 #130](https://github.com/linhongcun/video-studio/issues/130)与[最新策划记录](agent-development-value-review.md)。研究优先级不是用户逐项批准片名、开拍或教学效果已验证；该轮未做新视频，A02独立重制计划终止；当时保留旧媒体的决定已被上述最新删除指令取代，见L040。
- 2026-10-25用户实际观看Agent A02/v0.59.0后，明确认为“看完好像跟没看一样”“没什么营养”，质疑策划并要求更有价值、信息密度更高、更贴实际开发。这取代A02此前“尚未观看”的状态。旧流程、媒体与上线检查作为Git历史证据，不能作为独立课程价值或用户认可；当时先做策划复盘、暂停沿原20项顺序逐个开拍，未重渲或做真实模型新实验。该反馈及随后方向调整统一记录于[最新策划记录](agent-development-value-review.md)与L040。
- 2026-10-25的A02开工历史：用户要求先拉取最新代码，再继续下一期Agent内容，当时选A02/#132《AI说要调用工具，到底是谁在执行？》，EP.28、slug agent-tool-execution。已同步1834450d/v0.57.0后创建制作输入，编码前再同步e38fa923文档收尾；工程、检查及上线状态见[本期记录](https://github.com/linhongcun/video-studio/blob/321e8e8c1b4ad34a6ea09eed2bb5cf369d9ab6dd/episodes-codex/agent-tool-execution/README.md)和#132。使用退款咨询UI建立查询场景，核心是请求/应用执行/返回的分工；当时其余18项待安排，现按上方最新方向处置。
- 2026-10-25用户已观看LC.1 v0.57.0，指出介绍题意后直接给出现成解法，没有分析从哪里入手、为何决定这样做，要求LeetCode同类一并修订。六片独立审读后修订LC.1/3/11/206/704，保留已有完整末步分类推导的LC.70；五片新增推导在方法命名前，实际动态、正式MP4和统一网站检查通过；PR #246合并8bef491d，附注tag/Release v0.60.1后部署40150838653成功，35次完整HTTPS核验通过，172句字幕/20章及五片完整媒体SHA均一致。见L039和[本轮记录](leetcode-derivation-20261025/README.md)。不能把本批技术验收或此前赞许扩大为新版教学已被用户认可。
- 2026-10-25用户认可LC.704“这个视频也做得很不错”，并授权自选数道有信心的LeetCode批量制作，以共享准备与发布提高效率；本批选择LC.1两数之和/#75、LC.206反转链表/#77、LC.70爬楼梯/#81。三片已按v0.57.0合并上线，Release后部署40144462891及17次完整HTTPS核验通过，#75/#77/#81已completed关闭；具体证据见[批次记录](leetcode-batch-20261025/README.md)，用户随后观看LC.1并反馈缺少方法选择推导，后续修订按本节最新记录执行。
- 同次用户明确要求开工前拉取最新代码，检查重构、删除和开发冲突，并更新经验。已从2622e542/v0.56.3创建新制作分支，重新读清理记录、审计依赖并在当前工程干净安装；具体入口纳入AGENTS/pipeline/template，案例L032和[批次记录](leetcode-batch-20261025/README.md)。
- “一定要去查阅一些核心的权威资料。”
- 2026-10-24 用户强调：讨论当下流行、前沿技术及后续视频选题时，联网调研是重要环节。选题讨论阶段就应查阅近期一手资料，核对发布/更新日期并提供可核验链接；区分已核实事实、热度信号和选题判断，不把已有知识或项目资料当作当下趋势的联网证据。本次此前的 Agent 选题建议未联网，已向用户明确说明并开始补充调研。
- 同日用户要求根据权威、实际资料重新规划 Agent 开发系列，供后续制作参考。当时联网核验官方规范、文档和工程总结，整理为16期主线与4个深入方向；原始前置、拟演示、来源和适用边界保留在[选题记录](agent-development-topics.md)。原入门顺序现已撤回，历史资料不代表示例实测或成片效果结论。
- 同日用户认可当时全部选题，要求“先提 issue 到 GitHub 上，后面我会分批来做”。当时创建[系列总览 #130](https://github.com/linhongcun/video-studio/issues/130)，以及A01–A16（#131–#146）和B01–B04（#147–#150）共20个待排期issue。此为建单历史，当前状态以上方最新处置和GitHub为准，不再按20项全部待做理解。
- 用户随后要求先选择一期制作视频查看效果，当时选定A01 / [#131](https://github.com/linhongcun/video-studio/issues/131)，原题为EP.22《AI能回答问题，怎么才能真正帮你办事？》，制作与站点slug为agent-intro。A01后续重制与完成历史在Git中保留；当前已按最新指令撤下，制作/发布检查不代表用户已经观看认可。
- “制作动画的时候一定要通俗易懂，并且尽可能好看吧。”
- EP.16第一版被指出信息持续密集、主要变化是字幕；第二版通过逐步揭示、焦点移动和因果动作重做后，用户表示“这次就符合预期了”。详见教训L001至L004、成功经验S003至S005。
- EP.21 方案分章后，用户进一步要求新增独立的“什么是分布式事务”前置视频，现片作为深入讲解：先概念、再方案，循序渐进、层次分明。制作每集时还要根据指导适时积累经验，详见L009。
- 用户观看EP.21约6分29秒方案合集后明确反馈：视频太长、内容太复杂、动画表达不清楚，每种实现讲得不够详细；现在要求常见实现一集一个，少见/框架特例不单独展开。缩短靠拆分范围，不靠加速。机器检查通过与用户观看结论分开记录，见L012。
- 用户观看EP.05 CDN的v0.48.0后要求增加地图，直观看到从临近边缘节点取数据，并在合适时机点出CDN等重要术语。讲解应让观众轻松理解，也能学到正式名称；先动作后命名，避免术语堆积。地图应说明示意性质，区分地理接近与实际网络调度。返工检查不预写为用户已认可，见L019和[本次记录](cdn-map-terms-revision.md)。
- 动画要引导观众知道看什么、发生了什么。静帧整齐、文字不溢出、渲染成功，不等于讲解效果合格。
- 用户观看LC.11 v0.49.0后明确指出，成片下方持续增长的装饰进度条会影响注意力，要求去掉并避免以后重犯。新视频不添加与讲解无关的持续动态进度条；保留播放器原生进度控件，参与讲解因果的状态动画仍按内容需要设计，见L018。
- 用户随后进一步要求，算法题解视频最后贴出本题完整Python程序，供感兴趣观众暂停查看，让思路与具体实现直接在视频内闭环，不必再回头查完整解法。正文继续渐进解释关键行，片尾独立静态完整代码卡按本条明确要求另计；代码须与讲解、文章和执行源一致，保留无装饰进度条的规范。这是用户明确指导，不是尚未完成的新卡片验证结论。
- 用户后续明确修正：供暂停查看的代码卡5秒加暂停提示即可，不应按完整阅读时长延长；同时要求小改动缩短处理时间。小修先划定影响范围，复用已验收的不变部分，优先可证实的无损剪短；必要修后和上线检查保留，不重复无关检查，见L020。
- 用户进一步指出：已制作LeetCode视频共同默认观众知道题目，开头直接讲解法。算法视频要先介绍题目，再解释解法；默认观众没见过原题，用可视小例子交代输入、允许做什么、关键限制、目标和返回值。题号、标题、算法内部悬念以及文章题意不能代替视频题意，见L026。本轮修复已上线LC.11和LC.3，保留5秒完整代码卡及无装饰进度线；两片题意复述、实际MP4接点与末卡、新学习站字幕/四章检查已通过；v0.54.2由PR #201合并并部署40109143808成功，两片实际完整媒体/字幕/章节及Release条目GET通过，见docs/leetcode-problem-first/online-verification.json。2026-10-25用户回应“很好”并要求继续下一题，记录为本次修订的定性认可，不扩大为学习效果测量。

- 2026-10-24 用户认可设计模式方向，要求每种模式一个issue、一个独立视频，围绕为什么需要、具体解决什么、什么时候值得用展开；正式制作充分阅读权威资料，图文通俗解释，按内容调整而非统一套镜头和时长。选题池为[23种模式总览 #161](https://github.com/linhongcun/video-studio/issues/161)。用户随后授权先选一期完成并部署网站，本次选择D01策略模式/#163。

- 2026-10-24 用户实际观看策略模式D01 v0.52.0，认为整体问题不大，但明确要求每个主要章节有简短口头衔接，先说明下一部分要讲什么，帮助思绪跳转；仅换标题或直接讲新内容会让听众以为仍在上一模块。此要求纳入RULES和pipeline，按具体内容调整说法，不机械统一。
- 用户随后观看章节衔接修订版，指出模式仍没讲清楚、内容复杂，提供Refactoring.Guru布局作为参考。上一轮据此补了函数传参，但用户观看v0.54.4后进一步指出偏语法；这条历史取舍已由最新要求纠正，见L027/L030。
- 2026-10-25用户明确：设计模式要强调不绑定语言的思想。先讲变化怎样隔离、职责怎样分工、共同约定、选择与委托、替换维护边界和成本；函数、参数、类等只作具体实现，不能当模式定义或前置学习目标。视频按此修复并更新经验教训，语言实现后置可选图文。

- **设计模式先前观看反馈（2026-10-25）：**D02上线后，用户认为当前案例不如自己头条文章贴近日常产品，要求先给产品交互画面建立场景，再讲结构图各节点职责，并附简短代码供暂停。用户提出会员购买选择不同支付方式作为策略案例，偏好本系列以Java展示。已核对：该场景可按共同支付契约/可替换实现/结算委托来建模，但UI选项不证明网易云真实内部架构；Java有利于显式表达接口与持有关系，模式仍不绑定语言。当前只完成核对和规范记录，待验证的讲解方案见[复盘](design-pattern-product-scene-java.md)及L037；不把方案写成已重制、上线或被用户观看认可。两篇链接本次公共访问均显示内容不存在，未读到正文，未据此判定文章已删除。

- **设计模式当前执行范围（2026-10-25）：**用户随后决定不换之前的例子，担心为了模式强行换场景，只授权调整流程。本轮保留D01的100元两种定价、D02的订单17/摘要/记录，分别替换5句开场与结构旁白，补对应功能UI、逐角色职责映射和短Java卡；其余17/19句复用。已先同步最新e2a0add，随后整合5d79afd；原候选本地媒体与网站验收通过；PR #253合并后保留并行Agent撤下变更，网站按v0.60.4实际重建及36片/4方向、两片四浏览器用例验收通过，现已上线；Release后部署40152819279成功，2026-10-25T10:04:31.360708+08:00首轮13项canonical GET核对完整媒体/字幕/章节通过，#163/#164已completed关闭、#161同步，见[记录](pattern-flow-ui-java/README.md)。上一轮支付与购物车备选仅保留为历史，不代表本轮会换案例。


- **设计模式最新观看反馈（v0.60.4上线后，2026-10-25）：**用户表示“这次有这么一个背景铺垫，看这视频就好多了。”记录为本轮背景铺垫改善观看清晰度的正向反馈；后续在适合的内容中先交代功能、操作与目标，再讲结构和机制，沿用原例并按内容调整。用户没有逐片指定，不推断D01/D02均完整观看，不扩大为Java卡、全部细节或量化学习效果已经认可。已补入S017和L037。


- **两期明确认可与下一期（2026-10-25）：**用户随后明确表示“现在这两期设计模式看着好多了”，授权自选最有把握的下一模式制作。这补充了此前未逐片指定的观看范围，记为对D01/D02当前表达的定性认可，不扩大为学习效果测量。本次先从干净main同步ff730833，再选既有D03适配器/#165，slug adapter-pattern、EP31；通过商家发送发货提醒讲业务通知约定、适配器与外部服务的协作，保持已受理不等于已送达。本期12镜24句、5271帧/175.7秒，166项冻结输入、Java12组行为、独立真实动态/正式MP4与音轨一致性均通过；已整合LC70及Skills新主干，保留Skills的v0.62.0；D03旧未发布候选的24份站点文件按906cbad1归档，仅将本期首发候选顺延为v0.63.0。当时39个发布页、5个学习方向重建通过，1440/390双视口8次章节跳转、24句字幕、Java卡/正文入口、两张原生SVG和设计模式三期导航均通过本地验收；166项冻结输入与原媒体保持，不重做配音或编码。现已由[PR #264](https://github.com/linhongcun/video-studio/pull/264)合并ab49ce850a11a77695173cff5444aebdcdf68ec1，附注tag及[Release v0.63.0](https://github.com/linhongcun/video-studio/releases/tag/v0.63.0)发布后，[Pages 40158697480](https://github.com/linhongcun/video-studio/actions/runs/40158697480)成功。北京时间2026-10-25 11:38:39.015827，整套11项canonical普通GET通过，完整视频SHA25bf61a8521517af488b45cf13b66b27d94b4fd963738ca14b19c3176d4a8fe7/9,539,380字节、海报、24字幕/4章、Java/源码、三期导航、系列/资料库/RSS及真实Release条目均核验一致。首次线上脚本因首页Agent入口断言误写为series/agent/而中止，首次失败摘要保留；仅修QA工具后完整重跑通过，站点和媒体未改。首发核验后#165曾completed关闭，#161同步3项完成/20项待安排；用户随后已实际观看D03/v0.63.0并给出负面与纠正性反馈，见下方最新方向及L042；上述技术检查保留其实际范围，不能据此认定本片教学主线已讲清或获得认可。实际范围见[首发QA基线](../episodes-codex/adapter-pattern/revisions/business-boundary-v2/baseline/qa-final.md)、[首发网站检查](https://github.com/linhongcun/video-studio/blob/v0.63.0/episodes-codex/adapter-pattern/qa-site-browser.json)、[首发线上基线](../episodes-codex/adapter-pattern/revisions/business-boundary-v2/baseline/qa-site-online.json)、[首次检查记录](../episodes-codex/adapter-pattern/qa-site-online-attempt-1.json)、[版本处理](../episodes-codex/adapter-pattern/site-version-collision.json)和[开工记录](../episodes-codex/adapter-pattern/startup.json)。


- **D03最新观看反馈（2026-10-25）：**用户已观看适配器模式v0.63.0，认为讲解复杂，容易让人把它理解为接口不兼容时不得已加一层包装；要求讲清日常主动封装的两个收益：让外部能力符合业务约定，以及隔离外部接口升级对业务的影响。这是对D03主线的负面与纠正性反馈，取代此前“尚无观看反馈”的状态；D01/D02此前的认可不延伸为D03已获认可。旧稿、旧配音与实际技术验收历史保留，见[修前基线](../episodes-codex/adapter-pattern/revisions/business-boundary-v2/baseline/baseline-manifest.json)和L042。
- **D03主动业务边界修订（v0.64.1）：**本轮从干净main同步`5a5594fb`，保留订单17发货提醒，把“按业务定义通知约定、隔离外部接口升级”两项收益前置，再讲四角色、同一次请求去回和后来的V1/V2格式升级对照。新稿10镜20句，正文3861帧加Java150帧，共4011帧/133.7秒，比首发短42秒；V2请求和嵌套回执变化由适配转换及创建接线处理，原业务约定/发货流程保留。隔离仍以业务语义不变且能力满足为前提，保留维护成本；Adapter可以承担防腐边界转换，但不等于任意wrapper或完整ACL。受理/送达/未知边界留必要标签和图文，不再抢主线。旧稿、声音和实际证据保留，不用新检查改写v0.63.0已遭用户否定的事实。
- **D03本轮实际检查与交付：**184项冻结、原12组与升级8组共20组Java通过；独立真实预演36帧另7PNG/6封面、正式成片32帧覆盖16条字幕及根另13帧、PTS/DTS/AAC与完整20句音轨一致性通过。新视频SHA为f86d48b91d0bc0a00c3d5f51b69bc4ec57106d2dd422358a1c59d2f296528852，7,152,478字节，−16.0LUFS/−3.8dBTP。网站40课/5方向，初验8次章节跳转、20句字幕、Java/依赖链接和SVG通过；三处CommonMark粗体仅在站点派生稿修正后再定验，合计2次build/1次历史回归，player/VTT/meta/SB/媒体同SHA，原seek与字幕行为按不变范围复用，未声称重新播放；根实际看7张站点图。[PR #272](https://github.com/linhongcun/video-studio/pull/272)合并d90867fb47dd0b4ddb42310bfd3a08e0b1e1e150，附注tag及[Release v0.64.1](https://github.com/linhongcun/video-studio/releases/tag/v0.64.1)保留首发v0.63.0；Release后[Pages40176457473](https://github.com/linhongcun/video-studio/actions/runs/40176457473)成功，北京时间2026-10-25 16:29:20.004207，11项canonical GET完成完整媒体/海报、20字幕/4章、Java/源码依赖、导航与实际Release条目核验。具体范围见[本轮QA](../episodes-codex/adapter-pattern/qa-final.md)、[发布记录](../episodes-codex/adapter-pattern/revisions/business-boundary-v2/release.json)、[站点定验](../episodes-codex/adapter-pattern/qa-site-format-correction.json)和[线上结果](../episodes-codex/adapter-pattern/qa-site-online.json)。新版尚无用户观看反馈，不把制作/上线通过当作学习效果或认可；外部平台未新发。

## 趣味推理系列的当前安排

- 2026-10-25，用户确认新增经典智力题系列，并要求逐题提issue，后续逐一制作。已登记[首批10题总览 #204](https://github.com/linhongcun/video-studio/issues/204)及P01—P10（#205—#214）；各题按后续实际开工状态推进。
- 用户随后明确从赛马题开工，要求按照项目既有经验与教训做好视频。本次制作P01/[#205](https://github.com/linhongcun/video-studio/issues/205)，slug为horse-racing，新独立系列puzzles。先讲完整题意，逐次演示『三匹更快』的排除证据，视频聚焦七场构造；任意六场策略的严格下界放配套图文。制作与发布按已有GitHub持续授权推进，不包含其他平台新发。
- P01已由[PR #218](https://github.com/linhongcun/video-studio/pull/218)合并并发布v0.55.0，Release后部署40115332761成功。18镜36句、6327帧约3分31秒，最终视频SHA为d643c1d75a23568e5aed6f25115bdab033e5e4317285e36f4cdc933694e2f59f，−16.0LUFS/−3.7dBTP。数学与文稿审查、三段真实无字幕过程、126帧独立正式成片、110帧预演保真以及1440/390网页播放/36字幕/6章seek通过；北京时间2026-10-25 01:20:43首轮10个canonical GET核对完整媒体/字幕/章节及真实Release条目通过，#205已completed关闭、#204同步。实际结果见[发布记录](../episodes-codex/horse-racing/release.md)。未进行逐字ASR、全片听辨或初学者实验，不预写用户认可。02同号示例赛果冲突在编码前修复，见L028。
- **v0.55.0观看反馈与当时的代理解读：**用户已观看v0.55.0并明确表示“这个视频做得很棒”，认可主体；唯一指出结尾将完整证明引向配套文章，很多观众只看视频，因此要求调整。此前“尚未观看”的记录由本条更新，原技术证据保留。当时代理保留前17镜与封面，替换18起尾段，在视频内补齐六场不能保证的必要说明；#205曾重新打开跟踪，修订上线核验后已completed关闭，实际结果见下一条。本条不预记用户认可修订版，见L031。

- **v0.56.4技术与上线历史（已被最新观看反馈否定其篇幅）：**保留前17镜与34句源PCM，尾段改为落败计数与两固定世界证明，25镜50句、7章、8976帧约4分59秒。218输入、完整解码/−16.0LUFS与独立38帧正式MP4、两视口局部站点检查完成。视频SHA334af0a52a6184976e5544f647ec61201368bdc2948bea5addc456f6839cfcf8。原43点异分辨率启发式6处超限，已用同网格比较诊断闭合，原失败报告保留、媒体未改，详见本期qa-final。PR #228合并22f9d16f…，附注tag/Release v0.56.4后部署40143372825成功；北京时间07:40:17首轮10个canonical普通GET完整媒体/海报SHA、50句VTT、7章及实际修正条目通过，#205已completed关闭、#204同步。详见本期release.md与online-verification.json；用户随后已观看并明确否定证明段的复杂度和篇幅，按下一条最新要求精简。

- **最新方向：**用户实际观看v0.56.4后明确认为新增证明画蛇添足，导致复杂、冗长；视频不用展示或提及证明，文章保留完整证明即可。本轮回到原七场安排，用16镜的5+1+1=7简短收尾，删去重复回看及下界证明，不新增配音。上一轮把该反馈归纳成“视频必须完整证明”的规则已撤回，见L031。当前16镜32句、6章、5618帧约3:07的简短版已完成157输入、32句源PCM/前5581画面逐帧保持、实际8尾帧及两视口局部检查，SHA d3082f22eb6afec90cd0a6111bc4756d36c7d459a56630a5ab6a4883cc87740e；PR #233已合并7d1d6f63…，整合v0.57.0后以v0.57.1附注tag/Release发布；部署40146065288成功，北京时间08:21:11首轮10个canonical GET完整视频/海报SHA、32字幕/6章、文章proof及实际修正条目通过，#205已completed关闭、#204同步。用户随后回复“OK”，并要求总结经验、继续下一期；记录为简短确认与继续授权，不扩大为完整观看结论或学习效果测量。
- **P02四人过桥已上线：**用户授权自主选择最有把握的题目制作。本轮基于最新主干28b347db选择P02过桥题/[#206](https://github.com/linhongcun/video-studio/issues/206)，slug为bridge-torch、EP.29；视频先讲题意、过桥规则与具体安排，用19与17分钟对照说明方法，结尾简短回收。完整模型与最少性核验留文章，视频不追加证明或口头入口。本期16镜32句、4章、6025帧约3分21秒，正常语速。154输入冻结、四支实际无字幕176阶段、正式成片独立66帧与32点同网格保真、全轨和32句音频一致性均已通过；视频SHA c657f2928477a896a2d54faa1087fd9ad40517d37a2df7c99aa6563094fe38f4，−16.0LUFS/−3.9dBTP。首发v0.60.0，保留同期观察者、A02及数据库身份优化；14项发布副本、102页构建及1440/390真实字幕/4章/播放/目录检查通过，脚注窄屏换行问题见L038；PR #243已合并057b9d0d…，v0.60.0附注tag/Release后部署40149965870成功；北京时间09:20:03首轮10个canonical GET完整视频/海报SHA、32VTT/4章、独立目录与真实新增日志通过，#206已completed关闭、#204同步为完成2题。实际结果见本期qa-final与release。用户随后实际观看并明确表示“这个视频也做得很不错”，尤其认可动画流畅、人物从左岸到右岸以及携带手电的过程清楚；记录为对本期动态表达的定性认可，可复用做法见S004。

- **P03量水题已上线：**用户在认可P02动画后授权自主选择下一题。本轮基于7cc6f3a6选择[P03/#207](https://github.com/linhongcun/video-studio/issues/207)，slug water-jug、内部EP30。先讲3/5升无刻度空容器、合法操作与单个5升壶恰4升目标，再从容量差造2、小壶存2造1升空位推导六步；固定空间、同步水量、空满停流后落定，完整最少性核验与总量变体留文章。12镜24句、4977帧约2分46秒，130输入冻结、独立真实动态/正式成片/24句音源一致性及99页站点、1440/390播放检查通过。媒体SHA f5462dc2…235ef63；[PR #256](https://github.com/linhongcun/video-studio/pull/256)合并1b2ab500，首发v0.61.0，Release后Pages40153856609成功；北京时间10:22:14首轮9站点canonical GET完整媒体/海报SHA、24VTT/4章/目录/日志通过，另1份Release元数据由可用GitHub connector独立读取并标明来源。#207已completed关闭、#204同步完成3题。实际证据见本期qa-final.md与release.md；未执行平台新发、ASR或全片人工听辨。用户随后实际观看v0.61.0，评价大小壶互倒动画“挺流畅”“挺准确”，并认为整片“很清楚地说明了这个比较绕的逻辑”；记录为对本片动态表达与讲解清晰度的定性认可，可复用经验见S004，不扩大为量化学习效果。

- **P04三门问题已交付：**用户在认可P03后授权再选一题，本轮从干净最新4a00d8a0选择[P04/#208](https://github.com/linhongcun/video-studio/issues/208)。内部EP32、slug monty-hall，14镜28句、四章、5507帧约3分04秒；固定门号与奖位，先完整一局再连续缩入三个等权初始奖位，解释始终保留1/3、始终换门2/3，额外条件概率与规则变体只在文章，片尾简短。原EP31候选因并行身份占用保留隔离，原始TTS来源保持，经等价证明复用不变范围，新165项冻结后重新完整编码。数学、真实动态、独立52时点成片/88点保真、28句音源及两视口网页检查通过；实际首发v0.64.0，PR #267合并e73ffa53，Release后Pages40160813696成功，线上完整媒体/字幕/四章/目录与日志核验通过后#208已completed关闭，#204完成4题。保留Skills、适配器与LC70最新内容，旧Agent删除未恢复；[发布证据](../episodes-codex/monty-hall/release.md)记录真实能力范围。用户实际观看后先觉主持人规则绕，随后明确已看懂、视频制作没有问题，认为题目本身较奇怪；按最新反馈保留现版，制作认可与技术检查分开记录，见S004及本期release.md。
- **P05两枚鸡蛋已交付：**用户在澄清已看懂并认可P04后授权下一题，选择[#209](https://github.com/linhongcun/video-studio/issues/209)，slug egg-drop、内部EP33，经PR #270预留。12镜24句、四章、5257帧约2分55秒；先讲最后一枚为何不能跳过未知层，由固定10层晚碎的19次推得递减预算，再用原题楼层与两枚蛋完整演出F31的8次查找。实际8与保证最多14分开，严格最优性和完整边界留文章，视频简短结束。133冻结、数学／源码／实际动态／正式媒体和音轨、两视口站点检查通过，视频SHA f5876353…42b9179。并行LC200先发后，旧v0.65.0本地候选及证据原样归档，整合主干后保持同一媒体，重新完成v0.67.0完整站点验收；[制作PR #279](https://github.com/linhongcun/video-studio/pull/279)合并549ac45b，附注tag及[Release v0.67.0](https://github.com/linhongcun/video-studio/releases/tag/v0.67.0)后Pages40181102180成功。北京时间2026-10-25 17:36:27首轮9次普通站点canonical GET加1份独立Release证据完成完整媒体／海报／24句字幕／四章／五课目录与真实日志核验；#209已completed关闭，#204完成5题、剩余5题待安排。实际检查、能力范围及发布证据见[本期记录](../episodes-codex/egg-drop/release.md)，经验补入L003/S004/S006。用户随后观看并指出自然想到二分法，而视频开头一连串尝试缺少选择动机，因而看着懵；对照稿确认03直接给10层间隔、06直接给14次预算，未接住二分为何受限及预算来源。当前为负面与疑问反馈，不能再记为尚未观看或已认可；本轮先解释原理，未要求或执行重制，后续解释效果待用户确认。见[观看反馈](../episodes-codex/egg-drop/feedback.md)及L039；未执行P05外部平台投稿。

## GitHub 自主发布授权

2026-10-24 用户在认可EP.17后明确说：“代码可以提交合并了，视频可以布置上线了。以后做好后就可以自己这样做了……要是有问题，我会跟你说的。大不了你再重新改，再上个线就行。”

据此，后续视频制作和质量检查完成后，可自主合并主干、发Release、部署GitHub Pages并核验线上文件，不再逐期要求观看确认或widget。收到反馈后修正、检查并重新上线。资料与动态表达要求继续，检查能力不足须如实记录。平台新发不包含在本次持续授权中。真源见[RULES的STATUS](RULES.md#status)。

同日用户补充：“以后制作完将对应的那个issue也进行关闭吧。”后续制作、合并上线及核验完成后，以`completed`关闭对应制作issue，作为发布收尾，不再另问。未执行的平台事项仍如实保留，不扩大平台发布授权。

## 已验证案例与当前状态

### 设计模式D02：观察者模式（首发v0.58.0；当前v0.60.4）

- 2026-10-25，用户认可D01当前版本后要求开始下一个模式，并再次强调先拉取最新代码避免冲突。已从干净main快进至`1834450d6dd6e36762aa1862a72282c4e89822ac`，创建`codex/observer-pattern`，重读上游清理/手册与依赖变化，记录见[开工核对](../episodes-codex/observer-pattern/startup.json)。
- 选取既有[D02观察者模式/#164](https://github.com/linhongcun/video-studio/issues/164)，制作slug为`observer-pattern`。围绕同进程订单变化、订阅登记、共同通知约定与取消订阅讲语言无关的职责关系；具体实现仅作可选图文。已完成12镜24句/5章/4979帧约2分46秒，成片SHA76f38c96…c0c08；独立思想/真实动态/正式媒体及1440/390本地播放、24字幕和10次章节跳转通过。已由PR #236合并530ddc75…并首发v0.58.0，附注tag身份与正式媒体一致；Release后Pages40147093346成功，北京时间08:35:41首轮9个canonical GET完整视频/海报、24字幕、5章、SVG原生属性、D01↔D02及真实Release条目通过。#164已completed关闭、#161同步，详见本期release.md；未预记用户已观看认可D02。SVG站点派生稿与原冻结稿分开追溯，L034/L035记录真实制作问题。

### EP.23 · 设计模式D01：策略模式

- **本轮返工原因与方向：**用户观看v0.54.4后指出过多函数、参数等内容偏向语法；设计模式应强调不绑定语言的思想，明确要求修复视频并更新经验教训。本轮用结算流程、定价策略、选择三类职责，讲变化隔离、共同约定、委托、一次替换和维护边界/成本；语言实现仅入文章可选附录。不能仅将函数改名为办法，或将参数绑定当作模式定义，见L030。
- **当前设计思想版：**11镜22句、4410帧约2分27秒，新媒体SHA9293cf4d66319a44ac7808f5f75d8bdd1da3a3cec627b8da4d57f802466a1a57，-16LUFS/-3.8dBTP。根/独立思想审读、实际动态与正式成片、125源/解码/PTS/音轨一致性、两视口8次seek及22字幕验收通过，已按v0.56.1上线。保留章节衔接与同一100元订单，语言仅入可选附录；L030/S017及旧经验边界已更新。实际上线结果见本期release.md，不预记用户已观看认可。
- **设计思想版上线结果：**[PR #223](https://github.com/linhongcun/video-studio/pull/223)合并后发布v0.56.1，附注tag实际包含本次9293cf4d…a1a57媒体、4410帧和首发v0.52.0；Release后Pages部署40118351325成功。北京时间2026-10-25T01:58:59.083759+08:00，8个canonical普通GET的完整视频、海报、22VTT、四章/目录/源码/系列/RSS/更新日志核验通过，#163已completed关闭，#161同步。用户随后观看本版表示“目前看着问题不大了”，授权继续下一个设计模式；这是定性观看认可，经验教训不把技术检查或认可当学习实验。
- **v0.54.4实现讲解版历史：**13镜26句、4895帧约2分43秒，全新配音与画面；视频完整SHA为a7056ae8ccfe6783063b6c679174fa5d15ab410cac0628fe5de12e7fcc9e6696，−16.0LUFS/−3.7dBTP。137输入、完整解码/PTS、独立实际成片和两视口8次seek/26句字幕通过；用户后续反馈其偏向语法，不能用这些检查证明设计思想已讲清。ASR/听辨能力限制继续如实记录。
- **v0.54.4上线历史：**[PR #216](https://github.com/linhongcun/video-studio/pull/216)合并后发布v0.54.4，Release后Pages部署40113587396成功；北京时间2026-10-25T00:58:39.395227+08:00，8个canonical普通GET的完整视频、海报、26句VTT、四章/目录/源码/系列/RSS/更新日志核验通过，当时#163以completed关闭、#161同步。用户后续语法化反馈及新修订按本节最新方向处理，具体历史见[发布记录](../episodes-codex/strategy-pattern/release.md)。
- **章节衔接修订历史：**六句新口播与三镜动作已完成，5292帧约176.4秒，比原版增加3.13秒；十三镜原PCM、局部字幕/cue和时长严格相同，图像复用转码的代表帧最大平均差0.318/255。163输入、全PTS、完整解码、三处边界实际帧及两视口三章跳转已检查，发布收尾见本期release.md。
- **章节衔接修订上线历史：**[PR #198](https://github.com/linhongcun/video-studio/pull/198)合并后发布v0.54.1，Release后Pages部署40107945142成功。北京时间2026-10-24 23:41:19，8个canonical普通GET的新版视频完整SHA（7f5606a8…68726）、海报、32句VTT、四章与目录/源码/系列/RSS/更新日志实际核验通过；当时#163再次以completed关闭，#161同步。新版学习站两视口实际seek与播放已复验；用户后续对新手理解提出进一步修订意见，见本节最新反馈。

- 用户授权先选一期制作并部署网站，选定[#163](https://github.com/linhongcun/video-studio/issues/163)，slug为strategy-pattern，新独立系列design-patterns；其余模式仍为选题池。
- [首发制作工程](../episodes-codex/strategy-pattern/revisions/v0.52.0/release.md)为16镜32句、四章、5198帧，约2分53秒。同一100元示例订单展示规则抽离、外部选择、统一调用与返回，活动八折改七五折得到75元；新增规则仍需登记，单选不叠加。
- 六份公开资料、实际示例及最小diff、154项冻结、完整媒体解码与独立实际画面检查、桌面/手机32字幕和四章seek已完成。视频完整SHA为c80f9e44ee8eb668fb702266170d4fd8773d14f120e315b568d6ed5d07c27431，−16.0LUFS/−3.7dBTP；未执行逐字ASR或全片人工听辨，不声称用户已观看认可。
- 本期首发由[PR #192](https://github.com/linhongcun/video-studio/pull/192)合并，发布[v0.52.0](https://github.com/linhongcun/video-studio/releases/tag/v0.52.0)，Release后部署40104729342成功；线上8个canonical普通GET的完整视频/海报SHA、32条VTT、四章、源码/系列/RSS/更新日志核验通过，曾以completed关闭#163；首发证据见[历史发布记录](../episodes-codex/strategy-pattern/revisions/v0.52.0/release.md)和[历史线上报告](../episodes-codex/strategy-pattern/revisions/v0.52.0/online-verification.json)。

### LC.704 二分查找

- 2026-10-25，用户在认可题意前置修订后要求自选下一道LeetCode继续制作。本次选择[#76](https://github.com/linhongcun/video-studio/issues/76)，slug binary-search，独立算法系列展示LC.704，内部ep24。先交代升序无重复数组、目标和下标/-1，再用同一数组目标13/8解释安全排除、最后一格和空区间；片尾完整Python静态5秒并提示暂停。14镜28句、4748帧约2:38，137输入冻结；真实小样47阶段、正式MP4独立20阶段与44采样保真、全解码/−16.0LUFS及1440/390网站验证通过，媒体SHA9faef1ba…60ae。实际首发v0.56.0，保留P01先发布的v0.55.0；PR #219完成制作，PR #221修正并行版本身份，Release后部署40116314325成功，线上完整媒体/海报、28句字幕、四章及真实Release条目GET通过后#76已completed关闭。并行发版教训见L029，[发布证据](../episodes-codex/binary-search/release.md)保留实际结果，不预写新片用户认可。

### LC.3 无重复字符的最长子串

- **最新反馈与返工：**用户指出两条LeetCode视频缺少面向陌生观众的题意前置，要求先介绍题目再讲解法。v0.54.2已修复LC.3与LC.11开头并完成实际媒体及上线核验；用户随后回应“很好”并继续下一题。下述旧版本技术/上线证据保留，修后证据见本节用户偏好条目及本期qa-final。

- 用户在LC.11修订后授权再自选有信心的题目制作精品，本次选定[#79](https://github.com/linhongcun/video-studio/issues/79)，slug longest-substring。用abcbadea解释重复时为何连续收左边、最后窗口变短仍保留历史最长；不加入装饰进度线，完整Python卡5秒供暂停。
- 18镜36句、5078帧约2:49；官方题意/集合语义/平均复杂度已实际核验，独立有限实现测试、关键无字幕过程和真实配音PNG预检通过，161实际输入冻结。正式5078帧编码、完整解码与−16.0LUFS/−3.6dBTP通过，46采样保真检查通过；正式媒体SHA为c8adbb51…2043，80页站点构建、既有学习路径与1440/390新页复验通过，v0.53.0由PR #194合并并部署40105542981成功，线上完整视频/海报SHA、36句VTT、四章、系列/RSS与实际Release条目GET通过，#79已completed关闭；当前不声称用户已观看认可；实际范围见本期qa-final.md。

### EP.22 Agent 概念入门（已按用户要求撤下）

- **当前状态：**本期与A02一并移出发布目录及当前制作树，站点删除与部署验证见[撤下记录](agent-video-retirement.md)。下面是历史制作与反馈；原V2/V3工程入口已改为删除前的固定Git链接，不再是当前制作依赖。

- **最新开场建议：**用户观看V2后指出开头内部内容仍陌生，明确建议直接嵌入退款咨询对话或对应功能交互界面。此次V3在新目录agent-intro-v3仅替换开头0–236帧：首帧完整咨询目标、查询反馈、AI追问；已验音轨及237帧后的内容复用。此建议授权使用该功能UI，不套用旧“假应用窗”禁令要求再确认。场景入口与原来的主线/事实检查分别验收，实际结果见V3记录。
- **V1观看反馈：**用户已观看v0.50.0，明确指出主线模糊、开头铺垫多且像流水账，不知道要讲什么，要求优化并更新经验教训。此前媒体/事实检查通过不代表用户认可，旧版观看结论以本条为准，详见L021。
- **V2定稿：**[新版工程](https://github.com/linhongcun/video-studio/blob/321e8e8c1b4ad34a6ea09eed2bb5cf369d9ab6dd/episodes-codex/agent-intro-v2/README.md)为11镜22句、4章、2864帧，约95.47秒。唯一悬念是“智能体为什么查着订单却反问用户”，第二镜7.9秒开始、10.47秒进入首次查询，结尾解释返回结果怎样触发询问；固定流程比较移文章。旧制作目录和v0.50.0冻结产物保留；当时canonical网址为agent-intro、源码入口为agent-intro-v2/remotion；当前已撤下，不再提供活动课程入口。
- **本地结果与发布收尾：**视频SHA-256为f9cdfa3b10e0d26baa57ad64a71b34e31860a0304ad6b619a92f346bf3e8ec15，−16.0LUFS/−3.8dBTP。120项实际输入冻结、完整解码、119预演/120实际帧比对和干净重建已检查；实际范围及未执行的逐字ASR/全片人工听辨见新版qa-final。本次沿用[#131](https://github.com/linhongcun/video-studio/issues/131)跟踪返工，按v0.50.5收尾，合并、部署、线上完整SHA与completed关闭的实际记录保存在该issue，不预写用户已认可V2。

以下保留V1的制作与发布历史：

- 用户要求先选一期制作看效果，选定 A01 / [#131](https://github.com/linhongcun/video-studio/issues/131)《AI 能回答问题，怎么才能真正帮你办事？》，制作与站点 slug 为 agent-intro，新系列键 agent。
- [V1 历史制作工程](https://github.com/linhongcun/video-studio/blob/686473df4fe89f6083a2386a8631d5dc32f4c04a/episodes-codex/agent-intro/README.md)为20镜40句、5章、5420帧，约180.7秒；通过同一合成退款咨询解释模型请求、程序执行、结果回传和动态选择，只查询并给申请建议，退款始终未执行。V1 已从工作树清理，以上固定提交链接用于历史追溯；历史V3入口见 [V3 工程](https://github.com/linhongcun/video-studio/blob/321e8e8c1b4ad34a6ea09eed2bb5cf369d9ab6dd/episodes-codex/agent-intro-v3/README.md)。
- 实际媒体SHA-256为44b21f36f6b99b4106141548a6bbc70c7556a394e4f1e819949b0e2af9be9b9c，−16.0LUFS；171冻结输入、完整解码、73预演/74实际帧比对、18张独立实际成片图及干净构建已检查。未执行逐字ASR或全片人工听辨，详见[V1 最终报告](https://github.com/linhongcun/video-studio/blob/686473df4fe89f6083a2386a8631d5dc32f4c04a/episodes-codex/agent-intro/qa-final.md)。
- 站点正式构建、40条VTT、5章精确跳转、桌面/手机布局和完整媒体SHA已有本地证据；[V1 发布记录](https://github.com/linhongcun/video-studio/blob/686473df4fe89f6083a2386a8631d5dc32f4c04a/episodes-codex/agent-intro/release.md)、GitHub [v0.50.0](https://github.com/linhongcun/video-studio/releases/tag/v0.50.0)及制作issue保留当时的发布与线上核验状态。此为V1首发记录；用户随后已观看并批评主线与开头，之后又要求删除两期，不记为用户认可。

### EP.05 CDN 地图与术语返工

- [v0.50.3](https://github.com/linhongcun/video-studio/releases/tag/v0.50.3)已由[媒体PR](https://github.com/linhongcun/video-studio/pull/162)合并并[部署](https://github.com/linhongcun/video-studio/actions/runs/40102166946)，2026-10-24 22:24:22（北京时间）CDN视频/海报完整SHA、字幕、章节/源码入口及首页/更新日志实际GET通过；证据见[online.json](cdn-map-terms/online.json)。新版尚未被用户观看认可，历史平台投稿保留。

- 用户实际观看v0.48.0后要求加入地图及CDN等核心名称，本次按反馈返工。用同一公开图片演示临近边缘节点服务、未命中回源与命中短返，地图交代网络路径/时延调度的边界；09镜同时修正接收图片与等待文字的时序。
- 本次制作、独立复核、GitHub站点发布和线上核验均已完成；对应制作issue收尾以GitHub状态为准，不将本次自主发布写成用户已观看认可。

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
- v0.47.0已通过[PR #129](https://github.com/linhongcun/video-studio/pull/129)合并，主干/标签为`d2e949bbce1835cdc80399f7f7e77ff565f782c3`；[Release后部署40090373495](https://github.com/linhongcun/video-studio/actions/runs/40090373495)成功。四新片与两旧片完整媒体、112句字幕、18章、海报、路径及更新日志核验后，#125–128已completed关闭。
- 用户随后已经实际观看四片，指出成功/失败分支缺少大纲与全局观；这取代先前“尚未观看”的状态，但不否定已执行的文件/局部检查。最新修改方向见下一节，平台新发仍未授权。

### EP.21 按观看反馈增加全局流程与缩放定位（v0.51.0已上线）

- 用户希望类似树形结构，先建立全局、放大看每一块、再缩回定位。四片保持独立机制和短片范围；优先保留原音轨、字幕与时长，重做导航而非叠加密集大图。
- 每片先确认真实拓扑：2PC的拒绝与决定未知不同；TCC的确认/取消从同一预留前提分开；Saga的退款是新补偿且可能待恢复；Outbox的技术重试/重复与业务拒绝不同。重试回边和情景重置不画成新的业务结局。
- 统一稀疏地图、当前路径定位、跨分支连续缩放和结尾回收，并实际复核变焦中间态与关键动作没有被遮掉。尚未验证的设计不记为成功。
- 本次返工[#152](https://github.com/linhongcun/video-studio/issues/152)，原计划v0.47.1；制作期间主干已由其他协作任务推进至v0.50.5，本次完整保留那些提交，实际发布版本为v0.51.0。冻结分镜中的navigationRevision保留原计划设计ID，用实际package/Release确定发布版本。旧v0.47.0制作输入与成片可从上述Git提交和Release追溯，历史检查记录保留；L022记录实际用户反馈，L023记录变焦遮住动作起点的预检发现；S015记录实际复核支持的地图编排。745份预演记录、13段最终源无字幕过程的156个独立编码时点（另保留Outbox修前59点）、13,993帧时序审计和本轮干净复验已完成，最终成片与上线证据见各片qa-final/Release和#152。检查与用户认可继续分开。
- 已由PR #186合并，发布v0.51.0并经Release后部署40103321270成功；线上四片完整SHA/字节、112句字幕、18章、海报、学习顺序、原入门与旧合集及真实Release日志通过，其他协作视频的媒体/字幕/章节/海报亦保持。#152已在上述检查后以completed关闭；详见[线上证据](transaction-branch-online-verification.json)。用户随后实际观看并明确表示“现在看着就清晰多了”，认可本轮全局/局部导航；平台未新发。

- **后续用户交办：**扫描此前已上线视频，判断哪些缺少全流程与知识架构定位，对值得调整的内容执行重制。先按实际分镜和成片检查，优先处理多步骤、多情景与循环恢复，保留已清楚的单路径动画；依真实拓扑选择流程、状态机、树或分层图，不机械二叉化、不扩大单集范围。批次取舍与实际状态单独记录，未检查或未完成的片子不写为通过。

### 旧片全流程导航重制（#199，v0.56.2已上线）

- 用户认可v0.51.0的清晰度后要求扫描旧片并按价值重制。基线6765032/v0.54.0：29支当前内容，25支重新检查源码和229个实际编码时点，4支刚获认可的事务导航片保留；原长合集和下架隔离级别分别归档/隐藏。
- 本批选HTTPS、DNS、缓存一致性、消息队列、熔断器、分布式事务入门六片；9支适合局部增强，14支保留。逐片原因与实际证据见[扫描报告](flow-navigation-audit.md)及[制作issue #199](https://github.com/linhongcun/video-studio/issues/199)。已有全数组或调用关系图的算法/模式片不为统一皮肤整片返工。
- 复用已审共享相机，保留原配音、脚本、字幕和总帧数。按真实网络、读写路径、状态机或范围对照组织全局；导航的颜色、提示和标题也须与当前实例进度一致。制作/独立检查、正式编码、上线与用户新观看结论按实际阶段分别补齐。六支已正式编码并通过独立最终媒体复核，660冻结输入、原AAC与时序保持、六片fresh独立代表PNG复现通过；已由[PR #224](https://github.com/linhongcun/video-studio/pull/224)合并，随[v0.56.2](https://github.com/linhongcun/video-studio/releases/tag/v0.56.2)发布并经[Release后Pages部署](https://github.com/linhongcun/video-studio/actions/runs/40118710238)成功；线上六片完整SHA、字幕、章节、海报及更新日志核验通过，#199已以completed关闭，详见[线上证据](flow-navigation-audit/online-verification.json)。本轮仅更新GitHub站点，用户对六支新版的观看反馈后续另记。

### EP.28 · Agent A02：工具调用由谁执行（已按用户要求撤下）

- **最新用户观看反馈与处置：**用户已观看v0.59.0并明确否定本期信息收益，认为主要重复请求/执行常识；后续进一步否定基础接线与编码流程方向，提出研究热门AI概念的机制与深度。A02独立重制计划已终止，#132按`not_planned`关闭；六个API/工单实战单元及拟合并A01–A04的建议均为已撤回的未实施草案。本期V1媒体、负面反馈和技术检查曾在该轮保留；用户随后明确要求删除两期，当前媒体与工程移除，原始证据仅由Git历史追溯。关闭不代表教学价值修复或用户认可。系列当前研究安排见[复盘](agent-development-value-review.md)及L040，本轮无新TTS、渲染或模型实验。
- 用户要求同步最新代码后继续下一期，选定[#132](https://github.com/linhongcun/video-studio/issues/132)，制作/站点slug为agent-tool-execution，接A01。原始基线1834450d/v0.57.0，编码前整合e38fa923文档收尾，无生产输入交集；当时工程按锁独立npm ci，未用删除目录下的ignored依赖。
- [本期工程](https://github.com/linhongcun/video-studio/blob/321e8e8c1b4ad34a6ea09eed2bb5cf369d9ab6dd/episodes-codex/agent-tool-execution/README.md)11镜22句、3305帧、110.166667秒。开头退款咨询UI建立查询签收天数的目标，完整展示调用请求→应用检查/实际查询→返回先到应用再到模型→对话；再另起新用户无权限会话，查询0次，结尾区分请求与执行结果。
- 2026-10-25重新联网读取官方工具调用/执行宿主/授权文档，真实本地HTTP正常1次、拒绝0次；模型侧为固定fixture。128生产输入、独立73个有效动态阶段和29张正式编码帧、163预演/164编码帧保真、完整解码与−16.0LUFS检查通过；视频完整SHA为b1be594841f8e41d0922a4087c725bf05ccb0fd2252eab1388d1a1631d93211e。实际边界见[成片报告](https://github.com/linhongcun/video-studio/blob/321e8e8c1b4ad34a6ea09eed2bb5cf369d9ab6dd/episodes-codex/agent-tool-execution/qa-final.md)。
- 两个TTS候选裁尾风险与10镜说明中间态重叠分别追加L006/L003；功能场景入口的独立验证补入S002，不凑新编号。V1已按GitHub站点持续授权上线，真实版本、部署与线上核验见#132及本期site记录；没有逐字ASR/全片人工听辨或真实模型推理，平台未新发。用户已观看且评价信息收益不足，不能继续记为“未观看”或已认可。

## LeetCode 首期：LC.11 盛最多水的容器

- 2026-10-24，用户从本仓12条LeetCode选题中采纳[#78](https://github.com/linhongcun/video-studio/issues/78)，明确授权开始制作《盛最多水的容器：为什么每次都移动短边？》，完成后合并项目并发布网站。未授权外部平台投稿。
- 制作目录`episodes-codex/container-most-water/`，站点`episodes/container-most-water/`。独立算法系列展示LC.11，内部ep22仅用于排序/Release，不将网络或事务课程当作先修。
- v0.49.0初版为22镜44句、4章、6544帧，约3分38秒，冰糖原速。用同一输入`[2,3,10,5,7,8,9]`解释面积、固定短边的整组排除与正式扫描，保留36而非最后面积5。初版完整视频SHA为`624c2fa8dec7c8f96caad8b25d5890ae83c1854f4c16443617b32685002f18e0`。
- 初版真实时序/声学起音、186项冻结输入、全解码、114个预演记录与114个实际MP4帧的保真、独立目视和干净依赖首帧复现已按实际范围记录。未执行逐字ASR或全片人工听辨；这些是发布前检查，与后续用户观看结论分开保留。
- 本期发现QA传参不能保证实际隐藏字幕，修正后重出并查看真无字幕过程，见L016；安全排除的算法叙事做法与独立证据见S012。已由[PR #154](https://github.com/linhongcun/video-studio/pull/154)合并并发布v0.49.0，Release后部署40093925916成功；线上视频/海报完整SHA、44句VTT、四章、独立系列/RSS和更新日志实际GET通过，#78已以completed关闭。完整证据见[发布记录](../episodes-codex/container-most-water/release.md)与online-verification.json，平台未投稿。
- 同日用户已实际观看初版，明确表示“这个视频做得真不错”，认可主体讲解；唯一修改意见是去掉成片内底部装饰进度条，以免分散注意力，并要求更新教训。新版仅删除两个SVG矩形，主体预演像素、解码音频及全部时序保持；全6544帧底带扫描、独立正式成片与390/1440网页原生进度控件/章节/字幕复验通过。v0.50.1已由PR #157合并并经Release后部署40097496603上线，实际GET核验新版视频6d1e3b4c…8adb、海报、44句VTT、四章及更新日志通过，不预写为用户已观看认可新版。对应教训L018，S012已补认可范围，证据见本期qa-progress-removal-*。
- 用户进一步要求片尾展示完整Python解法并更新经验。本轮在原6544帧之后追加450帧、15秒静态代码卡，供暂停阅读；保留前面讲解与配音，旧字幕在6543结束，不新增口播。本期停留参数不作为全系列固定要求。16行程序与文章/显示源逐字相同，独立8代表用例执行通过；真实预演3个原段同帧PNG与旧版字节相同，代码卡首/中/末3帧相同，独立查看字号/缩进/最长行/返回值可读。原44句及人声PCM前缀保持，卡区人声全零；190输入冻结核对、6994帧正式编码、完整解码及−16.0LUFS/−3.7dBTP通过；独立实际查看硬切和最终return，全部450卡帧稳定且return可见；网站73页构建、旧课程/Agent回归、390/1440的3:53时长/四章/原生控件/44句VTT及片尾零cue/暂停阅读复验通过，v0.50.2已由PR #159合并，Release后部署40100807342成功；线上完整视频SHA为072ae1db…535b，海报/44句VTT/四章/系列/RSS/更新日志实际GET通过，证据见本期release.md和online-verification.json。S013记录用户指导和独立预演支持，不将此写成用户已观看认可新卡片或已测量学习收益。

- 用户随后要求把15秒代码卡缩为5秒，并质疑小改动耗时。本轮按5秒静态卡加暂停提示修正，原完整程序与正文继续保留；已复用旧编码画面快速转码，6694帧/连续PTS/末return/人声前缀/190输入及1440单页3:43时长和字幕检查通过，v0.50.4由PR #187合并并部署40102306544成功，线上视频完整SHA f95993b7…1c04、海报/44句VTT/四章及真实Release条目核验通过，不声称用户已观看认可新版。v0.50.2的15秒技术证据属于历史，当前方向见L020及S013后续修正。

## 网站的学习站定位

2026-10-24 用户认可网站审查结论，并要求按该方向调整。网站主品牌采用“IT小村”，定位为技术可视化学习站；Video Studio 保留为仓库和制作工程名称。主导航围绕首页、学习系列、全部内容与关于，搜索独立可达。系统原理下保留原有五个细分系列；Agent 开发、算法可视化和设计模式是独立学习方向，不与系统系列自动连接前后课。

首页先帮助选择方向与学习起点，再展示最近发布；全部内容支持方向、系列、标签和排序。读者可直接选择视频、图文与真实课程目录，窄屏保留正文目录。视觉沿用视频深蓝、青绿与少量暖金，保留柔和浅色阅读模式。规划内容必须与已发布内容区分。历史链接、期号、视频、海报、字幕和章节保留；此次检查和发布记录见 [网站改版记录](site-learning-redesign.md)。

## 视频复用边界

- EP.21的范围按最新用户反馈推进：先前从可靠消息改为分章合集解决覆盖要求，后续观看又暴露长片密度与深度问题，现改为常见实现独立短片。历史取舍与检查记录不删除，但不能把旧的总览方向当作当前授权目标。详见L008、L009、L012。

- 14或16镜、具体时长、字号、滚动位移及坐标都是单期实现，不照搬成后续硬规则。
- 官方ASR模型下载在当时环境被拒绝，后续重新检查能力。既有句级音频边界和声学起音不能冒充逐字识别或完整人工听辨。
- 授权范围和系列状态以最新用户指令及RULES的STATUS判断；GitHub站点已有持续授权，平台新发仍未授权。

### 数据库身份图形优化（#230，v0.58.1已上线）

- 2026-10-25，用户确认数据库圆柱与角色标签的建议，并明确选择MySQL icon，要求帮助观众识别数据库；保留内部记录、表格和事务范围，不把它们全部画成数据库。
- 本批10片：服务端缓存、缓存一致性、主从复制、2PC、负载均衡，以及事务入门、Saga、Outbox、本地事务、分库分表。索引树、库存行、锁、消息和TCC资源状态保持原表达。
- 使用Devicon的原色MySQL识别图标与数据库圆柱组合，按原比例显示，保留来源、MIT notice与品牌说明，不宣称官方授权或品牌背书。标记只表示数据库角色，不把通用机制的适用范围改成某个产品。
- 原声、字幕、分镜及相机保持；同库共同边界一枚、两独立库各一枚，标识随对象缩放；正式编码保留原AAC流。993项冻结声明、fresh依赖安装与10片类型检查已通过，两代表时点同尺度PNG字节与像素复现一致。[PR #235](https://github.com/linhongcun/video-studio/pull/235)已合并，随[v0.58.1](https://github.com/linhongcun/video-studio/releases/tag/v0.58.1)发布；[Release后Pages部署](https://github.com/linhongcun/video-studio/actions/runs/40147968820)成功。线上10支完整视频SHA、字幕、章节、封面、源链接与实际更新日志核验通过，#230已以completed关闭。仅更新GitHub站点；用户随后已给出数据库内容更清晰的定性反馈，具体观看片目未逐一确认。见[本批线上记录](mysql-database-identity/online-verification.json)。
- 开工已同步a5871f7；制作期间再fetch并审读新主干28b347d/v0.57.1，确认与993冻结项无交集，保留新增三条LeetCode和赛马短版。本批版本顺延v0.57.2；按新同步规范将旧目录依赖软链迁至保留的load-balancing工程，依赖依据为当前相同锁包图及已独立完成的fresh安装/构建，不把ignored旧工程作为后续入口。
- 发布收尾再同步b86168c/v0.58.0，保留同期观察者模式；本批最终编号按该主干顺延v0.58.1。此次仅新增其他内容与文档，播放器源码和本批10片媒体/冻结输入无交集，既有UI结果按实际0.57.2版本保留，不重贴为新版本。

- **用户观看反馈：**2026-10-25，用户明确表示“现在这个关于数据库的内容看着就清晰多了”。记为对本轮清晰度的正向反馈，后续沿用可辨识的数据库身份标记与中文库名，继续区分库、事务范围和内部记录；不扩写成每支视频均已观看认可。见S019。

### 产品交互入口单期试点（分布式事务入门，已上线）

- 2026-10-25，用户希望先看实际APP功能操作和页面反馈，再由同一业务对象展开机制，结尾回到页面；本次明确只选分布式事务入门做单期pilot（[#242](https://github.com/linhongcun/video-studio/issues/242)）。基线afe60158，范围01/02/20与04提交前重置，保留原声、原分镜字幕时序及5155帧；订单8124/商品7042/买1件持续对应，记录存在不等于整单成功。23帧独立预检、16帧编码采样及桌面/手机真实播放已通过，保留原AAC；已由PR #249合并，v0.60.2 Release后Pages部署及线上完整SHA/字幕/章节/海报/更新日志核验通过，#242以completed关闭；不记成用户观看认可。范围与基线见[试点记录](product-scene-intro/README.md)。

### 缓存与消息中间件身份优化（#271，v0.64.2已上线）

- 2026-10-25，用户要求扫描现有视频，像MySQL身份一样为缓存/MQ增加常见产品图标。最新f5327fd/网站v0.64.0基线共39已发布片，当前选4片：服务端缓存、缓存一致性用Redis共享缓存示例；消息队列原声的手动确认与断线重投递对应RabbitMQ；Outbox发送通道用Kafka示例。中文角色名、原声、字幕、时长、封面及导航保留；图标不贴本地/HTTP/CDN缓存、消息或库内进度。图标原图、许可与角色边界分别核实；25张独立预演、30张正式编码采样、原AAC/610保护项/484冻结声明、100条字幕/16章、桌面手机8次实际播放及最新主干兼容检查已通过，已由PR #275合并并随v0.64.2 Release发布，Release后Pages40178059672成功；四片完整SHA、100条字幕/16章、海报与真实更新日志线上核验通过，#271以completed关闭。不记成用户观看认可。实际结果见[批次证据](middleware-identity/README.md)。

## D02 观察者模式的实战重点（2026-10-25用户反馈）

用户要求直接调整已发布视频，减少手写观察者代码，明确跨服务业务通知常通过MQ发布订阅落地。保留原订单案例，但不能继续把维护名单和取消订阅作为绝大部分篇幅。进程内框架监听仍然适用，不将用户的实践取向扩大为所有观察者模式已经不用；本轮制作与实际验证见[实战修订](observer-mq-practice/README.md)。本条记录用户指导，尚不表示新版已获观看认可。

- **本轮交付：**D02已由PR #293合并42d49c74并发布v0.68.4，保持原URL和首发身份。新版144.4秒，173冻结、声音来源/时序、186预检采样/81正式采样与完整解码、56项网站静态验收通过；Release后Pages40195977106成功，2026-10-25T21:09:17.662178+08:00的9项线上GET核对视频完整SHA`f92a0211c6402b661231bacc137a459de4dcf9a4d0b40d9ff905fc53c0de6c33`及海报/VTT/20句/5章/更新日志通过，#292于核验后completed关闭。仅GitHub站点，无外部平台新发；没有全片人工听辨或逐字ASR，不预记用户已经观看认可。详见[实战修订](observer-mq-practice/README.md)。
