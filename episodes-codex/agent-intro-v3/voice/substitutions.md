# V3复用说明

本轮只改开场视觉；整条V2混音、voice.wav及全部22句旁白按完整SHA复用，没有发起新TTS或调整语速。以下保留原候选选择记录作为来源，不代表本轮重新生成。

# Agent 入门 V2：配音与候选记录

2026-10-24，agent_video_voice制作。11镜22句，全新MiMo冰糖原速配音，模型mimo-v2.5-tts。旧agent-intro的音频、候选与冻结输入均未复制或修改；新takes开始时为空。

## 原文与送模

逐镜旁白以单个换行连接、末尾无换行的SHA256为3b3fc460fc13e8cd4fbcf555181f1504cba1af7665d2e24a37c35e74700c95f6；完整script SHA256为92b617f3ae2e60066f6fa1646e0b0bf8d2e87cc1169f0dbb0eeb031c16da4f99，均与writer冻结通知一致，记录见script-narration-sha256.json。

没有读音替换或语速变换。共享prep为每句附加“好。”尾巴，字幕和旁白保留脚本原文；共享common.cut剪去尾巴。sents、jobs-a/jobs-b、picks和takes/*.txt.json保留实际输入与候选来源。

## 两个裁尾风险与修复

初轮生成22a。01-hook-2-a尾段仅0.130秒，有裁尾风险；以相同输入补b后，所选主句2.754秒、尾段0.453秒、最长低能量间隔0.30秒。06-choose-ask-2-a尾段仅0.115秒；同输入b所选主句5.023秒、尾段0.531秒、最长低能量间隔0.20秒。风险是信号判断，不等于识别出某字错误。

原a与风险证据保留在candidate-risks-a-partial.json、candidate-risks-a-after-hook-fix.json及takes。最终20a+2b，22/22送模文本、PCM格式及原raw转换一致，0最终信号警报，见selected-take-audit.json。未通过候选没有进入最终铺轨。

## 真实时序与响度

共享build输出4,582,400样本、2,864帧、95.4667秒，48kHz单声道PCM16。设置minShotFrames为null，extraAfter为空，不机械补到7.5秒；lead0.30秒、句内间隔0.35秒、镜间0.70秒、tail0.60秒。未缩放或加速任何声音。

实际完整解码及loudnorm分析输入测得−16.04LUFS、−2.10dBTP，LRA2.10；邻句响度差最大0.4LU，接缝样本跳变最大0.002702，inner_dropouts为空。

开头镜实际0–237帧；01两句speech区间9.00–123.38、133.88–216.50。02两句区间237.50–339.30、349.80–483.27。这些来自真实所选样本，不是均分估计。首2/5/15秒叙事与视觉闸门由root/renderer另作实际视频检查，本声音报告不替代该检查。

## 装配与能力边界

voice agent没有另写words/storyboard或起音算法。root使用episodes-codex/_shared/assemble_sentence_episode.py与唯一共享Rule生成句包络元数据，再执行共享place_v2、严格起音和句级时序检查。public音轨与voice.wav完整SHA一致，集成报告指针保留在qa-v2.json；没有重复运行同一root检查。

当前环境未安装faster_whisper/parselmouth，未发现可用模型；未绕过网络策略下载权重。未执行逐字ASR、句内字级对齐或全片人工听辨，不声称发音、变调全部验证通过。内部字符时间若存在，仅为共享assembler明确标注的句包络。

最终音轨SHA256：ed30552d9eb8886e573589586ea0d64c206569e6717e754917e8f246c9af1718。来源、选择、参数和整轨哈希见input-freeze.json；实际测量见qa-v2.json。声音作者完成后停写，若还需修改音频或旁白，须先通知root，重建相关时序并重新冻结。
