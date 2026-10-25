# dns · 片尾参考资料

本轮访问与核验日期：2026-10-25（北京时间）。

RFC Editor和MDN网站在本轮均被会话代理拒绝访问（Tunnel 403），因此实际阅读的是负责工作组或MDN官方GitHub仓库中的固定commit正文。下面同时给出正式链接和本轮实读链接；正式站点未记为本轮已访问成功。完整响应哈希、原文节选及访问结果见[核验记录](../../docs/reference-endcards/batch-1/source-verification.json)。

## R1 · IETF DNSOP：DNS Terminology

- 版本：RFC 9499 · 2024
- 正式链接：<https://www.rfc-editor.org/rfc/rfc9499.html>
- 本轮实读：<https://github.com/ietf-wg-dnsop/draft-ietf-dnsop-rfc8499bis/blob/e3a5137460722f7b391707e9e95f971e00df4dc5/rfc9499.xml>
- 固定commit：`e3a5137460722f7b391707e9e95f971e00df4dc5`
- 正文完整SHA-256：`29f32b14e5de3d15581ea66e54fa7135944dd1e258da58ae8449503aab888b7d`
- 实读章节：§4 DNS Transactions；§5 Resource Records（TTL）；§6 DNS Servers and Clients（迭代、递归、权威与缓存）
- 对应镜头：5, 6, 7, 8, 9, 10, 11
- 核验方式：实际HTTP 200读取固定正文，逐段审读，保留原文节选；未声称已访问正式站点。

支持的具体主张：

- 递归解析器代查，迭代查询按转介继续；权威服务器提供负责区域的记录
- TTL约束记录可以缓存的时间，缓存也可能提前移除

## R2 · MDN Web Docs：DNS

- 版本：持续维护文档 · 2026-10-25核验
- 正式链接：<https://developer.mozilla.org/en-US/docs/Glossary/DNS>
- 本轮实读：<https://github.com/mdn/content/blob/632359b60e58a4f5b2a69020dd79d0ecf38d4dbb/files/en-us/glossary/dns/index.md>
- 固定commit：`632359b60e58a4f5b2a69020dd79d0ecf38d4dbb`
- 正文完整SHA-256：`827d2c89bf49b3f0ffd98e7c79e54edab44144c3af6b1dba4f640311784d6461`
- 实读章节：DNS正文定义与DNS lookup段落
- 对应镜头：1, 2, 3, 12
- 核验方式：实际HTTP 200读取固定正文，逐段审读，保留原文节选；未声称已访问正式站点。

支持的具体主张：

- DNS把方便记忆的域名与IP地址等资源关联，查地址是页面加载前的一步

## 示例与边界

片中只演示无可用缓存时的典型逐级查询；递归解析器也可能转发，DNS可以返回多种类型的记录。`shop.example`与`203.0.113.10`是教学示例，不是真实服务查询结果。既有文章中的RFC 2606（1999，仅参考）和RFC 5737（2010，仅参考）继续作为示例命名、示例地址的背景文献；本轮未重新取得它们的正文，不将其标记为本轮verified，也不列入本次片尾卡。
