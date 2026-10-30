# Kafka发送确认：消息发出后，怎样才算发送成功？

唯一问题：send调用返回、发送成功结果与最终超时，各能证明什么，哪些结果仍然未知。

身份：EP.44 / Kafka MQ04 · 发送确认。主线沿订单7042的通知事件E01；固定orders主题P0，所有分支初始日志为空，下游通知待处理。正常、未知、序列化失败三个分支先总览再聚焦，切换必须明确重置；未知分支内部的应用重新send是同分支继续，不重置日志。

画面沿不可变Kafka style-v1。发送方观察、Kafka日志实际内容、下游业务三列固定，事件E01与订单7042始终对应；本例日志追加时显示记录从无到有，回应沿独立回路回到发送方。原记录不被响应或读取移走。先让观众看到查询结果的对象，再标Future；不把send保证为立即返回或保证返回时总为pending，本片仅选择返回时仍pending的正常调度。

固定Apache Kafka/Java客户端4.4.0；acks=all，enable.idempotence=true，retries=2147483647，max.in.flight.requests.per.connection=1，request.timeout.ms=45000，delivery.timeout.ms=120000，linger.ms=0，max.block.ms=60000；一条记录独占本批次，元数据已可用。Topic一个分区、RF3/minISR2/currentISR3，非事务，固定前提满足，不在本片展开副本机制。waiting动画非真实时长，省略等待须明示。

未知分支不是Future.get短等待超时：记录已追加且满足本例acks条件，但该批次及其内部自动重试的全部成功响应在总期限前均未被处理；请求失败先触发可重试，最终delivery到期以Kafka TimeoutException完成失败，Future.get对应ExecutionException(cause)。最终失败不会被迟到成功响应改写。关闭旧producer A，应用新producer B再次send同一eventId，为新的应用发送，允许追加offset1；不把producer幂等说成失效，不把eventId当producer去重序列。

本地失败分支选择自定义序列化器在send内同步抛SerializationException，先于accumulator.append，因此该记录未入待发送缓冲，未发送该Produce；不说没有任何元数据网络请求。它没有先返回Future，不显示pending或callback；只是这一确定本地错误可判本条未发送，不把所有异常统一为确定失败。

正文后无旁白5秒原题/机构资料列表。文章Figure按实际storyboard时序由root补完再冻结。全部为官方主张约束的有限教学模型，非Broker/网络故障注入实测，不展示伪造终端输出。

### 01 problem

旁白：网站的发送调用已经返回，就能显示发送成功吗？有时Kafka已经记下来了，发送方却只等到超时。
画面：订单7042通知发送检查功能，状态“待确认”，业务“通知待处理”；提出冲突，禁止先泄露某个分支为真实结局。
出处：R1/R2及research.md。

### 02 overview

旁白：先分清发送方、Kafka日志和下游业务。这次分别看发送成功、结果未知、确定未发送，判断每种结果能证明什么。
画面：三列机制稀疏总览，三路径normal/unknown/serialization；分支不是同一次发送连续经历的三个结局。
出处：R1/R2及research.md。

### 03 send

旁白：先调用发送，返回一个以后查询结果的对象。在这个示例里，记录暂存本地，后台还没发完。
画面：正常分支；E01在本地缓冲，send返回Future（结果对象）、pending，本例调度下日志空。
出处：R1及KafkaProducer.java927–951。

### 04 confirmed

旁白：后台把记录写进零号分区，并收到本例要求的成功响应。这个结果对象显示成功，带回分区零、位置零，给出这次发送的证据。
画面：先追加E01@P0/0，再回传成功，Future成功RecordMetadata；不让成功标签先于回传抵达。
出处：R1/R2及ProducerConfig.java133–150。

### 05 business

旁白：可下游通知还没处理，订单业务并没有因此完成。发送确认，只回答了这次写入结果，不替下游确认业务成功。
画面：正常结果回全局，发送方已确认，日志E01保留，下游仍待处理，明确三列边界。
出处：R1/R2及research.md。

### 06 unknown

旁白：回到相同的初始状态，再发送这条事件。这次记录已经写入，但成功响应一直没有被发送方收到。
画面：明确reset至空日志，聚焦unknown；E01再追加@0，屏蔽成功响应；“实际已写入”在日志观察栏，“仍待结果”在发送方栏。
出处：R1及ProducerBatch.java263–273。

### 07 auto-retry

旁白：客户端遇到可重试的失败，会在期限内自动重试。本例开启生产幂等，同一批次的重试，没有追加第二条记录。
画面：自动retry保留producer/session A和batch序列身份，读回同一offset0，没有新增日志记录。时间轴明示“省略等待，非实时时长”。
出处：R1/R2及ProducerConfig.java307–318。

### 08 timeout

旁白：总发送期限到达，结果对象最终失败，回调报告超时。发送方没有成功证据，不能据此断定日志里没有记录。
画面：delivery timeout最终Kafka TimeoutException；后台将同一最终结果传给Future与应用回调（两种观察方式，非两次确认）；Future failed、sender结果未知、日志实际E01@0同时可见，后续不将原Future改成功。
出处：R1及Sender.java185–216/362–375、ProducerBatch.java263–303。

### 09 app-resend

旁白：若应用重启后，把同一事件重新调用发送，这是一笔新的发送。这次成功写到位置一，虽然事件编号与原来相同。
画面：先关闭A，B新producer/session再次send E01，追加@1并成功；自动retry与应用重新send视觉身份分开；原E01@0仍在。
出处：R1及KafkaProducer.java177–182。

### 10 local-error

旁白：再回到初始状态，换成发送前就无法编码的内容。本地序列化直接报错，这条记录没进待发送缓冲，日志仍然为空。
画面：明确reset空日志，序列化器同步抛SerializationException，send未返回Future，无Produce箭头；只断言本条记录没发送。
出处：R1及KafkaProducer.java1080–1111。

### 11 recap

旁白：所以，要分清调用返回、发送确认和业务完成。超时可能结果未知；确定的本地编码失败，才是本例明确没发出去的对照。
画面：回稀疏三路径结果，成功证据/超时未知/本地未发各一简短标签；下游业务仍为独立边界，片尾资料。
出处：R1/R2及research.md。
