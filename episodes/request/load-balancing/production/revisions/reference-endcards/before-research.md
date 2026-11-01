# EP06 公开资料核验

访问日期：2026-10-24（北京时间）。本期实际读取下列官方正文，未以旧脚本或搜索摘要代替。

|编号|正文|核验内容与边界|
|---|---|---|
|R1|[NGINX HTTP load balancing](https://nginx.org/en/docs/http/load_balancing.html)|Introduction、Load balancing methods、Default configuration：同一应用可有多个实例；round-robin为一种分配方式，不是所有产品必用算法。正文网页未标发布日期，作当前维护文档使用。|
|R2|[NGINX HTTP health checks](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-health-check/)|Introduction、Passive/Active Health Checks：检测失败可临时避开实例，恢复后重新加入；主动探测和被动观察是不同机制。文档注明NGINX开源版支持被动检查，示例主动检查功能属于NGINX Plus。片中不点名产品，不暗示所有开源部署均自带主动检查。|
|R3|[NGINX HTTP health checks — Active Health Checks](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-health-check/#active-health-checks)|fails/passes可配置；片中“两次失败、两次恢复”是本期教学配置，不是该产品默认值或协议强制值。检查间隔、阈值影响发现时间，不承诺立即发现故障。|

教学设计：三个实例、请求编号与路径只用于说明选择关系，不是生产规模或性能测试。请求抵达、路由和响应返回是同一次请求的连续过程；图形不模拟机柜、设备或假控制台。前两镜的待处理表示应用处理能力不足，不声称已引入持久消息队列。

片外边界：负载均衡不等于请求任意重放安全，不保证已失败请求自动成功；共享数据库、会话状态与入口自身可用性仍需独立设计。视频只讲请求分配和可用实例选择，算法、重试与会话黏性留在文章。
