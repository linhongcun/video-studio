# D03 Java资料采用说明

访问日期：2026-10-25。本记录从生产实现前的独立调研转存，按最终冻结契约更新；原完整程序为[AdapterDemo.java](AdapterDemo.java)，本轮升级示例为[AdapterUpgradeDemo.java](AdapterUpgradeDemo.java)，实际编译与原12组＋升级8组结果见[verified-results.json](verified-results.json)。本记录不是视频质量或观众理解验收。

## 为什么本例符合对象适配器

业务使用者只依赖自己的Notifier目标约定，NotificationAdapter实现这个约定、组合持有VendorSdk，把同一请求的recipient/text转换为target/body，再把SDK的QUEUED/Q17转换为业务的ACCEPTED/Q17。这里有实际参数组织和结果语义差异，不只是给方法改名；也不通过继承或修改既有SDK来强行达成关系。main承担外部创建接线，替换SDK仍须维护适配器、配置和映射。

目标约定只表示提交并确认受理结果，不要求SDK没有提供的送达/撤回能力。已受理不能翻译为已送达。SDK异常及未知回包属于未确认，不能一律翻译为拒绝：请求可能已经被SDK收下，只是回复丢失。本实现每次提交最多委托一次，不自动重试或宣称幂等。

完整例中FakeVendorSdk只有本地返回；验证器自己的Probe独立捕获Payload与调用次数，并模拟已受理后丢失回包，区分“没有拿到回执”和“明确没有受理”。这是透明的教学契约，不是某个真实厂商的故障保证。

## Java契约采用范围

Notifier和VendorSdk是不同接口，NotificationAdapter实现目标并持有已有接口对象；接口不是请求必须穿过的运行中继。SendFailure是业务侧checked异常，VendorFailure是SDK声明的checked通信失败；仅后者被适配器翻译并保留cause。输入错误在委托前拒绝；未知回包单独失败。未把所有unchecked异常和Error伪装成受理失败。

源码先经独立子agent只读静态核查，确认上述契约和21行节选，无阻塞发现。之后的实际编译/运行证据独立记录在verified-results.json；“缺失送达能力”仍是契约与文稿审查边界，不虚构运行测试来证明真实世界不会送达。

以上21行指首版卡片。本轮保留原源码，新增SDK V2及其独立验证，当前卡为新源的15行分段节选；独立静态复核确认V2转换/故障边界、旧12组保留和新8组覆盖。当前生产身份以java-card.json及verified-results.json为准。

## 本轮业务边界与防腐职责核对

可以主动先定义业务需要的Notifier，再适配外部SDK；不是只有历史系统突然不兼容才用适配器。SDK V2改变请求字段、回执包装和状态词，而本例受理语义仍可实现，所以业务使用者原源保持不变，转换层和外部接线承担变化。

已实际阅读Microsoft官方Architecture Center防腐层文档的固定GitHub版本。它将ACL描述为在语义不同子系统之间的facade或adapter层，并强调业务侧仍使用自身模型、保护领域模型。准确表述是“适配器可以承担防腐边界中的转换职责”，不是“Adapter就是完整ACL”。本轮还读取JDK FilterInputStream的同接口wrapper说明，核对包裹/组合/转发本身不足以识别适配器。完整URL、固定commit、短原文和采用限制单列于[本轮证据](../sources/business-boundary-evidence.json)。

局部改动只在目标业务语义仍不变且新SDK仍提供足够能力时成立；它不保证SDK依赖、配置、外部接线和验证都不需要维护，也不能把缺失受理确认或接收者映射能力隐藏成普通字段调整。程序中的V1/V2请求各自独立，视频的升级段仅为后来开发变更对照。

## 已实际阅读的一手来源

网络政策已通过cloud-environment-runtime技能和当前实例状态核对：restricted/enforced；`raw.githubusercontent.com`、`api.github.com`允许，`docs.oracle.com`和Twilio站点不允许。本次只经正常代理访问允许的官方GitHub域名，未尝试绕过。以下均实际下载后逐行读取，访问日2026-10-25；原源保留版权头。没有阅读GoF全书，未声称核查过其全文。此处Java语义来自Java21官方公开源码内Javadoc及实现，不冒称已读完整JLS21。

OpenJDK固定版本：仓库`openjdk/jdk21u`，tag `jdk-21.0.8+9`，commit `54f2095960f01d957f2335cafa0defb956e13a2c`（2025-07-09）。Spring固定版本：仓库`spring-projects/spring-framework`，tag `v6.2.8`，commit `502b31a7f2b9710571bf973249ccb90c413982d0`（2025-06-12）。它们是本次可复查版本，不声称截至2026-10-25最新。

