# EP.01 权威资料核验

访问日期：2026-10-24（北京时间）。通过搜索工具实际打开正文并定位关键章节；检索摘要不作为制作依据。

## MDN：浏览器如何工作

- 公开来源：https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/How_browsers_work
- 核验主张：Navigation、Response、Parsing、Render正文；页面可随内容到达逐步解析绘制，资源可能派生更多请求。
- 适用边界：这是常见流程说明；连接复用、缓存与HTTP版本会改变具体步骤。

## RFC 9110（2022）HTTP语义

- 公开来源：https://www.rfc-editor.org/rfc/rfc9110.html
- 核验主张：§3.3–3.9请求响应、§4.2.2 HTTPS、§6消息抽象。
- 适用边界：不把HTTP请求限定为某一种线格式；片中不声称每次都建立新TCP连接。

## RFC 9111（2022）HTTP缓存

- 公开来源：https://www.rfc-editor.org/rfc/rfc9111.html
- 核验主张：§4缓存响应的复用与验证。
- 适用边界：缓存是否能直接复用取决于响应规则；不能说浏览器总先下载全网页。

所有片中值是示例，非真实测量或公开服务的实际查询结果。

## RFC 5737（2010，仅参考）：文档专用IPv4地址

- 公开来源：https://www.rfc-editor.org/rfc/rfc5737.html
- 实读§3–4：203.0.113.0/24属于文档示例地址块，不是本片真实测得的服务地址。
- 访问日期：2026-10-24（北京时间）。只用于选择示例，不把它当成可公开连接的真实网站地址。
