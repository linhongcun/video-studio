# D03 适配器模式：正式调研与事实映射

访问日期：**2026-10-25（北京时间）**。首发开工基线`ff730833e37e39edf9962ad414b0f325755adc73`；用户观看v0.63.0后的本轮修订从最新主干`5a5594fb`开始。通过允许访问的官方GitHub源读取正文，没有绕过当前网络限制访问其他站点。未取得GoF经典书籍全文，不声称读过相关完整章节；此前Refactoring.Guru记录不当作本次重读。

本轮唯一问题：**为什么在日常接入外部接口时主动包一层，让外部能力符合业务自己的约定，并隔离外部格式升级？** 用户指出首发讲法复杂且像被迫包装，因此本轮10镜20句先讲两项收益，再以原订单17提醒演一次去回和一次升级对照。规则/结果边界继续正确，但不再抢占主线；不固定真实短信/邮件供应方，不把教学UI当作真实产品源码证据。

## 实际阅读来源

| 编号 | 公开固定来源与时间 | 实际阅读及采用 | 限定 |
|---|---|---|---|
| S1 | [Spring官方TaskExecutorAdapter](https://github.com/spring-projects/spring-framework/blob/7bdf9c86f8657029567067051b7c6bd47b4ae67e/spring-core/src/main/java/org/springframework/core/task/support/TaskExecutorAdapter.java)，主干快照commit `7bdf9c86f8657029567067051b7c6bd47b4ae67e`，提交时间2026-10-24T15:05:57Z | editor通过GitHub connector取得并阅读完整源，再按commit固定重取。Javadoc明确暴露Spring侧TaskExecutor/AsyncTaskExecutor；实现目标接口，持有final Executor字段，构造接线，execute/submit委托，RejectedExecutionException转换为TaskRejectedException。支持一种对象适配器的契约/持有/委托/明确转换关系 | 主干快照不是稳定发布推荐；不借版权头断定文件更新年，不把任务执行中的同步/异步、装饰或错误策略推广为适配器统一语义 |
| S2 | [HTTPwg官方RFC9110 XML](https://github.com/httpwg/http-core/blob/bde37f634681bd5462568b73aa722af9c9a3ef5e/rfc9110.xml#L8578)，标准日期2022-06；读取快照commit `bde37f634681bd5462568b73aa722af9c9a3ef5e`（2025-11-14T08:08:17Z） | editor实际读§15.3.3/202 Accepted源码8578–8599行。接受处理不等于处理完成，请求最终可能不被执行；结果可以指向状态监控。用于核对“受理≠完成”语义边界 | 教学VendorSdk的QUEUED由本项目契约定义，不能因语义类似就声称它实现HTTP202。没有用RFC替自造SDK编造官方规范 |
| S3 | [OpenJDK21 Enumeration.asIterator](https://github.com/openjdk/jdk21u/blob/54f2095960f01d957f2335cafa0defb956e13a2c/src/java.base/share/classes/java/util/Enumeration.java#L85)与[Iterator可选remove](https://github.com/openjdk/jdk21u/blob/54f2095960f01d957f2335cafa0defb956e13a2c/src/java.base/share/classes/java/util/Iterator.java#L76)，jdk-21.0.8+9，commit `54f2095960f01d957f2335cafa0defb956e13a2c`（2025-07-09） | pattern_java取得并读完整源，editor另复读Enumeration28–129和Iterator58–105行。API注释说明将产出Enumeration的代码接到消费Iterator的代码；匿名Iterator真实委托原实例，remove仍抛不支持。支持适配使用约定与缺失能力不自动补齐的边界例 | 原Enumeration在asIterator后再直接遍历的语义未定义；匿名类捕获外部实例，不说它显式定义了持有字段。这里只参考设计关系，不把旧接口推荐为新业务API，不在视频展开遍历 |
| S4 | [Spring官方HandlerAdapter](https://github.com/spring-projects/spring-framework/blob/7bdf9c86f8657029567067051b7c6bd47b4ae67e/spring-webmvc/src/main/java/org/springframework/web/servlet/HandlerAdapter.java)与[HttpRequestHandlerAdapter](https://github.com/spring-projects/spring-framework/blob/7bdf9c86f8657029567067051b7c6bd47b4ae67e/spring-webmvc/src/main/java/org/springframework/web/servlet/mvc/HttpRequestHandlerAdapter.java)，同S1主干快照 | editor实际读完整源。共同SPI使DispatcherServlet不用包含具体handler类型的代码，具体适配器检查支持类型后委托handleRequest。用于交叉核对统一使用约定与实际委托 | 这里handler经每次参数传入，没有显式保存adaptee字段；不拿它证明本片“持有SDK对象”的结构，也不照搬框架全流程 |
| S5 | [Microsoft官方Anti-Corruption Layer文档源](https://github.com/MicrosoftDocs/architecture-center/blob/b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a/docs/patterns/anti-corruption-layer.md)，commit `b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a`（2026-10-24），Frontmatter ms.date为2026-05-28 | pattern_java本轮实际读完整106行；editor另通过GitHub connector重读完整正文。说明可用facade/adapter层转换通信，业务侧继续用自己的数据模型，核心目的是保护领域模型；还讨论维护、延迟与语义差异的适用范围 | Adapter不是ACL同义词。文档对没有显著语义差异的系统也有限制，不能把一层技术字段包装就宣称为完整领域防腐架构；本例只演示保护业务用法、把外部细节留边界的作用，业务规则仍在业务方 |
| S6 | [OpenJDK21 FilterInputStream](https://github.com/openjdk/jdk21u/blob/54f2095960f01d957f2335cafa0defb956e13a2c/src/java.base/share/classes/java/io/FilterInputStream.java#L28)，同S3固定commit | pattern_java本轮实际读28–75行：官方说wraps另一个输入流，仍沿InputStream约定工作。用于挑战“只要持有/包装另一个对象就是Adapter”的不足判断标准 | 源码未给出GoF分类；本例只证明wrapper结构本身不充分，不能据此给所有包装/装饰/代理下结论 |

本次editor来源URL、Git blob SHA、短摘录与读取范围保存在[`sources/editor-evidence.json`](sources/editor-evidence.json)。S1 blob为`38be515d885c408159cfba4382fe52169bf118d0`，S2 blob为`08e100400c819548ea4aec262e2d4d78d18321fa`；blob SHA与commit SHA含义不同，不混写。S4通过同次主干完整读取，不以类名独自判断设计意图。

### Java实现侧的补充阅读

pattern_java另实际读取同一OpenJDK21固定commit的InputStreamReader、Exception和RuntimeException完整Javadoc/源，及Spring6.2.8固定commit `502b31a7f2b9710571bf973249ccb90c413982d0`的TaskExecutorAdapter/HandlerAdapter/HttpRequestHandlerAdapter。读取URL、完整文件SHA、行范围及边界在[`demo-java/source-review.json`](demo-java/source-review.json)和[`demo-java/research-notes.md`](demo-java/research-notes.md)。

- InputStreamReader实际持有StreamDecoder并委托，不简单说它有一个InputStream字段；Javadoc的普通bridge用词不当作GoF Bridge分类。
- Exception的cause机制支持保存原异常，不能据此替通知业务决定什么算已受理。
- 固定Spring6.2.8源用于可复查结构证据，其旧AsyncListenableTaskExecutor已弃用，不建议照抄；本期主概念优先采用S1现代源。

这些是实际阅读与版本记录，不是本片已完成动态/成片检查，也不声称读过完整JLS或全部Spring文档。

本轮业务边界来源、实际完整文件SHA/范围/短引和采用限制见[`sources/business-boundary-evidence.json`](sources/business-boundary-evidence.json)。S5文件SHA256为`2c2f1586eb46629a57470c70ef645bfaf60428125654171780dfcfdf2380e48a`，Git blob为`5c75242fdf4cc3c264d6a80145eef3159c02692d`，二者不要混同。

## 关键短引

- S1：`Adapter that takes a JDK java.util.concurrent.Executor ... exposes a Spring ... TaskExecutor`；字段`private final Executor concurrentExecutor`；真实调用`concurrentExecutor.execute(...)`。转换后仍委托原对象，不是仅改名。
- S2：`accepted for processing, but the processing has not been completed`；`might or might not eventually be acted upon`。已接受处理不能推出最终完成。
- S3：`adapt code that produces Enumeration instances to code that consumes Iterator instances`；默认remove抛`UnsupportedOperationException`。适配不是自动创造原实例没有的操作。

- S5：`Communication ... always uses the data model and architecture of subsystem A`；`core purpose ... protect the domain model`。支持业务保有自身表达和边界保护目的，不支持把Adapter等同完整ACL。
- S6：`wraps some other input stream`，仍为InputStream使用约定。只凭包装/委托不够识别适配器，必须核对目标约定和转换意图。

## 片内事实与证据映射

| 使用位置 | 事实/设计关系 | 证据与范围 |
|---|---|---|
| 01–02 | 主动按业务定义收件人/正文→受理结果的约定，把外部细节集中到边界 | S1/S5支持消费方目标/保护自身模型，原订单17教学例给出具体业务约定；不等一次旧接口事故才设计 |
| 03 | Client依赖Target，Adapter履行Target并持有服务；Target不是运行中转 | S1/S3/S4与V1源实际关系；本片对象适配器，不声明所有实现必须组合持有 |
| 04–06 | 同次V1请求先转入参并调用服务，再转结果回UI；Q17原样保留 | 原AdapterDemo/VerifyAdapter字节保持，原12组运行继续通过；完整去回未省略为纯概念口号 |
| 07–08 | 外部输入改为destination/content，回执多包一层，V2Adapter/创建接线变，业务类型/调用保持 | 新AdapterUpgradeDemo/VerifyAdapterUpgrade与新增8组实际验证；独立V2测试不当作页面第二次提交，版本变化不在运行中热插 |
| 09 | 保护业务自己的规则/用法有防腐作用，仍有维护和能力前提 | S5原文及本例依赖边界；不声称完整ACL，不把业务规则搬到转换层，不把所有wrapper叫Adapter |
| 10 | 两项收益回扣：业务定约定、集中外部差异与升级影响 | 对本例结构与已验证变化范围的设计分析；只在业务需要/含义保持且可实现时隔离本次格式变化，不保证所有升级无影响 |
| 页面短标签/图文扩展 | 受理不等于送达，技术未知不能当确定拒绝，未补出可靠送达能力 | 原V1十二组和V2八组边界验证；S2支持接受不等于处理完成，但SDK协议是教学自定义，不能说用了HTTP202 |

## V1/V2例子的实际变化范围

| 项目 | V1 | V2/保留情况 |
|---|---|---|
| 输入 | Payload(target,body) | Envelope(destination,content) |
| 回执 | RawReceipt(status=QUEUED,ticket=Q17) | ReplyV2(receipt=ReceiptV2(state=ENQUEUED,reference=Q17)) |
| 业务结果 | Submission(ACCEPTED,Q17) | 同一含义和编号，均未确认送达 |
| 业务约定/使用者 | Notifier/Submission/ShipmentReminder | 直接复用原AdapterDemo的类型，原业务类字节不变 |
| 变化 | 原NotificationAdapter与外部接线 | 新NotificationAdapterV2及服务创建/接线；维护请求、嵌套结果和错误映射 |

[`demo-java/AdapterDemo.java`](demo-java/AdapterDemo.java)和原[`VerifyAdapter.java`](demo-java/VerifyAdapter.java)完整字节保留。新[`AdapterUpgradeDemo.java`](demo-java/AdapterUpgradeDemo.java)需要与原文件共同编译，以复用既有业务类型；新增[`VerifyAdapterUpgrade.java`](demo-java/VerifyAdapterUpgrade.java)检查V2。统一运行的实际结果见[`demo-java/verified-results.json`](demo-java/verified-results.json)：Java21下原12组＋升级8组共20组通过；当前卡片15行与新源节选同源，不再沿用首发21行错误防护主体。

V1/V2教学SDK无网络、无真实外发。程序中两版本是各自独立的测试请求；视频07–08只是后来升级的静态开发对照，不再次发送提醒。测试同时覆盖空/未知嵌套回执、缺编号、技术失败前后未确认、字段/编号精确保留、不暗中重试等；它们保证当前示例行为，不作真实供应方保证。

## 当前叙事与能力边界

产品操作→两项主动收益→四角色→一次完整运行→后来一次升级隔离→简短防腐作用/成本→两收益回收。原来接口对不上、拒绝/未知及能力限制的连续解释不再构成视频主线。Target仍只表示契约，真实消息沿业务方→适配器→服务、结果原路返回；Java后置，不逐行教语法。

“主动包装”本身不等于Adapter，必须有目标约定、把已有接口转换到该用法的意图和委托。完整ACL是保护领域模型的架构目的，可使用Adapter/Facade等，更可能包含业务语义转换；本片主要演示接口技术细节的边界隔离。没有语义冲突时不因一层薄包装就自称完整ACL。

旧受理/送达、拒绝/未知、异常保留与无自动重试规则仍在Java和文章扩展中；目标约定/服务能力不足时，上层也可能变化。资料阅读、编译运行、动态和正式媒体检查分开记录，不预写新稿用户认可、完整听辨、ASR或新手实验结果。

## 片尾参考资料

2026-10-26为存量原片整理title-author清单，2项一页5秒。TaskExecutorAdapter取实际源码类声明原名，明确Javadoc作者为Juergen Hoeller，机构Spring Framework；Anti-Corruption Layer pattern取正文H1完整原题，机构Microsoft · Azure Architecture Center，仅维护账号不足以推断个人作者。原技术实读日期均保留2026-10-25。

本轮2份完整固定官方raw GET仅补核原题／明确署名及原文身份：Spring5309字节／SHA2564b450a253fcfad5879f88fd12603269efb9ee116a8fd0a5103142e2be38beff0，Azure10713字节／SHA2562c2f1586eb46629a57470c70ef645bfaf60428125654171780dfcfdf2380e48a，与原25日business-boundary-evidence所记完整SHA完全相同。26日元数据补核不追记为技术新读，也未访问其他受限文档站。

两项直接支持对象适配器的契约／持有／转换委托及业务自己的模型边界。其余OpenJDK示例、wrapper反例与RFC202保留原文章拓展，不为条数加入片尾；未读GoF全文、旧Refactoring.Guru未重读的限制照旧。教学V1/V2与20组验证仍为既有工作，本轮不重新执行Java或改造视频、静默代码卡、原引用与配图。完整标题／署名证据、逐论点旧读与原研究Git blob／SHA、本轮原始响应字节和完整SHA见[本轮证据](../../docs/archive/2026-10/reference-endcards-batch-12/sources-adapter-pattern.json)，清单见[references.md](references.md)。
