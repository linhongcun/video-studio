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
