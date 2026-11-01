# MQ15 · 写入成功时，哪些副本已经跟上

固定Kafka/Java4.4.0，commit `1156b2752aaa28eafc0b4c4d387e63356793268d`。本次基线 `8769a592856fe2618e5daf3d84849bf4b052e22b`，新实体路径直接依赖`episodes/_shared`。作者只写本期production中的文稿/模型/src；root管声音/封面/正式闸门，publication代理管具名薄工具。禁止TTS/冻结/正式编码阶段仍有效。

核心问题：同一E01追加在哪，Leader何时获知每份进度，这个进度怎样决定确认。13镜是本期机制拆分结果，不复用上一片镜数或时长；预计约3–4分钟，最终按声音和动作停留定案。

| 镜 | 同一对象的动作与当前条件 | 实际执行源码对照 |
|---|---|---|
|01|网站发送订单7042的E01，提出“成功时三份是否都齐”的问题；未先标成功|ProducerConfig的acks契约用于定位问题，不代替后续实现|
|02|同一P0的B1主/B2/B3跟随日志，空日志下一位置均0；稀疏导航与本例条件|Partition维护leader/ISR、Replica本地与Leader已知进度；不摆无关机器|
|03|acks1：主日志写E01@0、末尾1；回复返回网站后才显示成功；两跟随日志仍空/HW0|Partition1219–1243，ReplicaManager878–917/1356–1366|
|04|选定“复制尚未追到”的合法调度，只停原主；有资格的存活ISR成员接管，但新主日志无E01；原主离线日志不凭空删除|PartitionChangeBuilder256–281/318–322；acks1不保证已复制|
|05|显式重置同样空日志，改acksall；原有稳定跟进名单3份，引入ISR，数量门槛2|Partition1230–1237；minISR不是只等够2份|
|06|3≥2先通过准入再主日志追加@0；等待目标requiredOffset=1|Partition1230–1243，ReplicaManager835–849|
|07|B2 Fetch(0)→主返回记录副本→B2同位置追加；主的原日志仍在，Leader已知B2进度暂仍0|ReplicaFetcherThread111–150；Partition1280–1321|
|08|B2下次Fetch(1)报告进度→Leader已知[1,1,0]；稳定3份中取共同进度0，引入HW；all仍pending|Replica.java69–101；Partition767–817/947–1035|
|09|B3 Fetch/追加/再报告1→Leader已知[1,1,1]→HW1→完成检查成功→响应回到网站|Partition1010–1040/968–979；DelayedProduce140–195|
|10|另一个明确单故障对照：从已经复制完整、进度收敛的all结果，只停主；存活ISR副本保留E01并clean接管。仅演数据保存/接管资格，不演KRaft投票|PartitionChangeBuilder256–281/318–322；接管初始化细节不冒充逐帧实录|
|11|显式空日志重置，稳定ISR2且第三份不满足额外catch-up候选：2≥2，当前两份追齐HW1后成功|Partition947–1040/1230–1243；第三份不在当前等待集合|
|12|再次空日志重置，稳定ISR1/min2：all在append调用前拒绝；本轮独立运行已确认该稳定ISR1分支为NotEnoughReplicas且物理LEO前后0（仅此case）|Partition1230–1240；不是所有失败都无追加|
|13|回收acks/ISR/HW关系；确认不等于所有盘fsync、也不等于通知业务完成；片尾原创|ProducerConfig/LogConfig与本期执行范围；afterappend/ISR过渡边界进文章|

## 明确取舍与边界

- `example-config.json`声明单producer、每分支单条E01、幂等关闭/retries0/inflight1、P0显式指定、RF3、minISR2、ELR feature0、unclean关闭。复制调度与故障是教学选择，不是默认时间、概率或benchmark。
- HW简化仅用于稳定ISR、无待加入副本，也无近期catch-up额外候选。本版4.4 `maybeIncrementLeaderHW`在under-minISR时直接返回；不画ISR1的acks1自动推进HW。
- 跟随日志真实写好与Leader获知进度是两个时点；Leader根据下一次Fetch里的末尾位置更新`Replica`状态。Follower不是给Producer各发一次回执。
- acks1故障分支与all完整复制分支各自从新空日志出发；不把旧branch的原记录移走或在后续分支复活。原主离线盘上的记录可仍在；本文关心新主可继续提供的日志，不声称所有物理字节都消失。
- minISR不足可以在本例追加前拒绝；追加后ISR变化可有`NOT_ENOUGH_REPLICAS_AFTER_APPEND`，其他超时也不能推断没有写入。该复杂路径留文章，避免冲淡正常共同进度的主因果。
- 源码事实、有限模型与deploy_diagnosis的实际三节点运行分别记录；7分支/34断言/33份官方解码快照已在独立运行回执中通过，原失败尝试保留。确切配置、局限、原字节映射见runtime-cross-evidence.json，不把教学中间状态当逐时点实测。不得把题名、class声明或方法名列表当作实现教学已经完成。
