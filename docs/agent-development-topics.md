# AI / Agent 概念视频：当前选题与资料依据

更新与核验：2026-10-25（北京时间）。

用户已明确转向以**Skill、MCP、Subagent、Goal等AI概念**为入口，讲机制、设计意图与取舍，并授权关闭过浅选题。Goal已确认是“目标驱动的Agent”。旧16期主线＋4项深入方向的制作顺序作废，上一版六个API/工单实战单元草案撤回；不再按基础接线逐条开拍。

**最新媒体处置：**用户进一步要求删除A01/EP.22与A02/EP.28两期试片；两期发布内容和制作工程退出当前树，取代此前保留旧媒体的决定。历史制作、QA与负面反馈通过删除前Git提交追溯；11项概念研究候选不变。范围及已完成的部署核验见[撤下记录](agent-video-retirement.md)。

详细依据与复盘见[当前策划](agent-development-value-review.md)，实时跟踪见[系列总览 #130](https://github.com/linhongcun/video-studio/issues/130)。以下是重写后的编辑研究候选，不是11支视频的固定排期，也不是用户已逐项认可的新标题或效果。

## 首片执行进度

用户随后授权自选最有把握的一期制作，已选择[Skills #139](https://github.com/linhongcun/video-studio/issues/139)。新EP.31 / agent-skills为12镜24句、约3分8秒；以接口兼容审查解释方法包、渐进加载、资料读取与脚本执行、上下文开销。已完成独立成片复核，本地站点验证已通过，GitHub发行与线上核验收尾进行中，尚无用户观看结论。其他10项继续作为研究候选，原两期仍保持撤下。实际状态见[本期记录](../episodes-codex/agent-skills/README.md)，下方研究设计不再解释为全部未启动。

## 优先研究池

| 候选 | 要解开的问题 | 必须超越的浅层讲法 |
|---|---|---|
| [Agent Skills #139](https://github.com/linhongcun/video-studio/issues/139) | Skill解决的不是再写一段提示词，而是怎样把可复用的工作方法打包、发现，并在有限上下文中按需使用。 | 名称/描述供发现与路由，完整指令在激活时加载，参考资料和脚本按需要读取；说明渐进加载为何影响上下文占用与触发质量。 |
| [MCP #138](https://github.com/linhongcun/video-studio/issues/138) | MCP究竟统一了哪层契约，哪些复杂性仍要由Host、Server与业务系统承担？ | 以同一外部能力的接入变化，展开Host/Client/Server、能力发现、请求/结果与数据访问职责。 |
| [Subagent #146](https://github.com/linhongcun/video-studio/issues/146) | 委派为何可能提高表现，又为何可能增加费用、丢失关键信息或制造文件冲突？ | 沿任务说明→子任务上下文→工具/环境→结果返回解释委派，区分角色名称、独立模型调用、上下文边界与权限边界。 |
| [Goal #248](https://github.com/linhongcun/video-studio/issues/248) | 谁凭什么判定目标完成？ | 目标/约束/计划/反馈分离，执行者与评估者、真实证据及继续和停止语义，超过while循环。 |

建议先研究Skills，再看MCP、Subagent、Goal。每项先用一个有解释力的对照检验内容密度，不能只堆术语或重放操作流程。区别是切入点，必须进入机制和取舍。

## 后续研究与储备

| 候选 | 当前问题 | 研究优先级 |
|---|---|---|
| [Context Engineering #135](https://github.com/linhongcun/video-studio/issues/135) | 上下文工程如何在每次调用中选择、组织、更新真正相关的信息，而不只是把更多资料塞给模型？ | 后续深入研究 |
| [Agent Harness #149](https://github.com/linhongcun/video-studio/issues/149) | 运行系统怎样组织模型、上下文、工具、会话状态与验证反馈，而不只是把读文件、改代码、跑测试重放一遍？ | 后续深入研究 |
| [Agent Memory #137](https://github.com/linhongcun/video-studio/issues/137) | 记忆的难点在写什么、何时召回、怎样更新纠错和遗忘；不能只演示跨会话读写一个偏好。 | 后续储备；先审独立增量 |
| [Durable Execution #140](https://github.com/linhongcun/video-studio/issues/140) | 长任务中的模型决策、持久状态和外部副作用怎样协调，为什么保存检查点不等于安全恢复？ | 后续储备；先审与既有幂等/事务系列的增量 |
| [Prompt Injection / Guardrails #142](https://github.com/linhongcun/video-studio/issues/142) | 外部内容、模型指令与真实执行权限之间的信任边界在哪里，各类Guardrails到底能限制什么？ | 后续深入研究 |
| [Agent Evals #144](https://github.com/linhongcun/video-studio/issues/144) | 评估Agent时，最终环境状态、执行轨迹和模型评分分别能证明什么？ | 后续深入研究 |
| [Context Compaction #147](https://github.com/linhongcun/video-studio/issues/147) | 有损上下文压缩可能遗漏后续所需信息时，如何保留目标、约束和证据入口，避免把摘要误当成完整事实？ | 后续储备；与上下文、记忆片交叉审读 |

## 旧选题处置

原20项为**1项完成历史＋9项撤题＋10项重构开放**；新增Goal后共11项开放候选。A/B编号保留作身份，旧前置链不再约束拍摄顺序。

| 旧项 | 当前处理与内容去向 |
|---|---|
| [A01 #131](https://github.com/linhongcun/video-studio/issues/131) | 保留completed制作历史；V3/v0.54.3曾上线，现已按用户要求撤下，发布内容与相关工程删除，不再作为在线课程。 |
| [#132](https://github.com/linhongcun/video-studio/issues/132) | not_planned；与A01重复，独立增量不足；工具请求、应用执行和结果回传作为后续概念的必要前置简述，不再把接线本身单独做一期。A02 V1/EP.28/v0.59.0曾上线，用户反馈价值不足；关闭表示取消独立重制，后续用户要求将原片和工程一并删除，不表示完成了改进或用户认可。上一版“真实模型＋工具循环”重拍建议同时撤回。 |
| [#133](https://github.com/linhongcun/video-studio/issues/133) | not_planned；自由文本/JSON/Schema/业务校验的基础接续不足以构成本系列独立一期；必要契约放在具体概念使用处解释，不以字段校验教程撑起单集。 |
| [#134](https://github.com/linhongcun/video-studio/issues/134) | not_planned；最小循环、继续/结束分支与步数限制偏基础接线，退出独立制作；目标驱动的Agent将另建Goal选题，研究目标、证据、评估器和终止语义，不把旧循环改标题后继续。 |
| [#136](https://github.com/linhongcun/video-studio/issues/136) | not_planned；原计划主要解释检索→拼上下文→生成的基础RAG流程，退出独立制作；检索选择、证据时效和上下文预算按后续概念需要解释。此决定不代表RAG整体没有研究深度。 |
| [#141](https://github.com/linhongcun/video-studio/issues/141) | not_planned；保存参数→等待批准→执行的基础审批流程不独立成片；保留实际权限、批准范围与执行边界的必要讨论。 |
| [#143](https://github.com/linhongcun/video-studio/issues/143) | not_planned；原计划侧重沿模型/工具日志排查常见故障，退出独立制作；执行轨迹作为检验概念和定位差异的证据，纳入评估与运行架构讨论。 |
| [#145](https://github.com/linhongcun/video-studio/issues/145) | not_planned；通用token、请求数与等待时间优化技巧不独立成片；具体开销必须结合上下文选择、委派与运行预算取舍解释。 |
| [#148](https://github.com/linhongcun/video-studio/issues/148) | not_planned；不再为MCP与Skills基础区别及组合使用另拍第三支重复对比片；该issue中Skills over MCP扩展的有价值部分并入两支主片，保留发现/分发、加载/执行、宿主支持、完整性与信任边界，不能用“一个给工具、一个给方法”作绝对划分。 |
| [#150](https://github.com/linhongcun/video-studio/issues/150) | not_planned；撤回以工单应用整合为终点的基础开发课程主线；把已讲功能再次串起来不保证新增机制理解或判断力。后续各概念按最能解释机制的例子设计，不强制套同一个退款工单。 |

其余十个旧issue已按上方研究范围重写，旧内容折叠为历史。该次仅处理策划与记录；随后本轮按用户要求删除两期，未制作或重渲替代视频。线上删除效果以撤下记录的实际部署核验为准。

## 内容与证据要求

- 面向已会基本编程的观众，用清楚场景或对照解释概念，不补一整套API接线前置课。
- 每项有出现原因、机制、近似方案差异与代价/失效边界；去掉热门标题后仍应值得观看。
- 代码、协议报文、交互和图解服务于论证，不把可运行工程设为所有概念片的统一门槛。涉及实际行为和性能时运行验证，示意与实测分别标注。
- 重新核验第一方资料、发布日期、产品/宿主/协议适用范围；不从官方文档存在推出“最热门”，也不从厂商案例推出普遍收益。
- 用户观看反馈、内容审读、技术QA与发布检查分别记载。当前新方向尚无成片效果结论。

## 本轮一手资料

访问2026-10-25（北京时间）；下方旧S01–S19仍可检索，版本与兼容性以当前核验和开工实测为准。

- [Agent Skills规范](https://agentskills.io/specification)：渐进加载和技能包结构。
- [MCP 2026-07-28规范](https://modelcontextprotocol.io/specification/2026-07-28)：无状态核心与逐请求能力协商，不能沿用旧初始化/会话叙事。
- [Skills over MCP](https://modelcontextprotocol.io/extensions/skills/overview)：可选扩展的发现与获取，不自动等于激活/执行；支持情况依宿主。
- [Claude Code Subagents](https://code.claude.com/docs/en/sub-agents)：上下文、权限、fork与环境隔离的区别，限该产品实例。
- [Claude Code Goal](https://code.claude.com/docs/en/goal)：评估者只读对话证据，不独立运行环境检查；Goal不是统一标准。
- [Context Engineering](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)、[Managed Agents架构](https://www.anthropic.com/research/managed-agents)、[Agent Evals](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)：后续机制研究的原始工程资料。

## 原始2026-10-24题库与资料档案

**以下仅保留研究及决策历史，原系列名、学习顺序、前置、演示和待排期状态均被上方当前安排取代。** 当时用户认可原题库，不代表对本次新命题或A02成片的认可；原“其余18项待排期”等数量不得用于当前状态判断。A01/A02媒体和QA仅通过删除前固定Git提交查阅，当前课程与工程已移除；撤题与删除均不改写历史。

<details>
<summary>展开原16期主线＋4项深入方向及S01–S19资料索引（历史方案）</summary>

## 系列定位与资料使用

建议系列名：**Agent 开发：从工具调用到可靠执行**。

目标观众：会基本编程、知道接口和 JSON，尚未系统开发过 Agent 的观众。各期先建立概念，再解释实现与选择；模型训练、数学推导和特定框架安装不作为入门前置。

选题按四个问题递进：Agent 怎样做事 → 怎样获得所需信息和能力 → 怎样正确恢复和控制操作 → 怎样证明改动有效。顺序是结合项目教学风格作出的编排判断，官方资料提供技术依据，不提供本项目的流量保证或行业热度排名。

资料主要来自协议维护者、产品/框架官方文档和原始工程总结。动态文档未标日期时如实注明；厂商实践只证明其报告的实现和场景，不能把收益推广到所有 Agent。旧工程文章可解释稳定概念，接口实现需要回到当前文档核对。

贯穿示例建议采用**退款工单 Agent**：查询示例订单 → 检索对应版本的退款政策 → 判断还缺哪些信息 → 生成带依据的处理建议 → 经应用层校验和审批后创建测试工单。前几期只查询和生成建议；后续写操作限定在测试服务。示例全部使用合成数据，域名使用 .example。

从 A04 的首个可运行示例就记录模型/工具事件，并用少量固定案例核对最终结果；A13、A14 再系统讲调试与评估。审批、权限和测试数据同样按实际演示需要从第一天落实，教学顺序不代表推迟这些措施。

## GitHub 选题跟踪

2026-10-24 用户已认可选题并要求先登记 issue，后续分批制作。系列总览：[#130](https://github.com/linhongcun/video-studio/issues/130)。以下 20 个选题均已建单，创建时为待排期；后续进度以 GitHub issue 的实际状态为准。

用户随后要求先做一期看效果，A01 / EP.22 已制作并按反馈更新至 V3，当前成片与检查入口见 [制作说明](https://github.com/linhongcun/video-studio/blob/321e8e8c1b4ad34a6ea09eed2bb5cf369d9ab6dd/episodes-codex/agent-intro-v3/README.md)；发布及线上核验见 #131。2026-10-25用户要求拉取最新代码后继续下一期，已启动A02 / EP.28；[本期工程](https://github.com/linhongcun/video-studio/blob/321e8e8c1b4ad34a6ea09eed2bb5cf369d9ab6dd/episodes-codex/agent-tool-execution/README.md)重新核验官方资料，实际本地HTTP演示有权限查询1次、无权限拒绝0次，模型侧为固定fixture。成片及上线状态以#132为准，其余18项继续待用户后续安排。

| 学习编号 | 选题 issue |
|---|---|
| A01 | [#131 AI 能回答问题，怎么才能真正帮你办事？](https://github.com/linhongcun/video-studio/issues/131) |
| A02 | [#132 AI 说要调用工具，到底是谁在执行？](https://github.com/linhongcun/video-studio/issues/132) |
| A03 | [#133 AI 返回了一段话，程序怎么稳定地接着处理？](https://github.com/linhongcun/video-studio/issues/133) |
| A04 | [#134 一个最小 Agent，怎么跑起来，又怎么停下来？](https://github.com/linhongcun/video-studio/issues/134) |
| A05 | [#135 提示词没变，Agent 为什么还是答错了？](https://github.com/linhongcun/video-studio/issues/135) |
| A06 | [#136 AI 怎么查到你自己的资料？RAG 的数据怎样走？](https://github.com/linhongcun/video-studio/issues/136) |
| A07 | [#137 换个会话，Agent 怎么还记得你？](https://github.com/linhongcun/video-studio/issues/137) |
| A08 | [#138 接了工具，为什么还需要 MCP？](https://github.com/linhongcun/video-studio/issues/138) |
| A09 | [#139 Agent Skills 是什么，怎样把工作方法交给 Agent？](https://github.com/linhongcun/video-studio/issues/139) |
| A10 | [#140 Agent 做到一半断了，恢复后为什么又办了一遍？](https://github.com/linhongcun/video-studio/issues/140) |
| A11 | [#141 Agent 要修改数据，怎样等人批准后再执行？](https://github.com/linhongcun/video-studio/issues/141) |
| A12 | [#142 网页里藏一句话，为什么会让 Agent 偏离任务？](https://github.com/linhongcun/video-studio/issues/142) |
| A13 | [#143 Agent 说完成了，究竟是哪一步出了问题？](https://github.com/linhongcun/video-studio/issues/143) |
| A14 | [#144 换了模型或提示词，怎么知道 Agent 真的变好了？](https://github.com/linhongcun/video-studio/issues/144) |
| A15 | [#145 Agent 怎么越跑越贵，又该从哪里优化？](https://github.com/linhongcun/video-studio/issues/145) |
| A16 | [#146 多个 Agent 一起干，什么时候才值得？](https://github.com/linhongcun/video-studio/issues/146) |
| B01 | [#147 任务没做完，上下文满了怎么办？](https://github.com/linhongcun/video-studio/issues/147) |
| B02 | [#148 有了 MCP，为什么还需要 Skills？它们怎样一起用？](https://github.com/linhongcun/video-studio/issues/148) |
| B03 | [#149 编程 Agent 背后的 Harness，到底做了什么？](https://github.com/linhongcun/video-studio/issues/149) |
| B04 | [#150 从零串起一个能恢复、可审批、可评估的工单 Agent](https://github.com/linhongcun/video-studio/issues/150) |

## 16 期主线

### A01 AI 能回答问题，怎么才能真正帮你办事？

- 核心问题：模型生成回复、预先编排的工作流、由模型动态选择下一步的 Agent，分别由谁控制执行过程？
- 拟演示：同一退款咨询，依次展示生成回复、固定查询流程、根据查询结果选择补充信息或继续处理的流程。
- 前置：无需 Agent 知识；片中补足模型与应用程序的区别。
- 本期边界：介绍一种实用的架构区分，不宣称 Agent 存在唯一公认定义；工具调用也可以用于固定工作流。把是否完成业务目标与是否结束生成分开。
- 依据：[S01]、[S02]。学完应能指出哪一步由程序预定、哪一步由模型决定。

### A02 AI 说要调用工具，到底是谁在执行？

- 核心问题：工具描述、调用请求、应用执行和工具返回值怎样衔接？
- 拟演示：模型提出查询订单的工具名及参数 → 程序校验 → 测试接口返回订单 → 结果交回模型；插入一次参数不合法或接口失败。
- 前置：A01，基本接口知识。
- 本期边界：生成调用请求不等于操作已执行；模型能选工具不代表获得对应业务权限。应用可以自行执行，也可以由托管运行环境执行。
- 依据：[S03]。学完应能从日志中区分模型提议和真实执行。

### A03 AI 返回了一段话，程序怎么稳定地接着处理？

- 核心问题：自由文本、合法 JSON、符合 Schema 的结构化输出分别保证到哪一层？
- 拟演示：把处理建议转成明确字段，展示缺字段、非法枚举被拦下，以及格式合法但订单号或资格判断仍然错误的情况。
- 前置：A02，JSON；Schema 在本期解释。
- 本期边界：结构符合约定不保证事实正确或业务合法；程序仍要处理拒绝、输出不完整和领域校验。工具参数契约与面向用户的结构化回答分别说明。
- 依据：[S04]。学完应能区分格式检查和业务检查。

### A04 一个最小 Agent，怎么跑起来，又怎么停下来？

- 核心问题：把前面零散的调用连成执行循环后，怎样处理继续、结束、缺信息和失败？
- 拟演示：查询订单 → 查询政策 → 输出建议；缺订单号时询问，持续无进展时达到应用设定的步数/预算限制并结束或交人处理。
- 前置：A01–A03。
- 本期边界：展示调用和结果等可观察记录，不把动画里的步骤说明冒充模型隐藏思考；停止生成也不自动证明业务完成。
- 依据：[S02]、[S03]；步数和预算是本示例的应用设计。产物为可追踪的一次完整执行和最小结果核对。

### A05 提示词没变，Agent 为什么还是答错了？

- 核心问题：每次调用真正送入模型的内容有哪些，怎样筛选与组织？
- 拟演示：显示指令、工具定义、历史、政策片段和工具结果；对比杂乱输入与保留相关证据的输入，用相同案例检查差异。
- 前置：A04。
- 本期边界：上下文工程包含整个输入的构成和更新；更长、更短都不自动更好。具体整理策略要随模型和任务重新评估。
- 依据：[S05]、[S19]。画面用具体输入块的进入/退出展示变化，避免整屏术语表。

### A06 AI 怎么查到你自己的资料？RAG 的数据怎样走？

- 核心问题：业务资料怎样经过检索进入本次回答？
- 拟演示：提问 → 检索对应版本政策 → 带来源片段进入上下文 → 生成有依据的建议；切换政策版本并展示找不到或证据不足的分支。
- 前置：A02、A05。
- 本期边界：RAG 不等于训练模型，也不必须新建向量数据库；SQL、文档系统等已有来源可以接入。先讲固定检索流程，再解释 Agent 自主决定何时检索的变化。
- 依据：[S06]。分开核对检索是否找对、回答是否得到证据支持；数据读取权限由应用保证。

### A07 换个会话，Agent 怎么还记得你？

- 核心问题：会话历史、跨会话记忆与当前模型输入怎样联系？
- 拟演示：同一用户切换会话后读取明确保存的语言偏好；换用户后不读取；更新偏好，再检查旧值是否被替换。
- 前置：A05、A06。
- 本期边界：短期/长期记忆按作用范围区分，不能直接对应“内存/数据库”；保存过的信息仍需按需读入当前上下文。偏好记忆不能替代权威业务记录。
- 依据：[S07]。示例同时展示用户隔离、更新和删除入口。

### A08 接了工具，为什么还需要 MCP？

- 核心问题：Host、Client、Server 怎样发现和接入能力，协议统一了哪些交互？
- 拟演示：同一个 Agent 接入两个示例服务，发现可用工具并调用；把模型选择工具、协议传递请求、服务执行分层显示。
- 前置：A02、A04。
- 本期边界：MCP 不自动完成业务编排，也不保证推理或操作结果正确；接入服务与获得业务授权分别处理。术语和具体报文分层展开。
- 依据：[S08]。本次核验以 2026-07-28 规范为基线；旧版握手和会话流程不能直接当作本版必需步骤。

### A09 Agent Skills 是什么，怎样把工作方法交给 Agent？

- 核心问题：任务说明、配套脚本和参考资料怎样按需加载？
- 拟演示：先发现技能名称与描述，再加载 SKILL.md，按需读退款审核清单；用相同案例核对流程是否被遵循。
- 前置：A04、A05；A08 帮助理解其与能力接入的区别。
- 本期边界：Skill 不重新训练模型；格式兼容、触发和脚本运行支持取决于宿主。不能简单把 MCP 和 Skills 说成互斥方案；更深入的协作放 B02。
- 依据：[S09]。2026-10-22 的治理更新可作文章背景，主体仍讲加载机制与任务流程，不把厂商安装量当本期效果证据。

### A10 Agent 做到一半断了，恢复后为什么又办了一遍？

- 核心问题：持久化执行状态怎样与外部副作用配合？
- 拟演示：创建测试工单后进程退出，恢复时重复创建；加入持久化检查点和业务幂等标识，再核对最终工单数量。
- 前置：A04；可链接项目既有幂等、分布式事务视频。
- 本期边界：保存检查点不自动实现外部操作恰好一次；恢复可能重跑节点或节点前半段。区分连接断开、执行进程退出和业务结果未知。
- 依据：[S10]、[S11]。这里讲应用状态恢复，不与 MCP Tasks 的远程任务跟踪混为一谈。

### A11 Agent 要修改数据，怎样等人批准后再执行？

- 核心问题：怎样让审批控制真正的执行边界？
- 拟演示：保存待执行工具和参数 → 暂停 → 批准或拒绝 → 恢复同一次运行；修改参数后要求重新确认。
- 前置：A10。
- 本期边界：模型生成“用户已批准”不构成应用授权。哪些操作需要审批由产品和权限设计决定，不是所有工具调用都应弹窗；审批应发生在相应副作用之前。
- 依据：[S11]。区分输入检查、输出检查、工具边界检查及审批。

### A12 网页里藏一句话，为什么会让 Agent 偏离任务？

- 核心问题：不可信内容怎样影响工具选择和数据流，怎样限制影响范围？
- 拟演示：在自建测试政策页中加入无害的指令诱导，显示资料来源边界、只读权限、隔离执行及外联限制分别在哪一步生效。
- 前置：A02、A05、A11。
- 本期边界：可信连接器也可能读回不可信内容；过滤、审批、沙箱各有作用范围。以明确威胁和可观察结果评估，不承诺彻底消除提示注入。
- 依据：[S12]、[S19]。只使用合成诱导和测试权限，不需要真实敏感数据。

### A13 Agent 说完成了，究竟是哪一步出了问题？

- 核心问题：怎样沿一次执行记录定位模型、工具、网络或业务检查的问题？
- 拟演示：分别制造查错订单、工具超时、未创建工单却声称成功；沿模型请求、工具参数、返回值、异常和最终状态定位差异。
- 前置：A04；承接此前各期已有的最小事件记录。
- 本期边界：Trace 是可观察的执行过程，不等于模型全部内部思考。记录可能含用户内容，需要脱敏与保留策略。
- 依据：[S13]。产物为能够定位失败环节的执行记录，而非仅一行最终回复。

### A14 换了模型或提示词，怎么知道 Agent 真的变好了？

- 核心问题：怎样建立可重复比较的任务评估？
- 拟演示：固定正常、缺信息、政策冲突、超时和重复请求案例，对旧版新版多次运行；核对最终状态、规则遵守、成本和延迟，保留未参与调参的案例。
- 前置：A13，清楚的业务成功标准。
- 本期边界：工具成功、JSON 合法、回复流畅和自报完成都不能单独证明目标完成；模型评分也要校准。区分重复运行的一致性和一次成功。
- 依据：[S14]。所有改善数字来自制作时实测，记录模型、配置、测试集和运行次数。

### A15 Agent 怎么越跑越贵，又该从哪里优化？

- 核心问题：成本和延迟分别花在输入、生成、调用次数还是工具等待上？
- 拟演示：在同一评估集上比较全量工具定义与按需发现、冗长结果与保留相关字段、串行与独立查询并行；逐项记录质量、token、工具费用和总耗时。
- 前置：A05、A13、A14。
- 本期边界：减少 token 不保证每种场景都更快；发现工具也增加步骤。固定模型与计价日期，不做跨供应商通用“省多少倍”的承诺。
- 依据：[S15]。先定位实际瓶颈，再做一次只改变一个主要因素的比较。

### A16 多个 Agent 一起干，什么时候才值得？

- 核心问题：任务可并行性、上下文分工和交接成本怎样影响效果？
- 拟演示：用单 Agent 与协调者/子 Agent 比较两个任务：可独立的多来源检索，以及必须共享最新状态的业务处理；同口径测质量、总费用、耗时和交接丢失信息。
- 前置：A05、A13–A15。
- 本期边界：角色数量不代表能力提升；Agent 之间能通信也不保证状态一致。厂商在研究任务中的收益不能直接推广到退款、编程等任务。
- 依据：[S16]。多 Agent 放在已有单 Agent 基线和评估之后，再决定是否增加复杂度。

## 4 个深入方向

| 编号 | 题目 | 演示与前置 | 资料与边界 |
|---|---|---|---|
| B01 | 任务没做完，上下文满了怎么办？ | 前置 A05、A07；比较压缩前后目标、约束、证据路径和未完成项，继续执行并核对关键条件。 | [S17]、[S19]；压缩可能丢信息，需有可恢复原始记录；官方示例使用合成资料，不能包装为真实客户收益。 |
| B02 | 有了 MCP，为什么还需要 Skills？它们怎样一起用？ | 前置 A08、A09；用明确支持扩展的客户端演示远程发现技能、按需读取资料、再调用工具。 | [S18]；Skills over MCP 是正式扩展，但宿主/SDK 支持仍各异。读取文件不等于自动激活；校验完整性不等于内容可信。 |
| B03 | 编程 Agent 背后的 Harness，到底做了什么？ | 前置 A04、A10–A14；在合成小仓库中展示读文件、修改、运行测试、接回错误并修正；分清运行循环、会话记录与执行环境。 | [S02]、[S19]；沿已核验开源实现/官方工程解释，不推断闭源产品所有内部细节，不把测试通过等同需求完全满足。 |
| B04 | 从零串起一个能恢复、可审批、可评估的工单 Agent | 前置主线；把订单查询、政策检索、审批、创建测试工单、故障恢复和结果核对串成分章实战。 | 复用对应主线来源。此片负责整合，不能代替前置概念；可分上下集，依内容完整性定长度。 |

MCP Tasks、Computer Use、A2A 和特定框架比较可以进入储备池。先根据实际任务和所用实现补充正文调研，再决定是否扩成独立选题，不与核心入门混排。

## 建议的首批与制作方式

第一批按 A01 → A02 → A03 → A04，形成“理解 Agent → 理解调用 → 明确数据契约 → 看见完整运行”的入口。第二批推进 A05–A09；其中 MCP、Skills 的配套文章可提前准备，但保留必要的前置入口。

后续排期综合观众评论中的疑问、观看反馈、示例可复现程度与技术更新决定。当前没有本项目相关视频的效果数据，不能按资料更新频率推断哪期一定获得更高播放。

每期保留概念解释和实现深度的边界：视频先用对象与状态变化建立主线；文章补代码、报文、版本兼容、参考资料和实验配置。实验失败要真实记录；未运行的流程写成拟演示，不用预制输出冒充实测。

开拍前重新核对核心页面和版本：模型标识、SDK 锁文件、MCP revision、宿主/扩展支持、计价日期。若官方正文与本文快照冲突，以重新核验后的事实修订脚本。

## 资料索引与关键证据

下面全部为一手公开来源，统一访问日期为 **2026-10-24（北京时间）**。每项标出页面自己的日期；“动态文档，未标”表示没有可靠的页面发布日期，不把搜索引擎抓取时间当首发时间。

### S01 工作流与 Agent 的架构区分

- [Building effective agents][S01]，Anthropic，2024-12-19。
- 支持：区分预先定义的编排与模型动态控制的执行方式，并按需求增加复杂度。
- 限定：正文已提示工具生态发生变化；这里只用于概念和架构取舍，不把 2024 年接口当当前实现。

### S02 实际编程 Agent 的执行循环

- [Unrolling the Codex agent loop][S02]，OpenAI，2026-01-23。
- 支持：模型产生回复或调用请求，运行层执行工具、回传结果并再次请求模型；环境修改也属于实际产物。
- 限定：描述该文时期的 Codex 实现，不能推导所有 Agent 都有完全相同的流程。

### S03 工具调用契约

- [Function calling][S03]，OpenAI，动态文档，未标。
- 支持：定义工具、接收模型调用、应用执行、回传输出和继续请求的步骤。
- 限定：Responses、Chat Completions 与 Agents API 的接法分别说明，不能混抄参数；视频代码需要锁定具体接口。

### S04 结构化输出的保证与限制

- [Structured model outputs][S04]，OpenAI，动态文档，未标。
- 支持：区分合法 JSON 与符合 Schema；正文也说明结构化结果仍可能包含错误。
- 限定：处理拒绝和输出不完整；格式检查不替代事实、权限和业务规则检查。

### S05 上下文工程

- [Effective context engineering for AI agents][S05]，Anthropic，2025-09-29。
- 支持：从整个模型输入及其随执行变化的角度管理信息，包括工具、历史和按需获取资料。
- 限定：具体提示与整理策略会随模型变化；只把它作为可验证的工程方法，不当作普遍定律。

### S06 检索与 RAG

- [Retrieval][S06]，LangChain，动态文档，未标；当前正文位于 Deep Agents 文档。
- 支持：检索外部信息进入生成流程；已有 SQL、CRM、文档系统可直接接入；区分固定检索与 Agent 决定检索。
- 限定：取回资料不保证相关、最新或授权正确，RAG 效果要分检索和生成两层核对。

### S07 记忆的作用范围

- [Memory overview][S07]，LangChain，动态文档，未标。
- 支持：会话内状态可持久化，跨会话记忆可按命名空间存取；两者按召回范围区分。
- 限定：本文借其概念说明作用范围，checkpointer/store 等名称是具体框架实现。

### S08 MCP 规范与版本变化

- [2026-07-28 规范][S08]，规范版本日期 2026-07-28；[同日官方发布说明](https://blog.modelcontextprotocol.io/posts/2026-07-28/)。
- 支持：该版本引入无状态协议核心，取消旧 initialize/initialized 交换与 Mcp-Session-Id；Tasks 转为扩展。
- 限定：协议层无会话不表示业务不得保存状态；弃用不等于旧实现即刻不能运行。路线图中的计划不能当成交付能力。

### S09 Agent Skills 格式与近期治理更新

- [Agent Skills Specification][S09]，动态规范，未标。
- 支持：SKILL.md 及可选脚本/参考资料结构；启动时加载技能名称与描述，激活时加载 SKILL.md 正文，配套资源按需读取。allowed-tools 仍标实验性、支持因实现而异。
- [Donating Agent Skills to the Agentic AI Foundation](https://www.anthropic.com/news/donating-agent-skills-to-the-agentic-ai-foundation)，Anthropic，2026-10-22。支持开放标准的近期治理变化，不据此推导本项目观众需求或跨平台行为完全一致。

### S10 持久化执行

- [Persistence][S10]，LangGraph，动态文档，未标。
- 支持：通过持久化检查点保留运行状态和恢复入口。
- 限定：持久化对象、后端和重放边界须按所用版本验证；不要用进程内保存器演示跨进程恢复成功。

### S11 中断与审批

- [Interrupts][S11]，LangGraph，动态文档，未标。支持保存状态、暂停、携带外部输入恢复；正文提醒恢复时中断所在节点从头执行。
- [Guardrails and human review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)，OpenAI，动态文档，未标。支持区分不同位置的检查和人工审批。
- 限定：不能把节点前半段外部副作用视作自动去重；不能让模型自报批准代替应用授权。

### S12 不可信内容与隔离边界

- [How we contain Claude across products][S12]，Anthropic，2026-05-25。
- 支持：以实际产品隔离与约束方式讨论提示注入等风险的影响范围。
- 限定：具体防护依产品、部署和威胁而定，不能说单项措施消灭所有提示注入。

### S13 执行追踪

- [Tracing][S13]，OpenAI Agents SDK，动态文档，未标。
- 支持：trace/span 记录模型、工具等运行事件及导出控制。
- 限定：记录可观察过程，不表示读取全部内部推理；按需要处理敏感输入输出。

### S14 Agent 评估

- [Demystifying evals for AI agents][S14]，Anthropic，2026-01-09。
- 支持：区分任务、重复试验、评分、执行记录与最终环境结果，结合多种方法判断任务表现。
- 限定：评估标准依任务定义；评分器及测试集也需检查，不能只以模型自报完成为依据。

### S15 成本、延迟与工具发现

- [Cost optimization][S15]、[Tool search](https://developers.openai.com/api/docs/guides/tools-tool-search)，OpenAI，均为动态文档，未标。
- 支持：从请求数、token、模型选择等因素定位费用；工具定义可按需发现，发现过程也有开销。
- 限定：不同 API 配置和模型支持范围各异；文中建议不能代替本项目实测，价格和收益需写日期与口径。

### S16 多 Agent 的实际取舍

- [Building multi-agent systems: When and how to use them][S16]，Anthropic，2026-01-23。
- [How we built our multi-agent research system](https://www.anthropic.com/research/multi-agent-research-system)，Anthropic，2025-06-13。
- 支持：围绕上下文隔离、任务并行、分工与协调解释多 Agent 的适用条件和成本。
- 限定：研究系统案例不等于所有任务的普遍收益；比较时保留单 Agent 基线。

### S17 上下文压缩与长期记忆的代码示例

- [Building Reliable Agents with Memory and Compaction][S17]，OpenAI Cookbook，2026-05-01。
- 支持：用当前任务压缩、跨任务经验与独立事实产物解释不同状态用途。
- 限定：示例材料为合成资料；代码阅读不等于本轮已复现实验，不把示例写成真实客户效果。

### S18 Skills over MCP

- [Skills extension][S18]，MCP 官方动态文档，未标。
- 支持：正文标注 SEP-2640 为 Final，通过发现和 Resources 读取 Skills；明确 SDK 与宿主支持仍在实现。
- 限定：读取 SKILL.md 不自动激活技能；需要按当前客户端支持和来源/内容校验流程演示。

### S19 长任务运行架构

- [Scaling Managed Agents: Decoupling the brain from the hands][S19]，Anthropic，2026-04-08。
- [Introducing the Agents API](https://openai.com/index/introducing-the-agents-api/)，OpenAI，2026-09-10。
- 支持：实际系统分别管理运行循环、持久会话与执行环境，以及长任务中的上下文管理和恢复问题。
- 限定：各服务接口和保证不同，不把厂商架构或效果数字推广成所有实现的必备结构或收益。

[S01]: https://www.anthropic.com/research/building-effective-agents
[S02]: https://openai.com/index/unrolling-the-codex-agent-loop/
[S03]: https://developers.openai.com/api/docs/guides/function-calling
[S04]: https://developers.openai.com/api/docs/guides/structured-outputs
[S05]: https://www.anthropic.com/research/effective-context-engineering-for-ai-agents
[S06]: https://docs.langchain.com/oss/python/deepagents/retrieval
[S07]: https://docs.langchain.com/oss/python/concepts/memory
[S08]: https://modelcontextprotocol.io/specification/2026-07-28
[S09]: https://agentskills.io/specification
[S10]: https://docs.langchain.com/oss/python/langgraph/persistence
[S11]: https://docs.langchain.com/oss/python/langgraph/interrupts
[S12]: https://www.anthropic.com/research/how-we-contain-claude
[S13]: https://openai.github.io/openai-agents-python/tracing/
[S14]: https://www.anthropic.com/research/demystifying-evals-for-ai-agents
[S15]: https://developers.openai.com/api/docs/guides/cost-optimization
[S16]: https://claude.com/resources/articles/building-multi-agent-systems-when-and-how-to-use-them
[S17]: https://developers.openai.com/cookbook/examples/agents_sdk/building_reliable_agents_memory_compaction
[S18]: https://modelcontextprotocol.io/extensions/skills/overview
[S19]: https://www.anthropic.com/research/managed-agents

</details>
