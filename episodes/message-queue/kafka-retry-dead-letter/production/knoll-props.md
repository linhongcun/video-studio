# EP.48 kafka-retry-dead-letter：失败处理怎样有限退出

依据：storyboard.json 2395bafc24d05235dc239fefe8b8ce0ca31290b6498b5d2cce4571511a9d7f91；covers.json e1b6781d61a81ffdc7069c8e74ffbcf6cc503549e73280820cf31a793e5fa289。尚未冻结，无旧冻结许可。
script 621c6d3122619b772c2cff04f1a0cd319d4e8acc9d51c84b70712c9c09a8a53f / voice 0f352895ff60739ba15321c727d232d9fe97ca905e643e9c7a3a1d4e72891c15 / words e0ae7c84f8bd8e4855158004f871f642a883100608823b956cb369250d806bf5 / cues 无独立文件 / shot_frames 由根共享voice生成，不另造时序。正文6018帧、15镜、1920×1080、30fps；状态表的from含/to不含，精确阈值见qa-own/state-timing.json。

## 本次身份与变化

首次制作，无上一冻结版本。整稿621c6d…/canonical旁白bb8438…独立通过；根已正式接受b声轨0f352895…（6018帧/200.6秒），初声6104与失败候选历史保留。作者未TTS、未改voice/words/board/script/params，也没有重建原声音。config.cover的unused旧短标题保持；实际cover/board使用根安装的正确covers.json，不额外改元数据追认重装配。

与前期相比，本片新建应用状态而非数据库唯一索引/生产批次或积压计数：同一E01从已取回、暂停新交付、预留调用名额、到期调用、未知恢复走到成功或等待处置。logicalHandler+eventId找同一文件状态；3是保守预留上限，保存后未实际调用便退出也消耗，不说精确执行了3次通知。Kafka4.4.0 classic单消费者/P0/manual commit；初始原恢复值0，E01@0、E02@1始终留在原日志。

## 画面类型

| 镜 | frame | 绝对帧（含端点） | 帧数 |
|---|---|---|---|
| 01 | canvas | 0–335 | 336 |
| 02 | canvas | 336–739 | 404 |
| 03 | canvas | 740–1125 | 386 |
| 04 | canvas | 1126–1533 | 408 |
| 05 | canvas | 1534–1911 | 378 |
| 06 | canvas | 1912–2295 | 384 |
| 07 | canvas | 2296–2707 | 412 |
| 08 | canvas | 2708–3131 | 424 |
| 09 | canvas | 3132–3519 | 388 |
| 10 | canvas | 3520–3925 | 406 |
| 11 | canvas | 3926–4371 | 446 |
| 12 | canvas | 4372–4695 | 324 |
| 13 | canvas | 4696–5104 | 409 |
| 14 | canvas | 5105–5542 | 438 |
| 15 | canvas | 5543–6017 | 475 |

全部canvas，无browser或假应用外壳。01/02先原日志、应用持有与暂停门，03再引入notify:E01文件状态与3名额；03–14原日志左、本机状态中、业务/死信右，保持同一事件。15为有明确概念定位的稀疏分支回顾，不把错误/重复现场改成业务成功现场。全文不用strike，无独立讨论题或下一期口播。

## 帧义与同步

Main从真实@storyboard读取句界，以实际局部起止计算条件动作；model.json是状态事实源。plan新增actualStateWindows只记录推导的整数窗口，id/slug/visualType/chapter/cues等共享装配字段未变，旧plan和差异在qa-own/plan-timing-adaptation.json；没有据此重装声音/分镜。

每个调用先到期且有名额，再保存IN_FLIGHT/+1，下一阶段才invoke。reserved的当前业务文字“本次尚未调用”，不把上次失败当成本次结果。05进程退出变结果未知；06保留原IN_FLIGHT到读回第一句完成后，再核验重读并recover。06就地解释幂等为“同一E01再调用，业务不能重复生效”。

07业务成功后另原commit，成功回调才原0→1/resume，E02仅取得交付资格、不假称已执行业务。08/09/10/13/14明确回共同状态，重置遮罩显示70帧后退场，先复位再改变条件。08满3挡住4；09永久拒绝首个结果便停止；10单独显式DLQ envelope的身份、来源、次数、原因，不让遮罩挡全镜。

11区分send结果对象、物理追加、成功metadata、本机确认保存。已获metadata但尚未保存时脚注明确未保存，原进度仍0。12另原commit请求和成功回调。13目标错误保持pending/原0，不从异常推定所有情况下DLQ空。14已退出进程的发送结果明确为历史，进程C不继承旧Future/观察结果；物理DLQ@0还在，新send可以新增@1。14六状态窗口至少63帧，角色/记录不移走。

移动圆点只在面板间空隙，原E01/E02不会从日志搬走。标题/脚注依据model当前事实和条件，结果不提前。章节头/IT小村沿共享style-v1，色值与字体不抄散副本。实际导入shared源码、style-v1与font ledger需由根加入最终冻结清单。

可审计DOM含model-state/process/phase/totalStarted/readyAt、原提交、active/paused/position/held、业务调用数/knownComplete、当前与退出前历史Future/metadata、物理原/DLQ日志。字幕默认开启；showSubtitlesfalse/hideSubtitlestrue可真实关字幕。状态采样/actual clips与4个实际字幕PNG范围见qa-own/self-review.json，非全片听辨/学习研究。

## 封面与配图

封面由根从本批模板生成、独立审图并安装，covers.json和cover-style.json为实际身份；作者不复制旧图或覆盖P。四个Figure整数帧为2212/3114/4354/5525，seconds=frame/30，MDX seekTo九位小数同步。源预演四图已实际打开；最终article/*.jpg仍待正式成片按整数帧抽取与核验。

## 默认编码与参考资料

默认render.py入口使用资料预检、实际冻结检查、正文、limitedBT709真实像素转换/混音及title-author资料附录。正文计划6018帧后追加4来源一页150帧，预期总6168帧/205.6秒；这是未正式编码的计划，不是媒体回执。资料只显示ClassicKafkaConsumer.java、FetchCollector.java、KafkaProducer.java、ConsumerCoordinator.java和Apache Kafka机构，完整链接/连续原文在文章/研究，不叠摘录、日期或暂停提示。

正式成片、资料首中末/正文交界、默认烧录字幕退场、AAC/PCM/颜色与播放器检查由根统一流程及独立复核执行，作者不freeze或正式编码。纯模型106检查与真实Kafka151断言分别留证；handler是受控fixture，不是真通知。旧预演错误图、模型/Java编译失败和声音旧候选均保留，不用新PASS覆盖历史失败身份。
