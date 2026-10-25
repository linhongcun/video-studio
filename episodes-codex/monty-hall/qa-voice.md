# P04 配音与句级装配检查

执行者：horse_voice。日期：2026-10-25（UTC）。范围是实际TTS输入、原始转换、声学包络、句级装配与来源一致性；未执行逐字ASR或全片人工听辨。

## 实际结果

- 冰糖／mimo-v2.5-tts，正常语速，无后期加速。14镜28句、4章，30fps，共5507帧、183.5667秒（3分03.57秒）。真实总长及全部镜窗已在视觉定稿前交付。
- 28份a、3份同文b，共31份raw、48kHz候选及请求正文全部保留。最终03第一句、05第二句、07第二句选b，其余25句选a；所有备选保留原句与原标点，只调整独立风格提示。
- 首轮03第一句最大低声间隔0.64秒，b降至0.36秒；05第二句原尾段仅0.04067秒，b为0.32712秒，低声间隔由0.65降至0.33秒；07第二句原尾段仅0.08104秒，b为0.42629秒。最终整轨inner_dropouts为空，最长句内低声间隔0.43秒。包络只定位裁尾或停顿风险，不作为识别错字的证据。
- 人声SHA-256：`c12883686897cef1f983aae434ef02745ac9b9bf27660c95160658d41ab2eee6`。48kHz、单声道、16-bit，共8,811,200样本。公开audio为实体副本，逐字节一致。
- 本期参数：句内0.45秒、镜间0.8秒、尾停2秒。实际最后一句至轨尾96,351零样本，即2.0073125秒。未追加证明、引流、程序卡或其他口播。

## 已执行的检查

1. root双审放行后，先核对script完整SHA `d85df3de…0c12a`、plan `7bc40e7c…efffcf`、config `b0ec8409…dd55d`，再运行共享prep/gen。生成来源原样记录于voice/input-provenance.json；整份脚本与旁白摘要的定义、完整SHA见voice/script-narration-sha256.json，没有用后来的元数据覆盖原生成身份。
2. 全部28个所选实际送模正文逐项等于冻结原句加裁尾词“好。”，无正文或标点替换。31份候选均通过原始WAV到48kHz的精确PCM转换核对；28份最终sentence PCM均与整轨对应样本区间逐字节相同。
3. 通过共享build、assemble、whole铺轨、label-onset-strict及sentence检查。whole最大偏移0帧、0违规；28句字幕与冻结旁白逐字一致且连续，音轨样本数与5507帧对应。两个真实句首cue为02“主持人”和14“每次都换”，−6至+2帧规则内0失败、0例外。
4. 最终WAV经ffmpeg ebur128实测−16.0LUFS、真峰值−2.2dB；最大邻句响度差0.4LU，拼接处最大逐样本跳变约0.006342。正式混音及编码音轨另查，不能用本项代替成片音量或内容一致性检查。
5. assemble.py只调用当前共享句级装配；subtitles.srt与captions.srt相同，storyboard与Remotion placeholder相同。当前meta.covers与covers.json相同（SHA `16281b06…e215a9`），装配时config仍为原SHA。封面或配置后续修改须重装配并同步副本，再交root冻结。

## 关键输入及能力边界

三分之一、三分之二、门号一／二／三，以及04“换门前”、09“当时”、10“做决定时／刚才”等历史锚点，已逐项记录实际送模正文与最终句样本，见voice/qa-critical-inputs.json。读音目标包括空门kōng、中奖zhòng、扇门shàn，见voice/reading-targets.json及pronunciation.md。上述检查只能证明输入与来源正确，不能证明实际音频逐字发音或语义均正确。

真实镜头起止和全部两句窗口见voice/shot_frames.json。重点04局部窗0.69–118.02／131.52–351.59帧；09为0.89–175.79／189.29–425.88；10为0.88–194.49／207.99–386.18。这些用于安排动作的句窗，不是“揭开”“当时”“做决定时”等内部词的声学时间。

已检索当前工具集合，没有可读取任意本地WAV进行语义收听或转写的工具。本地没有Whisper／Vosk／torch及可读ASR模型，未下载大模型。因此未执行逐字ASR、内部词对齐或全片人工听辨；words.json的chars字段为句包络兼容数据，不冒称逐字识别。

编码检查助手verify_encoded_voice.py已准备，按实际配置动态读取句数和冻结输入数；待正式媒体稳定后才运行。它核对整轨和每句波形、声道、延迟、增益及已知BGM贡献，不能替代语义听辨。当前实际183.57秒短于Wallpaper，助手的无需循环前提与当前总长相容，正式运行仍会检查实际样本长度。

机器证据：voice/qa-candidates.json、voice/qa-takes-a.json、voice/qa-candidate-comparison.json、voice/qa-audio-inputs.json、voice/qa-critical-inputs.json、voice/loudness.txt、voice/place_v2.json、label-onset-strict.txt、qa-timing.json。首轮临时build与picks另保留为voice/build-a.json、voice/picks-a.json；它们不代表最终媒体。生成、裁尾、铺轨及起音复用共享实现，未修改共享或旧期。
