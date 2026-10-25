# P05 配音与句级装配检查

执行者：horse_voice。日期：2026-10-25（UTC）。本报告核对实际送模文本、原始转换、共享处理、样本和句级时序；ASR、语义听辨及全片人工听辨均未执行。

## 实际结果

- 冰糖／mimo-v2.5-tts，正常语速，无speed参数或后期变速。12镜24句、4章，旁白654字含标点／577字不含标点，30fps，共5257帧、175.2333秒（2分55.23秒）。真实总长及句窗已交给视觉制作。
- 24份a及5份同文b共29份候选全部保留。01第一句、07第二句、08第二句、11第一句、12第二句选b，其余19句保留a；正文及标点未改，只有独立风格提示调整。
- 01／07／08／12被检查句的原始最大低声间隔分别0.74／0.76／0.61／0.56秒，所选b分别0.31／0.28／0.36／0.29秒。11第一句原尾段仅0.06883秒，b为0.745秒。最终整轨inner_dropouts为空，最大句内低声间隔0.46秒；这些测量只说明信号风险，不认定实际发生或消除了某个错字。
- 人声SHA-256：`2ea3e8b68eee14f11b6c5699bb865fe17d2c92f25a82d6e2cdcc249086b6ef2c`。48kHz、单声道、16-bit，共8,411,200样本。public/audio为实体副本，逐字节相同。
- 句内0.45秒、镜间0.8秒、尾停参数2秒。实际末句至轨尾97,367零样本，即2.0284792秒。最终WAV ebur128实测−16.0LUFS、真峰值−2.1dB；邻句响度差最大0.3LU，拼接最大逐样本跳变约0.001383。正式混音音量另行检查。

## 已执行的来源与装配检查

1. 仅在root双审PASS后核对最新script `8381171d…3bc2d6d`、pronunciation `b95df412…52f4bb8`等五稿完整SHA，再调用共享prep／gen。原始生成时间与来源保存在voice/input-provenance.json，两种旁白摘要及输入定义见voice/script-narration-sha256.json，未改写生成历史。
2. 24份所选实际请求正文均等于冻结原句加裁尾词“好。”，无F、英文字母或阿拉伯数字口播；裁尾词不入字幕。29份raw到48kHz转换均逐样本精确一致，24句最终sentence WAV与整轨对应样本区间相同。
3. 通过共享build、assemble、whole铺轨、label-onset-strict和sentence检查。最大铺轨偏移0帧、0违规，24句字幕与冻结旁白逐字一致且连续，采样数对应5257帧。计划声明0个命名cue，实际报告为0cue／0fail／0例外，没有沿用其他期的两个cue；每句仍有共享算法测量的句首起音。
4. assemble.py仅调用当前共享句级装配，subtitles.srt与captions.srt同字节，placeholder与storyboard同字节。初版空封面分镜`05783a0a…e662c6`及其QA来源已存voice/assembly-history，预演记录保留原来源身份。最终covers确认后仅重assemble／place／0cue／sentence检查，当前分镜`504f4706…a7eeec`已纳入最终封面，声音未重配或重build，元数据同步证明见voice/final-cover-sync.json。

## 源PCM与共享处理的精确复现

整轨全部8,411,200样本由7,617,833句样本及793,367零间隙样本组成，首部、句间、镜间及尾部间隙均为零，全部样本有来源。

新增检查先把共享common.cut的原始波形与已归一化、限幅的成品按单一线性增益拟合。临时诊断线0.995下，01第一句和05第一句未通过，最低相关0.99055063；原数值、失败项和结果完整保留在voice/qa-source-pcm-linear-fit.json，没有降低阈值或改配音。

该单一增益模型不能完整描述共享build的非线性峰值限幅。按root认可的核对方案，将相同sents／picks／params复制到ignored的remotion/out/voice-source-rebuild、直接读取同一takes，再调用同一共享build。复现的完整voice.wav、build.json以及全部24句WAV与生产文件逐字节相等；生产音轨、选段与时序全程未改。voice/qa-source-pcm.json记录原线性诊断及其边界，以官方共享处理的完整字节复现闭合来源一致性，不将线性近似充作处理后的PCM判定模型。该证明也不等于语义或音质听辨。

## 数量、动作句窗与能力边界

十四／二十七／三十九、十五到二十六、二十八到三十一、三十二碎与最高安全三十一、实际八次与保证十四次等实际送模文本及句样本逐项记录于voice/qa-critical-inputs.json。读音输入目标另见voice/reading-targets.json，区分序数第一枚yī和一枚yì，提示还hái、得děi；这些是输入证据，不能证明实际每个数字或多音字发音正确。

完整动作句窗见voice/action-windows.json，共享原始时序保留于voice/shot_frames.json。09镜from3443、duration448，局部两句为0.89–183.75／197.25–424.92帧；10镜from3891、duration455，为0.92–165.27／178.77–431.93；11镜from4346、duration400，为0.93–152.03／165.53–376.80。09的14／27两次与39一次、10的逐层试蛋、11的32碎均由视觉在实际句窗内安排，不能冒称数字内部词的精确时间。

当前工具集合没有可读取任意本地WAV进行语义收听或转写的工具；本地无Whisper／Vosk／torch及可读ASR模型，未下载大模型。ASRPerformed=false、semanticListeningPerformed=false、wordAlignmentPerformed=false、fullHumanListeningPerformed=false。words.json的字符时间为句包络兼容数据，不是逐字识别。

verify_encoded_voice.py已按本期动态句数准备，正式媒体稳定后再检查整轨／24句、声道、延迟、增益与已知BGM贡献。它不能替代语义听辨；当前音轨短于Wallpaper，正式运行仍须核对实际样本长度及冻结源。

其他证据：voice/qa-candidates.json、voice/qa-takes-a.json、voice/qa-candidate-comparison.json、voice/qa-audio-inputs.json、voice/loudness.txt、voice/place_v2.json、label-onset-strict.txt及qa-timing.json。首轮临时build与picks另存为voice/build-a.json、voice/picks-a.json，不代表最终选择。所有生成、裁尾、铺轨、起音及混音算法均未修改或复制为本期实现。

## 最终封面映射

最终covers SHA为`ffded0b151bad0f8a26e35671ac17784945bb9a929ee9453635da5e1ba965458`，分镜及placeholder SHA均为`504f4706df184c178e37b1027f73f320b232fb65beeaccf48b927dad3ca7eeec`。新旧分镜唯一变化路径为meta.covers，所有句窗、镜窗、字幕、动作和其他元数据精确相同；words保持`afefeb6cc703a464a18467ef08e6a940bc4c897238b553b796861bb9d703ea93`。公开音轨与原WAV均保持`2ea3e8b6…6ef2c`，5257帧／8,411,200样本不变。

captions.srt与subtitles.srt的完整SHA均为`393a13d8a8d6df22c4eb364e653a1f3d91c0c0ee0855e3dd1e8b5ed07621176e`。实际共享铺轨仍0偏移，0命名cue／0失败，句级检查通过。原input-provenance、script-narration摘要、sents、picks及build文件保持原字节。voice/qa-critical-inputs.json与voice/qa-audio-inputs.json补充当前最终SB／words／cover映射，没有把初版预演改写成新分镜的产物。ASR及语义听辨能力边界不变。
