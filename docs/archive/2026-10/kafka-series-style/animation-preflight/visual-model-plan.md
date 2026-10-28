# Kafka MQ01 动画与状态模型方案

基线：d7a5d768；仅设计方案，未改写旧工程，正式稿审查通过后才写新revision。

## 保留与重写

复用句级 storyboard/data 适配、Sequence/Audio、字幕条和声学窗口定义；Panel/Label/COPYFIT可按新风格重写。旧 RabbitMQ Queue、ready/unacked、处理ACK和移除记录动作不复用。主题统一读取不可变style-v1.json；背景复制为新revision公开实体，列入本轮冻结，避免未来目录扩展改变本集输入。

## 独立纯状态

以不可变 snapshot 表达 retainedLog、readPosition、committedOffset（初始null，尚未提交）、businessResults、pageKnownState。主例固定单topic/单分区/单消费者，offset0/1/2对应7042/43/44。

- append只增加日志，不改变read/commit/business/page；生产确认成功后网站可回复受理。
- read返回记录内容并推进内部readPosition；原retainedLog保持。画面按读取内容出现一份明确的后台工作副本，不复制可再次执行的业务。
- saveResult先产生业务结果；commit保存下一条恢复位点，不能删日志，不能改变页面状态。
- query读取业务结果，响应抵达页面后才改变pageKnownState。
- 主流程不发生保留清理。有限保留仅用文字边界解释，不编造逐条到秒删除。
- backlog是进入任务减业务完成，不是日志记录数。独立流量示例有显式重置，不继承7042的相反结果。

## 几何与连续动作

默认1920×1080。页头y48和标题y145；主视觉约y300–780；字幕y925起。网站服务左、Kafka分区日志中、后台消费者右；业务结果与Kafka消费进度分开。

日志用三个固定位置的记录格：offset0/7042、offset1/7043、offset2/7044，读前读后位置不变。追加从网站沿路径抵达指定格才提交日志状态；读取时强调原格，并让内容副本沿连续路径到消费者，原格始终可见。

业务处理条只表达本次任务工作进度。成功落点先保存业务结果；然后消费位点信号走向独立“消费进度”区域，首次提交1表示下次从1恢复，不画成删日志。页面查询走应用服务→业务结果路径，与Kafka提交路径空间分离。

缩回全局时保留同一对象角色与位置。短时任务全部完成后，单独显示未完成0、日志仍有3条；持续增长则先明确切换独立流量示例，再按完整时间窗输入2/完成1计算。

## 预检模型义务

纯函数逐阶段检查：日志只追加且主例永不因read/commit减少；读取不提前保存业务；commit不早于本例保存成功；page完成不早于查询响应；readPosition与committedOffset分别约束，poll不被延迟到业务完成后；每个完整流量窗entered−completed=unfinished。测试不能替代实际动态采样，须独立查看变形/飞行中段、所有状态落点及跨镜边界。

## 预计实际采样

每镜首/中/末之外，对append各记录到达、读取中段/到达、业务完成前/后、commit信号中段/到达、页面查询/响应、积压归零但日志仍在、情景重置和各完整计数窗分别采样。采样用实际Noto字体、真实无字幕props，并检查DOM文字和图形 bounds；最终编码再抽关键帧验证源图一致。
