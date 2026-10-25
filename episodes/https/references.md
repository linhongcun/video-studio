# https · 片尾参考资料

本轮访问与核验日期：2026-10-25（北京时间）。

RFC Editor和MDN网站在本轮均被会话代理拒绝访问（Tunnel 403），因此实际阅读的是负责工作组或MDN官方GitHub仓库中的固定commit正文。下面同时给出正式链接和本轮实读链接；正式站点未记为本轮已访问成功。完整响应哈希、原文节选及访问结果见[核验记录](../../docs/reference-endcards/batch-1/source-verification.json)。

## R1 · IETF TLS WG：The Transport Layer Security (TLS) Protocol Version 1.3

- 版本：RFC 9846 · 2026
- 正式链接：<https://www.rfc-editor.org/rfc/rfc9846.html>
- 本轮实读：<https://github.com/tlswg/tls13-spec/blob/c728b4efb4c12159371279227df6464541eafb58/rfc9846.md>
- 固定commit：`c728b4efb4c12159371279227df6464541eafb58`
- 正文完整SHA-256：`84da8cf41f1a6e4d94717d766d3e0fb47590348273f0f7cc63a366c0639233f3`
- 实读章节：§2 Protocol Overview；§4 Handshake Protocol；§5.2 Record Payload Protection
- 对应镜头：7, 8, 9, 10, 12
- 核验方式：实际HTTP 200读取固定正文，逐段审读，保留原文节选；未声称已访问正式站点。

支持的具体主张：

- 握手协商密钥并完成认证；TLS 1.3记录使用AEAD解密并验证
- 验证失败时拒绝记录并终止连接；握手内部并非先完成证书再开始全部密钥交换

## R2 · IETF HTTP WG：HTTP Semantics

- 版本：RFC 9110 · 2022
- 正式链接：<https://www.rfc-editor.org/rfc/rfc9110.html>
- 本轮实读：<https://github.com/httpwg/http-core/blob/3cdfb4df4dc47e75e9642efc99ab699a0495d883/rfc9110.xml>
- 固定commit：`3cdfb4df4dc47e75e9642efc99ab699a0495d883`
- 正文完整SHA-256：`22797e1c392d3a08cca9dca4d8affd7f3461fe574b333658c97b397627efb4d1`
- 实读章节：§4.3.4 https Certificate Verification
- 对应镜头：4, 5, 6
- 核验方式：实际HTTP 200读取固定正文，逐段审读，保留原文节选；未声称已访问正式站点。

支持的具体主张：

- HTTPS客户端须核验服务身份与目标源站是否匹配，证书核验用于防冒充

## R3 · MDN Web Docs：Transport Layer Security (TLS)

- 版本：持续维护文档 · 2026-10-25核验
- 正式链接：<https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Transport_Layer_Security>
- 本轮实读：<https://github.com/mdn/content/blob/c49748a0ce4fdf77427e29cb6edbca8953a514e7/files/en-us/web/security/defenses/transport_layer_security/index.md>
- 固定commit：`c49748a0ce4fdf77427e29cb6edbca8953a514e7`
- 正文完整SHA-256：`0e9786932ab7f83ab5d1a6b5467271d9fe5cf92650cce578b9e74b19977d551b`
- 实读章节：TLS概览的Encryption／Integrity／Authentication；TLS handshake；Server authentication
- 对应镜头：1, 2, 3, 5, 8, 9, 10, 11
- 核验方式：实际HTTP 200读取固定正文，逐段审读，保留原文节选；未声称已访问正式站点。

支持的具体主张：

- TLS提供传输中的保密、完整性与认证；网站证书将公钥关联到域名
- 这些保护面向客户端与服务端之间的连接，不作为商品信誉或服务端存储安全的保证

## 版本与边界

本轮实读的TLS工作组固定正文头部明确标为RFC 9846、日期2026-07，`obsoletes`包含8446；正文可核对握手、AEAD及失败终止要求，因此当前片尾采用9846。原稿RFC 8446（2018，仅参考）留作历史来源，不称为当前最新标准。MDN仍在部分文字中引用8446，本片使用MDN支持通用TLS保护与服务器认证，不据此判断最新RFC编号。

教学按理解顺序拆解握手内部内容，不作为真实TLS报文的逐条时序。视频只讲普通服务器证书认证的连接，不展开0-RTT、PSK或客户端证书。传输保护本身不保证网站商业信誉、端点未失陷或服务端存储安全。
