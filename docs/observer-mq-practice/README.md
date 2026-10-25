# D02 观察者模式实战修订

用户2026-10-25要求直接修改已发布视频，减少手写观察者实现，重点说明跨服务实践用MQ发布订阅。保留订单17、摘要和变化记录的案例和URL，压缩进程内原理，重做跨服务的事件路由、独立队列消费、离线积压、恢复重复投递与幂等，以及业务提交和消息发布的一致性边界。不能将“少手写”扩大成“观察者模式已经不用”。

开工工作区干净，fetch后从最新origin/main建立codex/observer-mq-practice，基线9834e2cd84b1081f8ab41ade369cf46b8b6ddf62。旧制作源码和媒体身份保存在`episodes-codex/observer-pattern/revisions/mq-practice/baseline/manifest.json`，旧视频通过该基线追溯；不覆盖旧检查结果以认可新内容。

依赖按当前remotion/package-lock.json真实npm ci安装257包，实体node_modules位于当前observer-pattern制作目录。音频使用/workspace/.venvs/video-studio/bin/python；numpy/scipy/soundfile导入通过。站点发布仍遵循已持续授权的GitHub主干、Release、Pages流程；外部平台未新发。

当前状态：10镜20句、4332帧/144.4秒已完成源制作和独立预检，正式编码中。音频20份原始转换PCM、文本与选段对应、共享裁尾和正文前缀/静默尾检查通过；无逐字ASR或完整人工听辨。219张原预演、83张澄清定验、17张Outbox定验均无COPYFIT；独立实际查看78个关键状态和连续04–07小样108个2fps解码帧，无阻塞。三比例封面重出并实际查看，Java完整程序8类行为重验通过，173项生产输入冻结并只读复核通过。

本轮对应重制issue为[#292](https://github.com/linhongcun/video-studio/issues/292)。发布前已再fetch到ef1dc4cd/v0.68.3，上游是另一片global-id修订及文档/版本更新，与173项冻结输入无交集；待无媒体读取时整合主干，版本按实际最新主干与标签选择，不预占或移动已有版本。

当前检查报告：`qa-voice-mq.json`、`qa-mq-preflight-independent.json`、`qa-mq-preflight-root.json`。旧站点QA归档于`revisions/mq-practice/legacy-published-reports/`，新发布同步真实render/mix/source身份，避免新版旁挂旧177.6秒报告。实际编码、构建与线上结果完成后追加。
