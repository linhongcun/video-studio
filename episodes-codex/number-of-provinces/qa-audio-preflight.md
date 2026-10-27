# 独立音频预检

独立预检通过，无阻塞。声轨SHA256 `253a3250c0ce97682488deed6ed08790ab0bc46748102409b37f199a7aea5dff`，48kHz单声道16位，5159帧/171.966667秒，public副本完全一致。24个新选中take的raw→WAV PCM实际重放全同；24次唯一共享load/cut的保留样本数及discard尾切与build一致，24句切片与整轨PCM逐样本全等。

起始、23处间隔与尾部全零；Python5009..5158正好150帧/5秒，240000个源voice样本全零、字幕到5008。独立共享句首起音3/0通过，wholeplace无拷贝复核0偏移/无violations，与制作报告全文SHA相同。实际-16.0LUFS/-2.1dBTP，无削波与内部dropout。

实际信号图`docs/archive/2026-10/number-of-provinces/audio-waveforms.png`的4组源/共享cut波形已逐组实阅，尾段分离与保留主体可见。此项是信号检查，不是中文人工听辨。没有逐字ASR、全片人工听辨或学习效果声明；正式编码与网站另验。
