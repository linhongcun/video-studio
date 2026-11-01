# P05二分开头修订：正式编码音轨检查

结论：通过，0失败。执行者horse_voice。检查本次新正式video.mp4、fresh remotion/out/voice.mp4及当前voice.wav；不修改169项冻结输入、原root报告或已固定的binary-qa.md。当前是**5569帧、185.6333秒**的修订成片，参考WAV为8,910,400样本。

正式视频：10,034,214字节，SHA-256 `b43510f3196f92964d21a3b854941a65f4af33fffd2484c171ca518f9f747c66`。新premix SHA-256：`952284ee8347c5407be282db6354f05812c01f545cea2379ca478efca40ca4c3`。当前voice SHA-256：`012e92bda809c774e80917c5502b3e58c5d565cb83e77e18f712d2910b57ff0f`。当前SB SHA-256：`95704da3dce129ca3e057d9551173949533d99b78ee6dac3e470c5a104ce593c`。

| 实测项目 | 结果 |
| --- | --- |
| Premix与当前WAV全轨相关性 | 0.99997727015 |
| Premix 24句最低相关性 | 0.99995820242 |
| Premix固定偏移／句间最大变化 | 0／0样本 |
| Premix单声道解码拟合增益 | -0.00994dB |
| Final与premix直接相关性：全轨／24句最低 | 0.96526582828／0.96142598979 |
| Final固定偏移／句间最大变化 | 95样本（1.97917ms）／0样本 |
| 已知人声＋Wallpaper重建：全轨／24句最低相关性 | 0.99982876822／0.99950945906 |
| 各句拟合人声增益最大偏差 | 0.010811dB |
| 句窗内拟合人声高于BGM | 11.78821dB |
| 实际mix报告：constant模式人声高于BGM | 12.1dB |

实际premix及final均为48kHz双声道AAC，各解码8,910,848样本，比当前WAV多448样本（9.33333ms）AAC尾填充。Premix从0覆盖完整参考WAV；final按实测95样本延迟对齐后，仍完整覆盖全部8,910,400源样本与24句，尾端余353个解码样本。没有句区间缺失或累计漂移。当前WAV末句后仍有97,367零样本／2.0284792秒，与AAC尾填充分开记录。

左右声道分别解码验证。Premix与原mono参考相关性分别0.99997727015、0.99997727015；final由各声道已知人声及音乐重建相关性分别0.99979962322、0.99977342315，两侧人声及音乐贡献均为正，没有丢侧或错轨的数值迹象。

本次另从实际当前WAV和仓库不可变baseline WAV重新读取20个复用句的样本区间，全部逐字节相同；前755帧前缀与原声相同，旧1676帧起后缀与当前1988帧起后缀相同。故本片是**20句原处理PCM复用＋03／04四句新配音**，下游统一后移312帧，未把20句说成重新生成。对应完整SHA及20句逐项检查在JSON的original20PCMReuse内。

方法保持原算法及阈值：前30秒FFT估计±4800样本内延迟，再比较完整对齐波形及24句实际startSample/endSample；每句只在全轨延迟±16样本内检查。Wallpaper长于当前修订时长，无需循环，按生产1秒淡入／2秒淡出做已知双源拟合；只读检验，没有重做配音、全轨归一化或混音。

169项冻结输入在检查前后均逐项匹配source-sha256.json，清单SHA为`fe45b05e132f1458e332da9b58b61d6568513b4bc08e95ba5c66f1388bc995ff`。根mix-report与out副本一致，SHA为`adb94fa2b670f69fe2631ae610006b7175618520909d34ed8185289e15419409`。原root qa-encoded-voice-content.json、qa-audio-content.json、voice/binary-qa.md和组合证明均保持原SHA；没有覆写原版音频报告，也没有改写原始单增益诊断或字节精确复现记录。

能力边界：ASRPerformed=false、semanticListeningPerformed=false、fullHumanListeningPerformed=false。波形／音源一致证明选定输入进入实际编码和混音，不能证明五十、二十五、楼层及次数逐字发音或语义均正确，也不代表已经人工听完。

本次完整结果只写在revisions/binary-opening/qa-audio-content.json/md及原生qa-encoded-voice-content.json。JSON保留原生数值并补充本次5569帧身份、20句PCM复用证明和显式能力字段；nativeReportSHA256固定本次原生报告原字节。报告落地后再核169源及受保护原报告。
