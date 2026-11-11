# P06本轮新配音独立有界QA

核验日期：2026-11-11 UTC。对象为`episodes/puzzles/twelve-balls/production/revisions/logic-20261111/twelve-balls`，基线`27329c38a`。

两份新`logic` take的文本元数据、非全零信号、无满幅削波、原始24kHz至48kHz的实际PCM转换、现行共享裁尾长度、装配后整轨对应PCM切片，以及28句原选take的身份检查通过。此结论不包含语义听辨、读音或逐字ASR。

检查脚本为[check-audio.py](check-audio.py)，完整SHA与数值证据为[audio-check.json](audio-check.json)。从仓根执行`python docs/archive/2026-11/puzzles-followup-logic/audio/twelve-balls/check-audio.py`，只读制作输入，输出限于本归档目录；不调用TTS、ASR或网络，也不重新装配音轨。核验所用共享裁尾实现按路径及SHA绑定于JSON。

| 实测项 | 12-first-balanced-1 | 12-first-balanced-2 |
|---|---:|---:|
| 选中take | logic | logic |
| 原始WAV | 24kHz、16bit、单声道 | 24kHz、16bit、单声道 |
| 实配句PCM | 48kHz、16bit、单声道 | 48kHz、16bit、单声道 |
| 实配样本数 | 512850 | 611602 |
| 实配时长 | 10.684375秒 | 12.741708秒 |
| 整轨范围，左含右不含 | 7662569–8175419 | 8192219–8803821 |
| 原始及实配满幅削波数 | 0 | 0 |
| 实配最长低幅段，10ms窗峰值≤0.005 | 0.29秒 | 0.26秒 |
| 实配4倍采样真峰值 | −2.1002dBTP | −2.1002dBTP |
| 共享cut抛弃独立尾段时长 | 0.440667秒 | 0.344625秒 |
| 共享cut及低幅修剪后长度与实配一致 | 是 | 是 |
| 实配PCM与整轨对应样本完全一致 | 是 | 是 |

装配整轨完整SHA-256为`4cc091cbd9f0b66d105f7819c3b299ba39b89ec67293a25ae0b2d1a5d1d64c2c`，与本轮`voice/build.json`一致；样本总数11121600与build记录一致。JSON保留实测首尾样本、首尾10ms峰值与跳变；这些数值不证明最后一个音节的语义完整。

28句保留输入分别比对当前选中标签、原／新准备文本及TTS文本，以及来源账本记录、旧制作目录和新revision中的完整SHA。84份文件（每句`.wav`、`.raw.wav`、`.txt.json`各一）全部相同。此处证明复用输入身份，未声称新整轨中这些片段的响度或PCM也与旧版相同。

## 定稿与实际识别范围

第一句定稿：

> 最后回到首称平衡这一路，一到八号正常，九到十二号还有八种轻重可能；要让最后一称能收尾，第二称每路至多留三种。

第二句定稿：

> 因此拿九、十、十一号对正常的一、二、三号，十二号留盘外：左重只剩三种偏重，右重只剩三种偏轻，平衡只剩十二号轻重两种。

两句均核对`script.md`、`voice/sents.json`、take的`.txt.json`及`voice/build.json`一致，送模元数据为定稿加“好。”抛弃尾巴；这只是文本来源核对。实际识别文本均为无，无法给出实际说出内容与定稿的语义差异。没有听辨裁掉的片段是否实际说“好”，也没有通过信号检查推定读音、连读或句尾音节正确。

本轮没有发出ASR请求。已知三次`Unsupported model`是2026-11-07的P09历史尝试：`mimo-v2.5`两次400，`mimo-v2-omni`一次400，证据为`episodes/puzzles/pirate-gold/production/revisions/motivation-20261107/pirate-gold/qa/audio-asr-04-responses.json`。它们不是本轮P06请求；本轮按既定边界不重复同配置模型，也不冒称ASR、语义听辨、逐字对齐、最终编码音频复核或全片实时观看已完成。
