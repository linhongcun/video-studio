# EP11 公开资料实读记录

访问日期：2026-10-24（北京时间）。通过搜索服务实际打开官方正文和定位章节，不使用旧稿或搜索摘要作为事实来源。文档中的产品名只用于出处，片中不点名厂商。

| 编号 | 实读正文 | 主张 | 适用边界 |
|---|---|---|---|
| R1 | [Envoy Local rate limit](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/local_rate_limit_filter)，开头、Retry-After、Example configuration | 本地HTTP限流可采用令牌桶，缺少可用令牌时可返回429；容量与每次补充量、时间间隔分别配置 | 配置决定规则作用范围；不是所有部署都按同一全局预算限流，429也可配置为其他状态 |
| R2 | [MDN 429 Too Many Requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/429)，正文与示例 | 限流规则可以基于服务、资源、IP或认证身份；响应可包含等待信息 | 页面“系统繁忙”不是HTTP429的同义词，更不能仅凭这句文案判断原因 |
| R3 | [MDN Retry-After](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After)，Directives | Retry-After可用日期或等待秒数告知后续请求应等待多久 | 服务端不一定发送，客户端支持也不同；按提示等待不保证下一次成功 |

教学配置：容量2，每秒补1，额满后不积累更多。请求甲乙在同一补充间隔内消耗原有额度，丙缺额被拒绝；之后才演示下一次补充。全片放慢展示，非真实时间速率，也不是建议将实际服务设为每秒一个请求。

内容边界：拒绝式令牌桶不替被拒请求排队；限流与业务库存判断、公平策略是不同问题。片中“不让所有请求同时成功”仅解释保护处理能力，不承诺避免所有过载或故障。

实现边界：令牌桶限制进入速率和允许的突发，不是并发计数器；后台示意位置只用于跟踪对象，不作为同时执行请求数量的硬承诺。
