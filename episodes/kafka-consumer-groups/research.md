# MQ02 · 归属表怎样决定分工

研究日期2026-10-30（北京时间）。本轮实际访问官方固定Kafka4.4.0源码提交`1156b2752aaa28eafc0b4c4d387e63356793268d`，直接读取执行方法、判断与状态更新；API/注释只用于交叉核对。原始文件与下载SHA见`sources/download-manifest.json`，具体调用/分镜映射见`source-execution-map.md`。没有把旧MQ02研究的verified、旧媒体或旧模型继承为本轮结果。

本片只回答分区归属表如何计算、安装并约束正常客户端请求。经典协议、显式Range、一个主题、相同订阅、无静态成员/无机架偏好固定。成员显示N1/N2/N3，实际算法输入member-01/02/03；选本轮leader为N1不表示按排序选leader。两个分区P0/P1各保存两条示例事件，两个独立组从保留起点0读取，读取不消费掉原记录。

## 实现事实

1. 经典组的协调者按group.id保存/选择本组成员，成功JoinGroup给组内leader完整订阅信息；负责计算的是该消费者客户端里的assignor。
2. Range的输入逐主题组织。分区先按编号排序、无静态ID的成员按member.id字典序；每名成员先有空列表。整数商为基础数量，余数使前几名各多一个。候选分区被移出unassigned，确保本次组内表不将一个分区分给两名。
3. 两分区三成员：基础0、余2；前两位依次拿P0/P1，候选为空，第三人仍空。第二个组只有S1时，重新计算得到两区。多topic时Range按每个topic算，不保证所有topic合起来全局最均衡。
4. 经典leader把表经SyncGroup交给协调者，成功后协调者在各成员响应里返回其列表。消费者反序列化、校验订阅，安装到SubscriptionState.assignment。
5. Fetch准备从assignment中枚举可读取分区，已有缓存/暂停/无有效位置等会继续过滤。正常客户端只将自己的可读取分区及offset加入Fetch请求；Broker回复请求，而非轮流向成员推送每条消息。此内部列表规则不是Broker层安全授权或业务恰好一次保证。

## 资料与原题

片尾只列实际源文件原名（R1 RangeAssignor.java、R2 ConsumerCoordinator.java、R3 AbstractFetch.java、R4 GroupMetadataManager.java），机构Apache Kafka。`*.metadata.json`保留官方GitHub Contents API实际返回的name/path/commit元信息，作为文件题名证据；机构依据官方apache/kafka仓库与本提交NOTICE头部，不从Git提交者推断个人作者。没有明确单一公开个人署名，故省略author字段。

完整公开链接及每条主张在references.json。补充依赖AbstractPartitionAssignor、AbstractCoordinator、SubscriptionState、Fetcher、ConsumerPartitionAssignor、ClassicGroup和design.md均实际下载，选定段落已读，不把整份长文件未读旁支写成全部阅读完成。源码代码原文保留，文章将引用原题与精确短行，中文解释与教学图分别标注。

## 最小真实运行与教学模型身份

本轮已用官方4.4.0分发依赖，直接编译本提交未经修改的RangeAssignor.java、AbstractPartitionAssignor.java与SubscriptionState.java，将新class置于classpath首位并核对实际加载位置。真实运行得到两分区/三名乱序输入成员的P0/P1/空，独立单人组取得两区，三分区对照则1/1/1。实际本地状态还验证了未就绪位置不可Fetch、seek0后按各自assignment可Fetch、暂停后为空。完整命令、JAR与源码SHA、实际类位置和输出在experiment/actual-execution.json及actual.stdout.txt，可用run_experiment.py复现。此为真实类的内存算法/状态执行，未启动Broker或JoinGroup/SyncGroup/Fetch网络端到端实验。

后续动画的有限状态模型用于可追踪画面与数值，不冒充Kafka源码执行。真实实验结果与模型交叉检查；协议/请求如何安装及形成的来源审查与算法真实运行分别声明。配音与渲染在独立审读实现主线后启动。
