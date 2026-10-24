# A01 / EP.22 配音与选段记录

2026-10-24，20镜40句。实际制作与检查：agent_video_voice。共享 MiMo 冰糖，模型 mimo-v2.5-tts；复用仓内 prep/gen/build、裁尾与声学起音实现，不变速。

## 送模文本与候选

字幕与旁白保留 script.md 原文。旁白统一说“智能体”，无英文 Agent 口播，无读音替换。共享 prep 只在每句末尾附加“好。”尾巴，由 common.cut 移除；原始送模文本保存在 takes/*.txt.json。jobs-a.json、jobs-b.json 和 picks.json 保留实际候选与选择。

初轮40句a全部生成。17-workflow-2-a 出现末段仅0.136秒、句内低能量间隔0.54秒的信号风险；这不等于识别出某字读错。保留 candidate-risks-a.json、build-a.json 及原候选，以相同送模文本补录b。所选17-b主句4.274秒、尾段0.457秒、最长低能量间隔0.11秒；最终39a+1b，全40句文本/PCM/raw转换审计0失败、0信号警报。详细记录见 selected-take-audit.json。

## 铺轨、起音与核验

共享build输出8,672,000样本、5,420帧、180.667秒；48kHz单声道PCM16。独立完整解码及loudnorm分析输入测得−16.02LUFS、−2.20dBTP，LRA2.30。邻句响度差最大0.5LU，接缝样本跳变最大0.004079，inner_dropouts为空。为达到共享最短镜长，09镜额外停留0.30秒、11镜0.0667秒；lead0.30秒、tail1.50秒已含在总帧数中。

voice/build-metadata.py只读共享build的真实句级边界，调用唯一共享Rule测句首起音，生成words/cues/shot_frames，不合成、剪切或改变音轨。04模型、07工具、14智能体均为真实句首。共享selfcheck已通过长度、镜长和3cue复算；ASR字段为空产生的日志差异不代表识别结果。

root完成共享place_v2整轨校验与实体复制，maxOffsetFrames=0；public音轨与voice.wav逐字节相同。root完成严格起音检查：3cue、0失败、0例外。脚本、40句字幕、5章、总帧数与声音样本核验见 ../qa-timing.json。未重复运行相同的root核验。

音轨完整SHA256：dd94b8b2963f099122a3e81d2bc066f18ff158ad9504c70cc2af291ca0360022。
words.json完整SHA256：d5245db0eb33a235fcbb7ea929fe6ba5cd1c3c0a20e150f446ec5d23830d6660。

## 检查能力与冻结

当前默认与制作虚拟环境均未安装faster_whisper/parselmouth，工作区没有发现可用模型权重；HF域名不在本机网络允许列表，未尝试绕过策略下载。未执行逐字ASR、句内字级对齐或全片人工听辨，不声称发音与变调全部验证通过。

words中的内部字符兼容字段明确保存整句时间包络，只有句首测得声学起音。输入、选择、配音和元数据哈希见 input-freeze.json，测量与执行范围见 qa-v1.json。声音侧最终停写后若再修改，须重新建立相关时序与冻结，不用更新清单来认可旧编码。
