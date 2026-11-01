# MQ04 issue 收尾文字草稿

状态：制作中，仅供根代理在真实交付后填写、审读及执行；本文件没有向GitHub发送内容。以下文字中的“已完成”段落均以同一版媒体完成制作、合并/Release/Pages及线上核验为使用条件。发布前不粘贴，不把占位字段留在正式issue。

## #312 收尾说明（待事实齐备后发送）

> MQ04 / EP.44《Kafka发送确认：消息发出后，怎样才算发送成功？》已完成GitHub站点交付，slug为kafka-send-confirmation。影片沿同一业务事件区分send调用返回、成功metadata、终态未知及本地确定未发送；成功确认不等于消费者业务完成，应用重新send同eventId不被生产者幂等自动去重。
>
> 成片与图文：https://linhongcun.github.io/video-studio/episodes/kafka-send-confirmation/
>
> 制作PR、merge完整SHA、Release、Release后Pages运行、实际帧数/时长/字节及完整媒体SHA：由根代理从publication.json及render-result.json填写。
>
> 冻结、来源/模型、声音、动态、实际编码、本地网站及线上canonical完整GET/原生浏览器核验：只填本期真实报告中的通过范围与数量，并链接release.md、qa-final及线上证据；实际能力限制按报告保留。
>
> 本轮仅GitHub与站点，无外部平台新发；未做的真实Broker、逐字ASR、全片人工语义听辨或真机测试不记完成，技术检查不代表用户观看认可。完成上述交付与核验后，以completed关闭本issue。

## #308 总览更新（保留历史记录，仅更新受影响段落）

完成交付后使用下列变更，不覆盖MQ01–03的既有版本与验收历史，不触碰取消题目的稳定编号：

1. 当前状态改为“9个核心选题中4个已交付（MQ01–MQ04），其余5期未开工”。在MQ04处补实际Release及本片链接；原14题维持取消，不恢复为储备任务。
2. 核心表MQ04/#312状态由制作中改为“实际Release已交付，线上核验通过”；MQ01、MQ02、MQ03既有首发/修订信息保留。其余5题为MQ05、MQ06、MQ07、MQ08、MQ15，不擅自启动或重编号。
3. 追加简短“MQ04交付”段：真实PR/merge/Release/Pages、标题/slug与成片链接，实际完整媒体SHA及canonical/原生浏览器结果，#312已completed关闭；所有字段以publication.json真实回执为准。
4. 范围说明保留：MQ04讲发送者可观察证据，副本确认仍由MQ15深入、消费幂等由MQ05处理，不因本片完工合并或恢复其他选题；仅GitHub站点，无平台新发，不预记用户已观看认可。

推荐实际发布顺序：确认目标部署和线上完整媒体身份 → 完成原生浏览器与截图实读 → 写本期publication.json/最终记录 → 将#312按completed关闭 → 更新#308并回读核对。未到上述阶段，当前真实状态仍为3项已交付、MQ04制作中、其余5项未开工。
