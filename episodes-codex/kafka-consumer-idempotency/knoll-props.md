# EP.45 kafka-consumer-idempotency：谁能为同一E01加分

依据：storyboard.json c79ef3670ebf23386855080144f32b46852a222ee8f5895d7ea05179c6750580；covers.json 0ea819efc6c58a35ac435efb4b8f111b676693c141fccbb1b3a4e650e466884c。尚未冻结，无冻结副本。
script fffe0eca9a3d4b377bee3d7b3c502fcd03be0af2cc31f023fc3a6ac7b7cab3d5 / voice 38b6b8e30f21b6ff572531603f8ab4b9cc1050c18c38a03d2fa85d5810bfcb39 / words d80335718a66b526f8080eba0a7a36adf19f221357c0a2ce077375c7cf303c19 / cues 无独立文件 / shot_frames 无独立文件；正文5497帧、14镜、1920×1080、30fps。状态挂点读取本镜实测voice.localStart/localEnd，准确表见`qa/state-timing.json`，不使用伪配音时序。

## 制作状态

本期首次制作，没有上一冻结版本。根统一接受的声音为01-problem-1 c、08-waiting-1 b、10-skip-and-progress-2 b，其余25句a；旧候选、失败assemble历史均保留。旁白canonical SHA 521b47d9fa0cacf069758fb9bab59856b9bef1738782c12a42ae98f078d1a7fe。不得因画面补查改动已接受声音或文字。

主问题是同一E01重来，谁取得本次加10分的资格。先展示两次提交间的退出空隙，再用查询对照、共同唯一键、等待后重检、同事务提交/回滚解释。E01/order7042/account17/+10始终相同；points是逻辑业务身份，进程名不进入键。T1/T2表示数据库尝试重叠，不宣称稳定Kafka分区有两个消费者拥有者。

与上一期相比，全部正文页型为新写的数据库因果canvas，不复用回执/生产者状态。Main只将model.json快照作为状态事实，实测board只驱动动作。正文不用源码截图、浏览器或全架构图。短写锁仅保护索引页检查到写入；当前事务等待不占该页锁。

## 画面类型

| 镜 | frame | 绝对帧（含端点） | 帧数 |
|---|---|---|---|
| 01 | canvas | 0–350 | 351 |
| 02 | canvas | 351–779 | 429 |
| 03 | canvas | 780–1142 | 363 |
| 04 | canvas | 1143–1488 | 346 |
| 05 | canvas | 1489–1802 | 314 |
| 06 | canvas | 1803–2123 | 321 |
| 07 | canvas | 2124–2495 | 372 |
| 08 | canvas | 2496–3025 | 530 |
| 09 | canvas | 3026–3392 | 367 |
| 10 | canvas | 3393–3778 | 386 |
| 11 | canvas | 3779–4151 | 373 |
| 12 | canvas | 4152–4589 | 438 |
| 13 | canvas | 4590–5026 | 437 |
| 14 | canvas | 5027–5496 | 470 |

全部canvas，无browser、页外网页角标、逐字输入或strike。示例页面/公共结果卡不表示外部系统UI实际录屏。`cueLog`、调研映射和说明文字只供审读；Main读取每镜id、from、durationInFrames、voice局部句界以及字幕字段。页身颜色来自共享不可变Kafka style-v1；坐标和字号以Main为准确实现。

## 状态与同步

左T1、右T2、中间公共已提交结果固定。每次尝试的未提交增量与公共积分分栏。只有提交时，公共积分和有效登记同帧更新。普通查询空结果、等待尚未返回、RETURNING空数组、RETURNING新行分别显示；只有本次成功返回新行，应用才执行加分。更新不恰好一行则整笔事务回滚，此防卫及外部副作用保留在文章。

08第一句明确标“回看刚才T1”，演示短页写锁，随后回当前T2等待；等待不延续短写锁。12完成脚注仅在t2-committed-after-abort出现，前面显示暂存/等待提交。05标题按实际公共积分是否20守卫，先显示待执行的顺序，再显示补登记太迟的结论。13明确重置0/登记空，再演示“先单独提交标记”造成漏加，和真实运行范围分开。

可审计DOM保留data-model-state、data-view-mode、公共值/未提交值、data-returning及移动体身份。无字幕模式showSubtitles:false/hideSubtitles:true真实支持。详尽状态阈值与源身份在`qa/state-timing.json`，源作者自查与范围在`qa/self-review.json`；预演不是全片人工听辨或教学效果研究。

## 封面与图文

封面由根从本批独立共享入口制作并安装；本目录`covers.json`和`cover-style.json`记录真实依赖，渲染实际读封面配置，不重新复制旧图覆盖。源作者不改封面/发布目录。

article-figure-plan.json固定4个准确整数帧：563、3001、3368、4565，seconds=frame/30；MDX的seekTo同步。源预演已实际看图，最终article/*.jpg仍待正式成片抽图核验。本期无另加讨论题/下期口播。

## 渲染与参考资料

默认`render.py`执行来源检查/冻结核对、正文、真实limited BT.709像素转换、title-author参考资料附录。references.json共4项：R1 KafkaConsumer.java（Apache Kafka），R2 nodeModifyTable.c、R3 execIndexing.c、R4 nbtinsert.c（PostgreSQL Global Development Group），片尾只显示实际原题与机构。正文5497帧之后预期一页150帧，计划总5647帧；这是待执行计划，不是已编码成片记录。附录首中末、正文交界、播放器和最终SHA由正式渲染后的独立检查确认。

模型90项检查/33快照是有限教学程序；实际Kafka4.4.0+PostgreSQL18.0运行89项断言由独立runtime证据支持，研究限定到实际执行分支。查询后晚补标记、标记先单独提交是有限对照，不冒称真实实验。

根统一控制冻结、正式编码、成片复核与发布。本目录没有以预演clip冒充正式正文或最终video.mp4。
