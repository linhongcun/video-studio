# EP05 CDN 地图返工独立预审

更新时间：2026-10-24T21:26:25.196707+08:00（北京时间）

本轮只读核对现有脚本、调研、文章、视觉方向、Main及现行规则；不将源审当成新版小样或成片通过。

1. **地图必须展示临近节点服务过程**：开头2秒同时有标题与远源站/临近服务冲突；渐进展示多地节点，仅被选中节点和当前路径高亮；同一用户、节点和图片跨镜可追踪。保留地图示意说明，旁白用合适/通常网络时延较低，不宣称始终地理最近或每次最短直线。
   当前差距：旧visual-direction3写避免世界地图，Main只有横排节点及其他节点文字，没有空间分布主线。用户本轮要求应优先落实。

2. **未命中、返回与留下副本必须按顺序**：本例先用户到所选edge检查未命中，再向源站；内容经edge回给用户，符合规则后该edge留下可复用副本；不让其他地图节点自动同步有图，不承诺首次必快。允许边收边转发，不强制收完整图才转发。

3. **命中短返与CDN术语在同一解释点兑现**：第二访客设定为同服务区域/同一节点，追同一公开图片；请求到达查得可复用副本后才返回，源站支路无本次取图流。多地节点的作用可见时点明内容分发网络（CDN），缩写逐字母读并对齐实际起音，完整显示至少63帧。

4. **把具体miss例子与普遍回源条件分清**：本例无图所以回源；不能扩成只有miss才可能联系源站。过期验证/更新、私人响应不共享等只保留必要短限定，更多协议分支留文章；上层缓存可让边缘miss不必直达origin。结尾不承诺修复程序/数据库慢，无虚构毫秒倍数。
   当前源审风险：旧Main09 refresh完成时用户image=true但state固定等待检查，且仅origin→edge返回流，无edge→user动作；新版应同步接收态及返回路径。此为源码风险，尚未以新版实际帧确认。

实际访问的官方正文（访问日期2026-10-24北京时间，通过启用的联网阅读工具）：

- [AWS How CloudFront delivers content](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/HowCloudFrontWorks.html)：Body: request delivery steps and regional edge cache sections; official implementation example, not universal topology. Suitable edge typically by latency; cache hit local reply; cache miss may use regional cache or origin; forwarding may start at first byte.
- [IETF RFC9111 HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html)：Body overview and sections4,4.2.4,4.3,5.2.2.7 through open/find tool excerpts. Reuse requires matching and permitted response; stale handling/validation are conditional; unqualified private prohibits shared storage.
- [Cloudflare Default cache behavior](https://developers.cloudflare.com/cache/concepts/default-cache-behavior/)：Default behavior and request collapsing body; document update visible Sep14 2026. Storage depends on headers/configuration; vendor defaults are not all-CDN protocol guarantees.

后续验收需真实无字幕过程小样、多阶段及最终MP4实际解码图，分别记录静帧/过程/听辨范围。本阶段无任何新版动态或听辨结论。未改期目录、全局docs或Git。

## 地图修订样稿追加预审

已实际读 `episodes-codex/cdn/revision-plan.md`：方向可进入实现和动态小样。地图03–08/12、09–11明确放大、仅所选节点保存副本、第二访客同地区的安排符合本轮要求。

两处措辞建议：03-2改“不能只看地图上的直线距离”；05-2改“这次仍要经过远端传输”，把回源前提绑定于本例该节点无图，避免任何首访必miss的印象。03-1与04-1可保留。

已发root和制作组。尚未查看新动态样品或新成片，不作该部分通过结论。
