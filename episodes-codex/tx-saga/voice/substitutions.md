# Saga短片：配音与选段

2026-10-24（北京时间），14镜28句。使用共享MiMo冰糖、prep/gen/build/common.cut/onset实现，不变速，不复制整轨算法。全部选择b，原始raw、48kHz单声道PCM16、送模文本、jobs/picks均保留。

## 送模文本

仅将Saga按整词送模为“萨嘎”，字幕和script.md保留Saga。每句按共享prep追加“好。”尾巴，再由共享common.cut移除。其余没有单句文本覆盖；jobs-b.json中28个任务的text均null，读取各句sents.tts。

## 实际检查

28句shared common.cut包络审计无剩余信号警报：没有达到0.5秒的句内低能量间隔、异常短主句或小于0.2秒/大于1.1秒的尾段隔离。逐句送模记录等于sents.tts，所选wav均48kHz单声道。详细信号数据见selected-signal-audit.json；信号风险检查不代表逐字听辨通过。

共享build输出3478帧、5,564,800样本、115.933秒。真实voice SHA256：25eb1fb8de4fb4dcbaf69160ef7dc1a511fd2fff13a106ef25a85432e05342a3。shared whole放置偏移0，public音轨为实体文件且逐字节相同。Saga和补偿均真实句首，严格声学起音0失败、0例外；selfcheck通过句长/镜长/样本/cue检查。

## 能力范围

本批环境没有可用官方medium ASR权重，没有执行逐字ASR、内部词级对齐或全片人工听辨。selfcheck的ASR不一致来自空ASR字段，不是识别通过或发现删字。words中的句内字符仅保存整句包络，只有句首起音实测。

root已另作独立原始raw转换/送模/输入审计，28/28原始音频转48k逐样本一致、剩余警报0，见qa-independent-inputs.json（root单独维护）。
