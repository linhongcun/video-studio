# P02四人过桥：v0.60.0已交付

已完成制作、合并、Release、Pages部署与线上完整核验。本期仅发布GitHub站点，未向外部平台投稿。

[观看视频与文章](https://linhongcun.github.io/video-studio/episodes/bridge-torch/)。内部EP29／趣味推理P02，16镜32句、4章，6025帧／30fps，200.8333秒，约3分21秒；1920×1080／H264／AAC48kHz，−16.0LUFS／−3.9dBTP。

## 发布身份

- [制作PR #243](https://github.com/linhongcun/video-studio/pull/243)已合并，生产合并提交为`057b9d0d293ff58f410129860b71b742340e5dd1`。
- [v0.60.0附注tag与Release](https://github.com/linhongcun/video-studio/releases/tag/v0.60.0)准确指向该提交，tag包含本期媒体、元数据及site版本0.60.0；Release id423079744，UTC2026-10-25 01:15:46发布。
- [Release后Pages部署40149965870](https://github.com/linhongcun/video-studio/actions/runs/40149965870)成功，head同上，build于01:16:11—01:18:59、deploy于01:19:03—01:19:17 UTC执行。生产合并用[skip ci]略过重复的Release前push部署；上述手动工作流完整执行npm ci、构建、上传和Pages发布。
- 发布前保留同期观察者、A02、MySQL身份优化与新观看反馈；实际版本顺延与冻结输入无交集记录见upstream-before-release.json。既有标签均未移动。

## 线上结果

北京时间`2026-10-25T09:20:03.991836+08:00`，首轮10个普通canonical GET全部通过：完整视频/海报SHA与字节、32句VTT逐字节、四章起点0/1259/2218/4282精确frame/fps、正文锚点及证明无视频seek、源码、P01/P02独立目录、首页/学习系列/RSS与真实v0.60.0新增日志一致。部署版本同为v0.60.0；没有cache-bust、Range、强制缓存或重试，未保存远端媒体。

- 视频10,730,649字节，完整SHA256：`c657f2928477a896a2d54faa1087fd9ad40517d37a2df7c99aa6563094fe38f4`。
- 海报120,389字节，完整SHA256：`9cfdf6e607ebd3a4e32faf480f470379e18faf19ef5d6d88dc0acc5dcb00757d`。
- [制作issue #206](https://github.com/linhongcun/video-studio/issues/206)已在核验后以completed关闭；[总览#204](https://github.com/linhongcun/video-studio/issues/204)同步为已完成2题，其余8题待后续安排。

本地数学、真实动态、配音、154源冻结、实际成片与两视口范围见qa-final.md；线上、部署与收尾原始数据为online-verification.json、deployment.json及issue-completion.json。没有逐字ASR、全片人工听辨、完整实时观看或初学者实验，也不预写用户已观看认可本片。
