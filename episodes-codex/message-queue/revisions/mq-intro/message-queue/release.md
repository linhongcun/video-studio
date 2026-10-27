# EP.10 MQ系列入门改造：发布记录

已随[v0.79.0](https://github.com/linhongcun/video-studio/releases/tag/v0.79.0)上线：[观看EP.10与配套图文](https://linhongcun.github.io/video-studio/episodes/message-queue/) · [MQ系列目录](https://linhongcun.github.io/video-studio/series/message-queue/)。保留原message-queue、EP.10、创建/首发时间、firstRelease与平台历史链接，新增系列收录，共用同一媒体。

开工基线`16689e572c594224bd779a9b4403964e049cc99c`；编码前同步到`ec5fd0a940d3c7c7beb37989e93f5c8d889a38f7`，保留上游交付记录。[PR #369](https://github.com/linhongcun/video-studio/pull/369)于2026-10-27 16:21:30（北京时间）合并，提交`34b8e306a5665ea08e61aa17c9a0e8e58ab1c87c`；附注tag v0.79.0指向该提交，Release于16:22:21正式发布。

正式视频3700帧／123.333秒，含150帧参考资料卡，6,430,510字节。完整SHA-256：`639d373be2afe007440e31a6877609c2b883bcc7a0af213a535b8caf4783b52e`。原根工程116项冻结保持通过，本revision161项实际输入与最终媒体的核验分别保留。[本轮QA](qa-final.md)与[站点身份保持](site-integration.json)记录具体范围。

[Release后Pages #40473036363](https://github.com/linhongcun/video-studio/actions/runs/40473036363)成功，部署于2026-10-27 16:32:55完成，head与附注tag均为上述合并提交。

- [13项普通canonical GET](online-verification.json)：7项资产完整SHA与6个页面内容通过，截至2026-10-27 16:34:08；视频、海报、VTT及4张图与本地定稿逐字节一致，更新日志含真实v0.79.0。
- [93项线上播放器检查](qa/online/verification.json)：1440/390视口实际播放、四章跳转、图片回看、原文浮层、24条字幕、资料首帧暂停与原生全屏通过。另有844横屏全屏截图；根代理实际查看3张播放器图。
- [36项系列检查](qa/online-series/report.json)：MQ目录仅1期，旧peak入口与原URL保持，学习方向按25个唯一slug统计，桌面/窄屏筛选通过。根代理实际查看目录与窄屏筛选2张图。

线上浏览器首次直接加载因环境代理CA未进入Chromium信任库而失败，保留于[传输记录](qa/online/transport.json)。后续保留canonical origin，由使用已配置CA验证的Python urllib获取远端真实响应，再交给Chromium完成上述实际交互；未关闭TLS验证，不声称浏览器原生TLS信任通过。普通GET完整资产校验独立进行，没有缓存绕过参数。

本片为教学状态与计数示意，未执行真实Broker实验；未进行全片人工听审、逐字ASR、物理手机测试或学习效果测量，不预记用户观看认可。仅GitHub站点交付，无外部平台重发。制作issue为#309，总览#308继续跟踪其余8期规划。

机器可读发布身份、实际部署及报告入口见[publication.json](publication.json)。
