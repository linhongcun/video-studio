# 送模文本与字幕映射

本轮只将送模文本中的Kafka替换为“卡夫卡”；script.md、字幕及words中的原文仍保留Kafka。由共享prep.py按voice/params.json的subst生成，实际涉及02-roles-2、04-accepted-1、11-buffer-2、12-recap-2。辅助尾句“好。”由共享流程用于裁尾，不进入字幕。

现有RabbitMQ入门只复用与新稿逐字相同且送模文本一致的01-submit-1、01-submit-2选定a take；没有复用旧ACK、排空、取走等句子。完整声音与文件SHA、生成/复用身份见input-provenance.json。保留声源是原take字节保持，重新build整轨不表示整轨或裁后句段与旧片完全相同。

本记录不宣称逐字ASR、真机听辨或全片人工语义听审已完成。句级声学/裁尾检查及实际完成范围另见voice QA。

02-roles-2保留a候选：共享裁尾测得辅助尾仅0.054秒，分离证据不足；改选同文b（辅助尾0.4555秒），未改正文或放宽裁尾算法。这是声学异常筛选，不等同逐字听辨已确认a语义错误。
