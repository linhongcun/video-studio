# EP.21 配音选段

28句均采用首轮a，原文无替换、无变速；逐句附加的“好。”由共享cut去掉。选段picks与所有take保留。共享build的inner_dropouts为空，邻句响度与拼接指标记录在build.json。

官方ASR medium本地没有可用权重，现行策略未授权HF，未绕过下载；没有逐字ASR或完整人工逐字听辨。words.json字符字段携带整句包络，仅句首onset实测。新术语都在句首，复用共享Rule严格窗口检查，无豁免。
