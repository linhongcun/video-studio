# 分布式事务入门：配音与选段

2026-10-24，20镜40句。共享MiMo冰糖，沿用仓内prep/gen/build、裁切与起音实现；不变速、不压时长。

## 送模文本

本期无英文缩写和ID口播，无术语读音替换。字幕与旁白保留script.md原文；prep仅在每句末尾附加“好。”尾巴，由共享common.cut移除。原始送模文本保存在takes/*.txt.json和jobs-b.json/jobs-c.json。

## 候选选择与信号风险

初轮40句b全部生成。独立审计发现11-not-machine-count-2、19-business-boundaries-2的末尾隔离片段仅约0.121/0.107秒，存在裁尾位置风险。它们是信号异常，不能据此断言读错了哪一个字。两句以相同送模文本生成c候选后风险消除，最终picks为38b+2c，无单句文字覆盖。候选、picks和jobs保留；初轮风险见candidate-risks-b.json。

独立代理逐句核对40句script/sents/jobs/picks一致、48kHz单声道PCM16、原始raw转换到48k后逐样本一致40/40。最终所选主句2.52–5.30秒，尾段0.305–0.730秒，主句最长低能量间隔0.40秒，无剩余信号警报。详细数据见selected-take-audit.json与qa-v1.json。

## 铺轨与真实时序

共享build实际输出8,248,000样本、5,155帧、171.833秒；整轨−16.0LUFS、测得真峰−2.1dBTP。邻句响度差最大0.5LU，接缝样本跳变最大0.002306，inner_dropouts为空。为达到共享最短镜长，仅06/08镜额外停留0.4333/0.1秒；lead0.30秒和tail1.5秒都已含在总帧数内。

root提供的assemble.py依据build的真实句级边界、共享声学Rule实测句首起音，生成words/storyboard/captions。共享place_v2 whole校验maxOffsetFrames=0，public音轨与voice.wav逐字节相同。严格起音检查三个首现术语0失败、0例外；selfcheck通过长度、最短镜长与cue检查。selfcheck日志中的ASR不一致来自空ASR字段，不是识别通过或识别出删字。

## 检查能力

本环境官方faster-whisper medium缓存不可用，local_files_only加载返回LocalEntryNotFoundError。未绕过网络策略下载权重。未执行逐字ASR、句内字级对齐或全片人工听辨；句内字符兼容字段仅保存整句时间包络，不是逐字时刻。只将句首实测起音用于三个术语标签。
