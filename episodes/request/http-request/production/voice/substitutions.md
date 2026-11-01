# 技术细节重制配音与检查边界

2026-10-25，root审读17镜34句旁白后，使用仓内共享`prep.py`、`gen.py`、`build.py`与冰糖音色制作；未修改共享配音、裁尾、起音或铺轨算法。

本轮所有34句均为新词，没有复用旧音频。原24个已选take保留，并由`revisions/depth-baseline.json`记录文字、送模文本与完整SHA；本轮审计验证原文件未变。新句使用`depth`命名，避免同句id误选旧音频。

## 送模文本

字幕和脚本保留原字。仅送模文本进行以下读音处理，完整输入见`sents.json`与选中take的`.txt.json`：

- HTTPS、HTTP、TCP、TLS、SYN、ACK、DNS、IP、HTML、DOM、CSSOM、UDP、QUIC、GET均逐字母拆写。CSSOM在CSS前替换，HTTPS在HTTP前替换，避免部分替换。
- 版本保持原稿的“一点一”“二”“三”；HTTP/1.1等兼容替换同样明确版本。
- Host送模写“霍斯特”，200送模写“二百”；不改变对应报文字段和状态码的显示。
- 每句按共享prep追加独立“好。”尾声，再由共享cut移除；不自行改裁尾算法。

## 候选与实际取舍

首轮34个depth候选中，`01-hook-2-depth`与`04-dns-2-depth`的独立尾段仅0.11秒，前者另含0.50秒以上句内低信号风险。以同文追加2个depthb候选并选择；不将波形风险当作已识别的错字或漏字。初轮完整SHA和风险保留在`revisions/depth-take-audit-first.json`，最终所选报告为`depth-take-audit.json`。未选候选与raw文件留在本机，不作为发布所需入库输入。

最终32个depth与2个depthb候选均满足当前审计：送模文本逐字相等、48kHz mono/16-bit、raw到48kHz PCM精确转换、共享cut独立尾段不少于0.12秒、没有0.50秒以上句内低信号。最短所选独立尾段0.13秒。

## 整轨与声学时序

- 5406帧，180.2秒，8,649,600个48kHz mono样本；音轨无变速。
- 整轨测量−16.0 LUFS；相邻句响度差最大1.1 LU，拼接采样跳变最大0.007422373164445162，句内长静音0项。成片混音响度与AAC仍由正式编码步骤另验。
- 实体公开音轨与voice.wav完整SHA均为`60d4b10d0e57abea68918ed576086721c50ddcb50cdef422956707b229e0f53a`。
- 共享whole铺轨最大偏移0帧；14个句首cue在−6..+2帧窗口内，0项失败，0项例外。完整时序与哈希见`depth-timing-report.json`，起音逐项结果见`label-onset-depth.txt`。

当前环境的项目Python未安装faster_whisper，/workspace未发现可用模型缓存，工具中也没有可用ASR/音频听辨接口。本轮未进行逐字ASR或人工听辨；不沿用历史“模型下载遭拒”作为本次已尝试的证据。字符包络仅兼容既有检查器，只有句首使用真实声学起音，不是句内逐字对齐。

## 冻结前视觉描述一致性校正

03镜实际为canvas URL拆解卡，因此仅将脚本/production中的画面描述改为全屏URL拆解，并将browserShots明确为01、15。导航文档用四段总览、五个子阶段及TCP/TLS括组解释实际画面。未改任何旁白、送模文本、选定take、build或音轨，未重新gen/build；只重跑assemble使脚本哈希与视觉metadata一致。原生成脚本完整SHA单独保留在`depth-generation-baseline.json`的generationScriptSha256，新生产脚本哈希为productionScriptSha256；审计逐镜将34句原文严格对应现有sents，未以新稿追认旧TTS。34句起止、字幕、声学cue和整轨SHA全部保持，14cue再次通过。逐字段差异及不变文件完整SHA见`depth-visual-consistency-proof.json`。
