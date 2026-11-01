# 配音与句级装配检查：视频内完整证明版

执行者：horse_voice。日期：2026-10-25（北京时间）。本记录针对实际生成的人声、PCM保留与句级时序，不代表全片听辨或观众理解实验。原18镜版本记录保留在voice/original-qa-voice.md；原音轨SHA为2af8c739…def66。

## 本次结果

- 最终25镜、50句、7章，30fps，共8976帧，299.2秒（4分59.2秒）。新尾18—25镜为16句、3101帧（约103.37秒）。未后期加速。
- 新尾仍使用冰糖／mimo-v2.5-tts和共享prep、gen、build。19首句另选b，最长包络低声间隔从0.54秒降至0.35秒；25首句按独立审稿修订后选b，明确“至少两匹没输过”。旧25a保留但未选用，首轮输入SHA与原句保留。
- 全部50份选定TTS输入逐项核对：唯一延续的字面差异是原07镜c候选在送模时去掉“示例结果”之后的逗号，字幕仍为原标点。
- 最终人声SHA-256：`0d82ee3bed5ed3be11192eaf1880e45ab658787342599bd98d8af4f3f53ead98`。
- 48kHz、单声道、16-bit，14,361,600样本。公开audio副本与主音轨逐字节相同。

## 前17镜的严格保留

原视频第18镜从5875帧开始，因此保留原声轨前9,400,000个PCM样本（18,800,000字节）。原第17镜从5581到5875，共294帧；本次这些边界不变。

新尾在独立临时工程经共享build处理，使用0.01秒最小起音空隙（0.3帧）。薄编排脚本revise_ending_voice.py只连接原PCM前缀与新尾，将尾句样本/帧位置统一加上9,400,000样本/5875帧，并合并来源记录，不复制TTS、裁尾、归一化、铺轨或起音算法。整条人声没有再次归一化，因此旧段没有被全局增益重新缩放。

实际比较通过：

1. 全部旧前缀PCM逐字节相同，原34句各自的样本区间和SHA逐一相同。
2. 前17个words镜头对象完全相同，包括全部句首起音、句子、包络和时序。
3. 前17镜的id、from、durationInFrames、narration、subtitles、voice与cueFrames逐字段相同；新18镜仍从5875帧开始。
4. 连接点前后各5毫秒峰值PCM为0，连接发生在静音中。此保留结论针对源人声，不能扩大为另行重编码/混音后MP4解码PCM必然相同。

## 共享检查与声学指标

- shared assemble、whole铺轨、label与sentence检查均退出0。whole偏移最大0帧、0违规；50句字幕逐字与最终脚本一致、逐镜连续，总帧数和样本数一致。
- shared label检查为0 cues、0 fail：plan未配置命名术语cue，不能扩大成全部主体动画或逐字起音都已验收。
- 最终人声ffmpeg ebur128实测−16.0LUFS、真峰值−2.2dB；邻句响度差最大0.5LU，拼接处最大逐样本跳变约0.00305。最长句内低声间隔0.46秒，inner_dropouts为空。最终混音视频仍由成片流程另外测量。

## 复现与边界

新尾实际临时工程为/workspace/horse-ending-tail。其params、build、sents、picks、jobs、输入SHA和候选检查以ending-*文件保留在voice目录，所有新候选复制回voice/takes。复现时用这些尾输入与选定takes调用共享build，再用revise_ending_voice.py连接可追溯原音轨前缀，随后调用共享assemble/place/check和脚本的--verify。不要直接对50句整条重新build后声称旧PCM仍保留。

本次没有执行逐字ASR、内部词对齐或全片人工听辨。words.json的chars/words字段是整句兼容包络，只有句首有声学起音依据。模型输入和声学包络检查不能证明每个实际发音正确，也不能替代真实音画与动态表达复核。

详见voice/ending-preservation.json、voice/ending-composition.json、voice/qa-audio-inputs.json、voice/ending-loudness.txt、voice/place_v2.json与qa-timing.json。封面快照及视觉修改须在最终冻结前同步核对，不因视觉修改重写旧声轨。
