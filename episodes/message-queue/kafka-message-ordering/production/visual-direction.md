# MQ06 视觉执行方向

共享不可变Kafka style-v1暖炭灰/橙/冰蓝，事件E01以冰蓝关联支付、E02以橙关联退款；具体页面状态PAID冰蓝、REFUNDED绿。全部ID前景色保持高对比，边框色不兼任低对比文字。Kafka原标记沿共享middleware-identity，不改原资产。

顶栏常驻输入先后/写入日志/交付记录/业务完成导航，底部927起字幕带。工作区域342–820。先展示同一订单页面与两条已发生事件，再进入具体结构；不套浏览器壳。

04先让相同7042落成同字节，05再用相同输入算hash取余，结果0出来后才说都到P0。06按分区批次队列尾进头出，真实模型有queued/inflight/appended阶段，原日志从空变E01@0再E02@1。07日志不搬走，移动副本/纯点在两容器间，内部列表依次append后才交给应用。只展示需要解释的字段，不逐个巡览类名。

08之后日志固定左侧，右侧订单页面投影和两个处理任务。实际写入顺序单独一行，不能用日志顺序推定完成。09/12显式同日志/同页面起点reset，受控并发中E01在写入前等，E02写完，之后放开E01覆盖；串行对照只在上一条真正写完后放行下一条。所有完成态标题/脚注绑定对应模型完成条件，不在移动中抢先。

13只画多生产者的条件示意，不擅自选择一个未定义的竞态结果。14标记正确对照，回收三段E01/E02链与已退款结果，末镜原创标记留宽。

Main DOM数据：data-model-state、data-log-records、data-buffer、data-returned、data-position、data-scan-offset、data-projection、data-app-mode、data-dispatch-order、data-completion-order、data-route；文本data-text/data-copyfit，原日志data-log-record/data-offset，移动纯点data-moving-dot。支持showSubtitles=false/hideSubtitles=true。

真实时序尚未形成时只做框架类型检查，不用大量placeholder图伪装动态预检。root真实voice/board后再看相邻完成态、运动中点、首2/5/15秒与4Figure，并保留任何真实失败和定向纠正。
