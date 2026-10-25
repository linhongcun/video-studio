# P04三门问题：v0.64.0已交付

[观看视频与文章](https://linhongcun.github.io/video-studio/episodes/monty-hall/)。内部EP32／趣味推理P04，14镜28句、四章、5507帧／30fps，画面时长183.5667秒，约3分04秒。先完整走一局，再穷尽三个等权初始奖位，回收始终保留1/3、始终换门2/3。条件概率细算与规则变体只留文章，视频无额外证明尾段或文章口头入口。本期仅发布GitHub站点。

## 发布身份

- [制作PR #267](https://github.com/linhongcun/video-studio/pull/267)合并提交`e73ffa53fb639cbf9540fab50cae4a45c89c407a`。
- [v0.64.0附注tag及Release](https://github.com/linhongcun/video-studio/releases/tag/v0.64.0)精确指向该提交；tag对象`8989644e29e3d07e4ce436e55267a4f442ca4238`，Release id423139804，UTC2026-10-25T04:08:38Z发布。已有tag未移动。
- [Release后Pages40160813696](https://github.com/linhongcun/video-studio/actions/runs/40160813696)成功，head同上。build 2026-10-25T04:08:55Z—2026-10-25T04:12:11Z；deploy 2026-10-25T04:12:14Z—2026-10-25T04:12:28Z。生产合并[skip ci]省略Release前重复部署，随后手动工作流完整安装、构建、上传与部署。
- 原规划EP31/v0.62.0被并行Skills先占，适配器后发v0.63.0；EP32已由PR #265预留。本期保留两者及LC70场景修订，不恢复退役Agent课程。原31候选与142输入记录原样隔离，原声音生成来源保持，按新EP32的165项清单完整重编码，没有将旧片重新标号。详见identity-revision/README.md及qa-final.md。

## 线上核验

北京时间`2026-10-25T12:13:00.607403+08:00`，首轮9个普通站点canonical GET全部通过：完整视频/海报SHA与字节、28句VTT逐字节、四章0/777/1898/4288帧定位、正文锚点/源码、独立四课目录、首页/系列/学习/RSS及实际v0.64.0新增日志一致。另1份真实Release通过GitHub connector独立读取，保留原响应和来源；报告分别记9次站点GET与1份connector证据，没有冒充10次本地HTTP GET。本次原生git/gh也正常，无身份或代理改写。

- 视频9,781,453字节，SHA256：`6bd1a2ddef82d584a5736d689c82d8564a2f7697c129ddee48c095614563d932`。
- 海报119,256字节，SHA256：`589700d61cb6fef7c62002d4f6a67f3e62a2d2a3cd021b60848bd9ba73a0e4b5`。
- VTT2,967字节，SHA256：`5da4cd890dc27912dbb33d9b4f051769c6e9209dcf2f9dccca214b5aacc4c3b9`。

核验无cache-bust、Range、强制缓存或站点重试，未保存远端媒体，见online-verification.json、release-connector.json、release-tag.json和deployment.json。[制作issue #208](https://github.com/linhongcun/video-studio/issues/208)已在核验后以completed关闭；[总览#204](https://github.com/linhongcun/video-studio/issues/204)同步完成4题、剩余6题待安排，见issue-completion.json。

## 检查范围

数学与主推理、原始预审的身份等价复用、新正式编码/5507连续PTS/88点同尺寸保真、独立52时点成片与根37时点、全轨/28句音源、14项发布副本以及1440/390站点播放阅读的实际范围见qa-final.md。165冻结输入在正式编码、媒体检查和合并后复验保持。

未执行ASR、发音/语义听辨、全片连续实时观看或初学者实验。P04尚无用户观看反馈；信号、模型与抽样检查不扩写为完整人工审听或学习效果。未执行外部平台投稿。
