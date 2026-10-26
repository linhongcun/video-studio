# 片尾参考资料 · 第六批

本批选择主从复制、分库分表、分布式ID三期存量视频，为片尾增加原始题名与作者/机构的简洁列表。每页最多4项、5秒；完整出处与论点对应保留配套文章。源资料与日期按实际阅读记录逐项标注，不把研究笔记当作官方全文响应。

开工从clean工作区同步最新主干`278f69a71151cada63e7068b4cfc0d5222501ac7`（v0.71.3），建立独立制作分支。三期Git发布原片与制作视频字节一致，完整原片、元数据、原文章/研究与旧冻结输入在各期`revisions/reference-endcards/`捕获；只追加资料卡，正文和音轨复用已发布原片。当前共享入口与锁文件保留，旧QA和旧制作记录不改写。

| 视频 | 原正文帧 | 入口 |
|---|---:|---|
| 主从复制 | 3560 | [页面](https://linhongcun.github.io/video-studio/episodes/db-replication/) |
| 分库分表 | 3760 | [页面](https://linhongcun.github.io/video-studio/episodes/db-sharding/) |
| 分布式ID | 5646 | [页面](https://linhongcun.github.io/video-studio/episodes/global-id/) |

实际来源、冻结、成片、浏览器及线上验证结果按其报告记录；不预记检查通过或用户观看结论。仅GitHub站点。

来源定稿为4/4/8项，共16项、4页，前两期各5秒，分布式ID两页共10秒。三期完整媒体保真与独立15张实际尾帧检查通过；两页长题名与明确作者完整显示。

技术主张沿用2026-10-24/25的实际官方阅读记录。分布式ID另于26日读取固定IETF书目核对RFC完整题名/显式作者，并从固定Redis官方文档补Sentinel完整题名；这些新读取仅用于题名/署名核对，不冒称本轮重读技术全文。原记录Git/blob/完整SHA及题名补查的固定URL/完整响应SHA分别保留。

三片当前冻结共449项（116/117/216），旧260项记录经原路径或明确before快照逐项保留；Global原tradeoffs完整校验保留，新增题名3份原文件也冻结。正文/SB/words/placeholder保持字节与mtime；不将扩展的输入清单说成旧批准片已按其重渲，媒体保真以完整Git原片为准。见production-entry-check.json。

两次站点构建均通过，最终23片实际附录/24片固定未换片存量通过；三片实际帧数和47日期/RSS检查通过。首次本地核对拦截RFC新书目缺出版机构IETF，随后只补该机构、重新冻结216及构建，不改原题/作者/refs/影片；见citation-publisher-correction.json与local-verification.json历史。

正式本地预检及6个浏览器用例通过：3次桌面1x尾段到ended、3次手机原生全屏、8张每页截图实际查看；RFC明确作者在真实HTML与画面均可见。只模拟Chromium手机视口，不声称真机/iOS或全片听辨。预览服务未运行导致的连接/失败截图尝试保留，重启后成功。见qa-browser.json与各attempt。

三份官方题名原文件按完整SHA逐字节保留；限定该目录的.gitattributes防止行尾转换，仅对Sentinel原文件保留其上游三处尾空白，不清洗后冒认原响应SHA。
