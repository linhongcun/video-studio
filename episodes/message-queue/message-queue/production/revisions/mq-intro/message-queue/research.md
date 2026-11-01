# EP.10 / MQ01 入门改造：公开资料与原理核验

核验日期：2026-10-27（北京时间）。这是独立 `mq-intro` revision 的新研究记录，不替换父目录2026-10-24/26记录，不追认旧媒体完成了本轮检查。

## 当前入口与证据身份

开工基线为 `16689e572c594224bd779a9b4403964e049cc99c`。基线发布元数据 `episodes/message-queue/meta.json` 的 `sourcePath` 指向 `episodes-codex/message-queue/remotion`；本轮从现有素材建立新的revision，保留EP.10、slug、首发日期、原Release与历史输入的身份。

本轮实际读取官方网页正文及对应固定源，机构均为RabbitMQ，未见明确个人署名，不把Git提交作者当作文献作者。公开文档页面显示RabbitMQ 4.4；Python教程为现行Work Queues教程，正文未标产品版本号。来源日期是核验日，不是出版日。

官方仓库固定commit：`a284a068ab720672b40ceed40f3f151d9829fb70`（仓库提交时间 `2026-10-26T16:03:34Z`）。通过GitHub connector `fetch_file`读取三份完整UTF-8源，并核对保存字节生成的Git blob身份与返回blob SHA一致。实际标题、连续短引、行号、论点上下文与保存文件SHA见 [sources/evidence.json](sources/evidence.json)。这不是shell完整HTTP GET记录，不捏造HTTP状态码。三份原文保存在本revision的 `sources/` 目录供逐字复核。

## 主张与最低必要边界

| 新编号 | 官方文档原题 | 本片使用 | 片内和图文必须保留的前提 |
|---|---|---|---|
| R1 | RabbitMQ tutorial - Work Queues | 任务变成消息，由后台worker稍后执行；网页受理与后台完成是不同阶段 | 原教程的模拟工作与本片7042订单节奏都是教学示例，不是RabbitMQ性能数字；本片不复制多worker轮询分发支线 |
| R2 | Queues | 队列和消息持久性、队列生命周期、ready与未确认投递、TTL和长度边界 | 固定durable quorum queue、non-exclusive、non-auto-delete、persistent消息；暂停发生在7042尚未投递之前；未配置TTL/溢出行为不能概括成永远保留 |
| R3 | Consumer Acknowledgements and Publisher Confirms | Consumer ACK送给Broker，允许其结束本次投递；发布确认与消费确认方向分开 | 固定手动ACK且业务工作完成后才确认；自动确认是另一种语义。ACK不会自动更新网页，也不能充当业务数据库的独立证明 |

原始题名、机构、连续原句及原文定位完整列在 [references.md](references.md)；视频片尾只显示三条原题与机构，采用 `title-author`，不显示摘录、链接或核验说明。

## 本片正常接力的教学选择

1. 7042是无真实含义的示例业务编号。生产者发布的是处理任务，不把“消息已提交”画成全部订单工作已经完成。
2. 为讲清消费者不在线时为什么还可以等待，本例使用不绑定消费者连接生命周期的队列。暂停场景表现为消费者尚未订阅或投递被暂停、7042从未进入消费端；不能只暂停处理线程却忽略prefetch可能已把消息推到客户端。
3. 恢复后，7042从ready变成已投递未确认；消费者完成必要业务并保存业务结果，然后将手动ACK送回Broker，Broker才可释放本次投递。Ready计数减少与本次业务完成不能画成同一个时刻。
4. 网站服务查询保存的业务状态，再把页面改为已完成。这条查询路径是本片选择的应用设计，不是RabbitMQ协议自带的页面通知，也不是把ACK转送给网页。
5. 一段短时输入高峰结束后，若后台净处理速度为正，积压可以排空。持续输入长期超过处理能力时，待处理量增长。速率、持续时间、单笔处理顺序均为示意，不称作实测，不给容量建议。
6. 本片只完成正常路径和积压边界，不展开确认丢失、重投、去重、Exactly Once、多消费者分工或复制协议；保留一句失败情况需要额外处理即可，后续视频仅作为拓展。

## 保留条件：避免从临时订阅队列推出持久任务结论

`durable`说明队列重启恢复语义，`persistent`说明发布消息持久性；它们不等于“所有故障永不丢失”，发布确认和正确路由仍有独立前提。Quorum queue不得被画成与消费者连接同生共死的exclusive队列。

Queues的Queue Properties、Temporary Queues、Exclusive章节分别定义了属性；exclusive队列随声明它的连接关闭而删除，auto-delete又有最后消费者取消后的删除条件。因此不能把Publish/Subscribe教程里临时、自动命名、`exclusive=True`的日志订阅队列搬来支撑“消费者离线后订单任务仍在”。本片使用Work Queues的durable task_queue方向，教程只提供原理与配置线索，不表示本轮已运行Broker演示。

队列、消息的TTL与队列长度限制会影响保留；资源也有限。本片仅声明所选配置和正常存储条件下任务继续待处理，不承诺无限容量或永久保留。发布确认的深入配置与故障窗口移至后续选题；入门画面不要把任意confirm误标为业务成功。

## 原理依据与原创推导分工

- 异步任务、队列属性、消息状态与ACK语义是官方来源支持的事实。
- “已提交/处理中/已完成”页面文字、业务状态查询接口、订单编号、速率曲线、暂停/恢复动作与镜头节奏是本片的教学和应用设计。
- 积压守恒关系及净排空条件是按本例输入/完成口径得到的推导，不是假托官方压测。不得把已拉取数量当作完成数量。

## 沿用与冻结保护

旧父稿的 `references.json` 只收Confirms和Reliability Guide，两条R编号与旧research表格的R1—R4不是同一编号体系。本revision独立定义R1/R2/R3，不按编号直接继承旧SourceQuote。旧详讲确认丢失与幂等的来源仍保留为旧片历史，不在新入门中虚构已使用。

父目录旧 `references.json`、`research.md`、`article.mdx`、`freeze.py`、旧冻结清单、历史QA和已发布媒体未由本任务改写。本轮新的参考资料输入及证据应随revision新冻结；不能在旧冻结中把日期改成今天。本轮只完成资料事实与来源核验，未声明Broker运行、配音、成片、附录渲染或线上SHA检查通过。
