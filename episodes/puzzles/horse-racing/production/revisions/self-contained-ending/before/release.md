# P01 发布记录

首发版本：[v0.55.0](https://github.com/linhongcun/video-studio/releases/tag/v0.55.0)。内部EP.24／趣味推理P01；[观看视频与配套图文](https://linhongcun.github.io/video-studio/episodes/horse-racing/)。

本地正式制作、独立成片与站点检查已完成，见qa-final.md。视频6327帧／210.901秒，完整SHA为`d643c1d75a23568e5aed6f25115bdab033e5e4317285e36f4cdc933694e2f59f`；站点副本与制作文件逐字节相同。

## 实际发布与核验

- [PR #218](https://github.com/linhongcun/video-studio/pull/218)已squash合并，交付提交为`3a3a16971aaeb7d69de1eb2d295176f5c80802e0`。v0.55.0是指向该提交的附注tag；Release ID422870621，发布于2026-10-24T17:15:46Z（北京时间2026-10-25 01:15:46）。
- Release后手动部署40115317894已取消；之后包含本片的主干部署[40115332761](https://github.com/linhongcun/video-studio/actions/runs/40115332761)成功，部署提交`5a41a16ebaadb8339e4bc592edf325a407e74295`，build于17:17:41Z、deploy于17:18:00Z完成。后续协作主干还加入了其他课程；首发tag与实际部署提交分开记录，没有移动tag或覆盖其他课程。
- 北京时间2026-10-25 01:20:43首轮10个canonical普通GET全200。视频12,834,952字节，完整SHA与上文相同；海报完整SHA为`15b9ef219d7f3d861d44fa6fc2bab83a0cbe850ebf01dab88955b8bfdc5b9cee`。
- 36句VTT与本地验收稿逐字节相等；6章frame/fps、正文锚点/seek、源码、P01唯一系列目录、首页puzzles入口、系列/学习目录/RSS及真实v0.55.0更新日志条目全部通过。
- 原始证据为[online-verification.json](online-verification.json)，站点目录保留相同字节副本。执行器[verify_online.py](verify_online.py)使用正常代理和CA信任，不加query、Range或强制缓存头，不保存远程媒体，无盲重试。P01首发版本与部署时站点总版本分别核验。
- [制作issue #205](https://github.com/linhongcun/video-studio/issues/205)已在完整线上核验后以completed关闭；[系列总览 #204](https://github.com/linhongcun/video-studio/issues/204)同步P01完成，其余9题待后续安排。

实际混音−16.0LUFS、−3.7dBTP；160项冻结输入在编码前后和同步主干后保持一致。本地数学、文稿、真实动态、正式成片与桌面/手机检查见[qa-final.md](qa-final.md)。未执行逐字ASR、全片人工听辨或初学者实验，不将检查写成用户已观看认可。本次仅发布GitHub站点，其他平台不在本次范围。

本记录与线上证据作为交付后的事实补记提交，不改已冻结媒体或首发tag。
