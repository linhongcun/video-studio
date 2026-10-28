# 分布式独立系列（2026-10-28）

状态：v0.86.0本地构建与分类检查通过，PR与站点发布待完成。

本轮按用户要求，将系统原理中的分布式内容独立为学习方向。开工同步至`origin/main`基线`2b418a9da0155fb29357c186238ed78feab0b8ed`，工作分支为`codex/distributed-standalone`。

- 沿用`distributed`系列及原URL，收录`db-sharding`、`global-id`、`distributed-tx-intro`、`tx-2pc`、`tx-tcc`、`tx-saga`、`tx-outbox`七篇，系列内顺序保持。
- 系统原理保留`request`、`cache`、`peak`，分库分表不再接在降级课程之后；分布式首末课不跨入其他学习方向。首页、学习页、内容库筛选及面包屑同步独立归属。
- MySQL、Kafka消息队列、Redis、工程算法等既有方向保持各自归属；事务历史合集`distributed-tx`继续只供回看，不进入当前目录与推荐路径。
- 本轮范围仅为站点分类、导航与文档，保留原EP、内容时间、文章和媒体，不扩充选题，不重编码视频，不重发外平台。

完整构建含日期、参考资料、图文与Pagefind检查通过，见[构建日志](build.log.gz)。[学习路径检查](learning-path.log)同时验证实际loader与构建产物：48篇、10个学习方向，系统13篇与分布式7篇各自归属明确。

[本地浏览器报告](qa-local/report.json)记录1440/390两视口240项检查，覆盖首页、学习目录、系列与7篇详情导航、筛选联动、旧分享链接、标签分组和其他方向边界；0项失败、0个未捕获页面错误。独立代理与根代理均实际查看桌面学习区和手机系列整页。未重新执行全片播放、听审、ASR或真机测试。

[保留核验](preservation.json)确认210份文件与基线Git对象一致：分布式7篇和系统末课的全部受版本控制的发布文件，以及分布式生产文章与输入清单。原EP、URL、内容时间和媒体不变。`secret_scan.py`与`git diff --check`通过；同步主干后保留当前MySQL、Kafka、Redis与LeetCode更新。

PR、合并SHA、Release、部署与线上核验回执在实际完成后补录，未执行项不计为通过。
