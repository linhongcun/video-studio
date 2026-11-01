# EP.02 权威资料核验

访问日期：2026-10-24（北京时间）。通过搜索工具实际打开正文并定位关键章节；检索摘要不作为制作依据。

## MDN：传输层安全

- 公开来源：https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Transport_Layer_Security
- 核验主张：Encryption、Integrity、Authentication及Server authentication正文。
- 适用边界：保护的是端点之间的传输，不能推出网站商业信誉、服务端存储安全。

## RFC 9110（2022）HTTPS与证书验证

- 公开来源：https://www.rfc-editor.org/rfc/rfc9110.html#section-4.3.4
- 核验主张：HTTPS与服务器证书身份匹配的要求。
- 适用边界：安全连接不是用户登录认证；证书有效不证明网站商品真实。

## RFC 8446（2018，仅参考）TLS1.3

- 公开来源：https://www.rfc-editor.org/rfc/rfc8446.html
- 核验主张：§2协议概览、§4握手、§5记录保护。
- 适用边界：为密码学流程补充原始标准；片中不展示TLS1.2的RSA传钥，不说全程所有元数据都隐藏。

所有片中值是示例，非真实测量或公开服务的实际查询结果。

## 2026-10-24 导航返工：实际复读正文

访问日期：2026-10-24（UTC）。rfc-editor.org 的直接文本请求被会话代理以403拒绝，改用TLS工作组官方GitHub仓库正文，并固定到实际读取的commit；没有把检索摘要当成正文。

- RFC 9846《The Transport Layer Security (TLS) Protocol Version 1.3》，2026-07：<https://github.com/tlswg/tls13-spec/blob/c728b4efb4c12159371279227df6464541eafb58/rfc9846.md>。固定commit `c728b4efb4c12159371279227df6464541eafb58`，Git blob `a4d216115eb4776746e727a4ac3d659982899243`。头部第4/10/14行列出number9846、obsoletes包含8446及日期2026-07，因而本轮以它复核TLS1.3机制；上面的8446仍作为原版制作历史参考，不称为最新标准。
- 实读Protocol Overview（第693–706行）及完整握手说明（第767–818行）：握手协商参数、认证对方并建立共享秘密，完成后保护应用数据；实际密钥交换和认证属于握手内部，不能把本片讲解顺序画成“证书完全核验完，才开始所有密钥协商”的协议时序。
- 实读Record Payload Protection（第3819–3828、3914–3923行）：TLS1.3采用AEAD，解密与验证是统一操作，输出明文或失败；失败时接收端必须以bad_record_mac终止连接。因此全局图接收节点写“解密并验证”，通过才处理内容，失败出口是“拒绝数据/终止本次连接”，不把完整性画成另一个独立的明文处理后步骤。
- 原有证书核验与身份关联的支持材料本轮再次实读MDN正文Server authentication、TLS handshake及Encryption/Integrity/Authentication段落：<https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/security/defenses/transport_layer_security/index.md>。证书绑定网站公钥与域名；服务器认证是Web安全基本部分；请求和响应的传输都受保护。没有将该文当作网站商业信誉或服务端存储安全的依据。

本轮地图只概括原片中的普通证书认证连接，不扩展到0-RTT、PSK或客户端证书；“未核验通过→停止正常发送”是本例安全路径，未画用户忽略警告后的例外操作。身份失败与受保护记录验证失败是两种不同判断，不能互连为同一条成功路径。

## 2026-10-25 片尾参考资料补充核验

本轮对照`references.json`／`references.md`读取资料正文，实际读取日期为2026-10-25（北京时间）。正式文档站点均被会话代理以Tunnel 403拒绝，因此改读负责工作组或MDN官方GitHub仓库固定commit；不沿用2026-10-24的访问记录冒充本轮联网结果。原文节选、完整SHA与可达性记录见[本批证据](../../docs/reference-endcards/batch-1/source-verification.json)。

- R1 IETF TLS WG，The Transport Layer Security (TLS) Protocol Version 1.3（RFC 9846 · 2026）：<https://github.com/tlswg/tls13-spec/blob/c728b4efb4c12159371279227df6464541eafb58/rfc9846.md>。实读§2 Protocol Overview；§4 Handshake Protocol；§5.2 Record Payload Protection；支撑：握手协商密钥并完成认证；TLS 1.3记录使用AEAD解密并验证；验证失败时拒绝记录并终止连接；握手内部并非先完成证书再开始全部密钥交换。
- R2 IETF HTTP WG，HTTP Semantics（RFC 9110 · 2022）：<https://github.com/httpwg/http-core/blob/3cdfb4df4dc47e75e9642efc99ab699a0495d883/rfc9110.xml>。实读§4.3.4 https Certificate Verification；支撑：HTTPS客户端须核验服务身份与目标源站是否匹配，证书核验用于防冒充。
- R3 MDN Web Docs，Transport Layer Security (TLS)（持续维护文档 · 2026-10-25核验）：<https://github.com/mdn/content/blob/c49748a0ce4fdf77427e29cb6edbca8953a514e7/files/en-us/web/security/defenses/transport_layer_security/index.md>。实读TLS概览的Encryption／Integrity／Authentication；TLS handshake；Server authentication；支撑：TLS提供传输中的保密、完整性与认证；网站证书将公钥关联到域名；这些保护面向客户端与服务端之间的连接，不作为商品信誉或服务端存储安全的保证。

固定TLS正文头部实际列出number 9846、date 2026-07及obsoletes包含8446，故本轮片尾与文章统一引用RFC9846；RFC8446仅保留为历史参考。MDN的TLS版本文字未作为最新RFC编号的证据。
