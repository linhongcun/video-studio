# EP05 公开资料核验

访问日期：2026-10-24（北京时间）。通过联网阅读工具实际打开正文，以下为独立概括。

1. AWS，How CloudFront delivers content（持续维护）
   https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/HowCloudFrontWorks.html
   读取交付流程与 regional edge caches 章节：请求被路由到适合服务的边缘位置，通常按网络时延接近；命中直接返回，未命中继续从上层或源站获取；返回内容可供后续请求复用。首字节到达时可开始转发。支持镜2–8。这里只借其真实实现核验通用流程，不将某一家分层拓扑画成所有 CDN 的固定结构。
2. IETF，RFC 9111 HTTP Caching，2022年6月
   https://www.rfc-editor.org/rfc/rfc9111.html
   实际阅读2、3、4.2、4.3节：缓存保存可复用的响应，使用受缓存键、存储条件和新鲜度规则限制；过期后可验证或按明确条件使用，不是永久有效。支持镜4、6–10。
3. Cloudflare，Default cache behavior（2026-09-14更新）
   https://developers.cloudflare.com/cache/concepts/default-cache-behavior/
   已打开正文，核验缓存受响应头与配置控制，不是所有内容都会自动缓存。支持镜6、9、10；厂商默认规则不当作普遍标准。
4. MDN，HTTP caching（持续维护）
   https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching
   实际阅读 Types of caches：共享缓存位于客户端与源站之间；个性化内容进入共享缓存可能造成信息泄漏，Cookie 本身也不能替代正确缓存指令。支持镜10。

## 边界

- 只讲同一公开商品图片。真实大陆轮廓用于说明相对地域；节点与网络路径仍为教学示例，不由线长推断真实物理线路、网络跳数、时延或保证性能；无无来源毫秒/倍数。
- 边缘“合适”不等于地理上最近，按路由、网络时延、负载与配置选择。
- 命中且可复用时才省掉本次取图的回源；未命中不承诺第一次一定快。
- 简化为一层边缘与源站，真实系统可能有多级缓存、请求合并、流式回填。
- 私人订单演示配置正确的私有响应绕开共享缓存，不主张仅有 Cookie 就会自动安全。
- 缓存不能自动修好源站程序和数据库瓶颈，动态内容加速的其他能力留在文章。

## 地图与术语返工的新增来源与复核

- 2026-10-24实际通过现有proxy读取Natural Earth官方维护者上游仓库README与110m land GeoJSON。README原文明确“Natural Earth is a public domain map dataset”及“free for use in any type of project”。固定commit `ca96624a56bd078437bca8184e78163e5039ad19`，GeoJSON完整SHA `9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9`，138160字节；本地原文、固定URL、许可依据与转换方式在assets/map/。未成功取得不存在的/LICENSE（404），不称其为一个已读取的许可证文件。
- 地图上只画大陆轮廓，不画行政边界。位置、调度和路径为示例，不暗示具体CDN部署或真实测量。地图的相对地域帮助理解临近服务点；“近”不能只看直线距离，需结合实际网络路径、时延与调度。
- 新词引入：CDN与内容分发网络并列，边缘节点与请求检查动作对应，回源与本例未命中后的长路径对应；没有新增DNS/Anycast/分层机制讲解。
- 独立事实预审remake_ep06_07本轮重新读取AWS交付流程、RFC9111与Cloudflare缓存正文，确认本例未命中回源、命中可复用短返及过期/私人边界；该独立来源复核与主制作实际读取原资料的记录分开，不把源审当成新片观看通过。
