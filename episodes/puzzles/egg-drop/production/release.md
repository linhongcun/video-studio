# P05两枚鸡蛋：开头修订与首发交付记录

## 当前开头修订：v0.70.2已上线并核验

用户看完首发后指出：自然想到二分法，却看不出开头各次尝试的目的；随后明确要求开头说明区别。本轮只替换03／04四句：先看50、25两次都碎后，零枚蛋而最高安全层仍可能是0…24，说明一直对半不能保证完成；再先交代第一枚圈范围、最后一枚逐层收尾的目的，接入固定十层晚碎的最坏十九次。其余二十句及主体保留，完整最优性证明仍留文章，不加证明口播或文章引流。尚无用户观看新版后的结论。

正文12镜24句、5569帧／30fps，185.6333秒。169项正文冻结输入、4336局部源帧精确复用、实际DOM／动态小样、新正式正文199点同网格及独立50时点、全轨24句双声道来源检查均已通过。正文视频10,034,214字节，SHA-256 `b43510f3196f92964d21a3b854941a65f4af33fffd2484c171ca518f9f747c66`；原二十句PCM／WAV保持，四句新声音替换使正文增加312帧。见[当前检查及能力边界](qa-final.md)。

旧v0.68.3／v0.68.4本地正文候选和其网站证据保留，未作为本轮公开发布。随后已整合主干b83a0b04／站点v0.69.1的最新参考资料流程：同slug换片也必须带实际静态参考卡，不能按旧视频SHA豁免。静态卡不承担证明，不增加新旁白。

已完成一页150帧静态来源卡：完整视频5719帧／190.6333秒、10,085,034字节，SHA-256 `94672a7375b77d0fa16234031056bc34df2c48ae61536b6ef4708acbfd04fa69`。原正文全部5569解码帧／PTS及8703 AAC包／PCM精确保持。原169正文、追加前13输入和当前185默认入口清单分阶段追溯；严格共享默认verify、资料卡独立7帧／4原图及根首卡实看通过。实际修订完成时间为2026-10-25T15:03:20.153406+00:00，metadata按毫秒记录。

v0.70.1完整站点构建126页、共享门槛及1440／390在当前CSS下的新实际播放、24字幕／四章、资料卡暂停／原生全屏／无字幕残留检查通过。最后v0.70.2整合每日温度后再次完整构建126页，完整P05 HTML仅页脚版本不同、17件/VTT/JS/CSS精确相同，因此明确复用v0.70.1的真实完整双视口检查，没有宣称再跑；本轮其他修订版本仅为本地候选。firstRelease v0.67.0与创建／首次公开日保留；本轮未执行外部平台投稿。

