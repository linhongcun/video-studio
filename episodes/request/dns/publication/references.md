# dns · 原题与原文短引

本轮固定正文复核日期：2026-10-25（北京时间）。原题按文档frontmatter／RFC题名／首个H1逐字保留；短引选取完整原句，不以内部supports或译名替代原文。

本轮GET状态、全文SHA、题名及原句位置见[核验记录](../../docs/reference-endcards/original-titles/sources-core.json)。正式入口与固定版本同时保留，原有canonical访问记录未冒充本轮重新访问。

## R1 · DNS Terminology

- 作者／机构：IETF DNSOP
- 年份／版本：RFC 9499 · 2024
- 原题位置：RFC front/title
- 正式文档：<https://www.rfc-editor.org/rfc/rfc9499.html>
- 固定原文：<https://github.com/ietf-wg-dnsop/draft-ietf-dnsop-rfc8499bis/blob/e3a5137460722f7b391707e9e95f971e00df4dc5/rfc9499.xml>

> In iterative resolution, the client repeatedly makes non-recursive queries and follows referrals and/or aliases.

原句位置：§6 · Iterative resolution。原始文件行号：960–961。

内部论点对应（制作解释，不作为原文引句）：

- 递归解析器代查，迭代查询按转介继续；权威服务器提供负责区域的记录
- TTL约束记录可以缓存的时间，缓存也可能提前移除

## R2 · DNS

- 作者／机构：MDN Web Docs
- 年份／版本：持续维护文档 · 2026-10-25核验
- 原题位置：frontmatter title · line 2
- 正式文档：<https://developer.mozilla.org/en-US/docs/Glossary/DNS>
- 固定原文：<https://github.com/mdn/content/blob/632359b60e58a4f5b2a69020dd79d0ecf38d4dbb/files/en-us/glossary/dns/index.md>

> DNS (Domain Name System) is a hierarchical and decentralized naming system for Internet-connected resources.

原句位置：Opening paragraph · line 8。原始文件行号：8–8。

内部论点对应（制作解释，不作为原文引句）：

- DNS把方便记忆的域名与IP地址等资源关联，查地址是页面加载前的一步
