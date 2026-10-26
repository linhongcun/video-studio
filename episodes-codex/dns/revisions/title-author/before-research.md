# EP.03 权威资料核验

访问日期：2026-10-24（北京时间）。通过搜索工具实际打开正文并定位关键章节；检索摘要不作为制作依据。

## RFC 9499（2024）DNS术语

- 公开来源：https://www.rfc-editor.org/rfc/rfc9499.html
- 核验主张：§4递归/迭代与转介、§5 TTL、§6解析器与权威服务器。
- 适用边界：DNS可返回多种记录；递归解析器可能转发，片中只选无缓存时的典型逐级查询。

## ICANN：What Does ICANN Do?（2012，仅参考）

- 公开来源：https://www.icann.org/resources/pages/what-2012-02-25-en
- 核验主张：域名系统将名字与地址关联的公开说明。
- 适用边界：较早材料仅参考；DNS不是下载网页，也不是所有域名永久对应一个IP。

## RFC 2606（1999，仅参考）示例域名保留

- 公开来源：https://www.rfc-editor.org/rfc/rfc2606.html
- 核验主张：§2 .example用于文档与示例。
- 适用边界：shop.example与203.0.113.10仅是教学图；画面不表示真实公开DNS会返回这些值。

所有片中值是示例，非真实测量或公开服务的实际查询结果。

## RFC 5737（2010，仅参考）：文档专用IPv4地址

- 公开来源：https://www.rfc-editor.org/rfc/rfc5737.html
- 实读§3–4：203.0.113.0/24属于文档示例地址块，不是本片真实测得的服务地址。
- 访问日期：2026-10-24（北京时间）。只用于选择示例，不把它当成可公开连接的真实网站地址。

## 2026-10-25 片尾参考资料补充核验

本轮对照`references.json`／`references.md`读取资料正文，实际读取日期为2026-10-25（北京时间）。正式文档站点均被会话代理以Tunnel 403拒绝，因此改读负责工作组或MDN官方GitHub仓库固定commit；不沿用2026-10-24的访问记录冒充本轮联网结果。原文节选、完整SHA与可达性记录见[本批证据](../../docs/reference-endcards/batch-1/source-verification.json)。

- R1 IETF DNSOP，DNS Terminology（RFC 9499 · 2024）：<https://github.com/ietf-wg-dnsop/draft-ietf-dnsop-rfc8499bis/blob/e3a5137460722f7b391707e9e95f971e00df4dc5/rfc9499.xml>。实读§4 DNS Transactions；§5 Resource Records（TTL）；§6 DNS Servers and Clients（迭代、递归、权威与缓存）；支撑：递归解析器代查，迭代查询按转介继续；权威服务器提供负责区域的记录；TTL约束记录可以缓存的时间，缓存也可能提前移除。
- R2 MDN Web Docs，DNS（持续维护文档 · 2026-10-25核验）：<https://github.com/mdn/content/blob/632359b60e58a4f5b2a69020dd79d0ecf38d4dbb/files/en-us/glossary/dns/index.md>。实读DNS正文定义与DNS lookup段落；支撑：DNS把方便记忆的域名与IP地址等资源关联，查地址是页面加载前的一步。

校正原笔记的章节定位：递归／迭代模式、递归解析器及权威服务器在RFC9499 §6；TTL在§5，§4是DNS事务术语。示例规范RFC2606／5737保留早期资料“仅参考”，本轮不标重新实读。

## 2026-10-25 原题与原文短引核验

按最新要求，片尾采用文献原标题及可核对的完整原句，不再用displayTitle／displaySupport概括替代题名。内部supports保持为论点映射，不能冒充原文。本轮13份去重固定正文实际GET记录、题名位置与各句原文见[统一证据](../../docs/reference-endcards/original-titles/sources-core.json)；本片sources的titleEvidence与quotation均指向该记录。XML仅解析实体和内联标记、合并排版空白；DNS的Markdown粗体标记按可见正文还原，不删改词句。旧canonical访问与其他历史来源记录继续保留。
