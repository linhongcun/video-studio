# MQ01 从 RabbitMQ 改为 Kafka：独立预审边界

日期：2026-10-28（北京时间）。审查基线：d7a5d7682080232617a03cc988b7c25cb50446f4。只读当前消息队列发布身份、现行mq-intro脚本/封面/参考资料和共享制作流程；本记录没有声称已读新的Kafka文稿、已核对Kafka权威原文、或运行真实Broker。后续技术审稿仍需实际Kafka原文与新片输入。

## 当前身份及保留范围

当前发布为message-queue / EP.10 / episodePart「MQ入门」，sourcePath指向episodes-codex/message-queue/revisions/mq-intro/message-queue/remotion。现行片123.333秒，12镜24句，最后5秒参考资料。旧根和mq-intro的2份冻结清单合计277条，当前完整匹配；这两套历史工程与回执需保留。新Kafka版本单建revision，不重写旧source-sha256，也不重新生成旧附录去追认新视频。

2026-10-28用户将本轮扩大为现有MQ01同步Kafka重制。原preservation-baseline.json保留原封面阶段身份，不能删条目令旧基线重新通过。后续另建范围清单，把已授权替换的发布video/article/meta/字幕/来源/封面逐项记录前后SHA与验收，新revision单独冻结；旧工程、其他系列和新puzzles cover-continuity仍继续全量保护。

## 不可直接复用的RabbitMQ机制

1. **取走、出队、消息消失。**Kafka消费是读取分区日志记录；消费或提交位置不会让该记录从日志立即消失。入门里的「消费者暂停，尚未取走7042」须改为尚未读取/处理，而不是仍可被取走的一条ready消息。动画不得把读取画成搬空唯一日志记录。
2. **ready / unacked / 手动ACK。**Kafka不采用本片RabbitMQ逐消息投递确认与ACK后释放消息的模型。07/08镜「投递待确认→ACK→队列结束投递/移除7042」不能只替换标识；旧07-ack句take及图形需重写。若新片带消费位点，明确这是某消费组在该分区的恢复进度，通常提交的是下一条要读的offset；提交不证明业务对外完成，也不触发日志删除。
3. **发布确认。**RabbitMQ publisher confirms不可直接沿用为Kafka协议名或成功条件。Kafka producer send异步回调/future完成与具体acks配置关联；若说acks=all，指当前ISR而非所有指定副本，且不能说每次调用立刻fsync落盘。入门可固定正常成功路径并把多副本/故障细节留后续，但要明确仅说明本例的Kafka写入回执，不能许诺绝不丢。
4. **durable/persistent/quorum queue、exclusive、auto-delete。**这些原RabbitMQ队列条件不是Kafka参数。Kafka留存受topic日志保留/清理策略及配置影响；消息未处理时仍可能过期，不能说消费者不读就永远保存。新视频只需简短说明本例在保留期内，不把全部生产配置塞进正文。
5. **排空。**短时高峰之后可排空的是相对于某消费进度的未处理积压，不是删除Kafka日志。动画可让待处理标记减少、已处理记录保留/淡化。持续入2/完成1的例子可重用计数思想，必须明示是教学示例和同一统计口径，不是Kafka吞吐测量。
6. **页面完成链路。**仍应保持业务结果保存与页面经网站服务查询结果的链路。Kafka生产成功、consumer poll返回、位点提交都不能直接将网页标「业务已完成」；ack或offset线不能直连页面。
7. **顺序和消费归属。**入门可限定同一topic的一个分区与一个消费者（必要时注明同一消费组），避免先讲分配协议。若画多分区，不应把topic画成一个全局FIFO；顺序边界为分区内，不保证多分区总体按到达时间处理。多消费组各自进度也不应画成一份共享完成标记。
8. **至少一次/恰好一次。**位点在业务成功后提交仍有业务成功而提交失败导致重读窗口；本入门若不讲故障无需展开，但不能给出「保证只处理一次」「自动幂等」或「提交位点与业务结果自动原子」的保证。Kafka事务也不能自动覆盖任意外部数据库副作用。

## 可保留的教学主线

订单7042已受理但后台尚未完成这一问题仍成立。功能页面→网站服务/生产者→Kafka日志→后台消费者→业务结果查询可以继续贯穿同一任务；固定正常提交、暂停读取、恢复处理、结果保存与页面获知的不同落点。消息队列的异步解耦、短时缓冲、持续净流入积压及有限等待代价都能保留，但图形和用词须以Kafka日志/进度模型重新表达。

## 共享流程要求

- 旧mq-intro已冻结；新revision的script/article/pronunciation、plan/scene与所有Kafka资料重新审读，不能将原R1/R2/R3的RabbitMQ证据原封不动变成Kafka依据。
- references.json按title-author规范记录实际原题/机构、titleEvidence与本轮原文证据，正文SourceQuote与Figure同源；正式编码前运行当前check-references --sources。
- 可复用现有语言中立的take，逐条核对原文件与新句相同再记录SHA和reuse来源；涉及取走/ACK/消息删除的旧句不可静默复用。重新装配真实句时与起音，不改旧takes或旧words/storyboard。
- 配音整轨复用episodes/_shared/voice/及当前句级装配入口，voice.wav复制为实体public音轨，words/storyboard timing绑定新整轨SHA；共享onset/place检查必须通过。
- 新输入冻结包含全部源码、音轨/选take、脚本/文章、Kafka引用证据及默认参考附录入口。前后核对同一份冻结，不将生成视频或附录回执伪装成编码前输入。
- 默认npm run render必须走render_with_references：先资料/冻结预检，再正文/混音，再默认5秒简表附录。最终发布video.mp4应含实际附录，不能用out/body.mp4。
- 先看无字幕真实动作中间态和跨镜接续，尤其日志被读取但仍保留、消费位置推进与网页获知分离；再看实际编码关键帧、音轨边界及全部参考页。未做的ASR/听辨/真实Kafka实验不得声称完成。
- 站点换片保留slug/EP、createdAt/publishedAt/firstRelease；updatedAt按实际新版实质修改时间，sourcePath指向新revision。刷新finalVideoFrames/referenceAppendix为新render-result回执；核对文章章节、VTT、Figure时点和截图，完整构建及双视口播放器/来源浮层/回看检查。

本记录用于提前排除RabbitMQ换标错误；它不等同新Kafka脚本技术审查已经通过。
