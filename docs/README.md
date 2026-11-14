# 项目文档

这里区分现行手册、持续维护的记录与已完成任务的历史证据。项目概览见[仓库 README](../README.md)，协作入口见 [AGENTS.md](../AGENTS.md)。

内容统一放在 `episodes/<series>/<slug>/`：`production/` 是制作工程与修订，`publication/` 是站点读取的发布内容；共享工具在 `episodes/_shared/`，新期模板在 `episodes/_template/`。本次按用户授权完成实体合并；旧路径、冻结身份与适配代码前后SHA见[迁移记录](archive/2026-11/episode-layout/README.md)，这次整理不代表重新制作或审片，重渲仍须冻结当前实际输入。

## 规范与制作手册

[RULES.md](RULES.md) 是规范的唯一真源；下列手册说明具体步骤和工具，本页只提供入口。

| 文档 | 用途 |
| --- | --- |
| [新环境制作与工具交接](production-setup.md) | 新机器依赖、当前入口定位、阶段产物与跨 coding 工具接续 |
| [制作流程](pipeline.md) | 从调研、脚本、分镜到配音、渲染、校验和发布 |
| [调研模板](research-template.md) | 公开来源、论点依据和参考资料清单 |
| [图文写作说明](article-style.md) | 起稿提纲、推导顺序、详略与排版、小结、引用配图及发布派生稿 |
| [分镜结构](storyboard-schema.md) | 分镜字段、时序和冻结输入 |
| [配音](voice.md) | TTS、整轨、发音及起音对齐 |
| [渲染](render.md) | 正文、代码卡、参考资料和封面的生成入口 |
| [校验](validate.md) | 校验命令、阈值与只读检查 |
| [质检清单](qa.md) | 冻结后预检和正式成片复核 |
| [发布](publish.md) | 站点与平台流程、版本和视频日期维护 |
| [制作说明模板](production-notes.template.md) | 交接记录格式；[EP.14 示例](examples/knoll-props.degradation.md) |

开新期使用[新期模板](../episodes/_template/README.md)；共享句级装配、时序、冻结和编码入口见[制作工具说明](../episodes/_shared/README.md)。

## 经验与项目记忆

| 文档 | 记录内容 |
| --- | --- |
| [教训](lessons-learned.md) | 已发生的问题、原因、修正措施和验证范围 |
| [成功经验](successful-practices.md) | 有实际证据支持的有效做法及适用边界 |
| [项目制作记忆](production-memory.md) | 用户偏好、指导和案例状态，包括尚未验证的建议 |

制作、返工及收到反馈时，从这些记录确认已有结论；单期参数和一次技术检查的结论仍以对应版本为限。

## 现行策划

[图文文章结构调研与重构方案](archive/2026-11/article-structure-research/README.md)整理业界来源与分类依据，用户确认后的六环节已进入 `RULES.md`、写作说明和模板；59篇应用与文章目录实现见[重构记录](archive/2026-11/article-structure-refactor/README.md)。

[AI / Agent 概念选题与资料依据](agent-development-topics.md)维护当前概念方向、研究候选和已有制作状态。候选及研究优先级不等于固定排期；具体任务状态以其中关联的 issue 和本期记录为准。

## 参考资料补齐

[存量清单](reference-endcards/inventory.json)记录固定旧片范围与各期补齐状态，并单独统计新增默认带资料的视频；[流程接入证据](reference-endcards/production-flow.json)记录新期默认生成附录及发布检查的接入结果。现行制作要求仍见上方调研、渲染、校验和发布手册。

`reference-endcards/` 中各批次的 README、检查报告和发布回执保留当次版本身份；已完成批次的入口也收录在[历史索引](archive/README.md)。

<!-- batch-12-publication-archive:start -->
固定原47期的参考资料附录已全部补齐，该批完成时48期发布视频均有附录。新片继续按现行模板默认生成与核验；完成范围、真实发布版本与边界见[最后一批归档](archive/2026-10/reference-endcards-batch-12/README.md)及[存量清单](reference-endcards/inventory.json)。旧来源与冻结证据字节保留，本次实体迁移涉及的原路径按迁移账本解读。
<!-- batch-12-publication-archive:end -->

## 历史任务与证据

[归档与历史任务索引](archive/README.md)汇总已完成的重制、修订、站点改版、仓库清理及平台整理记录。历史记录的正文、原路径与SHA保留当次制作身份；原路径因本次实体分类迁移发生变化时，通过迁移账本定位新文件，或从固定基线查看原输入。部分任务目录仍保留原位置，保留位置不表示仍在制作。

查当前单期工程时，先看 `episodes/<series>/<slug>/publication/meta.json` 的 `sourcePath`，再读对应制作目录的 README 和最新发布记录。历史报告中的帧数、SHA、版本号和检查结果只证明所列输入与当次产物；旧草案、候选构建和修前失败记录不能代替当前成片依据，技术检查也不等于用户已观看认可。

现行协作只按职责说明执行。历史记录中的旧协作称呼、账号与通知方式仅用于追溯当时情况，不作为当前工具需要寻找的人员或执行前提；冻结输入及真实出处作者保持原样。
