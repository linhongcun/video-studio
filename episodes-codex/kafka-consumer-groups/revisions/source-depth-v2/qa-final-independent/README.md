# MQ02 实际成片独立复核

执行者为本轮MQ03制作者，复核不同作者的MQ02。已按根实际成片就绪信号执行，机器与实图复核通过：5076帧/169.2秒/7,926,826字节，SHA-256 `43b1115336b22f14e257352690d12bfc65e663bfb3c18c4dc35b8feef9325159`。完整回执与实看文件SHA见 [encoded-independent.json](encoded-independent.json)。72个精确编码帧经9张联系表全部实看，另看4张Figure全PNG、4张根导出JPEG及最后body/首末资料全PNG；不冒称全片听辨。只写本QA目录，不修改生产输入/冻结清单，不重跑配音或长预演。

`sample-spec.json`依据当前冻结Main、board与model准备37个附加整数帧，覆盖分配两次写入、整表同步与逐成员响应、本地安装/Fetch/记录到达、N3空列表、另一组独立计算和四条记录读齐的前后。当前scene12从首帧4072即为points-installed；不用旧预演候选4085的状态推断。共享helper默认另采逐镜中/末、0/2/5/15秒、四个文章图位、正文末与资料首中末。

本次已执行的共享薄入口：

```bash
python3 episodes-codex/kafka-consumer-groups/revisions/source-depth-v2/qa-final-independent/run-audit.py --execute
```

薄入口仅核冻结身份并调用实际共享[final-independent.py](../../../../../docs/archive/2026-10/mq-source-depth-remake/qa/final-independent.py)，显式`--out-dir=qa-final-independent`，没有复制媒体核验算法。共享helper完成实际ffprobe、完整视频与AAC的`-xerror -err_detect explode`解码，并用精确整数`select n`取图；回执绑定实际videoSHA、冻结manifest、Main/voice与资料题名署名，初始`visualReviewed:false`。

本次已实际打开逐镜/邻帧联系表、四张文章全图及资料首末原图，并查看资料中帧，核正文烧录字幕、body最后帧到资料首帧无旧字幕、完整结果晚于最后记录到达、日志保留和组内/组间关系。实看清单、逐项结论与范围已写入报告，`visualReviewed:true`。结果不代替ASR、全片语义听辨、真机或用户理解度研究。文章JPEG的709→601导出与网站播放器交互由根按实际产物另验。
