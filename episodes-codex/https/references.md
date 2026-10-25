# https · 原题与原文短引

本轮固定正文复核日期：2026-10-25（北京时间）。原题按文档frontmatter／RFC题名／首个H1逐字保留；短引选取完整原句，不以内部supports或译名替代原文。

本轮GET状态、全文SHA、题名及原句位置见[核验记录](../../docs/reference-endcards/original-titles/sources-core.json)。正式入口与固定版本同时保留，原有canonical访问记录未冒充本轮重新访问。

## R1 · The Transport Layer Security (TLS) Protocol Version 1.3

- 作者／机构：IETF TLS WG
- 年份／版本：RFC 9846 · 2026
- 原题位置：frontmatter title · line 2
- 正式文档：<https://www.rfc-editor.org/rfc/rfc9846.html>
- 固定原文：<https://github.com/tlswg/tls13-spec/blob/c728b4efb4c12159371279227df6464541eafb58/rfc9846.md>

> Once the handshake is complete, the peers use the established keys to protect the application-layer traffic.

原句位置：§2 Protocol Overview。原始文件行号：701–702。

内部论点对应（制作解释，不作为原文引句）：

- 握手协商密钥并完成认证；TLS 1.3记录使用AEAD解密并验证
- 验证失败时拒绝记录并终止连接；握手内部并非先完成证书再开始全部密钥交换

## R2 · HTTP Semantics

- 作者／机构：IETF HTTP WG
- 年份／版本：RFC 9110 · 2022
- 原题位置：RFC front/title
- 正式文档：<https://www.rfc-editor.org/rfc/rfc9110.html>
- 固定原文：<https://github.com/httpwg/http-core/blob/3cdfb4df4dc47e75e9642efc99ab699a0495d883/rfc9110.xml>

> Certificate verification is used to prevent server impersonation by an on-path attacker or by an attacker that controls name resolution.

原句位置：§4.3.4 https Certificate Verification。原始文件行号：1420–1422。

内部论点对应（制作解释，不作为原文引句）：

- HTTPS客户端须核验服务身份与目标源站是否匹配，证书核验用于防冒充

## R3 · Transport Layer Security (TLS)

- 作者／机构：MDN Web Docs
- 年份／版本：持续维护文档 · 2026-10-25核验
- 原题位置：frontmatter title · line 2
- 正式文档：<https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Transport_Layer_Security>
- 固定原文：<https://github.com/mdn/content/blob/c49748a0ce4fdf77427e29cb6edbca8953a514e7/files/en-us/web/security/defenses/transport_layer_security/index.md>

> After the handshake, client and server use the secret key to encrypt and decrypt any messages, including HTTP headers as well as bodies.

原句位置：TLS handshake · line 32。原始文件行号：32–32。

内部论点对应（制作解释，不作为原文引句）：

- TLS提供传输中的保密、完整性与认证；网站证书将公钥关联到域名
- 这些保护面向客户端与服务端之间的连接，不作为商品信誉或服务端存储安全的保证
