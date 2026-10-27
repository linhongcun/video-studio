# MQ独立学习方向（2026-10-27）

用户明确将MQ作为独立系列，不再归入系统原理，并计划后续采用独立封面风格。此前v0.79.0的peak主系列加MQ额外收录仅作为历史方案保留。

本轮从最新主干`b50f6ae9add8d0dcfc0a960f208ece3b4f8c7ce9`建立分支，保留同期LeetCode统一封面更新。EP.10的主系列迁为`message-queue`，去掉额外收录字段；系统原理移除MQ，首页、学习页、内容库和视频课程目录均使用独立MQ方向。MQ不继承系统原理的前后课；系统链由缓存一致性直接进入限流。相同名称的学习方向与系列不在面包屑重复显示。

已随[v0.80.0](https://github.com/linhongcun/video-studio/releases/tag/v0.80.0)上线。此轮只调整站点分类与导航，视频、图文、封面及161项生产冻结输入保持；EP.10、原slug、创建/修改/首发时间、首发Release和外平台历史链接不变。后续MQ封面视觉体系独立，具体样式尚未确定；未新制封面，不预记视觉稿已获认可。

本地核验：

- 完整站点构建见[build.log.gz](build.log.gz)；当前学习路径与产物检查见[learning-path.log](learning-path.log)，MQ独立归属与无系统前后课断言通过。
- [基线](baseline.json)与[保留检查](preservation.json)记录26份本期既有发布文件逐字节保持，元数据仅改变主系列和去除额外收录字段。
- `--built`检查最初暴露归档事务视频的旧无附录SHA预期；基线、现行源与构建媒体均为同一e7c5a594…，改为验证构建媒体与当前发布源一致，修后通过，未改归档媒体。
- [126项独立浏览器检查](qa-local/report.json)通过：1440/390视口的首页、学习方向、目录、系统链与内容库联动筛选，以及11片既有LeetCode缩略图解码。根代理实际查看MQ窄屏方向、桌面MQ筛选和EP.10窄屏课程目录3张图。QA脚本调试的两次断言误用独立保留，不改站点以迎合检查。

实际发布与线上核验已完成，身份与证据见下方。只上站点，不重发平台，其余8期MQ规划未开工。上一轮媒体交付证据仍在[原发布记录](../../episodes-codex/message-queue/revisions/mq-intro/message-queue/release.md)，不覆写历史核验。

## 实际上线

[PR #375](https://github.com/linhongcun/video-studio/pull/375)合并为`9c2bf61e8bfa25561006ec8ed4848f6b80c085dd`；附注tag v0.80.0指向该提交，Release正式发布后执行[Pages #40512522108](https://github.com/linhongcun/video-studio/actions/runs/40512522108)，实际成功。

[14项普通canonical GET](online-verification.json)通过：视频、海报、VTT与4张图完整SHA一致，7个页面含准确版本和分类，更新日志含真实Release。[126项线上浏览器检查](qa-online/report.json)与本地同范围通过，MQ独立1篇、系统24篇、peak4篇，全站48个唯一条目；既有LeetCode的11张缩略图正常。根代理实际查看线上MQ窄屏目录与桌面筛选2张图，独立复核范围以线上报告为准。

浏览器保留canonical origin，远端响应通过已配置CA验证的urllib传输后执行真实交互；未关闭TLS验证，不声称Chromium原生CA信任通过。此轮未重复MP4播放、原文浮层或全片听审；完整媒体SHA独立核验，不将分类检查扩大为媒体重审。完整发布输入、范围与机器可读身份见[publication.json](publication.json)。

线上普通GET首轮唯一失败来自QA预期：更新日志页面展示Release正文而非原始标题，原断言查找仅在标题中的短语。实际v0.80.0链接和独立MQ正文当时已存在；改为核对真实Release链接与正文后14项通过，未改站点。首轮与所有普通GET尝试保留于[首轮报告](online-first-verification.json)和[请求记录](online-attempts.json)。
