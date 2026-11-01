# Outbox单集配音与选段

2026-10-24，14镜28句，复用仓内shared prep/gen/build、裁尾、声学Rule与铺轨，不复制算法、不变速。Outbox仅在送模文本替换为“奥特博克斯”，字幕与script保留原文；每句尾“好。”由共享裁尾去掉。jobs/picks与txt.json保留。

初轮28句b审计发现11-consumer-rollback-1的最后隔离尾段仅0.076秒，有裁尾位置风险；这是信号风险，不是识别出错字。以相同文本重配c后消除，最终27b+1c。selected-signal-audit.json剩余警报0；28句raw到48k转换逐样本一致、PCM16单声道、送模文本与sents相符。

真实整轨5,598,400样本=3499帧（116.633秒），−16.0LUFS，真峰−2.2dBTP，邻句最大0.6LU，接缝样本跳变最大0.005899，inner_dropouts为空。shared place whole偏移0且public音轨为同字节实体文件；Outbox、幂等两句首标签strict0失败0例外；shared selfcheck及check_sentence通过。

本环境official medium ASR local_files_only加载返回LocalEntryNotFoundError，未绕过网络限制。无逐字ASR、句内词级对齐或全片人工听辨结论；兼容chars是句包络，selfcheck空ASR不一致不是听辨通过。见qa.json、raw-conversion-audit.json与signal审计。
