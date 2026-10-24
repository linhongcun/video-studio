# EP.14 公开出处（宫崎 2026-10-22 16:40–16:42 北京时间核对；Azure／RFC 用 curl 抓 html，AWS 因 box TLS 失败改用 WebFetch，引文逐字摘自抓取文本；原文存 src/）

1. AWS Well-Architected Framework REL05-BP01《Implement graceful degradation to transform applicable hard dependencies into soft dependencies》 https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_mitigate_interaction_failure_graceful_degradation.html （src/aws-gd.txt；WebFetch 2026-10-22 16:40 北京时间；box curl TLS 失败）
   - "Application components should continue to perform their core function even if dependencies become unavailable. They might be serving slightly stale data, alternate data, or even no data. This ensures overall system function is only minimally impeded by localized failures while delivering the central business value."
   - "Desired outcome: When a component's dependencies are unhealthy, the component itself can still function, although in a degraded manner."
   - "Ideally, a component is able to perform its core function in an acceptable manner even when one or multiple dependencies fail."
   - "An ecommerce website might display data from multiple different systems like personalized recommendations, highest ranked products, and status of customer orders on the landing page. When one upstream system fails, it still makes sense to display everything else instead of showing an error page to a customer."
   - "Graceful degradation improves the availability of the system as a whole and maintains the functionality of the most important functions even during failures."
   - 用于：镜 11–18（关掉次要、保住核心功能／核心链路）；电商示例支撑「列表照常、某一项优惠先不算」。

2. AWS Well-Architected Framework REL05-BP07《Implement emergency levers》 https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_mitigate_interaction_failure_emergency_levers.html （src/aws-levers.txt；WebFetch 2026-10-22 16:40 北京时间；box curl TLS 失败）
   - "Emergency levers are rapid processes that can mitigate availability impact on your workload."
   - "Emergency levers work by disabling, throttling, or changing the behavior of components or dependencies using known and tested mechanisms."
   - "Desired outcome: By implementing emergency levers, you can establish known-good processes to maintain the availability of critical components in your workload. The workload should degrade gracefully and continue to perform its business-critical functions during the activation of an emergency lever."
   - "This may include mechanisms such as load shedding, throttling requests, or implementing graceful degradation."
   - 用于：仅文章（主动／预案关掉非核心能力＝emergency lever；片中只说「提前关掉搜索页里的红包计算」，不出口播「紧急拉杆」）。

3. Microsoft Azure Well-Architected Framework《Architecture strategies for self-healing and self-preservation》 https://learn.microsoft.com/en-us/azure/well-architected/reliability/self-preservation （src/azure-self.html／.txt；curl 2026-10-22 16:40 北京时间）
   - "Implement a graceful degradation mode"
   - "In these cases, ideally, your workload can maintain enough functionality for business to continue in a degraded state."
   - "Build alternative paths to complete your workload's essential functions: Reflect on your workload's critical flows and determine how you can maintain those flows when core components are unavailable."
   - 用于：镜 10–14、18（核心链路／essential functions；降级后仍完成下单）；文章「自动切到降级模式」。

4. Microsoft Azure Architecture Center《Throttling pattern》 https://learn.microsoft.com/en-us/azure/architecture/patterns/throttling （src/azure-throttle.html／.txt；curl 2026-10-22 16:40 北京时间）
   - "Graceful feature degradation: Turn off or degrade nonessential features so that essential features have enough resources. This strategy trades response completeness for availability."
   - "Feature B is less critical than Feature A or Feature C, so the system turns off Feature B and releases its resources."
   - 用于：镜 6–9、11（关掉搜索页红包计算＝非必要功能，把资源留给结算／下单）；文章图示对照。

5. Microsoft Azure App Configuration《Understand feature management》 https://learn.microsoft.com/en-us/azure/azure-app-configuration/concept-feature-management （src/azure-feature.html／.txt；curl 2026-10-22 16:40 北京时间）
   - "Instant kill switch – disable a misbehaving feature or dependency in seconds, without redeploying code"
   - "Operational toggle – turn a short-lived state, such as maintenance mode, on or off on demand"
   - 用于：仅文章（开关／功能开关实现主动降级；片中不出现「feature flag」英文术语）。

6. RFC 2606 §2 https://www.rfc-editor.org/rfc/rfc2606.html#section-2 （src/rfc2606.html／.txt；curl 2026-10-22 16:40 北京时间）
   - ".example" is recommended for use in documentation or as examples.
   - 用于：shop.example 示例网址。

未用：旧稿阿里云 AHAS（模块已停服）、JavaGuide 社区文、Google SRE 本轮未重新核对，不进本稿；片中不点名真实电商平台或云厂商。雪崩／级联故障已在 EP.13 文章讲过，本期文章只一句互见，不重讲。
