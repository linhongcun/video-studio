# 配音与句级装配检查：简短收尾版

执行者：horse_voice。日期：2026-10-25（北京时间）。本次根据用户最新要求，仅保留01—16镜，在“5＋1＋1＝7场”处结束，不新增口播。

## 实际结果

- 16镜32句、6章，30fps，共5618帧，187.2667秒（约3分07秒）。没有请求新TTS，没有归一化或加速。
- 源音轨为已追溯的v0.56.4，SHA-256为`0d82ee3bed5ed3be11192eaf1880e45ab658787342599bd98d8af4f3f53ead98`。保留前5581帧、8,929,600个PCM样本，追加37帧、59,200个全零样本，总样本8,988,800。
- 第32句16-seven-2结束于样本8,892,155（5557.596875帧）。到旧5581帧裁点之间的37,445样本全部为零；补零后总句尾静音2.0134375秒。连接点前后各5毫秒也全零。
- 新音轨SHA-256为`436489744f709d5b91c1f891927af268d6f5fc0d8b3d9cd44bea8b20795fae5b`，public/audio/voice.wav是逐字节一致的实体副本。

## 已执行的保留与共享检查

1. 原前5581帧的PCM逐字节相同；全部32句的样本范围、内容与逐句SHA逐项相同，没有截断末字。
2. 前15个words镜头对象完全相同，前15镜from、duration、字幕、voice与cueFrames逐字段相同。第16镜仍从5204帧开始，仅延长末尾静音，最终414帧；两句实际时间和PCM保持不变。
3. shorten_voice.py只进行本次源PCM截取与补零，再调用仓内共享assemble、whole铺轨、label及sentence检查，均退出0。whole最大偏移0帧、0违规；32句字幕与最终脚本逐字一致且连续，总帧数和样本数一致。
4. 源人声实测−16.0LUFS、真峰值−2.2dB；邻句响度差最大0.4LU，最长句内低声间隔0.46秒，inner_dropouts为空。混音成片另由媒体流程测量。

## 能力边界与来源

本次未执行逐字ASR、内部词对齐或全片人工听辨；原句没有重配。words.json的chars/words兼容字段仍为整句包络，句首有共享声学算法依据。label检查为0 cues、0 fail，不能扩大为所有主体动画同步均已验证。

本次严格保留结论针对源人声PCM，不直接等同于重新编码、混音后MP4的解码音频相同。旧长版QA保存在voice/proof-ending-qa-voice.md，作为历史记录，不当作本版已展示的内容。

专项证据：voice/short-ending-composition.json、voice/short-ending-preservation.json、voice/short-ending-loudness.txt、voice/qa-audio-inputs.json、voice/place_v2.json与qa-timing.json。原基线在revisions/short-ending/，操作由production根shorten_voice.py记录，原稿与配置未由本代理修改。
