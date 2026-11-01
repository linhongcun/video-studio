# agent-skills · 片尾参考资料

采用presentation:title-author，四项原题与真实作者/机构，每页最多4项、默认5秒，无摘录/定位/年份日期/提示。此为来源生产，不记录编码或发布已完成。

技术实读均保留 **2026-10-25**。26日只通过正式原页补核原始工程文章的H1与Written by署名；实际H1保留完整旧题，SEO短题不拿来替代。完整返回的TinyFish提取JSON与SHA保存，不称为源站原始HTTP字节摘要；未重读技术论点或执行demo。

证据见[sources-agent-skills.json](../../docs/archive/2026-10/reference-endcards-batch-12/sources-agent-skills.json)；[固定既有实读记录](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/agent-skills/research.md)及root原before记录为本仓历史证据，不是原站全文镜像。

- 基线：`f3610e244f9e23e7a9075e406bbc990ba53b7699`
- 原research Git blob：`75489ac9a4b592e5a826d60e748be7674628bd7a`
- 原research完整SHA-256：`1d7c8a659c740ef462a8b143b0bf8b975a4d03b52b45d51754b89f2cb73b8d58`（10280字节）
- 原article完整SHA-256：`13400d15c8a90e1a1943e702032448d039ba28d583a394f9af15270c596fd186`（11294字节）

## R1 · Specification

- 发布方：Agent Skills
- 版本：Agent Skills · 动态格式规范（旧记录未标发布日期）
- 正式链接：[Specification](https://agentskills.io/specification)
- [既有实读记录（2026-10-25，R1）](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/agent-skills/research.md#L7-L14)

- 原题证据：2026-10-25既有实读记录research.md第9行，S01来源英文原题
- 旧技术阅读范围：目录结构、frontmatter、正文、可选资源与progressive disclosure。
- 镜头对应：03, 05, 06, 10, 12

旧主张：技能以目录为单位，至少有`SKILL.md`；标准要求`name`和`description`，脚本、参考资料和资产可选。元数据用于发现，正文在激活时交入上下文，资源按需使用。

适用边界：约5000 tokens、500行属于编写建议，不是宿主统一硬上限；`allowed-tools`仍标实验性，支持依实现。格式相同不保证触发、依赖、权限或运行结果相同。

## R2 · How to add skills support to your agent

- 发布方：Agent Skills
- 版本：Agent Skills · 动态客户端实现文档（旧记录未标发布日期）
- 正式链接：[How to add skills support to your agent](https://agentskills.io/client-implementation/adding-skills-support)
- [既有实读记录（2026-10-25，R2）](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/agent-skills/research.md#L16-L23)

- 原题证据：2026-10-25既有实读记录research.md第18行，S02来源英文原题
- 旧技术阅读范围：三层加载、目录生成、模型/用户激活、资源列举及会话保留。
- 镜头对应：03, 04, 05, 06, 07, 10, 11, 12

旧主张：宿主可以扫描文件，也可用API或注册表发现；将候选名称、描述及访问位置交给模型。激活可通过普通文件读取或专用工具，用户显式选择也可由宿主注入。资源列表不等于资源正文已全部加载。

适用边界：模型自动选择是常见方式，不是本期demo已经实测的能力；“没有交给模型全文”也不等于宿主从未读取底层文件。已加载内容需要会话管理、去重和压缩策略，不应表现为任务结束自动清空。

## R3 · Extend Claude with skills

- 发布方：Anthropic
- 版本：Claude Code · 动态产品文档（2026-10-25实读）
- 正式链接：[Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [既有实读记录（2026-10-25，R3）](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/agent-skills/research.md#L33-L40)

- 原题证据：2026-10-25既有实读记录research.md第35行，S04来源英文原题
- 旧技术阅读范围：普通会话的description/body加载、调用控制、标准与扩展、上下文保留、工具预授权和触发评估。
- 镜头对应：05, 08, 11

旧主张：该产品将技能作为提示指导；与常驻CLAUDE.md相比，正文在使用时加载。已加载正文作为会话消息跨轮保留，压缩时按预算续带。工具执行和模型遵循不是仅凭文件格式自动保证的。

适用边界：Claude Code允许部分frontmatter省略，不能覆盖S01标准的必填要求；`disable-model-invocation`、fork等为产品特性。其`allowed-tools`是当轮预授权，非封闭工具白名单，不表示Skill能自行授予任意能力；标准和其他宿主的同名字段不可混讲。

## R4 · Equipping agents for the real world with Agent Skills

- 作者：Barry Zhang, Keith Lazuka, and Mahesh Murag
- 发布方：Anthropic
- 版本：2025-10-16 · 原始工程文章（2025-12-18开放标准更新）
- 正式链接：[Equipping agents for the real world with Agent Skills](https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills)
- [既有实读记录（2026-10-25，R4）](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/agent-skills/research.md#L42-L49)

- 原题证据：26日正式原页h1限定提取的实际主标题；与旧research.md第44行原题一致，区别于缩短SEO title
- 旧技术阅读范围：技能结构、PDF案例、上下文过程、代码执行及先评估再补技能的建议。
- 镜头对应：03, 05, 06, 07, 08, 10, 12

旧主张：详细参考材料可以在需要时读取；配套脚本可以直接经工具执行，不必先把脚本源码或待处理文件全文塞进模型，必要结果再回传。

适用边界：旧文解释稳定设计，不作为当前SDK接口说明。确定性程序执行不等于程序正确、输入覆盖充分或完整业务兼容；本片自制检查器仅覆盖明确的必填规则。

## 署名与保留范围

原工程文章明确写：Written by Barry Zhang, Keith Lazuka, and Mahesh Murag, who all really like folders. Special thanks to the many others across Anthropic who championed, supported, and built Skills. 所以个人作者列完整三人，不以公司metadata作者或模糊“团队”代替，不遗漏Keith Lazuka。其余文档按旧明确第一方机构列出，无个人作者猜测。

旧article/research完整前缀、全部锚点、五条脚注、程序块及现有SourceQuote/Figure链接保留；原机制与本地demo/受委派模型执行的不同范围保留，没有新demo、自动触发或效果试验。未改SB/voice/words/media、共享或QA；不预记新成片/上线/用户认可。
