# tx-outbox · 片尾参考资料

采用 `presentation: title-author`：视频只列英文文献名与明确作者Chris Richardson，最多4项/页、默认5秒；不显示摘录、定位、年份/日期、链接或提示。

技术访问日及书目归属沿用 **2026-10-24（北京时间）**。本轮没有新的原站正文、当前H1或公开byline读取；作者不是由Git账号或贡献者推断。Transactional outbox忠实沿用旧英文书目题名，不凭印象添加Pattern:，也不声称证明当前页面没有分类前缀。2020文章保留完整旧原标题。

来源证据见[sources-tx-outbox.json](../../docs/reference-endcards/batch-8/sources-tx-outbox.json)；[固定既有实读记录](https://github.com/linhongcun/video-studio/blob/61d3b984a594578a67bc34aa374cccd0326cd9d6/episodes-codex/tx-outbox/research.md)及[原研究归档](../../docs/reference-endcards/batch-8/tx-outbox-evidence/prior-research-61d3b984.md)为本仓证据，非官方固定正文。

- 基线：`61d3b984a594578a67bc34aa374cccd0326cd9d6`
- 原research Git blob：`0986a194beed12659bbcfb57dd52847c3ec27a5e`
- 原research完整SHA-256：`46d4971b74525c7e0f87bb496cc9b9143584b7a41a91f3fe5535366b6f19dc5f`（2687字节）
- 原article Git blob：`5397917b4840a533ac2b27bf9f9a391761be020f`
- 原article完整SHA-256：`0878d922eeda4386c5047e6f92b741ea742816dd218814ba9b94a5b8f31a3f59`（4441字节）

## R1 · Transactional outbox

- 作者：Chris Richardson
- 发布方：microservices.io
- 版本：原作者模式文档（旧记录未标首次发表年）
- 正式链接：[Transactional outbox（原作者文章）](https://microservices.io/patterns/data/transactional-outbox.html)
- [既有实读记录（2026-10-24，R1）](https://github.com/linhongcun/video-studio/blob/61d3b984a594578a67bc34aa374cccd0326cd9d6/episodes-codex/tx-outbox/research.md#L8)
- [既有题名与作者记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/61d3b984a594578a67bc34aa374cccd0326cd9d6/episodes-codex/tx-outbox/article.mdx#L48)

- 原题位置：2026-10-24既有实读书目：article.mdx第48行，Chris Richardson：后的英文文献名
- 署名位置：article.mdx第48行的Chris Richardson明确署名，research.md第8行同名原作者资料记录
- 实际阅读段落：Solution、Participants、Result context
- 镜头：06, 07, 08, 09

支持的主张与边界：08–09：relay在发送后、记录完成前中断可重发；需要消费者处理重复。模式正文未给原始发表年，按当前原作者正文引用，不从页脚推断年龄。

## R2 · Handling duplicate messages using the Idempotent consumer pattern

- 作者：Chris Richardson
- 发布方：microservices.io
- 版本：2020-10-16 · 原作者文章
- 正式链接：[Handling duplicate messages using the Idempotent consumer pattern（原作者文章）](https://microservices.io/post/microservices/patterns/2020/10/16/idempotent-consumer.html)
- [既有实读记录（2026-10-24，R2）](https://github.com/linhongcun/video-studio/blob/61d3b984a594578a67bc34aa374cccd0326cd9d6/episodes-codex/tx-outbox/research.md#L10)
- [既有题名与作者记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/61d3b984a594578a67bc34aa374cccd0326cd9d6/episodes-codex/tx-outbox/article.mdx#L49)

- 原题位置：2026-10-24既有实读书目：article.mdx第49行，Chris Richardson：后的英文文献名
- 署名位置：article.mdx第49行的Chris Richardson明确署名，research.md第10行同名原作者资料记录
- 实际阅读段落：Why duplicate messages、Tracking IDs、PROCESSED_MESSAGE
- 镜头：10, 11, 12

支持的主张与边界：10–12：处理标识应有唯一约束，并与业务修改同一本地事务；提交后确认消息。2020-10-16原作者文章，未早于2020。

## 保留范围

原article/research全文、frontmatter、章节锚点和四条脚注完整保留，仅末尾新增片尾参考节。旧AWS Transactional outbox及Making retries资料继续保留，不将未新核实的个人作者改成AWS机构署名来凑片尾。

本轮只完成既有记录核对与来源输入，没有新官方完整正文SHA；未执行冻结、编码、声音/成片复核或发布，不预记用户认可。
