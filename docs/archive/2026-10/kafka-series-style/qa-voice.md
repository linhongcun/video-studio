# Kafka MQ01：配音与装配检查

日期：2026-10-28（北京时间）。范围：当前新revision的24句选定take、共享构建与真实句时装配。尚未冻结或正式编码，未重写旁白。

最终选段：2句精确复用旧mq-intro的01-submit-1/2 a take，其余22句新配；共23个新take生成任务，其中02-roles-2-a保留为未选候选，最终选b。实际HTTP尝试次数未单独记录，不把任务数写成精确网络请求次数。完整来源、送模文本、文件完整SHA与选段身份见voice/input-provenance.json。

- 已逐项复核24条provenance与voice/sents、picks、实际选中wav/raw.wav/txt.json；复用6文件逐字节匹配原来源和旧冻结SHA，新选66文件SHA相符。新稿只有这2句与旧文本和送模文本同时一致；旧RabbitMQ ACK、取走和排空等句未复用。
- Kafka仅在送模文本替换为“卡夫卡”，字幕与script原文不变。01复用取原选段，其他使用共享voice/gen.py、默认冰糖；无变速。替换与未选候选依据见voice/substitutions.md。
- 02-roles-2-a的共享cut辅助尾测得0.054秒，分离证据不足；保留该候选后用同文b重取，辅助尾0.4555秒。算法与阈值未修改。这是声学筛查，不声称ASR/人工听辨已经证明a漏字或b语义全部正确。
- 24份选中wav均为PCM16、48kHz单声道，保存的送模文本逐字相符。共享build形成5915200样本、3697帧、123.233秒正文；整轨SHA为279e539a9d6d13e45861b303f211529b55252f32faf29722be022f42a0c4ef0d。重建整轨不宣称旧整轨或裁后句段完全相同。
- build报告为−16.0LUFS，内部truepeak日志−2.2dBTP；相邻响度差最大0.5LUFS，拼接窗口样本跳变最大0.0051214，无超过0.5秒的inner dropout。正式混音与最终编码还需另测，不用这些值代替成片结果。
- 新12镜、24句、4章、真实句窗/连续字幕/整轨铺放/样本数检查通过。2个声学cue窗口通过：Kafka diff−2.53帧、消费位点diff−0.83帧；0失败、0例外。仅整句边界和句首起音，不提供内部逐字时间。
- 各镜自然长度8.7–12.467秒，extraAfter为空，没有为压缩时间而加速，也没有在冻结前静默重新装配。实际动作按当前句窗预检，若需额外可读停留，先记录原因并经制作协调后重装配与复验。

真实动画handoff为/workspace/work/kafka-production/timing-handoff.json；相应storyboard/words及实体remotion/public/audio/voice.wav已交动画代理。命令原日志、选take/裁尾筛查、provenance重验和阶段摘要在/workspace/work/kafka-production/voice-logs/。

能力边界：未执行逐字ASR、全片人工语义听审或真机测试。保存输入文本、声学筛查、自然句时与字幕一致性检查，不能冒充听懂每个实际词。正式媒体和播放器检查另作记录。
