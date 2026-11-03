# P07 · GitHub交付记录

当前状态：制作、GitHub发布与线上核验均已完成；#211已以completed关闭，#204已同步完成6/10。

- 基线：89fb1705a6f51c934a720d825a26e2593c4a1836；冻结工程提交c3a8102fd7ee2aa441c411901da82afa49e660a6。
- EP53／趣味推理P07／birthday-paradox；首发站点版本v0.101.0，首次制作，不重发平台。
- 11镜22句四章，正文3681帧＋150帧资料，共3831帧／127.7秒；最终MP4 6,330,401字节，完整SHA-256 `40369e384d53c916b6c9f6f3ef46537026f6e0993d62b472581e89afeecbb609`。
- 151项输入冻结manifestSHA `78f9aa6e060943e7bce32bf82932c490c0a5642d77c202e68b614171eca5ccbf`；来源预检、声轨/句级时序、独立动态与43个正式媒体点、完整解码/附录保真通过，见qa-final.md及qa/。
- 图文两幅最终片截图在70秒和107秒；两源原文引用、三比例封面、四章与22cue完整。两次必要站点build通过；首轮默认原生字幕问题仅补metadata后，双视口50项动作/18次严格PTS复验通过，输入保真记录与失败均保留。
- 新增变更按原规则秘密扫描无旗标；原全仓282项既有旗标保持如实FAIL，与本期无交集且字节未变，见qa/secret-scan-review.json及secret-scan-final.json。

范围：Chromium桌面/触屏模拟及Fullscreen API，非物理手机；连续预演通过解码序列审查，未声称全片实时观看、逐字ASR、全片人工语义听辨或学习效果评估。初始海报loading弧与手机内嵌资料小字的实际限制保留；横屏Fullscreen资料列表清楚且不被控件遮挡。尚无用户观看本期结论。

## 实际发布与收尾

[PR461](https://github.com/linhongcun/video-studio/pull/461)于2026-11-03T06:54:23Z合并d48fdbd4546d91b05458c60748475dfce69e27f0；附注tag对象10e646a24728591fd62a8bb2900bf5565183c72f精确指向该提交。[Release v0.101.0](https://github.com/linhongcun/video-studio/releases/tag/v0.101.0)于06:57:35Z发布，之后06:57:38Z触发的[Pages41593158486](https://github.com/linhongcun/video-studio/actions/runs/41593158486)于07:06:01Z成功。

线上原生HTTPS浏览器50项动作／18次严格PTS通过（07:04:50–07:05:19Z，发生于首轮同SHA部署成功后、Release后dispatch构建期间，未改写成后续执行）；发布后整套10个普通canonical GET核对完整媒体、海报、两图、22句VTT、四章、系列／资料库／RSS和真实Release链接通过。源码链接按当前站点固定到部署SHA，资料首帧的原生字幕结束点为122.699秒；三处旧审计假设已只在QA工具内纠正，诊断与原失败保留，生产输入、媒体和站点均未因此变更。实际时刻、完整SHA和检查结果见publication.json、online-verification.json及qa/site-online-native/。

#211于2026-11-03T07:21:16Z以completed关闭；总览#204为6/10完成，P06及P08—P10仍未开工。仅本站交付，无外部平台新发，未预记本期用户观看认可。
