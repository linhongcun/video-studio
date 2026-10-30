# Kafka发送确认：消息发出后，怎样才算发送成功？

MQ04 / EP44，保留原标题与URL。本轮新声新画面，不复用旧媒体或旧验收。开工主干923305b49cea1b18d7fc7e4dd8ac70ad830bc673，目录仅本revision。

唯一问题：send返回为何不是发送确认；成功、缺回应与重传时，哪些内部状态决定结果。详见outline.md与implementation-map.json；所有画面来自固定版本真实代码约束的教学模型，不冒充真实Broker/网络实验。

视觉：Kafka style-v1；调用方/F1、本地P0批次队列、Sender在途、Kafka日志和近期生产者状态，分层渐进展开。P1最多淡背景，不成为第二条示例。正常链先完整走通，09/14显式重置空日志，13是缺回应分支的后续新应用send，不重置原日志。保留本批E01与F1身份；箭头流动与结构状态同源。

设置：Kafka/Java4.4.0固定commit1156b2752aaa28eafc0b4c4d387e63356793268d，orders/P0，一记录一批、非事务；acks=all、enable.idempotence=true、max.in.flight=1、linger.ms=0；其余确认/重试配置沿本轮research固定。成功范围满足本例acks条件，不画副本轨道或承诺全部刷盘。实际调度可在send返回前完成，本片仅固定返回时仍待定的示例。Future/callback由同一次批次完成驱动，不画成两次确认或声称二者固定同时可见。

本批发送标记映射：A=producerId501、epoch0、sequence0..0；B=producerId902、epoch0、sequence0..0。首次出队发送时已分配本批标记（不是重试后新加）；10镜只是展开查看。先看“发送者当前身份 A·0 + 批序号0..0”保持不变，再按动作出现producerId/epoch/sequence小标签，口播不背字段定义。Broker只在本例近期状态仍保留时复用offset0；未命中仍需有效epoch/序号校验，不能直接else无条件append。

正文不展示源码长卡，最多可在11镜用两行明确“教学伪代码”的条件提示，非必要时只用结构与状态对照。完整调用链/异步回调顺序、幂等状态有限保留和其他失败边界留文章。正文后5秒无旁白原题/机构简表。

### 01 problem

旁白：网站把订单通知发给Kafka，发送调用返回了，就能显示成功吗？也可能消息已经写入，发送方最后却只等到超时。
画面：发送调用返回，就能显示成功吗？；按outline镜表和implementation-map对应条件逐步显示，完成态不得抢先。
出处：implementation-map.json对应镜号；原始来源见research.md。

### 02 overview

旁白：先跟着同一条事件，看记录怎样走到Kafka，结果又怎样回来。本地缓冲、后台发送和Kafka日志，分别记着不同的状态。
画面：沿一条事件看内部接力；按outline镜表和implementation-map对应条件逐步显示，完成态不得抢先。
出处：implementation-map.json对应镜号；原始来源见research.md。

### 03 buffer

旁白：事件先编码、选好分区，加入这个分区的批次队列。同一分区可合成一批发送，这里只跟踪零号分区的一条事件。
画面：记录先进入分区批次队列；按outline镜表和implementation-map对应条件逐步显示，完成态不得抢先。
出处：implementation-map.json对应镜号；原始来源见research.md。

### 04 future

旁白：调用交回一个等待这次结果的对象，叫作Future。它连着这批记录的完成结果；此刻记录还在本地，结果仍然待定。
画面：结果对象，连着原来的这批记录；按outline镜表和implementation-map对应条件逐步显示，完成态不得抢先。
出处：implementation-map.json对应镜号；原始来源见research.md。

### 05 inflight

旁白：后台取出满足发送条件的批次，记入在途集合后发出。在途集合记着哪些批次还在等响应，原来的结果对象继续等。
画面：后台取出批次，登记在途，再发请求；按outline镜表和implementation-map对应条件逐步显示，完成态不得抢先。
出处：implementation-map.json对应镜号；原始来源见research.md。

### 06 append

旁白：Kafka校验这批记录后，把事件追加在位置零。还会保存这批发送的身份、序号和原位置，后面识别重传要用它们。
画面：先追加记录，再保存本批发送状态；按outline镜表和implementation-map对应条件逐步显示，完成态不得抢先。
出处：implementation-map.json对应镜号；原始来源见research.md。

### 07 confirm

旁白：成功响应回来，后台按分区找到刚才那一批，填入返回的位置。同一次完成通知回调，也让原来的结果对象结束等待，给出成功结果。
画面：成功回应完成原来的结果对象；按outline镜表和implementation-map对应条件逐步显示，完成态不得抢先。
出处：implementation-map.json对应镜号；原始来源见research.md。

### 08 business

旁白：这才是本例的发送成功证据，能定位到零号分区、位置零。下游通知还没处理，写入确认不会替业务宣告完成。
画面：发送成功，仍不等于业务完成；按outline镜表和implementation-map对应条件逐步显示，完成态不得抢先。
出处：implementation-map.json对应镜号；原始来源见research.md。

### 09 missing-response

旁白：现在回到空日志，重新对照同一条事件。这次记录已经追加，但成功响应没有回来，发送方仍在等结果。
画面：共同起点重置：已追加，却缺少回应；按outline镜表和implementation-map对应条件逐步显示，完成态不得抢先。
出处：implementation-map.json对应镜号；原始来源见research.md。

### 10 same-batch

旁白：遇到可重试失败，后台重传原批次，保留这批发送的标记。重传时仍带着同一个发送者身份，以及原来的批次序号。
画面：重传原批，发送标记保持不变；按outline镜表和implementation-map对应条件逐步显示，完成态不得抢先。
出处：implementation-map.json对应镜号；原始来源见research.md。

### 11 broker-dedup

旁白：Kafka找到这个发送者的已存状态，核对身份和完整批序号，认出还是刚才那一批。于是返回原位置零，跳过追加；业务事件编号并不参与这个判断。
画面：Broker认出旧批，复用原位置；按outline镜表和implementation-map对应条件逐步显示，完成态不得抢先。
出处：implementation-map.json对应镜号；原始来源见research.md。

### 12 timeout

旁白：可本例的成功响应一直没被处理，总发送期限终于到达。结果对象和回调都报告失败，已经写下的事件却不会因此消失。
画面：总期限到达，结果失败但记录仍在；按outline镜表和implementation-map对应条件逐步显示，完成态不得抢先。
出处：implementation-map.json对应镜号；原始来源见research.md。

### 13 new-session

旁白：如果应用关闭旧生产者，再用新会话重发同一事件，发送者身份就换了。这是新的发送，通过校验后可追加到位置一，不是原批次的自动重试。
画面：新会话重发，已是新的发送；按outline镜表和implementation-map对应条件逐步显示，完成态不得抢先。
出处：implementation-map.json对应镜号；原始来源见research.md。

### 14 local-failure

旁白：再回到空日志，看一个确定未发出的短对照。本地编码直接失败，事件还没进批次缓冲，也没有先返回等待对象。
画面：一眼对照：入缓冲前就编码失败；按outline镜表和implementation-map对应条件逐步显示，完成态不得抢先。
出处：implementation-map.json对应镜号；原始来源见research.md。

### 15 recap

旁白：调用返回，不代表已经发送成功；收到成功结果，才有本次发送的证据。无成功回应可能仍已写入；同批重传认发送身份和序号，不认业务编号。
画面：调用返回、发送证据、业务完成，各看哪一步；按outline镜表和implementation-map对应条件逐步显示，完成态不得抢先。
出处：implementation-map.json对应镜号；原始来源见research.md。

