# http-request · 片尾参考资料

本轮访问与核验日期：2026-10-25（北京时间）。

正式文档站点本轮被会话代理以Tunnel 403拒绝访问；实际正文读取使用以下固定GitHub版本。完整HTTP状态、SHA-256、版本和逐论点短引保存在[本轮证据](../../docs/reference-endcards/batch-2/sources-http-request.json)，不将canonical访问失败记为成功。

## R1 · MDN Web Docs：Populating the page: how browsers work

- 年份／版本：持续维护文档 · 2026-10-25核验
- 正式链接：<https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/How_browsers_work>
- 本轮实读固定正文：<https://github.com/mdn/content/blob/9945c1ccba85d04624c7608c48b61e2eed98d579/files/en-us/web/performance/guides/how_browsers_work/index.md>
- 来源身份：MDN Web Docs官方内容仓库。
- 实读章节：Navigation／DNS lookup；Parsing／Building the DOM tree／Preload scanner／Building the CSSOM tree；Render／Style／Layout／Paint
- 对应镜头：1, 2, 4, 13, 14, 15, 17
- 固定commit：`9945c1ccba85d04624c7608c48b61e2eed98d579`
- 正文完整SHA-256：`07b10af00b15a72bda36eb38ebdee77ceab7b2dfa44a4546b1a84ca44d0c570d`

支持的主张：

- 浏览器先查找地址；HTML可以边接收边解析，并发现样式、脚本和图片等其他资源
- DOM与CSSOM参与渲染，布局确定位置与尺寸，绘制形成屏幕像素

## R2 · IETF HTTP WG：HTTP Semantics

- 年份／版本：RFC 9110 · 2022
- 正式链接：<https://www.rfc-editor.org/rfc/rfc9110.html>
- 本轮实读固定正文：<https://github.com/httpwg/http-core/blob/3cdfb4df4dc47e75e9642efc99ab699a0495d883/rfc9110.xml>
- 来源身份：IETF HTTP工作组公开仓库中的RFC9110发布XML。
- 实读章节：§4.2.2 https URI Scheme；§4.3 Authoritative Access；§7.2 Host and :authority；§8.3 Content-Type；§9.3.1 GET；§15.3.1 200 OK
- 对应镜头：3, 4, 11, 12, 17
- 固定commit：`3cdfb4df4dc47e75e9642efc99ab699a0495d883`
- 正文完整SHA-256：`22797e1c392d3a08cca9dca4d8affd7f3461fe574b333658c97b397627efb4d1`

支持的主张：

- URL中的主机、路径和端口职责不同，HTTPS未写端口时默认使用443
- GET请求取得目标资源的表示，200表示请求成功，Content-Type说明表示的媒体类型

## R3 · IETF：Transmission Control Protocol (TCP)

- 年份／版本：RFC 9293 · 2022
- 正式链接：<https://www.rfc-editor.org/rfc/rfc9293.html>
- 本轮实读固定正文：<https://github.com/wesley-eddy/rfc9293bis/blob/3baedef270170d063c66ef995fca1f72281a3912/rfc9293.xml>
- 来源身份：RFC9293署名编辑Wesley M. Eddy的公开仓库wesley-eddy/rfc9293bis，实读rfc9293.xml原始发布XML；不是IETF组织仓库，也不是同仓的draft-eddy-tcpm-rfc9293bis.xml草案。
- 实读章节：§2.2 TCP Interfaces；§3.4.1 Initial Sequence Number Selection；§3.5 Establishing a Connection及图6
- 对应镜头：5, 6, 7, 8, 9, 17
- 固定commit：`3baedef270170d063c66ef995fca1f72281a3912`
- 正文完整SHA-256：`f1e1de545db91fcd07cba806570df56ef8534bd97717dccd534ac92f37cacc98`

支持的主张：

- TCP提供可靠、有序的字节流；双方交换并相互确认各自的初始序号
- 三次握手中第二报文合并SYN与ACK；SYN占一个序号，纯ACK不占序号，服务端收到最终有效ACK后建立连接

仅文章拓展：

- §3.5及图8：历史重复连接发起是三次握手的重要设计原因；严格支线留在文章。

## R4 · IETF TLS WG：The Transport Layer Security (TLS) Protocol Version 1.3

- 年份／版本：RFC 9846 · 2026
- 正式链接：<https://www.rfc-editor.org/rfc/rfc9846.html>
- 本轮实读固定正文：<https://github.com/tlswg/tls13-spec/blob/c728b4efb4c12159371279227df6464541eafb58/rfc9846.md>
- 来源身份：IETF TLS工作组公开仓库中的rfc9846.md。
- 实读章节：§2 Protocol Overview；§4 Handshake Protocol；§4.4 Authentication Messages；§5.2 Record Payload Protection
- 对应镜头：10, 17
- 固定commit：`c728b4efb4c12159371279227df6464541eafb58`
- 正文完整SHA-256：`84da8cf41f1a6e4d94717d766d3e0fb47590348273f0f7cc63a366c0639233f3`

支持的主张：

- TLS在握手中完成必要认证、密码参数协商与共享密钥材料建立，随后用流量密钥保护应用数据
- TLS 1.3记录保护使用AEAD；证书身份与握手协商出的流量密钥承担不同职责

## 取舍与边界

片尾四项核心资料分两页，每页默认5秒。MDN仅支持地址查找及解析/渲染，不采用其旧式TLS往返数、14KB或16.67ms等数值。TCP采用作者仓库内编号9293、日期2022-08的原始发布XML，不使用同仓9293bis草案，不把作者仓库标成IETF工作组官方仓库。TLS固定正文头部实际标注9846、2026-07并替代8446。HTTP/1.1精确报文格式、缓存、HTTP/2和HTTP/3边界的既有补充资料继续留文章，不让新增片尾改变正文。