| 官方源与实际读取范围 | 本次采用内容与限制 |
|---|---|
| [Enumeration.java](https://github.com/openjdk/jdk21u/blob/54f2095960f01d957f2335cafa0defb956e13a2c/src/java.base/share/classes/java/util/Enumeration.java#L85)，全文129行，重点44–50/85–127 | 官方说明把产出Enumeration的代码接到消费Iterator的代码，asIterator返回实现Iterator的匿名对象，hasNext/next委托原Enumeration的两个方法；remove仍不支持。匿名类通过外部实例捕获，不应谎称这段显式写了private字段。适配后直接继续操作原Enumeration的遍历语义未定义，不能忽略状态约束。 |
| [Iterator.java](https://github.com/openjdk/jdk21u/blob/54f2095960f01d957f2335cafa0defb956e13a2c/src/java.base/share/classes/java/util/Iterator.java#L76)，全文135行，重点58–103 | 目标接口可以有明确的可选能力和失败约定；remove默认抛UnsupportedOperationException，适配不会自动补齐底层没有的删除能力。不因此向本例Notifier加入optional删除方法。 |
| [InputStreamReader.java](https://github.com/openjdk/jdk21u/blob/54f2095960f01d957f2335cafa0defb956e13a2c/src/java.base/share/classes/java/io/InputStreamReader.java#L34)，全文205行，重点34–45/62–63/87–91/167–203 | Javadoc描述字节到字符的转换；实际实现extends Reader、持有StreamDecoder并委托。它不是简单直接持有InputStream字段的两方法包装；解码/预读有额外语义。此处bridge是普通说明词，不等于GoF Bridge模式分类。正文不搬这些底层细节抢主线。 |
| [Exception.java](https://github.com/openjdk/jdk21u/blob/54f2095960f01d957f2335cafa0defb956e13a2c/src/java.base/share/classes/java/lang/Exception.java#L28)，全文125行，重点28–38/70–85；[RuntimeException.java](https://github.com/openjdk/jdk21u/blob/54f2095960f01d957f2335cafa0defb956e13a2c/src/java.base/share/classes/java/lang/RuntimeException.java#L28)，全文120行，重点28–43 | 非RuntimeException的Exception子类为checked，若向调用边界传播需要声明；RuntimeException为unchecked。Exception(message,cause)保存cause，支持将VendorFailure翻译为SendFailure并保留原原因。这不规定通知领域应该把什么视为成功，后者是本例业务契约。 |
| [TaskExecutorAdapter.java](https://github.com/spring-projects/spring-framework/blob/502b31a7f2b9710571bf973249ccb90c413982d0/spring-core/src/main/java/org/springframework/core/task/support/TaskExecutorAdapter.java#L34)，全文176行，重点34–62/86–115/161–174 | 官方明确称Adapter；实现Spring侧接口、final Executor字段及构造器接入、向组合对象委托；把RejectedExecutionException翻译为TaskRejectedException，展示异常也可属于边界转换。该版本的AsyncListenableTaskExecutor已deprecated，不能据此推荐新项目照抄其完整API；这里只引用组合/委托和明确异常映射，不把通知超时类比成线程池明确拒绝。 |
| [HandlerAdapter.java](https://github.com/spring-projects/spring-framework/blob/502b31a7f2b9710571bf973249ccb90c413982d0/spring-webmvc/src/main/java/org/springframework/web/servlet/HandlerAdapter.java#L24)，全文92行；[HttpRequestHandlerAdapter.java](https://github.com/spring-projects/spring-framework/blob/502b31a7f2b9710571bf973249ccb90c413982d0/spring-webmvc/src/main/java/org/springframework/web/servlet/mvc/HttpRequestHandlerAdapter.java#L27)，全文65行 | 框架通过共同SPI处理不同handler，具体适配器implements HandlerAdapter、supports先判定类型、handle再委托handleRequest。这个类每次通过handler参数取得已有对象，没有持有被适配对象字段；不能充当本例“显式持有SDK”的直接源证据。 |

所有下载URL、完整源码SHA、行数及两个tag解析到commit的实际GitHub API结果见[source-review.json](source-review.json)。原下载副本仅留工作区调研目录，未把完整第三方源码复制进本例。资料阅读、实现测试与视频/学习效果验收分别记录。
