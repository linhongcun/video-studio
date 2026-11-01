# EP.49 kafka-replica-acks-v1：把物理复制与已知进度拆开

依据：storyboard.prevoice.json 89c55c8712fab02c0a8efc168ee6f66dddb59885eefad647a2aebbaf00f4d1e3；covers.json 29274a41456029c423ba51823923b31a981c61b998c85a29b33a7ce49a27e948。PREVOICE估计时序，不是冻结分镜或实际声音。script e74248fa4cdccec594ffd3a36677498b92438eea78e43cf3ec8e92a4c9b1e42d；实际voice/words/cues/shot_frames：无作者测量（由root另行生成）。当前占位6566帧、13镜，所有下表绝对帧仅为估计；实际声音定案后重写该表。1920×1080/30fps。

## 相对上一冻结

无。本期fresh工程，没有旧冻结输入；未复制旧音频、回执、QA或历史输出。不改旧片或共享style。正式编码尚未执行。

## 相对上一期的变化

三份数据副本的日志固定空间，新增独立物理下一位置/Leader已知位置、稳定ISR准入与共同进度计算。只有canvas机制图，不开浏览器、DevTools、无关应用壳；无strike。全局导航四段；页外发送回执点沿x=72通道。prevoice段长非真实例外，实际durationExceptions待真实装配。

## 画面类型与估计段长

| 镜 | id | frame | PREVOICE绝对帧 | 估计帧数 |
|---|---|---|---|---|
| 01 | problem | canvas | 0–394 | 395 |
| 02 | replicas | canvas | 395–945 | 551 |
| 03 | leader-ack | canvas | 946–1367 | 422 |
| 04 | leader-loss | canvas | 1368–1986 | 619 |
| 05 | all-reset | canvas | 1987–2476 | 490 |
| 06 | admission | canvas | 2477–2986 | 510 |
| 07 | copy-second | canvas | 2987–3462 | 476 |
| 08 | report-second | canvas | 3463–4007 | 545 |
| 09 | copy-third | canvas | 4008–4531 | 524 |
| 10 | all-survives | canvas | 4532–4973 | 442 |
| 11 | two-isr | canvas | 4974–5511 | 538 |
| 12 | one-isr | canvas | 5512–6001 | 490 |
| 13 | recap | canvas | 6002–6565 | 564 |

## 主要空间与叠字

Header标题[100,126,1720,60] fs44；条件条[100,204,1720,32] fs23；网站结果区[100,272,1720,90]。三日志[100/710/1320,430,500,350]；原记录槽各[x+24,534,450,74]，E01为前景色；物理下一位置各[x+24,632,450,36] fs26，主已知位置[x+24,710,450,34] fs25。共同进度栏[100,807,1720,86]，抽象脚注[100,849,1720,38]。字幕[110,929,1700,108] fs37，最多两行正常阅读；无字幕模式同时覆盖selectComposition与resolved props。

## 计数与同步

全部计数从model.json对应快照读取，不能独立插值成另一事实：本地追加当帧才物理nextOffset0→1；下一Fetch报告抵达当帧才Leader已知0→1；HW1才有本条完成条件；网站成功在响应抵达后。模型39态/505有限断言不是Broker测量，真实7分支运行另有原始配置与日志。stateAt及sceneTiming是动画/门禁同源时点入口。

## 封面

root独占本期封面及真实covers.json；本文件仅绑定上列当前SHA，不复制或改写封面。三比例6图及独立审图由root统一，实际安全区看covers/cover-style回执。本期正文不导入会增长的共享catalog。

## 方框、讨论题与下期

主要方框是参与复制的日志和网站结果容器；不是把旁白切成大字卡。无下期预告。discussionQuestion：最小同步副本数为二，为什么同步名单仍有三份时不能只等两份？

## 参考资料附录

采用现行presentation:title-author（模板旧original-title-quote说明不沿用）。R1 Partition.scala，R2 ReplicaManager.scala，R3 ReplicaFetcherThread.scala，R4 DelayedProduce.java，R5 PartitionChangeBuilder.java；无公开个人作者，机构Apache Kafka。5项、每页最多4项、默认5秒，预期两页；原文/定位/版本/链接只在完整来源与文章，不上视频列表。默认render.py进入本期薄包装及同色共享references引擎，输出video.mp4含正文与附录。正式帧数/MP4SHA/资料退场/手机播放器实际结果均尚未产生，后续不能用prevoice自采代替。
