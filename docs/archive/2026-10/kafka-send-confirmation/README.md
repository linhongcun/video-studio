# Kafka MQ04 · 发送确认

任务：[#312](https://github.com/linhongcun/video-studio/issues/312)《Kafka发送确认：消息发出后，怎样才算发送成功？》，身份为 **EP.44 / Kafka MQ04 / kafka-send-confirmation**，系列总览[#308](https://github.com/linhongcun/video-studio/issues/308)。正式成片、本地检查、GitHub主干/Release/Pages与线上完整媒体和实际播放器核验均已完成，#312已以completed关闭。

本轮以 `2c54aa7c5f4e3236500728d3078b356d06625099` 为同步基线，分支为codex/mq04-20261030；实际开工与环境检查见[startup.json](../../../../episodes-codex/kafka-send-confirmation/startup.json)。只复用现行MQ03基础设施和锁文件，不沿用旧配音、成片、冻结清单或验收回执；旧片与共享style-v1保持。

本期沿同一业务事件区分send调用返回、后台发送、生产者所观察的成功或失败结果与实际日志记录。成功metadata不证明消费者业务完成；超时终态下结果未知，不能直接推断未写入；本地序列化失败另作明确对照。模型/源码解释与真实Broker实验分开记录，具体版本、配置、故障条件和画面动作以定稿研究与分镜为准。

制作入口见[本期README](../../../../episodes-codex/kafka-send-confirmation/README.md)，逐步完成的事实写入[制作与发布记录](../../../../episodes-codex/kafka-send-confirmation/release.md)。本期11镜22句、4章，正文3417帧加150帧资料页，共3567帧/118.9秒、6,189,865字节，完整媒体SHA为 `a3dd3f640b0032e363d7010410b496c6321a951b2e6c257ee2fde1efda3c2e13`。175项输入冻结；本地HTTP完整媒体身份与48项网站动作/20次严格PTS通过，A2长原文浮层另补两项实际触摸滚动与亮暗实图检查，范围见本期发布记录。[PR #440](https://github.com/linhongcun/video-studio/pull/440)合并 `8d852e2ccf8e751efbd6f095d508edca991410a5`，首发[Release v0.96.0](https://github.com/linhongcun/video-studio/releases/tag/v0.96.0)，Release后[Pages 41035467904](https://github.com/linhongcun/video-studio/actions/runs/41035467904)同SHA成功；自身发布前push重复运行41035382103已主动取消，未记为失败。

本轮仅GitHub主干、Release和Pages，无外部平台新发；技术检查不预记用户观看认可。当前4/9核心已交付，其余5题未开工，原14个取消题目不恢复。#312已在2026-10-30T09:57:41Z完成线上核验后按completed关闭，#308已同步，见[实际发布回执](../../../../episodes-codex/kafka-send-confirmation/publication.json)。


[线上HTTP核验](../../../../episodes-codex/kafka-send-confirmation/online-verification.json)14项普通canonical GET于北京时间2026-10-30T17:55:05.689215+08:00通过，完整MP4/海报/VTT/四图一致，4章22cue、四课目录与真实更新日志正确；[线上原生Chromium](../../../../episodes-codex/kafka-send-confirmation/qa/site-online-native/report.json)48动作/20严格PTS与[线上A2亮暗触摸滚动](../../../../episodes-codex/kafka-send-confirmation/qa/site-online-supplement/report.json)两项通过，实际查看六图。直接原生HTTPS，无TLS绕过或HTTP回填；资料与原生控件分离、所看图无等待弧。无真实Broker/Java/网络故障/序列化器或业务副作用实验、逐字ASR、全片人工语义听辨、物理手机或学习效果测试，不将技术通过写成用户观看认可。
