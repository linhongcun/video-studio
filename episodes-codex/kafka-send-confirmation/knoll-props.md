# MQ04 · 制作说明

本期为EP44 / Kafka MQ04 · 发送确认，11镜22句。旁白、分镜计划和事实模型由本期独立文件提供；Remotion读取model.json快照与真实storyboard.json，不沿用MQ03模型、文字或媒体。制作事实以最终源冻结和输出回执为准，本文件不预记尚未执行的质量检查。

三列主体：发送方观察、Kafka实际日志、下游业务。初始日志为空，同事件E01/订单7042贯穿；正常成功、最终超时未知、确定本地未发送三条独立路径在总览建立。06/10明确回共同起点，09保持原@0并由新producer/session追加@1。自动重试维持原批次，不能追加重复卡；确定序列化错误在Future返回前结束，不画出站记录。Future失败与“没有成功证据”的认识边界分开，不把未知写成确定未追加。

源码入口为remotion/src/Main.tsx，字体配色读取共享kafka-covers/style-v1.json。prepare.py、assemble.py转发现行共享句级工具，装配后只适配真实Kafka palette和样例元数据并记录前后SHA；不复制起音/裁尾/TTS算法。依赖来自本期锁文件fresh npm ci，记录在qa/dependency-installation.json。

默认npm render经本期render.py调用参考资料完整流程，正文先由Remotion编码，再由normalize-color.py实际pc601→limitedBT709像素转换与逐帧参数归一化，共享混音后追加同色原题机构资料。references-renderer.py仅在私有命名空间复用共享引擎，不修改历史共享实现。正文、资料与最终音视频的实际流、帧、AAC/PCM与颜色检查分别记录。最终交付是video.mp4，不能用out/body.mp4代替。

三比例封面沿共享Kafka模板，仅新增本题catalog与准确示意图；style-v1不变，旧MQ图形与冻结保持。实际可增长封面输入逐字保存cover-inputs/并映射原路径/SHA，本期冻结本地快照，不依赖未来会增长的共享catalog。所有源停写、来源与真实声画动态预检通过后才正式冻结编码。
