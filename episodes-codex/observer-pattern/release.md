# observer-pattern：v0.60.4实际发布

本期修订随PR #253/#254合并并上线，首发身份保持；对应#164已completed关闭。完整批次记录见[本轮发布](../../docs/pattern-flow-ui-java/release.md)。


本轮保留D01的100元会员90/活动80单选和D02的订单17/摘要/变化记录，只调整功能操作→结构职责→原机制协作→Java暂停节选的顺序。每片5句新配、17/19句复用；正文讲语言无关思想。两期媒体SHA、冻结输入、原URL、首发版本、日期和封面保持可追溯。

- 内容PR [#253](https://github.com/linhongcun/video-studio/pull/253)合并8e97948；最终发版PR [#254](https://github.com/linhongcun/video-studio/pull/254)合并bb9b4e9782ed4b7b2d12a8fac9fd478193febfb8。
- [v0.60.4 Release](https://github.com/linhongcun/video-studio/releases/tag/v0.60.4)与附注tag确切指向bb9b4e9782ed4b7b2d12a8fac9fd478193febfb8，整树同最终检查分支10f75487。tag内D014778帧、firstRelease v0.52.0；D025328帧、firstRelease v0.58.0。
- [Release后Pages部署40152819279](https://github.com/linhongcun/video-studio/actions/runs/40152819279)完成成功，工作流head与tag相同。
- 2026-10-25T10:04:31.360708+08:00，首轮13个canonical普通GET全部200；完整视频流/海报SHA与本地一致，22/24句字幕全文/时间、4/5章及锚点、Java图文入口与卡区、源码/课程目录/首页/全部内容/RSS与真实Release链接通过。未加缓存查询，不保存远端媒体。
- #163/#164已再次以completed关闭，#161同步；其余21项待安排。外部平台未新发。

D01视频SHA-256：791a9696b561a8a815167b4e0eb45ed1251bcc3931d5759a5269e2964a808613。

D02视频SHA-256：6a8435f5fe3c51e1e7bd61b8b83af3dd52457f15884ff4074bbb8721f4279a6f。

并行PR #252先撤下Agent试片并占用v0.60.3。合并后整树检查拦截差异，旧tag未动；旧候选46项证据按提交原字节归档，最终站点按新主干重新构建/四浏览器例/18seek验收为36片、4方向。之后仅QA脚本允许未来新Agent课的变更，补跑当前回归、确认整个dist指纹不变，未重做音视频或浏览器检查。见merge-race-rebuild.json、candidates/v0.60.3/archive-path-map.json及postbuild-regression-update.json。

资料、Java实际运行、独立动态与正式MP4、信号和网站检查均按实际范围记录；没有逐字ASR、全片人工听辨、初学者实验或本轮用户观看认可结论。S017/L029/L032/L037已同步实际证据与限制。

## v0.68.4 · MQ实战修订（仅GitHub站点）

[PR #293](https://github.com/linhongcun/video-studio/pull/293)合并到`42d49c743bb48bf41c7c4151e5288ef32b53e8ce`，附注tag v0.68.4准确指向该提交，分支与实际主干整树一致；标签和Release此前未占用，未移动历史标签。保留原slug、createdAt/publishedAt和首发v0.58.0，仅更新内容修改时间和本次时长/描述。

新版10镜20句，正文4182帧加Java150帧，共4332帧/144.4秒；主线改为跨服务RabbitMQ发布订阅、独立队列、处理后确认、离线积压、断连检测后的重投/幂等及一致性边界。真实媒体完整SHA为`f92a0211c6402b661231bacc137a459de4dcf9a4d0b40d9ff905fc53c0de6c33`。173冻结项、原理Java8类运行、20句音轨来源/PCM/起音、独立预检186采样及正式81采样、全解码和−16.0LUFS/−3.8dBTP通过。网站构建与56项静态验收通过。无全片人工听辨/逐字ASR或真实broker集成，不将采样写成逐帧观看。

[Release](https://github.com/linhongcun/video-studio/releases/tag/v0.68.4)创建后，[手动Pages部署40195977106](https://github.com/linhongcun/video-studio/actions/runs/40195977106)成功；发布前自动部署40195898433由本任务取消，以包含实际Release的手动部署取代。北京时间2026-10-25T21:09:17.662178+08:00，9项canonical GET验证视频/海报/VTT完整SHA、20条字幕、5章精确时点、原页面/源码/课程衔接、RSS和真实更新日志。线上视频全文与正式验收文件完全一致。

对应实战修订issue为[#292](https://github.com/linhongcun/video-studio/issues/292)，在上线核验通过后以completed关闭。外部平台未新发；用户尚未反馈新版观看结论。证据见qa-mq-release-identity.json和site-online-verification.json。
