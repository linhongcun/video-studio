# 配音与句级装配检查

执行者：horse_voice。日期：2026-10-25（北京时间）。本记录针对实际生成的人声、共享装配与句级时序，不代表全片听辨或观众理解实验。

## 实际产物

- 最终18镜、36句、6章，30fps，共6327帧，210.9秒（3分30.9秒）。未后期加速。
- 冰糖／mimo-v2.5-tts，经共享prep、gen与build生成。36句主候选加3份备用，共39份takes及原始wav保留；最终34份a、1份b、1份c。
- 最终人声SHA-256：`2af8c739a08c2cf9c1972b22a0c31e1dd30cb6260fc92af749dd987a693def66`。
- 48kHz、单声道、16-bit，10,123,200样本。public/audio/voice.wav为实体副本，与主音轨逐字节一致。
- 句内停顿0.45秒、镜间0.8秒、片尾2.4秒；未使用代码卡或额外末尾程序附录。

## 已执行的核验

1. 最终脚本与plan的SHA在请求TTS前记录于voice/input-provenance.json，并在最终build前与检查时复核一致。09与18的审稿修订已纳入，不用旧take配新脚本哈希。
2. 共享裁尾与实际包络检查覆盖全部36份主候选。01-hook-2改选b；07-champion-order-1改选c，后者仅在送模文本去掉“示例结果”后的逗号，组名之间顿号保留。公开脚本、字幕原标点不变。候选比较见voice/qa-candidate-comparison.json，差异见voice/substitutions.md。
3. 最终共享build报告为−16.0LUFS，内部4倍过采样真峰值−2.2dBTP；邻句响度差最大0.5LU，拼接处最大逐样本跳变约0.00212。最终最长句内低声间隔0.46秒，inner_dropouts为空。此为人声指标，最终混音视频另测。
4. 共享assemble对全部36句计算声学句首起音，写入words.json及storyboard。whole铺轨报告最大偏移0帧、0违规；总帧数、样本数、字幕逐字与逐镜连续性及章起点检查通过。
5. 共享label检查结果为0 cues、0 fail：本期plan未配置首现命名术语cue，不能扩大成36句逐字起音或全部主体动画同步已验收。

## 能力边界

本环境未发现可用的faster-whisper与可读本地ASR模型，没有执行逐字ASR、内部词对齐或全片人工听辨。words.json中的chars/words兼容字段是整句包络，只有句首有声学起音依据。包络、TTS文本一致与裁尾检查不能证明每个发音都正确，也不能代替实际音画动态复核。

机器结果：voice/qa-audio-inputs.json、voice/place_v2.json、qa-timing.json。各镜真实起点/时长及句首在voice/shot_frames.json和words.json中，供视觉小样按最终音轨核验。storyboard的covers快照若后续封面变更，最终冻结前需同步核对；不得为同步封面改动音轨或字幕时序。
