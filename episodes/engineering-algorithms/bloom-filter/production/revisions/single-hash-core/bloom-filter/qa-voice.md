# 新修订配音阶段核验

9镜18句，真实合成28个全新候选，选8a、10b；原版takes零复用。正文4570帧、152.333333秒。voice.wav与public实体副本SHA-256均为`a4d7301062cbc203fc4c88204655c073231bcb9c0ee77f19bd66f83b94b28b26`；最终SB/placeholder SHA为`d6ab108fd8e3272d5cbf13b114db3a2a165971a22d3c730c6015cbf6b5b05bd8`。

- 来源及裁切：18条请求与原始PCM转换无失败，裁尾保留单独尾段，未改变字幕或送模正文。0.50秒筛选是保守信号旗标，不等同缺词判断；原始a/b结果完整保留。
- 3个最终原始低电平区间为0.59/0.58/0.51秒；通过独立FFT定位，裁切后的内部PCM及旗标区间与原take逐样本相同。未为消除源停顿反复TTS，最终qa-voice-takes.json的原warnings和needs-review筛选结果保持；后续来源核验见voice/pause-review.json与qa-voice.json。
- 整轨：实际共享build在临时工程重放所选音源，得到相同全文WAV SHA；18个sentence WAV与整轨对应样本窗精确相同。整轨实测-16.04 LUFS、-2.2 dBTP，相邻句最大0.5 LU。归一化后保留2个已对应源区间的低电平旗标，不将shared build的旧字段inner_dropouts解释为语义缺失；尾部2.012771秒为零PCM。
- 时序：共享assemble、whole铺轨、严格起音和句级检查实际通过。08从3286帧开始，共655帧；第二句起317帧，重建与查询分别有317/30秒和338/30秒。当前未添加extraAfter，动作适配另由真实动态预检判断。
- 封面：按root要求用共享assemble同步最新covers，移除meta.covers后完整SB深比较不变，voice/words/SRT/句时序SHA不变；首次SB/words/时序QA保留快照，见qa-cover-metadata-sync.json。

范围仅为所选原始音源、裁切来源、混音前WAV及真实时序。未执行逐字ASR、语义听辨、字母读音识别或全片人工听辨；完整编码、背景音乐、片尾资料和网页尚须后续检查。
