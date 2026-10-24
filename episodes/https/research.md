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
