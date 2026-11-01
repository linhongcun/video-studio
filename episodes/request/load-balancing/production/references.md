# load-balancing · 参考资料

实际访问／核验日期：2026-10-26（北京时间）。两份固定正文均来自NGINX官方公开仓库并经本轮完整GET读取；题名与连续完整原句均按原文保留。

完整HTTP状态、全文SHA、题名／原句位置与配置边界见[核验记录](../../docs/reference-endcards/batch-3/sources-load-balancing.json)。原2026-10-24调研记录保留，不冒充本轮新读。

## R1 · Using nginx as HTTP load balancer

- 作者／机构：NGINX
- 版本：维护文档 · 2026-10-26核验
- 正式文档：<https://nginx.org/en/docs/http/load_balancing.html>
- 固定原文：<https://github.com/nginx/nginx.org/blob/a8e5cbef9776c487521e2903ffcf5d2fcb111eeb/xml/en/docs/http/load_balancing.xml>
- 题名位置：article/@name · line 9
- 全文SHA-256：`65abf5d7e4b0a529a672fa8018095fb06b3318b5a6d5cdd6173dceea3b2b0787`

> When the load balancing method is not specifically configured, it defaults to round-robin.

原文位置：Default load balancing configuration；原文件行号88–89。

内部论点对应（制作解释，不是原文引句）：

- 可将同一应用的多个实例组成服务组，由入口按选定规则分配HTTP请求
- NGINX未另配算法时使用轮询；轮询、最少连接和会话关联等方法各有取舍，不能推广为所有系统必须轮流分配

## R2 · HTTP Health Checks

- 作者／机构：NGINX
- 版本：维护文档 · 2026-10-26核验
- 正式文档：<https://docs.nginx.com/nginx/admin-guide/load-balancer/http-health-check/>
- 固定原文：<https://github.com/nginx/documentation/blob/463c9ec87b77b4bb138ce4edb3449ffefc623cdc/content/nginx/admin-guide/load-balancer/http-health-check.md>
- 题名位置：frontmatter title · line 4
- 全文SHA-256：`4ec71bbb17714adf71062bfbd6997239c63b67b73742fcbd475e416c47db90c9`

> The server is marked as unhealthy, and NGINX Plus does not send client requests to it until it once again passes a health check.

原文位置：Active Health Checks；原文件行号81–81。

内部论点对应（制作解释，不是原文引句）：

- 主动检查向上游发送专门探测，检查失败时可暂停向该实例分配请求，通过要求的检查后恢复
- fails与passes支持配置失败和恢复阈值；视频两次失败／两次成功是教学配置，不是默认或通用强制规则
- NGINX开源版支持被动检查；本资料中主动探测功能属于NGINX Plus，不能将两者混同

## 使用边界

主动探测以NGINX Plus文档说明为依据，开源版的被动检查另行区分。片中“两次失败、两次恢复”只是一组教学阈值；不是产品默认值。检测不是瞬时完成，跳过故障实例主要保护后续分配，不会自动修复旧请求。共同数据库瓶颈、跨实例会话和入口可用性保留为边界，不据此构造性能倍数。
