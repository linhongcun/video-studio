# Kafka MQ08 / EP48

《重试与死信：失败消息，为什么不能一直重试？》；#316；基线8769a592856fe2618e5daf3d84849bf4b052e22b，新实体production目录制作。

本期主机制是应用自己保存调用名额、阶段与下次时间：到期且有预算→保存预留→调用；成功直接提交原进度，临时失败仍有名额则等待，永久拒绝/耗尽才转DLQ。Kafka pause不退回记录、不设置定时器或重调业务。固定同E01/7042，原P0中E02在后，原日志仍保留。状态目录仅承诺同机保留目录的进程恢复，不是多机共享或断电实验。

15镜30句922字的完整稿已独立通过，script SHA621c6d3122619b772c2cff04f1a0cd319d4e8acc9d51c84b70712c9c09a8a53f，canonical无分隔旁白bb8438b59500e17fd37d4e2851f6a7f2eb0ab37bb17bfc761988f536e7378364。script/config保持根初次配音阶段锁定字节；plan仅按根授权补实际状态窗口，共享装配字段未变，旧版和差异保留。根已正式接受最终b声轨6018帧/200.6秒，voice SHA0f352895ff60739ba15321c727d232d9fe97ca905e643e9c7a3a1d4e72891c15；作者不自行选段或TTS，初声6104及失败候选保持。

- sources/与source-chain-notes.md：新鲜官方固定Kafka4.4.0 commitGET、原题/机构、实际执行链/精确行号。references.json四项title-author，4段连续源码原文与raw逐字对应，共享来源预检通过。
- examples/：真实Java Kafka worker与本机状态核心；纯Java44检查包含子JVM退出/恢复，不是Kafka实验。实际Worker编译曾拦截AppInfoParser包名，旧源/修正留qa-editorial/worker-compile-import-correction。
- build_model.py/model.json/model-verification.json：106有限检查、41快照。旧跨进程Future模型问题与修正均保留，当前进程C不继承旧Future，物理DLQ记录与journal独立保留。
- 独立真实Kafka运行：8case/15worker/6halt/151断言通过，docs/archive/2026-11/mq08-15-implementation/runtime/runs/mq08-20261101T092105.198110Z；作者实际读取范围见qa-editorial/runtime-author-review.json。业务仅可控fixture，不是真通知。运行500ms与模型虚拟400ms分开，辅助E02订单字段差异已说明。
- article.mdx/4图位计划：四章可独立阅读，核心SourceQuote齐，图位已按最终声音定为2212/3114/4354/5525整数帧和frame/30秒，MDX同步启用；源预演已看，成片后才生成核验JPEG。
- remotion/：新Main读取model/plan与实测@storyboard，fresh npmci257包，类型检查通过。MechanismPreview/MechanismSequence按明确状态参数运行，prevoice固定45帧/阶段只是过程自查，不假装配音时序。Main无测得board便不注册，不能用空声轨正式渲染。
- qa-prevoice/self-review.json：46原状态实图、7受影响修正图和2张先对象后术语的开场图、9状态接触表、关键原图、3段实际675帧短序列/33解码帧/7接触表已打开审读。旧错误图/源与旧短片保留，修后局部复验；非全片听辨、非最终时序或正式成片验收。

根统一声音/封面/冻结/正式编码/publication与发布。公共thin wrappers由mq_publication维护；本作者不改共享、旧冻结、发布目录或git。默认render接共享真实limitedBT709转换与原题/机构资料附录，不能只交正文。尚未freeze或正式编码。

实际final6018作者自查已收束：151帧PNG/DOM、26张接触表、10张关键原图、4张真实字幕图实际审读；6段1757帧无字幕连续短片完整解码，并实际打开107个解码取样组成的21张接触表。结论与范围见`qa-own/self-review.json`，源身份见`qa-own/production-candidate.json`。作者现停止生产输入写入，等待独立动态；不是正式成片或全片听辨通过。新A helper仅改作者输出目录/身份，来源SHA与差异在qa-own/helper-provenance.json。
