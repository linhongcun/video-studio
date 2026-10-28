# 计算机网络独立系列（2026-10-28）

状态：已随[v0.87.0](https://github.com/linhongcun/video-studio/releases/tag/v0.87.0)上线，本地与线上分类检查通过。

本轮将现有网络课程独立为「计算机网络」学习方向。开工同步至`origin/main`基线`43259b689a25d6df490c3cc488c0d351f37ef087`，工作分支为`codex/network-standalone`，保留同期Redis系列封面更新。

- 沿用`request`系列ID与原URL，收录`http-request`、`https`、`dns`、`cookie-session`、`cdn`、`load-balancing`、`browser-cache`七篇，保留EP.01–07及原顺序。
- 展示名称统一为「计算机网络」，介绍范围以现有Web通信入门内容为准，不将独立归类视为制作新课程或补齐全部网络知识的授权。
- 系统原理保留`cache`、`peak`两部分共6篇，从`server-cache`开始。网络与系统首末课断开，系列内部继续衔接；首页、学习页、内容库筛选和面包屑同步独立归属。
- 分布式、MySQL、Kafka消息队列、Redis及其他既有学习方向保留。本轮只调整站点分类、导航和文档，原文章、媒体与内容时间保留，不重编码视频，不重发外平台；既有历史档案保持原身份。

旧`series=request`及`track=systems&series=request`分享链接继续打开网络课程，手动切换到不兼容方向时仍清除系列筛选。

完整构建含日期、参考资料、图文与Pagefind检查通过，见[构建日志](build.log.gz)。[学习路径检查](learning-path.log)验证实际loader与构建产物：48篇、11个学习方向，网络7篇与系统6篇归属明确，系统缓存到流量治理的顺序保持。

[本地浏览器报告](qa-local/report.json)记录1440/390两视口310项检查，覆盖首页实际点击、锚点可见性、学习目录、旧系列URL、7篇详情导航、系统6篇衔接、筛选与旧分享链接、标签和其他方向边界；0项失败、0个未捕获页面错误。独立代理实际查看三张截图，根代理查看桌面学习区及手机系列整页。

[保留核验](preservation.json)确认202份文件与基线Git对象一致，包括网络7篇和系统首课全部受版本控制的发布文件，以及网络生产文章与输入清单。原EP、URL、内容时间和媒体保持；`secret_scan.py`与`git diff --check`通过。本轮未重做全片播放、听审、ASR或真机验证。

## 实际上线

[PR #418](https://github.com/linhongcun/video-studio/pull/418)合并为`544e57e8ecb8d9c1134fe1c766ba25b646e7e1f2`，附注tag `v0.87.0`指向同一提交。发布前复核主干新增`a225bd5c4deed62cadcc3ae637d1ffd71abfbe2a`仅涉及Redis回执与记忆，无站点运行代码或本轮课程输入交集；合并时保留这些更新。正式Release后触发[Pages #40671903914](https://github.com/linhongcun/video-studio/actions/runs/40671903914)，结果为成功。

[42项普通canonical GET](online-verification.json)通过：网络7篇的视频、海报、字幕与首幅配图共28项完整SHA-256与本地构建一致；14个页面确认新版本、网络入口及更新日志。没有缓存绕过，TLS证书校验保持开启。

[线上浏览器报告](qa-online/report.json)记录相同两视口310项通过、0个未捕获页面错误，使用Chromium直接网络与严格TLS访问canonical站点。独立代理与根代理均实际查看手机首页点击后的锚点落位及原系列URL整页，未见标题遮挡或横向溢出。完整媒体核验另见上述GET报告，不将页面检查当作全片听审或真机验证。发布身份汇总见[回执](publication.json)。
