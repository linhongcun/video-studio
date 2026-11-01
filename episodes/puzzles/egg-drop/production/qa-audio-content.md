# P05／EP33 正式编码音源一致性检查

结论：通过，0失败。执行者horse_voice，仅只读检查已稳定的新正式video.mp4、remotion/out/voice.mp4及原voice.wav。检查前后133项冻结输入逐项匹配同一清单，未重配、重build、重混音或修改源。原始单增益诊断及共享build字节精确闭合报告均保持原字节。

正式视频SHA-256：`f5876353b2d2f4b8f6709e59a6091edfd2ab1ae5303e239751e1b9eca42b9179`，9,546,440字节；5257帧、30fps、175.2333秒。新premix SHA-256：`68c41bea9f1e5ae7a1a9da1eacc70f4cfe669bbcc653347e4841d5abd64e403e`。原WAV为48kHz单声道16-bit，8,411,200样本，SHA-256：`2ea3e8b68eee14f11b6c5699bb865fe17d2c92f25a82d6e2cdcc249086b6ef2c`。

| 实测项目 | 结果 |
| --- | --- |
| Premix与原WAV全轨相关性 | 0.99997659697 |
| Premix 24句最低相关性 | 0.99995865562 |
| Premix偏移／各句最大偏移变化 | 0／0样本 |
| Premix单声道解码拟合增益 | -0.00976dB |
| Final与premix直接相关性：全轨／24句最低 | 0.96522799969／0.96177416483 |
| Final固定偏移／各句最大偏移变化 | 95样本（1.97917ms）／0样本 |
| 已知人声+BGM重建：全轨／24句最低相关性 | 0.99984715958／0.99975039858 |
| 各句拟合人声增益最大偏差 | 0.008086dB |
| 句窗内拟合人声高于BGM | 11.77973dB |
| 生产mix报告：constant模式人声高于BGM | 12.0dB |

实际premix及final均为48kHz双声道AAC，各解码8,412,160样本，比原WAV多960样本（20.00000ms）的AAC尾填充。Premix从样本0完整覆盖原WAV；final按实测95样本固定延迟对齐后，仍完整覆盖全部8,411,200源样本及24句，尾端还余865个解码样本。没有句区间丢失或累计漂移。原WAV尾停97,367零样本／2.0284792秒，与AAC尾填充分开记录。

左右原生声道分别解码核对，premix与原WAV相关性分别0.99997659697、0.99997659697；final由已知人声+BGM重建的相关性分别0.99981698779、0.99980290545，两侧人声和音乐贡献均为正。没有丢侧或错轨的数值迹象。

方法：前30秒FFT估计±4800样本内全轨延迟，再验证完整对齐波形及24句实际startSample/endSample；每句只在全轨延迟±16样本内搜索。Wallpaper长于本片，无需循环，以生产1秒淡入／2秒淡出作为已知音乐来源，双源拟合只检查实际贡献，不重做生产归一化、限幅或混音。固定的小延迟按实测记录，未对成片作补偿修改。

当前分镜SHA为`504f4706df184c178e37b1027f73f320b232fb65beeaccf48b927dad3ca7eeec`，冻结清单SHA为`01a072baad2799520e9b5041789422bf9de2677b508cf557c43623ed72f3801f`。原声源线性单增益诊断voice/qa-source-pcm-linear-fit.json的两项未过0.995及最低0.99055063原样保留；voice/qa-source-pcm.json的共享非线性build完整WAV／24句／build元数据字节精确复现也原样保留。本次比较的参考为已经过共享处理的最终WAV，未拿单一线性增益近似替代源PCM闭合证明。

能力边界：ASRPerformed=false、semanticListeningPerformed=false、fullHumanListeningPerformed=false。上述数值只验证选定声音输入完整进入实际编码和混音，不能判定楼层、次数或多音字发音逐字正确，也不代表已人工听完。

完整数值、24句、双声道、阈值及实际命令见qa-audio-content.json；该文件保留原生qa-encoded-voice-content.json的数值，补充当前身份、显式能力字段及原诊断文件完整SHA。nativeReportSHA256固定原生报告原字节；报告落地后再次核对133项冻结输入及原源PCM记录。
