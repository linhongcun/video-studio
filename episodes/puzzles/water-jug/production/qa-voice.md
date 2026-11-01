# P03 配音与句级装配检查

执行者：horse_voice。日期：2026-10-25（UTC）。检查范围为真实送模文本、声学包络、句级装配和来源一致性；未执行逐字ASR或全片人工听辨。

## 实际结果

- 冰糖／mimo-v2.5-tts，正常语速、无后期加速。12镜24句、4章，30fps，共4977帧、165.9秒（2分45.9秒）。已在视觉定稿前交付真实总长和动作句窗。
- 首轮24份a，02两句、03第一句、06第二句各补b，06第二句再补c，29份原始候选和请求正文均保留。最终20a、3b、1c；所有备选都保留原句和原标点，只调整风格提示。
- 02两句原始最大低声间隔由0.56/0.65秒降为b的0.25/0.42秒；03第一句由0.74降为0.39秒；06第二句a/b/c分别0.77/0.72/0.34秒，c约3.63汉字/秒。最终整轨inner_dropouts为空，最大句内低声间隔0.46秒；这些是包络数据，不是词义或发音判断。
- 人声SHA-256：`9f2cedc1efedc6738cc8f74b4c301fcb6a25f0aa2da0f61c2d061d1c0437777c`。48kHz、单声道、16-bit，共7,963,200样本。公开audio为字节一致的实体副本。
- 本期参数：句内0.45秒、镜间0.8秒、尾停2秒；实际最后一句结束至轨尾2.00977秒。未加速、未新增口播或程序卡。

## 已执行的检查

1. 使用最终script SHA `bff2a618…511cd`、plan SHA `c2d44be2…2038`完成共享prep；TTS和build前后再核对同一全文。原始生成来源记录在voice/input-provenance.json，完整旁白摘要及明确定义记录在voice/script-narration-sha256.json。
2. 逐项检查全部24份选定take实际送模文本，均等于冻结句子加共享裁尾词“好。”；“好。”未入字幕。所有29份候选的raw到48kHz转换均有精确PCM核验，所选24份均通过。全部24个最终句子PCM与人声整轨对应样本区间逐字节相同。
3. 通过共享build、assemble、whole铺轨、label-onset-strict及sentence检查。whole偏移0帧、0违规；全部24句字幕与旁白逐字一致、连续；帧数和样本数一致。互倒、五减三两个句首cue均在−6至+2帧规则内，0失败、0例外。
4. 最终ffmpeg ebur128实测−16.0LUFS、真峰值−2.2dB；邻句响度差最大0.4LU，拼接处最大逐样本跳变约0.001096。成片混音和编码音轨另行按正式媒体检查。
5. assemble.py只调用当前共享句级装配；subtitles.srt与共享captions.srt逐字节相同。storyboard与Remotion placeholder逐字节相同；meta.covers与当前covers.json相同，封面变更须重装配后再冻结。

## 动作时间与能力边界

真实镜头起止与两句局部窗口均在voice/shot_frames.json。六个动作镜为04装满、05倒出三升、07倒空小壶、08转存两升、10重新装满、11倒出一升；已向视觉制作人员交付实际窗口。句窗可以安排完整动作，不能作为“倒水”“一满”“才停”等内部词的逐字时间。

数字使用三升、五升、两升、一升、四升等中文原句。读音表及独立风格提示覆盖倒水／倒空的dào、空着／倒空的kōng、空位的kòng、升shēng、剩shèng；voice/reading-targets.json列出输入目标，voice/qa-critical-inputs.json列出全部实际请求及句样本。这些只能证明输入来源正确，不能证明实际发音逐字正确。

已检索当前工具集合，无可读取任意本地音频进行语义收听或转写的工具；本地无Whisper/Vosk/torch及可读ASR模型，未下载大模型。因此未执行逐字ASR、内部词对齐或全片人工听辨。words.json的字符起止为句包络兼容字段，不冒称逐字对齐。后续完整波形一致性只检验选定音源是否进入编码及混音，不替代语义听辨。

机器结果：voice/qa-takes-a.json、voice/qa-candidate-comparison.json、voice/qa-audio-inputs.json、voice/qa-critical-inputs.json、voice/loudness.txt、voice/place_v2.json、label-onset-strict.txt、qa-timing.json。共享生成／裁尾／铺轨／起音实现及旧期均未修改。
