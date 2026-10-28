# 独立音频预检

数值检查与实际波形图查看通过。声轨SHA256 `31461ffb9a6c5a527547625f751b701f74b1824084fe8082f4859bf2bb0b8019`，48kHz单声道16位，5988帧/199.600000秒，public副本完全一致。6个新选中take的raw→WAV PCM实际重放全同；20组旧raw/WAV/sidecar按60份文件完整SHA与text/tts复核；26次唯一共享load/cut的保留样本数及discard尾切与build一致，26句切片与整轨PCM逐样本全等。

起始、25处间隔与尾部全零；Python5838..5987正好150帧/5秒，240000个源voice样本全零、字幕到5837。独立共享句首起音3/0通过，wholeplace无拷贝复核0偏移/无violations，与制作报告全文SHA相同。实际-16.0LUFS/-2.2dBTP，无削波与内部dropout。

实际信号图见`docs/archive/2026-10/number-of-provinces/audio-waveforms.png`，已实际查看其中4组原始/保留信号，确认主体波形与尾切形态；这不代替汉语语义听辨。没有逐字ASR、全片人工听辨或学习效果声明；正式编码与网站另验。
