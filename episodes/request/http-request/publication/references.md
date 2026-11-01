# http-request · 原题与原文短引

本轮固定正文复核日期：2026-10-25（北京时间）。原题按文档frontmatter／RFC题名／首个H1逐字保留；短引选取完整原句，不以内部supports或译名替代原文。

本轮GET状态、全文SHA、题名及原句位置见[核验记录](../../docs/reference-endcards/original-titles/sources-core.json)。正式入口与固定版本同时保留，原有canonical访问记录未冒充本轮重新访问。

## R1 · Populating the page: how browsers work

- 作者／机构：MDN Web Docs
- 年份／版本：持续维护文档 · 2026-10-25核验
- 原题位置：frontmatter title · line 2
- 正式文档：<https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/How_browsers_work>
- 固定原文：<https://github.com/mdn/content/blob/9945c1ccba85d04624c7608c48b61e2eed98d579/files/en-us/web/performance/guides/how_browsers_work/index.md>

> Once the browser receives the first chunk of data, it can begin parsing the information received.

原句位置：Parsing · line 103。原始文件行号：103–103。

内部论点对应（制作解释，不作为原文引句）：

- 浏览器先查找地址；HTML可以边接收边解析，并发现样式、脚本和图片等其他资源
- DOM与CSSOM参与渲染，布局确定位置与尺寸，绘制形成屏幕像素

## R2 · HTTP Semantics

- 作者／机构：IETF HTTP WG
- 年份／版本：RFC 9110 · 2022
- 原题位置：RFC front/title
- 正式文档：<https://www.rfc-editor.org/rfc/rfc9110.html>
- 固定原文：<https://github.com/httpwg/http-core/blob/3cdfb4df4dc47e75e9642efc99ab699a0495d883/rfc9110.xml>

> The GET method requests transfer of a current selected representation for the target resource.

原句位置：§9.3.1 GET。原始文件行号：4658–4660。

内部论点对应（制作解释，不作为原文引句）：

- URL中的主机、路径和端口职责不同，HTTPS未写端口时默认使用443
- GET请求取得目标资源的表示，200表示请求成功，Content-Type说明表示的媒体类型

## R3 · Transmission Control Protocol (TCP)

- 作者／机构：IETF
- 年份／版本：RFC 9293 · 2022
- 原题位置：RFC front/title
- 正式文档：<https://www.rfc-editor.org/rfc/rfc9293.html>
- 固定原文：<https://github.com/wesley-eddy/rfc9293bis/blob/3baedef270170d063c66ef995fca1f72281a3912/rfc9293.xml>

> Each side must also receive the remote peer's initial sequence number and send a confirming acknowledgment.

原句位置：§3.4.1 · lines 1445–1448。原始文件行号：1447–1448。

内部论点对应（制作解释，不作为原文引句）：

- TCP提供可靠、有序的字节流；双方交换并相互确认各自的初始序号
- 三次握手中第二报文合并SYN与ACK；SYN占一个序号，纯ACK不占序号，服务端收到最终有效ACK后建立连接

## R4 · The Transport Layer Security (TLS) Protocol Version 1.3

- 作者／机构：IETF TLS WG
- 年份／版本：RFC 9846 · 2026
- 原题位置：frontmatter title · line 2
- 正式文档：<https://www.rfc-editor.org/rfc/rfc9846.html>
- 固定原文：<https://github.com/tlswg/tls13-spec/blob/c728b4efb4c12159371279227df6464541eafb58/rfc9846.md>

> Once the handshake is complete, the peers use the established keys to protect the application-layer traffic.

原句位置：§2 Protocol Overview。原始文件行号：701–702。

内部论点对应（制作解释，不作为原文引句）：

- TLS在握手中完成必要认证、密码参数协商与共享密钥材料建立，随后用流量密钥保护应用数据
- TLS 1.3记录保护使用AEAD；证书身份与握手协商出的流量密钥承担不同职责
