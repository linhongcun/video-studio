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

## 第四批片尾资料核验（2026-10-26）

本轮只追加来源输入，原调研及访问日期保留。片尾采用两个原始题名与连续完整原句，详细GET响应、题名/引文证据及边界见[sources-rate-limit.json](../../docs/reference-endcards/batch-4/sources-rate-limit.json)。

- R1 原题：Local rate limit；原题位置：reStructuredText document heading (line 3)；固定正文：https://github.com/envoyproxy/envoy/blob/83297dad103f3dbd6320d0b29cd1e7781cf45305/docs/root/configuration/http/http_filters/local_rate_limit_filter.rst。
  - 原句（142字符）：If the local rate limit token bucket is checked, and there are no tokens available, a 429 response is returned (the response is configurable).
  - 位置：Opening behavior description (lines 15–16)；全文SHA-256：`7db0308c39cb772046dc9e604df049ae591871926ea2252a7bcdf695bc178bdf`。

- R2 原题：429 Too Many Requests；原题位置：frontmatter title (line 2)；固定正文：https://github.com/mdn/content/blob/87ca9db1ebe56eb20c1f20b91fca43955d8f0e26/files/en-us/web/http/reference/status/429/index.md。
  - 原句（87字符）：Implementations of rate limiting vary; restrictions may be server-wide or per resource.
  - 位置：Opening discussion (line 14)；全文SHA-256：`9d00420fcbd41b38a4016031ec5df0c13f8a495295d38b4c0b3487c60c5bbe8b`。

- 实际GET了Envoy同一固定提交的过滤器文档、TokenBucket和LocalRateLimit API源。max_tokens、tokens_per_fill、fill_interval分别定义容量、每次补充量与补充时间间隔；1秒补1的示例不是通用默认组合，fill_interval为必填。
- Envoy文档明确缺额可配置429、进程或连接作用范围、启用/执行的区别，以及Retry-After选项默认关闭和发出条件。没有据此声称所有429都来自该过滤器或所有限流实例共享一个全局额度。
- MDN429原题与状态说明、可选Retry-After、服务/资源/IP/身份范围已读取。所选短引直接复制第14行，不展开宏或改写源句；Envoy短引只合并排版换行。
- 容量2、每秒补1、甲乙丙和两个后台位置均为教学设计。限流不等同并发计数、库存判断或公平策略；等待后是否通过仍取决于当时额度与其他条件。
- 本轮仅访问官方GitHub/API允许目的地，未重试canonical页面，不将旧资料日志标为本轮已读。没有更改脚本、配音、分镜、冻结、媒体或根保存的baseline/body副本。