[修订PR #334](https://github.com/linhongcun/video-studio/pull/334)已合并为 `e836ab1b49bf285bb636b5c1d44f90e99bf9fc99`。[v0.70.2附注tag及Release](https://github.com/linhongcun/video-studio/releases/tag/v0.70.2)指向该提交，tag对象 `b0e54e1ff8ef1a7f7fe2fb1b520a7391685dcd03`，Release id423489425，于2026-10-25T15:33:30Z公开。[Pages40207511206](https://github.com/linhongcun/video-studio/actions/runs/40207511206)于15:33:33Z在同一head触发，已成功，build至15:37:26Z，deploy为15:37:30Z—15:37:47Z；随后线上完整资源核验与issue收尾通过。详见[当前QA](qa-final.md)、[tag身份](revisions/binary-opening/release-tag.json)与[实际Release响应](revisions/binary-opening/release-connector.json)。

北京时间2026-10-25T23:39:38.816097+08:00，首轮9次普通canonical站点GET及1份独立GitHub Release证据核验通过：完整视频／海报SHA与字节、24条VTT逐字节、原四章0／1288／1988／3755、来源链接、普通证明锚点、目录／首页／学习／系列／RSS及真实v0.70.2更新日志一致。最终视频10,085,034字节，SHA-256 `94672a7375b77d0fa16234031056bc34df2c48ae61536b6ef4708acbfd04fa69`；字幕2,872字节，SHA-256 `ffa00f50a975b7d2ee3f0f12ad2cd0f82911a3fa9af2c6e687df33a9cbc0cd36`。没有cache-bust、Range、强制缓存或站点重试，没有保存远端媒体。

核验后#209已以completed关闭，#204同步P05当前v0.70.2、完成5题／余5题。首发v0.67.0、原标题／URL及创建／首次公开日保持；updatedAt为实际附录完成时间2026-10-25T15:03:20.153+00:00。未执行外部平台新发，尚无新版用户观看结论。见[本轮线上报告](revisions/binary-opening/online-verification.json)与[issue收尾](revisions/binary-opening/issue-completion.json)。

## 首发v0.67.0历史交付

[观看视频与文章](https://linhongcun.github.io/video-studio/episodes/egg-drop/)。内部EP33／趣味推理P05，12镜24句、四章、5257帧／30fps，画面时长175.2333秒，约2分55秒。由固定10层晚碎的19次引出剩余预算，构造14、27、39等递减间隔并在100层封顶，完整F31实例用8次确定最高安全31层。实际8次与保证最多14次分开；严格最优性与完整边界只留文章，视频简短结束，无证明尾段或文章口头转介。本期只发布GitHub站点。

## 发布身份

- [制作PR #279](https://github.com/linhongcun/video-studio/pull/279)合并提交`549ac45b53e078547fe53ef2c7f8677f0a918db5`。
- [v0.67.0附注tag及Release](https://github.com/linhongcun/video-studio/releases/tag/v0.67.0)精确指向该提交；tag对象`0522b4e316963c33b2363e643fcb8fc71b41708d`，Release id423291635，UTC2026-10-25T09:32:49Z发布。没有移动既有tag。
- [Release后Pages40181102180](https://github.com/linhongcun/video-studio/actions/runs/40181102180)成功，head同上。build 09:33:00Z—09:35:01Z，deploy 09:35:04Z—09:35:35Z，均晚于Release发布。生产合并带[skip ci]，随后手动工作流完成安装、构建、上传与部署。
- EP33已由PR #270预留。编码前整合37e096c2／v0.64.1，发布前发现LC200已先发v0.66.0，完整整合2da29e20和后续仅文档的3b6b2020，保留全部并行课程与退役Agent删除。旧未发布v0.65.0本地候选、截图、原日志、关键HTML及报告原样归档`qa-site-candidates/v0.65.0-4aa95321`，首发元数据顺延v0.67.0后重新构建、回归和双视口验站点。133项冻结输入与同一视频完整SHA保持，没有重配音或重编码；版本在发布元数据，不是片内身份变更。详见upstream-before-release.json及qa-final.md。

## 线上核验

北京时间`2026-10-25T17:36:27.059304+08:00`，首轮9次普通站点canonical GET全部通过：完整视频／海报SHA与字节、24句VTT逐字节、四章0/755/1676/3443帧定位、正文普通锚点／源码、独立五课目录、首页／系列／学习／RSS及实际v0.67.0新增日志一致。另1份真实Release由GitHub connector独立读取，保留原响应与来源；报告分别记9次站点GET和1份connector证据，没有冒充10次本地HTTP GET。

- 视频9,546,440字节，SHA256：`f5876353b2d2f4b8f6709e59a6091edfd2ab1ae5303e239751e1b9eca42b9179`。
- 海报141,760字节，SHA256：`52a090fddae73acf16ee1523f90e190c840b54e91896649634dfe84aaad79bb6`。
- VTT2,737字节，SHA256：`fe9af436254cff99d6d412662d1429bfca64b429bd3536fd670ddbd8a45430cf`。

核验无cache-bust、Range、强制缓存或站点重试，未保存远端媒体。见[线上报告](online-verification.json)、[真实Release](release-connector.json)、[附注tag](release-tag.json)和[部署证据](deployment.json)。核验后，[制作issue #209](https://github.com/linhongcun/video-studio/issues/209)已以completed关闭；[总览#204](https://github.com/linhongcun/video-studio/issues/204)同步完成5题、剩余5题待安排，见[issue收尾](issue-completion.json)。

## 检查范围

两路线各101阈值与独立107规模DP、五稿双审、原声完整shared build字节复现、5257帧源树、487点实际DOM、无字幕独立137阶段、6封面、正式视频全解码／连续PTS／147点同网格保真、独立实际MP4 52点和root原尺寸5图、全轨与24句音源，以及1440/390站点播放阅读的实际范围见[成片检查](qa-final.md)。原失败、修复和各次证据保留；133冻结输入在正式编码、媒体检查和最终合并后复验保持。

未执行ASR、发音／语义听辨、完整人工审听、全片连续实时观看或初学者实验。来源、模型、DOM和抽样检查不扩写为这些未做检查或学习效果。发布时P05尚无用户观看反馈，后续实际反馈见下节；P04认可不迁移为本片认可；本期未执行外部平台投稿。

## 用户观看反馈

用户随后实际观看v0.67.0，表示自然想到二分法，而视频开始的一连串尝试没有先解释目的，因此看着懵。对照首发稿，03直接提出每隔10层、06直接给14次预算，二分法的资源限制和预算来源没有前置。这是方法动机与观看理解方面的负面反馈，不能继续记为未观看或制作获得认可。最初先解释原理并记录诊断，随后用户明确要求改视频开头，现已执行上节所述03／04修订。首发技术检查保持原范围；修订正文通过不等于用户已经认可新版讲解，详见[反馈记录](feedback.md)。

## v0.70.3 · 原始题名与原文摘录

参考资料卡改为实际原题、逐字原文短引和位置，原讲解/声音/代码卡保持；当前发布5719帧，完整SHA-256：`d88cb96faeeb0170a24366f0a6509f2bc0e693ae0a1f66058a30151e8652e4a5`。[PR #338](https://github.com/linhongcun/video-studio/pull/338)、[Release](https://github.com/linhongcun/video-studio/releases/tag/v0.70.3)与[Release后Pages](https://github.com/linhongcun/video-studio/actions/runs/40210425589)已完成，41次canonical GET覆盖本片完整视频/海报SHA、VTT、原章节/日期/引用和更新日志通过。实际来源、媒体保真与播放器范围见[本批记录](../../docs/reference-endcards/original-titles/README.md)。仅GitHub站点，无平台重发；不表示用户已观看认可。

## v0.71.2 · 题名与署名简表

资料片尾统一只显示完整原始题名和作者/机构，一页5秒；原引文/定位等保留文章研究，正文、声音、代码卡不变。当前5719帧，完整SHA-256：`63a234100265096b88ba69fd49bf65d91463cc53f9109b9c6763c2fb31d75247`。[PR #345](https://github.com/linhongcun/video-studio/pull/345)、[Release](https://github.com/linhongcun/video-studio/releases/tag/v0.71.2)与[Release后Pages](https://github.com/linhongcun/video-studio/actions/runs/40284847950)完成，69次canonical完整GET覆盖本片媒体/海报SHA、字幕、章节/日期、引用及更新日志通过。实际检查与限制见仓库docs/reference-endcards/title-author。仅GitHub站点，无平台重发或本版观看认可。
