# D02 观察者模式：恢复模式主线的编辑复核

本轮编辑日期：**2026-10-25（北京时间）**。开工基线`d515f0d4a136667766e5201217e6e5fb746ea861`。用户最新反馈否定v0.68.4将大部分篇幅转为MQ工程的方向，本轮改回观察者模式的动机、角色、订阅、通知、退出和取舍，MQ仅留一镜简短应用。v0.68.4的技术检查仍属于其历史媒体，不代表其教学方向获认可，也不能充当新成片检查。

要回答的问题：**订单发生变化后，怎样让需要它的功能各自响应？接收方增减时，怎样把来源变化与接收后的具体处理分开？**

## 资料复用与访问声明

本轮没有新发起网络检索。编辑复用2026-10-25上一轮实际取得并阅读的公开正文，本次重新读取已保存的相关章节，核对新脚本与文章。重新编辑、重读本地证据与新访问网页是不同动作，不将它们合并表述。

- 主要使用`revisions/mq-practice/research-observer-pubsub.json`，完整SHA-256 `14f768fbc12a65ca5398ea67e225cbdb4c10fef45f1745958fb90559fde49215`。其中Microsoft Observer与Azure Pub/Sub均有完整取回正文和元数据。
- 七页旧证据中的RabbitMQ与Outbox正文保留在`revisions/mq-practice/research-rabbitmq-outbox.json`，完整SHA-256 `cb742536cd64bc30d11861aed681ec729e51a6015195854217fb66baf7cfec68`。它们是前一编辑方向的历史调研材料，除发布/订阅拓扑交叉核对外，不支撑本轮扩大讲解范围。
- 更早的原12镜公开来源映射，可由`revisions/mq-practice/baseline/script.md`及其基线Git版本的`research.md`追溯；本轮只复核相关映射，不声称重新取得或通读其中所有资料。
- 未取得或声称阅读GoF书籍全文。Microsoft网页取回时虽有通用授权提示，工具实际返回了公开正文，没有访问私有账户内容。

## 当前主张的主要公开依据

