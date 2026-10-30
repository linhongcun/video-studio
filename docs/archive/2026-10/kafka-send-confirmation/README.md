# Kafka MQ04 · 发送确认（待线上交付）

任务：[#312](https://github.com/linhongcun/video-studio/issues/312)《Kafka发送确认：消息发出后，怎样才算发送成功？》，身份为 **EP.44 / Kafka MQ04 / kafka-send-confirmation**，系列总览[#308](https://github.com/linhongcun/video-studio/issues/308)。正式成片与本地网站检查已完成；Release、Pages和线上核验仍待执行，不在本页预记远程通过。

本轮以 `2c54aa7c5f4e3236500728d3078b356d06625099` 为同步基线，分支为codex/mq04-20261030；实际开工与环境检查见[startup.json](../../../../episodes-codex/kafka-send-confirmation/startup.json)。只复用现行MQ03基础设施和锁文件，不沿用旧配音、成片、冻结清单或验收回执；旧片与共享style-v1保持。

本期沿同一业务事件区分send调用返回、后台发送、生产者所观察的成功或失败结果与实际日志记录。成功metadata不证明消费者业务完成；超时终态下结果未知，不能直接推断未写入；本地序列化失败另作明确对照。模型/源码解释与真实Broker实验分开记录，具体版本、配置、故障条件和画面动作以定稿研究与分镜为准。

制作入口见[本期README](../../../../episodes-codex/kafka-send-confirmation/README.md)，逐步完成的事实写入[制作与发布记录](../../../../episodes-codex/kafka-send-confirmation/release.md)。本期11镜22句、4章，正文3417帧加150帧资料页，共3567帧/118.9秒、6,189,865字节，完整媒体SHA为 `a3dd3f640b0032e363d7010410b496c6321a951b2e6c257ee2fde1efda3c2e13`。175项输入冻结；本地HTTP完整媒体身份与48项网站动作/20次严格PTS通过，A2长原文浮层另补两项实际触摸滚动与亮暗实图检查，范围见本期发布记录。版本、merge、Release与部署身份仍在发布时依最新主干核对。

本轮仅GitHub主干、Release和Pages，无外部平台新发；技术检查不预记用户观看认可。现有3个核心选题已交付，MQ04本轮制作中，其余5题未开工；原14个取消题目不恢复。全部必要线上核验后，再按规则completed关闭#312并更新#308。
