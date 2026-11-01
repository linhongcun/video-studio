# EP.49 kafka-replica-acks-v1：把物理复制与已知进度拆开

依据：storyboard.json 0e8c7f7feb673a3c41d1906a2dc0c3a4f2f546a6a03b5b61ee631614ce7834f3；covers.json 29274a41456029c423ba51823923b31a981c61b998c85a29b33a7ce49a27e948。实际最终接受声音时序，5460帧/182秒、13镜。script 619e9a37ac6560c56c36e5d331b4ee45d45851bbed19c5c27aa48d14ad20b147；voice 388aa7072e3329d76360aca4063c20b901d642bdad256307869a40200286b9d9；words d0471c0219cadae423638aadda0396c07bd4ca32a2fb8dbc5f5c6144c6a9b555；cues 37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570；shot_frames 73fca0e2f2ac34c3de29dd94ccda49af7e37bd5b57e312608594d32df408e0d1。原PREVOICE原稿/40张自采与失败记录均保留，不替代真实时序复核。画布1920×1080/30fps。

## 相对上一冻结

无。本期fresh工程，没有旧冻结输入；未复制旧音频、回执、QA或历史输出。不改旧片或共享style。正式编码尚未执行。

## 相对上一期的变化

三份数据副本的日志固定空间，新增独立物理下一位置/Leader已知位置、稳定ISR准入与共同进度计算。只有canvas机制图，不开浏览器、DevTools、无关应用壳；无strike。全局导航四段；页外发送回执点沿x=72通道。实际段长来自最终声轨，无手填延时或文字旁白改写。

## 画面类型与真实段长

| 镜 | id | frame | 实际绝对帧 | 真实帧数 |
|---|---|---|---|---|
| 01 | problem | canvas | 0–296 | 297 |
| 02 | replicas | canvas | 297–770 | 474 |
| 03 | leader-ack | canvas | 771–1125 | 355 |
| 04 | leader-loss | canvas | 1126–1640 | 515 |
| 05 | all-reset | canvas | 1641–2042 | 402 |
| 06 | admission | canvas | 2043–2442 | 400 |
| 07 | copy-second | canvas | 2443–2846 | 404 |
| 08 | report-second | canvas | 2847–3300 | 454 |
| 09 | copy-third | canvas | 3301–3751 | 451 |
| 10 | all-survives | canvas | 3752–4113 | 362 |
| 11 | two-isr | canvas | 4114–4553 | 440 |
| 12 | one-isr | canvas | 4554–4983 | 430 |
| 13 | recap | canvas | 4984–5459 | 476 |

## 主要空间与叠字

Header标题[100,126,1720,60] fs44；条件条[100,204,1720,32] fs23；网站结果区[100,272,1720,90]。三日志[100/710/1320,430,500,350]；原记录槽各[x+24,534,450,74]，E01为前景色；物理下一位置各[x+24,632,450,36] fs26，主已知位置[x+24,710,450,34] fs25。共同进度栏[100,807,1720,86]，抽象脚注[100,849,1720,38]。字幕[110,929,1700,108] fs37，最多两行正常阅读；无字幕模式同时覆盖selectComposition与resolved props。

## 计数与同步

全部计数从model.json对应快照读取，不能独立插值成另一事实：本地追加当帧才物理nextOffset0→1；下一Fetch报告抵达当帧才Leader已知0→1；HW1才有本条完成条件；网站成功在响应抵达后。模型39态/505有限断言不是Broker测量，真实7分支运行另有原始配置与日志。stateAt及sceneTiming是动画/门禁同源时点入口。

## 封面

root独占本期封面及真实covers.json；本文件仅绑定上列当前SHA，不复制或改写封面。三比例6图及独立审图由root统一，实际安全区看covers/cover-style回执。本期正文不导入会增长的共享catalog。

## 方框、讨论题与下期

主要方框是参与复制的日志和网站结果容器；不是把旁白切成大字卡。无下期预告。discussionQuestion：最小同步副本数为二，为什么同步名单仍有三份时不能只等两份？

## 参考资料附录

采用现行presentation:title-author（模板旧original-title-quote说明不沿用）。R1 Partition.scala，R2 ReplicaManager.scala，R3 ReplicaFetcherThread.scala，R4 DelayedProduce.java，R5 PartitionChangeBuilder.java；无公开个人作者，机构Apache Kafka。5项、每页最多4项、默认5秒，预期两页；原文/定位/版本/链接只在完整来源与文章，不上视频列表。默认render.py进入本期薄包装及同色共享references引擎，输出video.mp4含正文与附录。正文5460帧，5来源资料按默认两页共300帧，预计含附录5760帧；最终媒体/退场/播放器真实结果仍须正式编码后核实，不用prevoice或正文预演代替。


4幅文章图位：1621／3281／3732／4964；详见article-figure-plan.json，均按原整数帧除30回看，正式编码后逐张实际抽图验收。
