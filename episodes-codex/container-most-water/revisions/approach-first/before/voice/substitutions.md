# 盛最多水的容器：配音选择与实际检查

2026-10-24（北京时间），22镜44句、正文868字。由Codex配音制作代理执行。音色冰糖、mimo-v2.5-tts，沿用仓内共享prep/gen/build与common.cut；不加速、不拉伸语音，不复制铺轨或起音算法。每句仅按共享prep追加片外“好。”裁尾，没有字词送模替换，字幕与script保留原文。

## 候选与风险处理

首轮b候选6句触发本期保守的尾声裕度筛查（共享裁尾所选最后间隔之后的片外尾声少于0.35秒）：01-hook-1、02-data-1、10-bound-1、12-advance-left-1、17-optimal-1、22-closing-1。其中12-advance-left-1另有原始PCM削顶。此筛查只标示裁尾/信号风险，不据此宣称识别到错字或某个音节缺失。

这6句分别定向换c/d；01第一句和17第一句的c仍未达到本期尾声裕度，最终换d。最终选择38b + 4c + 2d，44句包络警报为0。初始缺少soundfile导致的未生成批次记录保留在gen-b-initial-failed.log；补必要依赖后才实际生成，没有将失败任务当作有音频。

全部所选原始raw、48k单声道PCM、实际送模txt、jobs与picks均保留。selected-take-audit.json逐句记录SHA、PCM格式、原音频/主句/片外尾声时长、句内最大静音、削顶比例、实际送模文本及raw→48k逐样本一致性。candidate-risks-b.json保留首轮完整风险。所有44份所选转换与原始raw按相同ffmpeg设置重新转换后逐样本一致。

## 整轨

共享build输出6544帧、218.133333秒、10470400个48k样本；全轨没有变速。音轨完整SHA256为`29255ab792320bb56569df5743b218e5cf62ff97da2de41fd7b25ee066f05de5`。

实际PCM综合响度−16.0LUFS；4倍过采样真峰、相邻句响度差、拼接跳变与各项数值见qa-v1.json，原始响度测量日志见audio-loudness.log。所选来源削顶比例均为0；最小片外尾声约0.357秒，最大句内低能量间隔0.39秒；整轨inner_dropouts为空。没有为通过检查改共享算法或放宽阈值。

## 能力限制

本机通过huggingface_hub的local_files_only=True分别检查官方medium/small/base/tiny缓存，均返回LocalEntryNotFoundError，记录在asr-capability.json。未尝试绕过网络策略下载权重。未执行逐字ASR、句内词级对齐或全片人工听辨，不生成假的asr.json，也未运行会依赖缺失ASR的完整run.sh。

父任务将使用仓内共享assemble_sentence_episode.py，以真实句级TTS/build边界和共享声学起音装配words/storyboard；其中字符兼容字段若出现，仅是整句包络，不是每字识别。术语“双指针”位于07镜第二句句首，允许真实句首声学起音检查。独立代理核验记录另行提供；本文件不将制作方信号检查当作用户已观看认可。
