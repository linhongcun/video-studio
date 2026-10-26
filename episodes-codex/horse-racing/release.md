# P01 简短结尾：v0.57.1

用户观看v0.56.4后认为证明画蛇添足、复杂冗长，明确要求证明只留文章，视频不展示也不提。当前删去重复回看及下界证明，直接在七场安排回收后结束，不加新配音或口头引流。

- 当前16镜32句、6章，5618帧，约3分07秒。
- 视频11077352字节，SHA：`d3082f22eb6afec90cd0a6111bc4756d36c7d459a56630a5ab6a4883cc87740e`。
- 157项冻结、32句源PCM保留、前5581帧逐帧解码一致、末37帧静态卡、完整解码/连续PTS及−16.0LUFS/−3.6dBTP检查通过。实际末卡独立8帧查看与根查看通过。
- 文章完整证明和原lower-bound锚点保留，视频不再有对应章节。首发仍为v0.55.0，不移动既有标签。

整合后95页构建、1440/390两视口32字幕/6章/末章与末帧、文章独立证明可读性和14项完整副本SHA均通过；本次合并后发布Release，再触发Pages构建部署，避免重复中间部署。实际PR、标签、部署、线上完整媒体/字幕/章节与issue收尾结果完成后补齐。平台新发不在范围。

v0.55.0与v0.56.4的媒体和检查可通过Git标签与revisions/self-contained-ending追溯；前者主体曾获用户认可，后者证明篇幅已被明确否定，不能继续写成“尚未观看”。

## 实际发布进度

[PR #233](https://github.com/linhongcun/video-studio/pull/233)已合并，附注tag v0.57.1实际指向7d1d6f63b0cfe7ba824aca851c0724b523d5d7e3；已核对该树的版本、5618帧、首发v0.55.0及完整视频SHA。

[Release v0.57.1](https://github.com/linhongcun/video-studio/releases/tag/v0.57.1)发布于北京时间2026-10-25 08:16:38（UTC 00:16:38Z），随后于00:16:41Z手动触发[Pages部署40146065288](https://github.com/linhongcun/video-studio/actions/runs/40146065288)。合并提交跳过中间自动部署，Release后的正式工作流执行完整站点构建与部署。构建于00:19:08Z完成，部署于00:19:28Z成功，实际运行记录在short-ending/deployment.json。

北京时间2026-10-25 08:21:11，首轮10个canonical普通GET全部通过：完整视频11077352字节与d3082f22…3cc87740e完整SHA、海报完整SHA、32句VTT逐字节、6章的精确帧/秒及锚点、无证明视频章或旁白入口、文章原proof锚点与正文、源码/系列/学习目录/RSS，以及v0.57.1实际修正条目。全量媒体只流式计算SHA，未保存远程媒体、未加查询/Range/强制缓存头，也未盲目重试。完整证据见online-verification.json及本修订同字节副本。

#205已在上述检查后以completed再次关闭，#204同步3分07秒与v0.57.1；其余九题仍待安排。此次只上本站，平台未新发。本轮短版尚无用户观看反馈。

<!-- batch-11-publication-archive:start -->
## 存量片尾参考资料第十一批 · v0.77.1

[PR #365](https://github.com/linhongcun/video-studio/pull/365)已合并，发布[v0.77.1](https://github.com/linhongcun/video-studio/releases/tag/v0.77.1)，[Pages 40345988177](https://github.com/linhongcun/video-studio/actions/runs/40345988177)成功；合并提交`51350cdd8a415363269cb4c64ff73bdf73f19e99`。2026-10-26T23:13:23+08:00完成17项规范URL完整GET和5次公开GitHub身份读取，四片完整MP4 SHA、海报、全文字幕、资料页、原章节/日期、更新日志与tag/Release/Pages身份一致。原存量累计42/47，当前站点含新增Redis为43/48有附录，分别记数。实际响应见online-verification.json。

本期1项、1页，每页150帧5秒，原body5618帧→最终5768帧，完整SHA256 `a4837cc8760b8087ea38744092cf4cd6c66c29c744ef4d0ede56f0e33c31bdf0`。原制作MP4与Git原片完整SHA相同。本期没有代码卡，原全部收尾/声画、数学源、原文章/研究/脚注与首发日期保持。

各项实际阅读日期：R1 Problem #055 – horse racing：2026-10-25。六项资料均保留25日实际技术阅读；26日赛马补官网固定原题/明确作者，过桥补README题名并复用OEIS身份记录，量水核相同固定Doocs第三方镜像和组织名，三门只复核旧完整阅读记录、无新GET。未把元数据核验改写成新技术读，未引用未读论文或官方原站。

当前675项输入与原606项均已实核，0缺件；末字幕仅按实际derived报告处理，源分镜/words保持。原选题议题早已关闭，未重关。完整证据留docs/reference-endcards/batch-11/，不迁移冻结材料。
<!-- batch-11-publication-archive:end -->
