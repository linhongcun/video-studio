# EP10 公开资料实读记录

访问日期：2026-10-24（北京时间）。实际通过搜索服务打开官方正文并定位相关章节；不是只看摘要。公开文档当前显示RabbitMQ 4.4，片中不要求观众使用该产品，教学机制限定如下。

| 编号 | 官方正文 | 支持本片的主张 | 本片保留的边界 |
|---|---|---|---|
| R1 | [Work Queues](https://www.rabbitmq.com/tutorials/tutorial-two-python)，Work Queues / Message acknowledgment / Message durability | 耗时工作可作为任务消息交后台处理；处理完成后确认；持久化需队列与消息配合 | 例子不是全局严格FIFO；可靠保存不等于业务已完成 |
| R2 | [Consumer Acknowledgements and Publisher Confirms](https://www.rabbitmq.com/docs/confirms)，Basics / Automatic Requeueing / When Will Published Messages Be Confirmed | 发布确认与处理确认属于不同通信方向；手动确认下连接关闭会重投未确认任务；持久消息进入持久队列的确认发生在保存后 | 发现断连需要时间；重投不代表新业务；路由失败和确认需共同处理 |
| R3 | [Reliability Guide](https://www.rabbitmq.com/docs/reliability)，Data Safety on Publisher/Consumer Side | 发送者、队列、消费者共同负责安全；不确定的确认可能造成重复，应让业务可安全重试 | 无恰好一次或永久不丢承诺；只有确认消息丢失与业务未做完要区分 |
| R4 | [Queue Length Limit](https://www.rabbitmq.com/docs/maxlength)，Overview / Overflow Behaviour | 积压有资源与策略边界；到达上限后的行为可配置 | 不能把队列当成无限缓存；某些策略会丢旧消息，某些拒绝新发布 |

片中教学设计：7042/7043/7044是无真实含义的业务编号；一次只处理一笔和三笔瞬时抵达仅用于看清状态，不是性能测试。画面中的移动时间经过放慢，不代表官方时延。

本轮相对旧片的内容修正：不再用“有队列就不会丢单”作绝对承诺。开头改问提交与完成的区别，把可靠保存、消费完成、确认丢失三个阶段分开。消费侧的记录仅表示队列维护的未确认状态，不是一笔新订单。


## flow-map-20261024 / #199：导航关系正文复核

实际阅读日期：2026-10-24。复用root取回的RabbitMQ官方仓库正文，原始URL为 https://raw.githubusercontent.com/rabbitmq/rabbitmq-website/main/docs/confirms.md ，本地只读材料 `/workspace/.video-studio-flow-audit/authorities/rabbitmq-confirms.md`，31,197字节，SHA-256 `861abccf819fddcdaddd661255914d867d6ed511a9ff19311bfef73d0907b127`；检索元数据在同目录retrieval.json。此处记录实际阅读正文，不把代理摘要当作出处。

- 正文The Basics / Are Publisher Confirms Related to Consumer Delivery Acknowledgements（42–88行）明确两者互不知晓：发布确认只覆盖发送者和broker，消费确认只覆盖broker和消费者。因此地图保存回执必须标接收方网站；处理成功后的确认必须标接收方队列，不能将入队回执接到业务完成。
- Consumer Acknowledgement Modes（123–172行）区分自动与手动，手动正面确认才告知队列可把本次投递标为已处理。片中仅保留现有手动确认示例，不宣称所有模式都在业务完成后等待。
- Automatic Requeueing（520–535行）说明未确认投递在原channel/connection关闭后重新入队，发现不可用客户端需要时间，消费者必须准备处理重投并考虑幂等。因此回路条件是手动确认下断连被发现且仍未确认，不用普通超时直接触发无条件重投；回路不能推断业务必定未完成。
- When Will Published Messages Be Confirmed（603–618行）对可路由的持久消息与持久队列，确认要等可靠保存；无法路由也可能收到confirm，所以本例画明任务已写入目标队列，不将任意confirm视为业务成功。持久化/路由和程序可靠性边界保留原文章，不扩展成其他消息方案。

导航仅把原片已经分别讲过的两类回执、未完成中断、业务成功但确认未达两个情景放回同一生命周期。第10镜仍止于复用已有结果，队列未收到处理确认；从复用到队列结束的虚线是后续要求，不假装该事件已经发生。

## 2026-10-26 片尾原题与原文核验

本轮实际GET RabbitMQ官方仓库固定commit `29cb9ecf131223ad9b7faf61921ac3683008f722` 的`docs/confirms.md`与`docs/reliability.md`，两份全文均200。原题分别为`Consumer Acknowledgements and Publisher Confirms`与`Reliability Guide`，来自frontmatter，未拼接小节或改写题名。[本片证据](../../docs/reference-endcards/batch-4/sources-message-queue.json)保存完整SHA、连续完整原句、原定位及逐论点段落。

核对重点为发布确认与消费确认互不替代、目标队列与持久配置下的保存条件、手动确认断连重入队，以及确认不确定造成的重复／幂等边界。无法路由也可能confirm，重投不能反推业务一定未完成，不作exactly-once承诺。旧Work Queues与Queue Length Limit脚注沿用原历史日期，不记作本轮重新读取。原article主体、frontmatter、锚点、旁白、分镜、旧冻结与媒体保持。
