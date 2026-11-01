# D03发货提醒的Java对象适配器

本例仍是商家为订单17发送发货提醒：接收者`buyer17@shop.example`，正文“订单17已发货”。这是假想通知SDK的本地教学示例，`FakeVendorSdk`没有网络调用或真实外发；未据此断言真实产品内部采用此结构。

完整可独立编译程序为[AdapterDemo.java](AdapterDemo.java)。业务使用者`ShipmentReminder`仅依赖`Notifier`；`NotificationAdapter`实现该业务目标接口，并组合持有既有`VendorSdk`，把`recipient/text`转换为`Payload.target/body`后调用一次，再翻译结果。创建与接线在`main`，接入另一SDK时仍需维护构造、配置与映射规则，不能称整个项目无需变化。这是核心设计关系演示，未实现完整产品UI、真实发货或生产通知服务。

## 明确的业务和异常契约

`Notifier.send(recipient,text)`返回`Submission(Status,reference)`，另声明checked `SendFailure`：

| SDK结果 | 业务可知结论 |
|---|---|
| `QUEUED`且ticket非空白 | `ACCEPTED`与原ticket，如`Q17`；只代表已受理，等待送达回执 |
| 明确`REJECTED` | `REJECTED`和空字符串reference，表示本例没有受理凭据 |
| SDK声明的`VendorFailure` | `SendFailure`表示受理结果未确认，保留同一原始cause |
| null回执、null/空白/未知状态、QUEUED缺ticket | `SendFailure`表示未确认，不能默认受理或拒绝 |

`RawReceipt.status`采用String，因此未来未知值是实际可达的协议输入。本例不大小写归一化、不trim、不截断正文或凭据。null/空白业务接收者或正文在委托前抛`IllegalArgumentException`，SDK调用零次；它不验证真实渠道地址格式或业务长度政策。

每次有效业务提交最多委托SDK一次，无自动重试或去重。通信异常可能发生在SDK受理之后，不能当作明确拒绝，更不能据此断言重复提交安全。只翻译SDK契约声明的通信失败；不吞掉意外的编程错误或Java Error。协议错误没有可用原始异常时，不编造cause。

`ACCEPTED`不等于送达。SDK没有提供的送达确认、撤回、持久化或幂等保证，适配器不能凭转换自动补齐。这些是本例明确契约，不是适配器模式普遍规定的全部故障语义。

## 实际编译与只读复核

从仓根运行：

```sh
python3 episodes-codex/adapter-pattern/demo-java/verify.py
```

默认仅在临时目录编译、运行和逐行核对代码卡，不写源码、卡或已有结果。审读并有意改变源后，才使用显式`--write-artifacts`更新卡及结果；写入发生在编译与行为检查成功之后。实际工具链、源码/验证器/来源记录SHA、命令、stdout和12项结果见[verified-results.json](verified-results.json)。

本机为OpenJDK21.0.12.1，`jdk.compiler`模块可用；验证器实际以`java --module jdk.compiler/com.sun.tools.javac.Main`编译完整程序及独立[VerifyAdapter.java](VerifyAdapter.java)，再运行两者。不会用D01/D02记录替代本例Java验证。

12组可观察行为为：正常受理与原ticket；明确拒绝；SDK失败cause；SDK先受理再丢回包且不重试；null回执；null/空白状态；可达未知状态；QUEUED缺ticket；六种非法输入委托前拒绝；Unicode/字段/凭据精确映射；两次独立提交；业务使用者接入独立Notifier替身并原样传播未确认。验证器拥有自己的SDK Probe，通过捕获实际Payload与调用次数检查行为。

“目标接口没有送达/撤回能力”的限制由契约和源码/文稿审查说明，不伪造一个无关能力单元测试来代替语义检查。运行通过也不代表视频画面或初学者理解已经验收。

## 暂停代码卡与完整源

实际卡源为`remotion/src/java-card.json`，标题明确“Java关键代码 · 节选”，从完整Java的两个标记区间提取：目标约定与适配器，以及main外部创建接线和一次调用。每一显示行都有源行号、移除缩进和完整源码SHA，可由只读验证器核对；不是一屏完整可复制编译程序。

卡片省略外层类/import、业务返回和SDK DTO/异常定义、参数/无效回执防护帮助方法、ShipmentReminder/FakeVendorSdk完整类及main打印。关键的实现接口、持有、参数转换、委托、已知结果映射和异常翻译仍可见。正文先讲职责与协作，卡片供暂停阅读，不逐行口播语法。

## 实际阅读的一手来源

访问日2026-10-25。公开固定commit链接、源文件完整SHA、实际读取范围和采用限制见[source-review.json](source-review.json)，完整调研边界见[research-notes.md](research-notes.md)。本次从允许的官方GitHub域名实际读取源码与其Javadoc，未绕过网络限制访问Oracle/Twilio；未阅读GoF全书，不冒称核查其全文或完整JLS。

- OpenJDK21u `jdk-21.0.8+9`，commit `54f2095960f01d957f2335cafa0defb956e13a2c`：`Enumeration.asIterator`给出目标接口对象与原Enumeration委托；`Iterator.remove`明确保留不支持能力。`Exception`/`RuntimeException`源码Javadoc说明checked与unchecked及cause。`InputStreamReader`实际继承Reader、持有StreamDecoder并委托，不能把其中普通词bridge当成GoF Bridge的分类证据。
- Spring Framework `v6.2.8`，commit `502b31a7f2b9710571bf973249ccb90c413982d0`：`TaskExecutorAdapter`实现目标接口、持有final Executor、委托并翻译明确拒绝异常，是本例组合关系的直接参照。该版本的Listenable接口已deprecated，不建议新项目照抄完整API。`HttpRequestHandlerAdapter`通过每次handler参数取得已有对象，没有持有它的字段，不用于证明本例的“持有SDK”。

源码阅读提供可核查的结构和Java契约依据，不证明假想通知服务采用某个真实厂商的语义。测试证明本例在声明范围内运行，不能推导真实送达或生产可靠性。
