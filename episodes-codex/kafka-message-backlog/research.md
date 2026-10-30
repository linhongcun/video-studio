# MQ07 · 分工怎样限制拉取，业务步骤怎样限制真正完成

本轮实际复读：2026-10-30（北京时间）。制作基线f01411f7e2a2d1cef480cd0f6b73d4c29d7169f3，分支codex/mq05-07-implementation-20261030；EP47、kafka-message-backlog、#315。只写本新目录，旧源/shared/mtime不改。遵循S023/L060：把结构、判断和更新沿同一事件兑现，不用来源数量或速率公式替代因果。

固定Apache Kafka/Java4.4.0 commit `1156b2752aaa28eafc0b4c4d387e63356793268d`。所有源码来自本轮真实固定commit完整GET，URL/时间/字节/SHA在sources/download-manifest.json；原题由官方GitHub Contents API的name/path核验，保存*.metadata.json。没有个人署名证据，因此片尾使用Apache Kafka机构，不推定提交者为作者。完整下载不意味着全文逐行阅读：以下是实际阅读过的相关执行上下文；无关机架匹配/其他消费协议分支未逐条审读，CompletedFetch.java仅下载备用，不作为本期独立实读结论。

## 固定前提

同一个notify组、同一个orders订阅、2分区；classic、显式RangeAssignor；无group.instance.id/client.rack，12动态成员。C01…C12只是本例member.id排序后的别名，不是client.id或到达顺序。旧两位在扩容后示例排序中为C07/C12，因此可以均失去原分区；不预测实际运行随机memberId会产生相同别名归属。

分配比较不运行通知任务。之后独立共同起点才开始E01及业务计数，避免把旧拥有者的未完业务随新表消失。业务追踪期间分配稳定、位置有效、未暂停、节点正常、无待交付缓存/故障/重试、无自定义消费拦截器。max.poll.records=1，enable.auto.commit=false。

应用明确选择每个分区内串行等待通知API成功，不另设并行工作池。Kafka分区单拥有者只约束分配，不自动证明应用只有两个线程。本文“只有两路通知处理”来自两份非空分配列表和这一应用选择共同作用，不泛化所有应用。

## 实读执行链与片内兑现

| 执行位置 | 实际结构/判断/更新 | 影片兑现与限制 |
|---|---|---|
| RangeAssignor.java:128–171 | 以topic的订阅成员形成状态，所有成员先建空列表；按剩余候选及maxAssignable截取，再assign | 不能把消息逐条平均推送十二人；先建空表再逐分区填表 |
| AbstractPartitionAssignor.java:80–94/150–160；RangeAssignor.java:239–250 | 先按分区编号排序元数据；无静态身份时比较memberId；Collections.sort；计算整数商与余数 | 示范member-id排序，2/12=0余2；不说老成员必保原分区 |
| RangeAssignor.java:216–218、280–289 | addAll写成员列表；额外名额用后递减；removeAll移除已分候选 | P0给第一位、P1给第二位，候选耗尽其余空；先动作再完成说明 |
| SubscriptionState.java:315–328、486–496、515–520、1251–1252 | 协调结果重建assignment集合；fetchable遍历assignment并查未暂停/未撤销/位置有效等 | 本地列表的所有者清楚；空列表不会产生分区候选，不声称进程完全无通信 |
| AbstractFetch.java:343–349、420–483 | 排除已缓冲分区，empty候选直接返回空请求映射；正常候选使用position.offset并builder.add | 从已安装列表到数据Fetch；不是按消费者总数凭空增加日志通道 |
| FetchCollector.java:152–185 | 只交付仍assigned/fetchable的记录；构造nextPosition并subscriptions.position | 客户端拿到E01时读取位置已推进，不能因此记业务完成 |
| ClassicKafkaConsumer.java:650–684 | poll收集Fetch，再return ConsumerRecords给调用者；本例不设置拦截器 | 图中先交还记录，再进入应用通知步骤 |
| KafkaConsumer.java:231–257 | Javadoc应用示例另调insertIntoDb，再手动提交 | 只作API示例交叉核对，不当客户端内部数据库实现 |

片尾及补充引用来源的永久源码链接及完整raw核验链接放在article.mdx资料段，reference中的quotation逐字连续匹配实际文件。正文短窗仅保留Range计算表达式与明确标注的应用伪代码；其他执行依据通过结构和动作兑现，完整链留本文与文章。

## 教学速率与逐事件模型

速率不是官方数字或实测benchmark。每个教学一秒窗口左边界新增事件，右边界每分区完成min(可用事件数,1)；动画播放秒数不当作模型时钟。

前5步，每步向P0/P1各写2条，共4进；应用每区最多1条成功，共最多2完。按E01…事件逐个追踪：五步20进、10完，P0/P1各5条未完成。日志不删除，未完成账=unread+inFlight，完成独立保存在completed；首次poll两个位置已前进，但完成仍为0。

对照只改流入为每步1条，P0/P1逐秒交替；两区初始各5条，按各自可用量计算，十步后清空。若都路由到P0则不是同一条件，P1排空后的空闲能力不能抵消P0积压，不能套总额净速率。模型另验清空后仅一条到达时实际完成1，绝不生成负积压。enable.auto.commit=false且模型刻意不提交，故业务完成后committed lag仍可大于零；不把该lag当所有业务未完成量。

model.py生成27份深拷贝快照、246有限断言（以实际model-verification.json为准），包括分区归属、已拉取与完成分离、逐区处理和边界。断言是教学模型检查，不冒充真实Kafka或受众理解实验；不以断言数量评判讲解深度。

## 真实运行的独立范围

本轮已实际复读[runtime07输出](../../docs/archive/2026-10/mq05-07-implementation/runtime/runs/mq07-20261030T153232.191596Z/probe.stdout.txt)及observations/assertion-summary，20项实际断言PASS，身份绑定见runtime-cross-evidence.json。第一段只观察classic Range两分区2→12动态成员的稳定分配，只有2份非空；本次新增added-03/added-04得到P0/P1，原A/B均为空。它们不是教学C07/C12的相同身份或排名。第二段是独立单成员classic组，安装P0/P1并实际poll E01/E02，受控latch等待时polled2/completed0、position各1/committed各0，释放后completed2再各提交1。这不是十二成员同一业务测试，不是通知API副作用或吞吐benchmark，不证明片中每秒4进/2完与十秒排空假设。

## 制作闸门

script.md为12镜24句，精确旁白与全文SHA见editorial-version.json，已获独立编辑及根批准；根统一生成并接受最终6058帧声轨，voice SHA f4f478dcedbd17e10df0f50ed6ae5f724726f5f5ef580f99db4d4fcca49c2803。root仍统一生产冻结/正式编码/发布。本期四图已按真实board定稿整数2250/3260/4320/5418、seconds=frame/30与MDX seekTo；作者实际PNG/短窗自审见qa-self-finaltiming，独立动态与正式MP4关键帧仍待验。新字体账本为docs/archive/2026-10/mq05-07-implementation/font-environment.json，后续冻结须实际覆盖共享style/adapter与字体账本。

补充执行定位：[AbstractPartitionAssignor分区排序与成员比较](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/AbstractPartitionAssignor.java#L80-L160)；[FetchCollector位置更新](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/FetchCollector.java#L152-L185)。