| 编号 | 来源与本轮重读范围 | 支持内容 | 不作的推广 |
|---|---|---|---|
| M1 | [Microsoft：Observer design pattern](https://learn.microsoft.com/en-us/dotnet/standard/events/observer-design-pattern)；重读概述、When to apply、角色清单、When to consider alternatives | 来源与观察者分工、登记关系、共同接收约定、通知数据、取消关系；单应用简单通知可使用已有标准事件 | .NET接口只是具体实现；文档明确一般接口不规定通知次序，不能把示例的顺序或同步方式当作模式定义 |
| M2 | [Azure Architecture Center：Publisher-Subscriber pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/publisher-subscriber)；重读Context/problem、Solution及Existing technologies | 分布式发布者通过消息基础设施面向各订阅输出通道，优先采用已有产品；只用于09应用联系 | 这是分布式消息结构，不是GoF观察者结构的逐项实现；本轮不展开其确认、故障恢复和一致性工程 |
| R1（辅助） | [RabbitMQ：Publish/Subscribe](https://www.rabbitmq.com/tutorials/tutorial-three-python)；上一轮已读全文，本轮仅核对保存的拓扑说明 | 同一事件可路由到各业务订阅；应用图不能把两个业务画成竞争同一队列 | 教程临时队列、自动确认等配置不进入本片，也不借它作可靠性承诺 |

上述公开正文的UTF-8 SHA-256：

```text
M1 aea66f0646c714c5eded6ee1e1aa3cc329f4cab71003c2ea8ca76178878d6d57
M2 205f97029405f88777655b3e888c433f6357eb122151c57f6877d77490d1e1ff
R1 6d3490ac8fae6e6601d0339feba15eeccd83faee9232d9c719f6e72fa5fccec0
```

Microsoft取回元数据M1的`updated_at`为2026-06-02，M2为2026-06-03；`ms.date`并非同一字段，不混写发布日期。RabbitMQ为此前取回的动态正文，本轮不另断言产品版本。

## 原模式资料映射的继承范围

旧12镜调研记录还列有[Cornell CS2112的Observer教学节](https://courses.cs.cornell.edu/cs2112/2022fa/lectures/patterns/index.html)、[Microsoft观察者最佳实践](https://learn.microsoft.com/en-us/dotnet/standard/events/observer-design-pattern-best-practices)、[Refactoring.Guru Observer](https://refactoring.guru/design-patterns/observer)及[Node.js Events](https://nodejs.org/api/events.html)。这些链接保留为原研究路径，不伪记本轮新访问。

本轮事实主要用已保存且重新读过的M1核对，不需要把Node同步顺序、框架接口或某篇文章的特定约定搬入模式定义。动机与收益中的“接收方独立变化、把响应细节留给各方”是基于这一职责分工对自建案例的设计分析，不是市场占比或性能测试结论。

## 镜头与主张映射

| 镜头 | 主张或动作 | 依据与限制 |
|---|---|---|
| 01 | 商家改变示例订单状态，摘要与记录联动，提出通知问题 | 自建教学场景；不执行真实付款，不推断真实商家架构 |
| 02 | 接收方经常增减时，写死各方处理会牵动订单；按观察者关系分离变化与响应 | M1的来源/接收者分工及本例设计分析；不宣称所有直接调用都差或模式天然更快 |
| 03 | 来源、共同观察者约定、摘要与记录分别承担职责 | M1；共同约定是接口，不是消息中转服务，Java名不是模式定义 |
| 04 | 两方先登记，来源保存当前接收者；约定通知数据 | M1；明确回看付款前，不能把重置误作同单倒退或第二次付款 |
| 05 | 本例来源先更新，再通知；摘要自己显示，记录自己追加 | M1与`demo-java/ObserverDemo.java`已有实现；依次同步只是本例选择，不推为通用顺序保证 |
| 06–07 | 第一次处理结束后摘要退出，后续同单已发货只通知记录 | M1的订阅/退出关系及Java例子；退出不抹除过去，灰显摘要历史值不能冒充当前状态 |
| 08 | 共同约定不变时可调整接收关系，维护生命周期与间接路径有成本，固定简单关系可直接调用 | M1及本例设计分析；不称完全解耦或新增功能完全无需修改 |
| 09 | 实际常借助已有事件机制；跨服务可用MQ发布订阅，订阅方分别处理 | M1 alternatives、M2；只是相近思想的应用联系，无行业比例数字，不声称所有系统必须用MQ |
| 10 | 回到来源变化、通知当前订阅者、各自响应的核心 | 回收同一案例，不能以消息工程问题取代开头的模式问题 |

## 示例程序与行为证据

`demo-java/ObserverDemo.java`保留完整可运行实现，`demo-java/verify.py`为既有编译及行为核验入口。本轮不将旧运行结果预记为再次执行，实际制作会在新报告中记录运行范围。来源维护状态与名单；摘要保存最后接收状态，变化记录保存已收到事实；程序中同一订单先已付款、再已发货，摘要在两次之间取消。

该程序的同步调用、通知开始时名单快照、相同状态不发、错误传播与重入保护等属于实现选择。本片只展开主线，不把这些细节全部塞入视频；完整源码供需要的人复查。片尾5秒静默Java关键节选只连接角色与实现，不是完整程序或跨服务客户端。

## 范围与验证边界

视频与文章主线均为观察者模式；文章在唯一简短实战段之前的模式正文约1967中文字，应用段约122字，模式内容占这两部分约94%，不是MQ教程。视频仅09一镜联系应用，不讲ACK、离线积压、重投、幂等或Outbox；历史七页证据不成为重新加入这些支线的理由。

脚本、音轨、声学起音、动态表达、封面、正式媒体与线上检查须按本轮实际输出重新记录。公开资料与程序运行分别支持事实和示例行为，不等于观众已经理解，也不预记用户已认可新版。
