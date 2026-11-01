# tx-2pc · 片尾参考资料

采用 `presentation: title-author`：只列完整原题与机构，每页最多4项、默认5秒，不上屏摘录、定位、年份/日期、链接或提示。四项覆盖可靠准备/锁、可靠共同决定、分别落实与按原决定恢复，不以一页容量省略稳定决定依据。

技术实读：**2026-10-24（北京时间）**。题名/机构补查：**2026-10-26**，只读明确列出的官方固定题名及文档根文件；不把这些GET或其SHA当成技术正文的新读取或旧响应。

完整证据见[sources-tx-2pc.json](../../docs/reference-endcards/batch-7/sources-tx-2pc.json)；[固定既有实读记录](https://github.com/linhongcun/video-studio/blob/656b525f533037f1c0dff6383c4afa69926e612c/episodes-codex/tx-2pc/research.md)和[归档副本](../../docs/reference-endcards/batch-7/tx-2pc-evidence/prior-reading-656b525f.md)均为本仓研究记录，不是官方固定正文。

- 基线：`656b525f533037f1c0dff6383c4afa69926e612c`
- 原research Git blob：`1922e85db1c71ee8970ea7eb45a00ce0867b9f66`
- 原research完整SHA-256：`b91f42e29c199b1baf0c0cf6ec9f7c1e9cf9c5205fdbe5019f3cfcda3c85b4f8`（3342字节）

## R1 · XA Transactions

- 机构：Oracle / MySQL
- 版本：MySQL 8.4 Reference Manual
- 正式链接：[XA Transactions（官方文档）](https://dev.mysql.com/doc/refman/8.4/en/xa.html)
- [既有实读记录（2026-10-24，R1）](https://github.com/linhongcun/video-studio/blob/656b525f533037f1c0dff6383c4afa69926e612c/episodes-codex/tx-2pc/research.md#L7)

- 原题位置：2026-10-24既有article.mdx第44行脚注的原题部分
- 技术实读位置：Resource Manager/Transaction Manager，以及两阶段流程段落
- 镜头：01, 02, 03, 04, 05, 06, 07, 08, 09, 10

支持的主张与边界：先准备并收集结果，再共同决定；参与资源必须支持相关协议，XA接口不与2PC并列当另一算法。

## R2 · XA Transaction States

- 机构：Oracle / MySQL
- 版本：MySQL 8.4 Reference Manual
- 正式链接：[XA Transaction States（官方文档）](https://dev.mysql.com/doc/refman/8.4/en/xa-states.html)
- [既有实读记录（2026-10-24，R2）](https://github.com/linhongcun/video-studio/blob/656b525f533037f1c0dff6383c4afa69926e612c/episodes-codex/tx-2pc/research.md#L8)

- 原题位置：2026-10-24既有article.mdx第45行脚注的原题部分
- 技术实读位置：PREPARED、COMMIT/ROLLBACK、RECOVER与detached段落
- 镜头：03, 04, 11, 12, 13

支持的主张与边界：准备状态可恢复，最终按决定终结；不把连接断开画成自动撤销。

## R3 · PREPARE TRANSACTION

- 机构：The PostgreSQL Global Development Group
- 版本：PostgreSQL current（旧实读记录未标具体主版本）
- 正式链接：[PREPARE TRANSACTION（官方文档）](https://www.postgresql.org/docs/current/sql-prepare-transaction.html)
- [既有实读记录（2026-10-24，R3）](https://github.com/linhongcun/video-studio/blob/656b525f533037f1c0dff6383c4afa69926e612c/episodes-codex/tx-2pc/research.md#L9)

- 原题位置：2026-10-24既有article.mdx第46行脚注的原题部分
- 技术实读位置：Description与Caution
- 镜头：03, 04, 11, 12, 13, 14

支持的主张与边界：prepare的状态可靠保存，尚未提交，锁继续持有；长期prepared会妨碍运行。只转述机制，不给出自行手工操作生产待决事务的建议。

机构补证：[官方固定postgres.sgml](https://github.com/postgres/postgres/blob/a5ccf20801c821b72bb04d56b7320d52149a1ce5/doc/src/sgml/postgres.sgml)，第28行corpauthor，SHA-256 `8becdc072d08b07da4f91a6fe0564963e11700d5e34386c6de431aac2aef170a`；这是机构署名信息，不是PREPARE技术正文快照。

## R4 · Narayana Project Documentation

- 机构：Narayana Project
- 版本：官方项目文档（旧实读记录未标发布版本）
- 正式链接：[Narayana Project Documentation（官方文档）](https://www.narayana.io/docs/project/index.html)
- [既有实读记录（2026-10-24，R4）](https://github.com/linhongcun/video-studio/blob/656b525f533037f1c0dff6383c4afa69926e612c/episodes-codex/tx-2pc/research.md#L11)

- 原题位置：2026-10-26题名补查：官方book_info.adoc第4行，index.adoc第6行包含该文件
- 技术实读位置：Two-phase commit overview、Failure Recovery中的稳定决定与恢复段落
- 镜头：05, 06, 07, 08, 11, 12

支持的主张与边界：协调者提交决定先稳定记录，恢复后按既有决定完成，不可随参与方各自超时改成相反结果。正文为当前项目文档，不据页脚猜首次发表年份。

原题补证：[官方固定book_info.adoc](https://github.com/jbosstm/narayana/blob/e3581c58f702af60c6a0d5ef0a5b9a95ca37fcf8/docs/src/main/asciidoc/project/book_info.adoc)第4行，SHA-256 `7d02d37575f51aad6835e4e3a77012d15a12f1918aeec179f7ef9bee8b8e1af4`；同提交index.adoc和docs/pom.xml确认project组装。旧jbosstm/documentation归档迁移说明只用于查找现行官方仓库，不冒充当前技术规范。

## 保留范围

旧article/research全文、frontmatter、锚点和所有脚注原字节保留。准备不是提交，可靠共同决定在最终指令之前；已准备而未知时不能自行猜回滚，恢复按既有决定完成。未承诺同毫秒全局可见、任意远程调用自动事务或永久无条件恢复，不增加性能数字及配置建议。无个人署名证据，省略author，不从Git账号或版权名推断个人作者。

本记录仅完成来源输入；不预记冻结、编码、成片/声音复核、发布或用户认可。
