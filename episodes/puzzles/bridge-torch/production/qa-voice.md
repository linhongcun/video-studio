# P02 配音与句级装配检查

执行者：horse_voice。日期：2026-10-25（北京时间）。本检查覆盖实际TTS输入、声学包络、句级装配和元数据，不冒称逐字ASR或全片听辨。

## 实际结果

- 冰糖／mimo-v2.5-tts，正常语速、无后期加速。16镜32句、4章，30fps，共6025帧，200.8333秒（约3分21秒）。实际时长比选题预估稍长，已在视觉定稿前告知root与制作人员。
- 首轮32份a候选，07-reset-1仅补一份b，共33份候选及原始wav均保留；最终31a、1b。07的初轮整轨低声间隔0.51秒，新b为0.17秒，字词及标点不变。15-net-saving-2原始包络虽为0.52秒，整轨为0.34秒，保留原候选。
- 人声SHA-256：`b7d1585a6a88137fa90217b388410802434bbe85bb0834e0133bfc1820d2fbbb`。48kHz、单声道、16-bit，共9,640,000样本。公开audio为实体副本，逐字节一致。
- 参数仅写本期voice/params.json：句内0.45秒、镜间0.8秒、片尾2秒；未添加程序卡、证明或额外口播。

## 已执行的核验

1. 请求TTS前锁定并记录最终script/plan SHA，最终build前再次核对一致。全部32份选定takes的实际送模文本逐项与对应sents核对，均一致；共享prep增加的“好。”仅用于裁尾，不入字幕。
2. 对全部候选使用共享common.load/cut检查实际裁尾与包络。最终inner_dropouts为空，最长句内低声间隔0.42秒；未为通过阈值修改共享算法。
3. 共享assemble生成实际句首声学起音、words与storyboard。whole铺轨最大偏移0帧、0违规；32句字幕与冻结旁白逐字一致并连续，采样数和帧数一致。
4. 手电、同行、回到起点3个句首命名cue均在−6至+2帧窗口内，0 fail、0例外；算式“五减三”沿用第15镜第二句时间，不新增术语cue。
5. assemble.py只是当前共享装配的薄包装，subtitles.srt与共享captions.srt逐字节一致。当前storyboard.meta.covers与本期covers.json一致，后续封面变更需重装配核验。
6. 最终人声ffmpeg ebur128实测−16.0LUFS、真峰值−2.2dB；邻句响度差最大0.6LU，拼接处最大逐样本跳变约0.00575。最终混音成片另按媒体流程测量。

## 动作所用句窗与能力边界

04镜从1259帧开始，总307帧：第一句局部0.32–109.72，第二句123.22–283.73。05镜从1566帧开始，总277帧：第一句局部0.73–129.01，第二句142.51–253.16。窗口内的两次动作仍由视觉实现与动态复核决定，不将句包络当成“过去／回来”等词的逐字时间。

已检索当前工具集合，没有可读取本地任意wav做语义收听或转写的工具；本地没有Whisper/Vosk/torch及可读ASR模型，本次未下载大模型。因此未执行逐字ASR、内部词对齐或全片人工听辨。重点数字句的核验范围明确为实际送模文本和句边界，见voice/qa-critical-inputs.json；它们不能证明实际每个数字的发音均正确。

机器结果与来源：voice/input-provenance.json、voice/qa-takes-a.json、voice/qa-candidate-comparison.json、voice/qa-audio-inputs.json、voice/loudness.txt、voice/place_v2.json、label-onset-strict.txt及qa-timing.json。完整时序在words.json和voice/shot_frames.json。生成、裁尾、铺轨和起音均复用共享实现，未修改共享或旧期。

## EP29身份元数据同步

上游观察者模式占用EP28后，本期仅将非口播内部身份同步为EP29。原TTS生成script SHA继续原样保存在voice/input-provenance.json，未改写为新稿SHA；当前全文SHA与旁白摘要分别记录在voice/script-narration-sha256.json及voice/metadata-sync-ep29.json。

没有请求TTS、运行build、归一化或编辑音轨。全部32句文本、16个words镜头对象、全部句窗和声学句首起音严格相同；所有镜头字段除timing.source摘要外严格相同。音轨与公开实体副本SHA均保持b7d1585a…d2fbbb，6025帧不变。共享assemble/place/onset/sentence重新检查通过，storyboard与placeholder逐字节同步，covers快照为当前封面。
