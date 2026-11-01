# EP.01 技术细节版：公开资料核验

访问日期：2026-10-25（北京时间）。本轮重新读取公开正文，不把旧脚本、旧分镜或对话作为事实出处。环境允许GitHub而未列入RFC Editor/MDN站点；实际阅读使用HTTPWG、TLSWG、QUICWG、MDN的公开仓库源，以及固定提交的RFC全文镜像。下面同时给出规范入口和本次实读入口，不把搜索摘要当作已读正文。若镜像与规范后续勘误冲突，应重新核对；本片不声称覆盖全部勘误或实现。

## R1 · MDN：Populating the page: how browsers work

- 来源：[公开文档](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/How_browsers_work)；[本次实读的MDN源文件](https://github.com/mdn/content/blob/main/files/en-us/web/performance/guides/how_browsers_work/index.md)。源文件未标更新时间，读取当前main。
- 主张：DNS查找地址；HTML可以边接收边解析，解析时可发现其他资源；DOM与CSSOM参与样式计算，布局确定几何位置，绘制形成像素。
- 实读位置：Navigation / DNS lookup；Response；Parsing / Building the DOM tree / Preload scanner / Building the CSSOM tree；Render / Style / Layout / Paint / Compositing。
- 原句短引：“Once the browser receives the first chunk of data, it can begin parsing”；“The DOM is the browser's internal representation of the markup.”；“Layout is the process by which the dimensions and location ... are determined”。
- 用在：01–04、13–15、17。
- 边界：流程用于建立因果关系，实际下载、解析、样式和绘制可以重叠；不把整片顺序当成严格串行屏障。本文TLS段仍有“五次额外往返”“总共八次往返”等旧式描述，不能直接用于当前TLS1.3延迟结论；本片不用这些数字，也不用14KB、16.67ms、TTI等旁支断言。

## R2 · RFC 9110：HTTP Semantics（2022）

- 来源：[规范入口](https://www.rfc-editor.org/rfc/rfc9110.html)；[本次实读的HTTPWG发布XML](https://github.com/httpwg/http-core/blob/main/rfc9110.xml)。文档日期2022年6月。
- 主张：URI的scheme、host、port和path具有不同职责；HTTPS缺省端口443；HTTP表达请求/响应语义，200表示请求成功，Content-Type说明表示的数据类型。
- 实读位置：§3.3–3.9，§4.2.2–4.3.4，§6，§8.3，§9.3.1，§15.3.1。
- 原句短引：“If the port subcomponent is empty or not given, TCP port 443 ... is the default”；“The 200 (OK) status code indicates that the request has succeeded.”
- 用在：02–04、10–12、17。
- 边界：DNS结果可能包含多个地址，实际远端可能是反向代理或CDN；IP和端口没有替代HTTP的host与path。HTTPS语义不绑定所有HTTP版本必须使用TCP，主线明确为HTTP/1.1。客户端实际证书验证还包括信任链、有效期、域名等检查，本片不演成完整验证器。

## R3 · RFC 9293：Transmission Control Protocol（2022）

- 来源：[规范入口](https://www.rfc-editor.org/rfc/rfc9293.html)；[本次实读的固定提交全文镜像](https://github.com/ze-software/ze/blob/4de24d43d2b871de07b4a71ea6eef72a576f2cd8/rfc/full/rfc9293.txt)。核对文首RFC编号、2022年8月日期、正文小节与图6。
- 主张：TCP提供可靠、有序的字节流；序号标识字节序号空间；双方各自选择初始序号并相互确认；第二次报文合并SYN和ACK，确认号是期望的下一个序号；SYN占一个序号，纯ACK不占序号。
- 实读位置：§2.2；§3.1 Sequence Number / Acknowledgment Number；§3.4；§3.4.1；§3.5，图6、图8。
- 原句短引：“TCP provides a reliable, in-order, byte-stream service”；“Each side must also receive the remote peer's initial sequence number and send a confirming acknowledgment”；“the ACK does not occupy sequence number space”。
- 用在：05–09、17；文章的消息边界、历史重复SYN补充。
- 状态核对：图6中主动发起端在收到有效SYN+ACK后进入ESTABLISHED并发送最终ACK；被动端收到有效最终ACK后才进入ESTABLISHED。动画不能把双方同时变成已建立，也不能在第一次报文发出前显示建立完成。
- 第三次的边界：视频解释服务端需要对其SYN/初始序号的确认；规范§3.5进一步指出主要原因是避免历史重复连接发起造成混淆。不能只讲“三次测试收发功能”，也不能声称三次握手保证此后不会断线、不会丢包或没有攻击。
- 示例：`SYN seq=1000`；`SYN+ACK seq=5000 ack=1001`；`ACK seq=1001 ack=5001`。数字是人工教学选择，不是抓包，不是规范默认初始值。第三次不带数据只是本次选定的最简情形，不否认合法携带数据的情形。

## R4 · TLS 1.3：TLSWG当前发布源（2026）

- 来源：[TLSWG公开源rfc9846.md](https://github.com/tlswg/tls13-spec/blob/main/rfc9846.md)；其文首标注number 9846、date 2026-07、obsoletes 8446，标题为The Transport Layer Security (TLS) Protocol Version 1.3。本次实际读取该版本，不把它标成2018年的RFC8446。
- 主张：TLS认证通信方、协商密码参数并建立共享密钥材料，记录层用流量密钥保护通信；本次采用证书认证的新建连接。
- 实读位置：Introduction；Protocol Overview；Handshake Protocol / Cryptographic Negotiation；Certificate / CertificateVerify；Record Protocol。
- 原句短引：“A handshake protocol ... authenticates the communicating parties, negotiates cryptographic algorithms and parameters, and establishes shared keying material”；“the record protocol ... protect[s] traffic ... using the traffic keys”；“If PSK is not being used, then asymmetric key exchange and certificate-based authentication are always used.”
- 用在：10；文章TLS与TCP职责区分。
- 边界：证书不等于用于加密后续网页内容的流量密钥；实际握手还有签名证明、Finished等，不将三个简化标签冒充完整TLS报文交换。PSK恢复和0-RTT不在主线，不能说每次HTTPS都重新发证书；QUIC中的TLS集成方式另见R8，不一概画成TLS over TCP。

## R5 · RFC 9112：HTTP/1.1（2022）

- 来源：[规范入口](https://www.rfc-editor.org/rfc/rfc9112.html)；[本次实读的HTTPWG发布XML](https://github.com/httpwg/http-core/blob/main/rfc9112.xml)。文档日期2022年6月。
- 主张：请求行包含method、request-target与HTTP-version；HTTP/1.1请求必须有Host；响应使用状态行；HTTP/1.1默认持久连接。
- 实读位置：§2.1、§3、§3.2、§4、§6、§9.3。
- 原句短引：“A client MUST send a Host header field ... in all HTTP/1.1 request messages”；“HTTP/1.1 defaults to the use of persistent connections”。
- 用在：11–13、16；文章报文与连接复用。
- 边界：画面是TLS解密后的教学明文；响应只显示状态行、Content-Type及正文节选，省略其他字段与消息定界，不称为完整可直接发送报文。同一连接可以复用，但并不保证浏览器只开一条连接。主线不把HTTP/1.1画成HTTP/2流的交错复用。

## R6 · RFC 9111：HTTP Caching（2022）

- 来源：[规范入口](https://www.rfc-editor.org/rfc/rfc9111.html)；[本次实读的HTTPWG发布XML](https://github.com/httpwg/http-core/blob/main/rfc9111.xml)。文档日期2022年6月。
- 主张：已有响应满足缓存规则时可直接复用，否则可能需要验证或重新请求。
- 实读位置：§1、§4、§4.2。
- 原句短引：“A cache considers a stored response ‘fresh’ ... if it can be reused without ‘validation’”。
- 用在：02、16。
- 边界：缓存“存在”不代表可以直接使用；视频说“能复用时”，不声称全部缓存都绕过网络。DNS缓存、HTTP缓存与现成连接是不同对象，不混成一个开关。

## R7 · RFC 9113：HTTP/2（2022）

- 来源：[规范入口](https://www.rfc-editor.org/rfc/rfc9113.html)；[本次实读的HTTPWG发布源XML](https://github.com/httpwg/http2-spec/blob/main/draft-ietf-httpbis-http2bis.xml)。文件名含draft，但文首number=9113、date May 2022；本次核对其发布正文。
- 主张：一条HTTP/2连接可以同时包含多个打开的流，并交错传输不同流的帧。
- 实读位置：§2，§5。
- 原句短引：“A single HTTP/2 connection can contain multiple concurrently open streams, with either endpoint interleaving frames from multiple streams.”
- 用在：16。
- 边界：HTTP/2使用二进制帧，不能把第11镜HTTP/1.1文本请求行当成HTTP/2线上格式；流的并发不代表同一TCP连接的丢包对其他流毫无影响。

## R8 · RFC 9114：HTTP/3（2022）

- 来源：[规范入口](https://www.rfc-editor.org/rfc/rfc9114.html)；[本次实读的QUICWG发布源](https://github.com/quicwg/base-drafts/blob/main/rfc9114.md)。文首为2022年6月HTTP/3。
- 主张：HTTP/3映射到QUIC，使用UDP端点，不走TCP三次握手；QUIC集成TLS1.3。
- 实读位置：§1；§2；§3.1；§10.1。
- 原句短引：“HTTP/3 does not use TCP”；“QUIC also incorporates TLS 1.3 ... at the transport layer”。
- 用在：16与文章版本边界。
- 边界：UDP作为承载不意味着HTTP/3没有可靠传输、拥塞控制或加密，不能画成不可靠的任意丢失数据。这里只点明流程不同，不在本片展开QUIC握手或性能比较。

## R9 · RFC 2606：Reserved Top Level DNS Names（1999，仅参考）

- 来源：[规范入口](https://www.rfc-editor.org/rfc/rfc2606.html)；[本次实读的固定提交全文镜像](https://github.com/scateu/communication-standard-collection/blob/4595ecfcd666836b2cfc4cc3a04d291b4ef01d50/RFC/rfc2606.txt)。
- 主张与短引：§2，“‘.example’ is recommended for use in documentation or as examples”。
- 用在：全片示例网址选择，不作为TCP或HTTP机制的主论证；不发起真实shop.example服务查询。

## R10 · RFC 5737：IPv4 Address Blocks Reserved for Documentation（2010，仅参考）

- 来源：[规范入口](https://www.rfc-editor.org/rfc/rfc5737.html)；[本次实读的AWS s2n-quic固定提交全文镜像](https://github.com/aws/s2n-quic/blob/d20f8fad59aab4815ad901c06b5730608ff7dd24/specs/www.rfc-editor.org/rfc/rfc5737.txt)。
- 主张与短引：§3，“203.0.113.0/24 (TEST-NET-3) are provided for use in documentation”。
- 用在：04的203.0.113.10只作示例，不是实际解析结果，不声称可公开连接。

## 核验取舍

本片不使用任何未测量的固定延迟、报文大小、市场占比或性能加速数字。TCP重传、拥塞控制、关闭连接、DNS递归全过程、JavaScript阻塞、证书链细节留在本片范围外；这些省略不改变本次正常路径的各层职责。第09镜是同一次第三次ACK的解释回看，不算第四次握手。第16镜展示版本与复用边界，不把它们混入主线的同一次HTTP/1.1请求。

## 2026-10-25 片尾参考资料补充核验

本轮重新GET并读取下列固定正文，日期2026-10-25（北京时间）。正式站点本轮不可达的事实、实际HTTP 200响应、全文SHA及逐论点短引分别记于[本片证据](../../docs/reference-endcards/batch-2/sources-http-request.json)。历史正文与旧访问记录保留，不以旧状态冒充本轮核验。

- R1 MDN Web Docs，《Populating the page: how browsers work》（持续维护文档 · 2026-10-25核验）：<https://github.com/mdn/content/blob/9945c1ccba85d04624c7608c48b61e2eed98d579/files/en-us/web/performance/guides/how_browsers_work/index.md>。实读Navigation／DNS lookup；Parsing／Building the DOM tree／Preload scanner／Building the CSSOM tree；Render／Style／Layout／Paint；对应：浏览器先查找地址；HTML可以边接收边解析，并发现样式、脚本和图片等其他资源；DOM与CSSOM参与渲染，布局确定位置与尺寸，绘制形成屏幕像素。
- R2 IETF HTTP WG，《HTTP Semantics》（RFC 9110 · 2022）：<https://github.com/httpwg/http-core/blob/3cdfb4df4dc47e75e9642efc99ab699a0495d883/rfc9110.xml>。实读§4.2.2 https URI Scheme；§4.3 Authoritative Access；§7.2 Host and :authority；§8.3 Content-Type；§9.3.1 GET；§15.3.1 200 OK；对应：URL中的主机、路径和端口职责不同，HTTPS未写端口时默认使用443；GET请求取得目标资源的表示，200表示请求成功，Content-Type说明表示的媒体类型。
- R3 IETF，《Transmission Control Protocol (TCP)》（RFC 9293 · 2022）：<https://github.com/wesley-eddy/rfc9293bis/blob/3baedef270170d063c66ef995fca1f72281a3912/rfc9293.xml>。实读§2.2 TCP Interfaces；§3.4.1 Initial Sequence Number Selection；§3.5 Establishing a Connection及图6；对应：TCP提供可靠、有序的字节流；双方交换并相互确认各自的初始序号；三次握手中第二报文合并SYN与ACK；SYN占一个序号，纯ACK不占序号，服务端收到最终有效ACK后建立连接。
- R4 IETF TLS WG，《The Transport Layer Security (TLS) Protocol Version 1.3》（RFC 9846 · 2026）：<https://github.com/tlswg/tls13-spec/blob/c728b4efb4c12159371279227df6464541eafb58/rfc9846.md>。实读§2 Protocol Overview；§4 Handshake Protocol；§4.4 Authentication Messages；§5.2 Record Payload Protection；对应：TLS在握手中完成必要认证、密码参数协商与共享密钥材料建立，随后用流量密钥保护应用数据；TLS 1.3记录保护使用AEAD；证书身份与握手协商出的流量密钥承担不同职责。

RFC9293本轮改用署名编辑Wesley M. Eddy公开仓库中的rfc9293.xml，固定commit 3baedef270170d063c66ef995fca1f72281a3912；XML的RFC编号、2022-08日期、TCPM与编辑姓名、§3.4.1、§3.5和图6均已核对。这是作者保留的原始发布XML，不是工作组组织仓库，也不是9293bis草案。原第三方全文镜像记录继续作为历史制作来源。MDN的旧TLS延迟数字不采用；RFC9110仅支撑语义，不冒充RFC9112的完整HTTP/1.1报文语法。
