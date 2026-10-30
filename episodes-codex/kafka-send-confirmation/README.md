# Kafka MQ04 · 发送确认（EP44）

[选题#312](https://github.com/linhongcun/video-studio/issues/312)，[系列#308](https://github.com/linhongcun/video-studio/issues/308)。本期区分send调用返回、生产者确认结果与消费者业务完成，跟踪实际日志与发送者所知，明确结果未知和本地确定未发送的差别。正式标题、示例、配置与镜头以定稿的episode-config、script、research和storyboard为准。

本轮基线为 `2c54aa7c5f4e3236500728d3078b356d06625099`，分支 `codex/mq04-20261030`，开工同步记录见startup.json。制作入口仅复用保留的MQ03基础设施源码和当前锁文件，不继承旧成片、配音、冻结清单或QA/发布回执。新期依赖按当前锁文件安装，共享Kafka style-v1及旧片输入保持。

稿件、句级音轨与分镜已生成；正式动态预检已接受，175项生产输入已冻结并停写，正式媒体及四幅图已产出并完成根代理实看，本地网站、GitHub发布与线上核验均已完成；#312已以completed关闭，#308已同步4/9已交付。冻结清单SHA-256为 `5886ba7ec04585ed01d70c459ac385d2ae8194522cb4626f58a8e2986ca5c671`。检查结论只依本期实际报告记录，不用上一期数字代替。

## 本期示例与当前时序

11镜22句、4章；当前正文时序3417帧/113.9秒，voice.wav的完整SHA-256为 `2dc60dc34160c538c8d0e9f41dbb18b0c0e91b6d558e5d6eb542520dd18ac7e4`。这些是现有句级装配输入的身份，最终成片为3567帧/118.9秒，3417起为150帧资料页；实际媒体身份与检查范围见release.md，网站与远程交付结果见文末及release.md。

固定Kafka/Java客户端4.4.0、orders/P0和通知事件E01/order7042。正常、未知与本地序列化失败分别从共同空日志起点对照；未知分支内保持原日志，自动retry沿生产者A同批次身份，最终delivery期限失败后关闭A，再由应用新producer B重新send同eventId。Future与callback是同一发送完成结果的两种观察方式；晚到成功不改写原失败终态，成功metadata也不替消费者确认业务完成。完整acks/幂等/超时配置和模型限制见research.md，不展开MQ15副本机制。

## 已存在的制作入口

以下命令从仓根执行，按资料/稿件定稿、配音装配、独立预检、停写冻结、实际编码的先后使用。首次配音后保留选定takes，不为普通复核重请求非确定性TTS。密钥只来自环境变量MIMO_API_KEY，不写入仓库或日志。

```bash
node site/scripts/check-references.mjs --sources episodes-codex/kafka-send-confirmation
python3 episodes-codex/kafka-send-confirmation/prepare.py
python3 episodes/_shared/voice/gen.py --dir episodes-codex/kafka-send-confirmation
python3 episodes/_shared/voice/build.py --dir episodes-codex/kafka-send-confirmation
python3 episodes-codex/kafka-send-confirmation/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes-codex/kafka-send-confirmation --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/kafka-send-confirmation
python3 episodes-codex/kafka-send-confirmation/verify.py
```

模型验证与关键连续小样采用本期实际生成的入口和报告，另行补入。没有逐字ASR或全片人工语义听辨时如实记录；信号/句级窗口检查不冒充上述能力。

所有源负责人停写，真实音轨下的状态、路径、COPYFIT、三比例封面与4:3安全区检查完成后：

```bash
python3 episodes-codex/kafka-send-confirmation/freeze.py
python3 episodes-codex/kafka-send-confirmation/freeze.py --verify
npm --prefix episodes-codex/kafka-send-confirmation/remotion run check:types
bash episodes-codex/kafka-send-confirmation/render-final.sh
python3 episodes-codex/kafka-send-confirmation/verify.py --final
```

默认render包含正文、实际pc601→limited BT.709像素转换、混音与同色原题/机构参考资料，每页最多4项、默认5秒。最终交付video.mp4，不交付out/body.mp4。文章Figure图位在编码前按本期时序固定，成片后从准确帧生成并实际查看；limited BT.709视频导出JPEG时明确转换到full BT.601。冻结后需要改稿时保留旧制作稿，以带前后SHA的站点派生记录处理，不重写清单追认旧媒体。

## GitHub站点与浏览器

本期站点元数据结构见publication-meta.schema.json，真实日期与帧数由本期制作记录和render-result产生；schema不是已安装或已验收的回执。publish.py识别完全匹配本期身份的7键封面临时meta，真实已发布创建/首发身份仍受保护。

按[接入说明](publication-guide.md)完成本地安装与build后，运行本期qa/site-independent.py执行真实桌面/触屏模拟、播放器/章节/配图/原文交互、准确解码帧与Fullscreen API检查；另须实际看截图并记录范围。网页数据就绪或seek成功不代替界面实看，真机与模拟范围分开。Release后的普通canonical完整GET与原生浏览器检查分别留证，不把HTTP字节一致扩写为播放和可读性通过。

根代理负责版本、PR/合并、附注tag/Release、Pages、线上核验与issue收尾。仅GitHub与本站，无外部平台新发；实际最终状态见release.md及后续publication.json，技术检查不预记用户观看认可。


本地网站本轮实际检查：HTTP完整媒体SHA与生产/发布/dist一致，48项桌面/触屏模拟动作和20次严格PTS通过；补充A2长原文面板亮暗主题的两次真实触摸滚动，底部出处链接完整可见。实读六张截图后再记visualReviewed，证据见qa/site-independent/report.json与qa/site-supplement/report.json；这些是本地证据；远程交付另由下述canonical证据确认，物理手机未测试。


## 实际上线与issue收尾

[PR #440](https://github.com/linhongcun/video-studio/pull/440)已合并 `8d852e2ccf8e751efbd6f095d508edca991410a5`，发布[Release v0.96.0](https://github.com/linhongcun/video-studio/releases/tag/v0.96.0)；Release后[Pages 41035467904](https://github.com/linhongcun/video-studio/actions/runs/41035467904)在该SHA成功。14项普通canonical完整GET于北京时间2026-10-30T17:55:05.689215+08:00通过；[线上HTTP证据](online-verification.json)核对完整MP4/海报/VTT/四图、4章22cue、四课MQ目录与实际Release更新日志。

[线上原生浏览器](qa/site-online-native/report.json)48项动作/20次严格PTS与[线上A2补验](qa/site-online-supplement/report.json)两主题触摸滚动通过，实际查看六张线上图后标记visualReviewed；全程原生canonical HTTPS，无TLS绕过、HTTP回填或fallback。资料页与844横屏控件分离，所看图无等待弧；能力范围仍仅Chromium视口/触屏模拟及Fullscreen API。

#312已在2026-10-30T09:57:41Z以completed关闭，#308已同步：4/9核心已交付，其余5题未开工，旧14题维持取消。仅GitHub与本站，无外部平台新发；无真实Broker/Java Producer/网络故障注入/序列化器或业务副作用实测、逐字ASR、全片人工语义听辨、物理手机或学习效果实验，不预记用户观看认可。完整交付回执见[publication.json](publication.json)。
