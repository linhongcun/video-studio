# P10本轮新配音独立有界QA

核验日期：2026-11-11 UTC。对象为`episodes/puzzles/prisoners-light/production/revisions/logic-20261111/prisoners-light`，基线`27329c38aae4e8388a9999ab1c357fa9c8783fd9`。

三份新`logic` take的文本元数据、非全零信号、无满幅削波、原始24kHz至48kHz的实际PCM转换、现行共享裁尾长度、装配后整轨对应PCM切片，以及25句原选take的身份检查通过。此结论不包含语义听辨、读音或逐字ASR。

检查脚本为[check-audio.py](check-audio.py)，完整SHA与数值证据为[audio-check.json](audio-check.json)。从仓根执行`python docs/archive/2026-11/puzzles-followup-logic/audio/prisoners-light/check-audio.py`，只读制作输入，输出限于本归档目录；不调用TTS、ASR或网络，也不重新装配音轨。核验所用共享裁尾实现按路径及SHA绑定于JSON。

| 实测项 | 03-assign-roles-1 | 04-send-once-1 | 04-send-once-2 |
|---|---:|---:|---:|
| 选中take | logic | logic | logic |
| 原始WAV | 24kHz、16bit、单声道 | 同左 | 同左 |
| 实配句PCM | 48kHz、16bit、单声道 | 同左 | 同左 |
| 实配样本数 | 614500 | 388472 | 498843 |
| 实配时长 | 12.802083秒 | 8.093167秒 | 10.392563秒 |
| 整轨范围，左含右不含 | 1433208–2047708 | 2384518–2772990 | 2789790–3288633 |
| 原始及实配满幅削波数 | 0 | 0 | 0 |
| 实配最长低幅段，10ms窗峰值≤0.005 | 0.20秒 | 0.21秒 | 0.20秒 |
| 实配4倍采样真峰值 | −2.2003dBTP | −2.2002dBTP | −2.2002dBTP |
| 共享cut抛弃独立尾段时长 | 0.420875秒 | 0.447167秒 | 0.550375秒 |
| 共享cut及低幅修剪后长度与实配一致 | 是 | 是 | 是 |
| 实配PCM与整轨对应样本完全一致 | 是 | 是 | 是 |

装配整轨完整SHA-256为`a13eb3f4e69616a21bc9be9b186296f72b15eed3bd8a2ceecb968e077ce0531a`，与本轮`voice/build.json`一致；样本总数10179200与build记录一致。JSON保留实测首尾样本、首尾10ms峰值与跳变；这些数值不证明最后一个音节的语义完整。

25句保留输入分别比对当前选中标签、原／新准备文本及TTS文本，以及来源账本记录、旧制作目录和新revision中的完整SHA。75份文件（每句`.wav`、`.raw.wav`、`.txt.json`各一）全部相同，包含03第二句原take。此处证明复用输入身份，未声称新整轨中这些片段的响度或PCM也与旧版相同。

## 定稿与实际识别范围

03第一句定稿：

> 灯只能留亮灭，累计数量需要由人记；个人记录不能直接共享，这套办法固定一名计数员，其余九十九人各只成功发一次，避免重复算人。

04第一句定稿：

> 灯亮时已有一份未收信号，再开也留不下第二份；发信人若擅自关灯，这份信号就会丢失。

04第二句定稿：

> 所以未发者只有遇到灭灯才开灯，并自己记住已发；遇亮还没发成功，就保留资格继续等，成功发过以后永不再开灯。

三句均核对`voice/jobs-logic.json`的任务范围、`script.md`、`voice/sents.json`、take的`.txt.json`及`voice/build.json`一致，送模元数据为定稿加“好。”抛弃尾巴；这只是文本来源核对。实际识别文本均为无，无法给出实际说出内容与定稿的语义差异。没有听辨裁掉的片段是否实际说“好”，也没有通过信号检查推定读音、连读或句尾音节正确。

本轮没有发出ASR请求。已知三次`Unsupported model`是2026-11-07的P09历史尝试：`mimo-v2.5`两次400，`mimo-v2-omni`一次400，证据为`episodes/puzzles/pirate-gold/production/revisions/motivation-20261107/pirate-gold/qa/audio-asr-04-responses.json`。它们不是本轮P10请求；本轮按既定边界不重复同配置模型，也不冒称ASR、语义听辨、逐字对齐、最终编码音频复核或全片实时观看已完成。
