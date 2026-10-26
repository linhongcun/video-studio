# EP40 新配音与实际时序核验

状态：数值与来源检查通过。10镜20句，21个全新候选，最终19a+1b。sharedprep/gen/build/assemble/wholeplace/strict-onset/check_sentence按顺序实际执行；当前正文4482帧、149.4秒、7171200个48kHz单声道PCM样本。

完整WAV SHA-256：`0c48b0538985b74cce8e31e8ed6f45196ae03d6b2cdc09886b26eba2b9932805`。当前实际分镜/实体placeholder SHA：`66da8fe0d4a9d7cd9ff021e4d4c90be44ebecddef8485868ce88eef63fc7c04f`。首份分镜与封面回填后的分镜仅meta.covers不同，声音、words/SRT与全部镜/句/cue/字幕时序保持，证明见qa-cover-metadata-sync.json。

请求文本与raw→take PCM转换、共享cut源区间均核对。20段规范化sentence PCM与整轨相应窗口逐样本一致；独立临时目录调用实际sharedbuild全文重放，WAV完整SHA相同。实测-16.0LUFS、-2.1dBTP，相邻句最大0.4LU；零PCM尾段2.019417秒。

源审保留5个0.50–0.62秒低电平旗标，整轨保留4个对应源旗标；source-interval和PCM重放证明这些不是裁尾/铺轨新制造的缺口。原始a报告与短尾b比较结果保留，不清空warnings。五个source interval的pre-track证明在voice/pause-review.json，最终组合结果在qa-voice.json。

这些检查仅核声学/来源/时序。没有ASR、逐字对齐、语义或全片人工听辨；当前尚未检查正式编码/混音成片。保留旧两份Bloom共264个唯一冻结输入/媒体全文SHA不变，见qa-voice-old-inputs-after.json。
