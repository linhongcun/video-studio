# D03 适配器模式：正式调研与事实映射

访问日期：**2026-10-25（北京时间）**。开工基线`ff730833e37e39edf9962ad414b0f325755adc73`。通过允许访问的官方GitHub源读取正文，没有绕过当前网络限制访问其他站点。未取得GoF经典书籍全文，不声称读过相关完整章节；此前Refactoring.Guru记录不当作本次重读。

本期唯一问题：**已有通知服务的使用方式与业务目标约定不兼容时，怎样把原有能力接进业务，同时保留请求和结果的含义？** 用商家向订单17买家发送一条发货提醒展开，不固定为真实短信/邮件供应方，不把教学UI当作真实产品源码证据。

## 实际阅读来源

| 编号 | 公开固定来源与时间 | 实际阅读及采用 | 限定 |
|---|---|---|---|
| S1 | [Spring官方TaskExecutorAdapter](https://github.com/spring-projects/spring-framework/blob/7bdf9c86f8657029567067051b7c6bd47b4ae67e/spring-core/src/main/java/org/springframework/core/task/support/TaskExecutorAdapter.java)，主干快照commit `7bdf9c86f8657029567067051b7c6bd47b4ae67e`，提交时间2026-10-24T15:05:57Z | editor通过GitHub connector取得并阅读完整源，再按commit固定重取。Javadoc明确暴露Spring侧TaskExecutor/AsyncTaskExecutor；实现目标接口，持有final Executor字段，构造接线，execute/submit委托，RejectedExecutionException转换为TaskRejectedException。支持一种对象适配器的契约/持有/委托/明确转换关系 | 主干快照不是稳定发布推荐；不借版权头断定文件更新年，不把任务执行中的同步/异步、装饰或错误策略推广为适配器统一语义 |
| S2 | [HTTPwg官方RFC9110 XML](https://github.com/httpwg/http-core/blob/bde37f634681bd5462568b73aa722af9c9a3ef5e/rfc9110.xml#L8578)，标准日期2022-06；读取快照commit `bde37f634681bd5462568b73aa722af9c9a3ef5e`（2025-11-14T08:08:17Z） | editor实际读§15.3.3/202 Accepted源码8578–8599行。接受处理不等于处理完成，请求最终可能不被执行；结果可以指向状态监控。用于核对“受理≠完成”语义边界 | 教学VendorSdk的QUEUED由本项目契约定义，不能因语义类似就声称它实现HTTP202。没有用RFC替自造SDK编造官方规范 |
| S3 | [OpenJDK21 Enumeration.asIterator](https://github.com/openjdk/jdk21u/blob/54f2095960f01d957f2335cafa0defb956e13a2c/src/java.base/share/classes/java/util/Enumeration.java#L85)与[Iterator可选remove](https://github.com/openjdk/jdk21u/blob/54f2095960f01d957f2335cafa0defb956e13a2c/src/java.base/share/classes/java/util/Iterator.java#L76)，jdk-21.0.8+9，commit `54f2095960f01d957f2335cafa0defb956e13a2c`（2025-07-09） | pattern_java取得并读完整源，editor另复读Enumeration28–129和Iterator58–105行。API注释说明将产出Enumeration的代码接到消费Iterator的代码；匿名Iterator真实委托原实例，remove仍抛不支持。支持适配使用约定与缺失能力不自动补齐的边界例 | 原Enumeration在asIterator后再直接遍历的语义未定义；匿名类捕获外部实例，不说它显式定义了持有字段。这里只参考设计关系，不把旧接口推荐为新业务API，不在视频展开遍历 |
| S4 | [Spring官方HandlerAdapter](https://github.com/spring-projects/spring-framework/blob/7bdf9c86f8657029567067051b7c6bd47b4ae67e/spring-webmvc/src/main/java/org/springframework/web/servlet/HandlerAdapter.java)与[HttpRequestHandlerAdapter](https://github.com/spring-projects/spring-framework/blob/7bdf9c86f8657029567067051b7c6bd47b4ae67e/spring-webmvc/src/main/java/org/springframework/web/servlet/mvc/HttpRequestHandlerAdapter.java)，同S1主干快照 | editor实际读完整源。共同SPI使DispatcherServlet不用包含具体handler类型的代码，具体适配器检查支持类型后委托handleRequest。用于交叉核对统一使用约定与实际委托 | 这里handler经每次参数传入，没有显式保存adaptee字段；不拿它证明本片“持有SDK对象”的结构，也不照搬框架全流程 |

本次editor来源URL、Git blob SHA、短摘录与读取范围保存在[`sources/editor-evidence.json`](sources/editor-evidence.json)。S1 blob为`38be515d885c408159cfba4382fe52169bf118d0`，S2 blob为`08e100400c819548ea4aec262e2d4d78d18321fa`；blob SHA与commit SHA含义不同，不混写。S4通过同次主干完整读取，不以类名独自判断设计意图。

### Java实现侧的补充阅读

pattern_java另实际读取同一OpenJDK21固定commit的InputStreamReader、Exception和RuntimeException完整Javadoc/源，及Spring6.2.8固定commit `502b31a7f2b9710571bf973249ccb90c413982d0`的TaskExecutorAdapter/HandlerAdapter/HttpRequestHandlerAdapter。读取URL、完整文件SHA、行范围及边界在[`demo-java/source-review.json`](demo-java/source-review.json)和[`demo-java/research-notes.md`](demo-java/research-notes.md)。

- InputStreamReader实际持有StreamDecoder并委托，不简单说它有一个InputStream字段；Javadoc的普通bridge用词不当作GoF Bridge分类。
- Exception的cause机制支持保存原异常，不能据此替通知业务决定什么算已受理。
- 固定Spring6.2.8源用于可复查结构证据，其旧AsyncListenableTaskExecutor已弃用，不建议照抄；本期主概念优先采用S1现代源。

这些是实际阅读与版本记录，不是本片已完成动态/成片检查，也不声称读过完整JLS或全部Spring文档。

## 关键短引

- S1：`Adapter that takes a JDK java.util.concurrent.Executor ... exposes a Spring ... TaskExecutor`；字段`private final Executor concurrentExecutor`；真实调用`concurrentExecutor.execute(...)`。转换后仍委托原对象，不是仅改名。
- S2：`accepted for processing, but the processing has not been completed`；`might or might not eventually be acted upon`。已接受处理不能推出最终完成。
- S3：`adapt code that produces Enumeration instances to code that consumes Iterator instances`；默认remove抛`UnsupportedOperationException`。适配不是自动创造原实例没有的操作。

## 片内事实与证据映射

| 使用位置 | 事实/设计关系 | 证据与范围 |
|---|---|---|
| 01–02 | 订单17发货提醒的产品操作、业务需要受理结果，与外部格式不同 | 本项目自造教学示例，所有输入标示例；没有真实外发或真实厂商架构断言 |
| 03–04 | Client依赖Target；本例Adapter履行Target并持有Adaptee；契约不是运行中继 | S1/S3/S4交叉核对与本例实际源码；本片采用对象适配器，不声明所有适配器都采用同一种组合实现 |
| 05–06 | 同一recipient/text转换成target/body后，真正委托SDK | demo源码及12组行为验证捕获字段与调用次数；正文不讲Java语法 |
| 07–08 | QUEUED/Q17→ACCEPTED/Q17，回同一产品页已受理/等待回执 | 本例契约+实际运行；S2仅支持接受不等于完成的标准边界，不证明SDK使用HTTP202 |
| 09 | 明确拒绝可映射拒绝；通信异常/未知不能改成确定接受或拒绝 | 本例SendFailure政策、受理后丢包等实际验证；SDK异常cause保留，无自动重试 |
| 10–12 | 业务目标约定不变时隔离服务使用细节，装配/配置仍需改；额外转换层有成本 | 对本例依赖/代码关系的设计分析；不声称普遍提高性能或零修改，S3作缺失能力辅助例 |

## 教学SDK冻结契约与实际运行

- 提醒目标只要求**提交并返回受理结果**，不承诺送达。
- `ShipmentReminder`只使用`Notifier`，不解释供应方DTO或原状态。
- `NotificationAdapter`持有`VendorSdk`，将`recipient/text`原值对应到`Payload(target,body)`，每次提交只委托一次。
- 明确`QUEUED`且有非空ticket时返回`ACCEPTED`和同一编号；明确`REJECTED`返回业务拒绝和空reference。
- null/空/未知回执或QUEUED缺编号属于未确认，抛`SendFailure`；供应方技术异常转换并保存cause。不能把“调用没拿到回包”当作“供应方必定没收到”。无自动重试、去重或投递事务承诺。
- `FakeVendorSdk`无网络，只模拟协议结果；它不真的排队/投递提醒，不能被当成真实服务能力证据。

[`demo-java/AdapterDemo.java`](demo-java/AdapterDemo.java)与独立[`VerifyAdapter.java`](demo-java/VerifyAdapter.java)已由pattern_java在OpenJDK21实际编译运行，12类行为场景通过，卡片21行逐字来自完整源。实际结果、编译命令和源码SHA见[`demo-java/verified-results.json`](demo-java/verified-results.json)。这证明所选实现行为，不是消息真实送达、视频已经教懂或用户已观看的结论。

## 叙事、图文与不进入主片的支线

01先看一次产品操作和已受理目标，02明确回到接入前，避免在正在运行的请求中“现造”适配器。03逐角色、04模式名，05再回看同一次提交；运行路径Client→Adapter→SDK，返回原路，Target只作契约依赖。页面/结构/Java保持同一对象、收件人、正文和Q17。

拒绝与未知只作一段语义规则，不再发第二条；第二SDK、复杂异常恢复、回执查询或消息中间件不展开。Java关键节选只连接角色与实现，完整代码放图文复查，正文不变成语言课。转换的意义和限制在视频闭环，图文只补字段与证据。实际动态/媒体检查另行记录，不用资料阅读或Java运行替代。
