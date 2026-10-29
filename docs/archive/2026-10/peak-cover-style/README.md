# 高并发、高可用、高性能系列封面统一

日期：2026-10-29（北京时间）。本地封面、独立安装与站点验收已完成，已按v0.90.1发布并通过线上核验。

从clean最新d3c163ef/v0.89.2开工，保留最新系列并列结构、Redis两期新媒体和LC547矩阵开头。当前peak四期为EP.11限流、EP.12幂等、EP.13熔断、EP.14降级，完整原标题、元数据、媒体、日期、链接与旧冻结保持；只统一封面。

深青蓝、亮青、暖黄、Noto字体与真实EP组成独立模板。生成背景仅提供无事实的边角线条，具体中文与四种机制由确定SVG绘制。限流不画成排队或并发数量上限；幂等同支付7042只产生一次扣30、100→70的效果；熔断暂停可选运费险故障调用，必要校验仍在；降级为搜索参考价199未计红包，结算核验减20为179，不把价格差误画成缓存错误。

三种规格1920×1080、1080×1440、1440×1080，4:3将完整竖版0.75倍居中，关键内容x315..1125、底边<918。新增题沿[共享模板](../../../../episodes-codex/_shared/peak-covers/README.md)扩展题名、真实EP与机制图。

当前四期生产封面与海报不在冻结输入中，可独立安装；原covers.json/Cover/制作脚本和400冻结声明保护。外平台作品封面未修改，未启动未来选题；不预记用户对新样式的认可或观看效果。

## 本地验收

- 12真实三比例封面、36份SVG/PNG/JPG，8项源码输入和2份实际Noto字体身份匹配；独立实际查看全部12PNG，12SVG重新生成逐字节相同。9份合成文字压力只检查排版，不是未来选题或封面。4:3 fresh字体/重要图形136对象检查通过，底边最大900<918。
- 44安装图全等原候选，8sidecar正确配对并绑定真实EP/sourcePath、输入与字体SHA、sitePoster及3:4海报；2754保护路径、49份元数据与400冻结声明全部保持，目标与冻结零交集。
- 最新锁文件npm ci、完整站点build、学习路径通过：49参考输出、48文章、74精确引文、55配图、135页面。依赖图不变，仅版本0.89.2→0.89.3。
- 实际26项双视口功能检查、18原截图与28个原资产字节比较通过。独立实看两张合辑中的18图及代表原图；root实看桌面library及手机幂等/降级海报。源码图与列表封面完整可见。

初始原生海报截图有白色loading弧。额外8张数据ready和2张idle手机截图在readyState4/networkState1/暂停时仍有弧，没有隐藏控件或播放正文冒充封面；早期stable命名过早，原字节与真实功能结果保持，[勘误](site-qa/poster-state-erratum.json)明确未证明视觉稳定。手机控件会盖下部问题，不能把图片安全区等同全部原生控件状态无遮挡；非物理手机、未点原生全屏按钮。三轮HTTP keepalive重置分别10/10/2，浏览器pageerror0，日志保留。完整范围见[最终QA](site-qa/final-summary.json)。

ZIP内24张完整图片逐字节匹配候选，预览与包完整SHA见[交付检查](delivery-check.json)。原v0.89.3本地验收前多次fetch仍为d3c163ef，23项完整GET计划未执行、无旧版上线；最终整合状态见下节。

## 发布前统一入口整合

首次合并前，新主干`3beb56c549b20e666023774b919fc414454abe87`已将学习系列与全部内容合为统一入口，版本v0.90.0。旧PR合并因版本冲突被拒，没有旧版tag/Release；本轮整合提交`1a5a0910`完整采用新运行文件，两个版本JSON取完整theirs后顺延v0.90.1。原12封面/ZIP不重做。

14上游路径与2754保护/400冻结零交集，12非版本运行文件字节与mode等新上游；依赖图保持，episodes/episodes-codex/design树全等原封面提交90ae7716。完整构建与学习路径重新通过，原0.89.3报告、18图和补采勘误原位保持；新0.90.1另做26功能/18图/28原资产检查，未借旧通过结果追认新runtime。root另实看统一入口手机、桌面四卡列表和手机幂等海报。

最终/library为统一主入口，/learn为legacy JS redirect且保留search/hash；首页/导航三入口、手机菜单、四卡筛选和四poster/播放暂停及代表Fullscreen API通过。原生弧仍按实况记录，不再补采或隐藏控件；本轮9次HTTP keepalive reset、pageerror0。见[上游证明](upstream-integration/integration-report.json)、[最终UI](site-qa/integration-0.90.1/report.json)。原0.89.3 checker/plan原字节另存online-plan-before-upstream，0网络身份保持；最终23GET计划按新入口真实契约prepare，等待发布。

## 发布与线上核验

[PR #427](https://github.com/linhongcun/video-studio/pull/427)合并为`1c18eb8d78937c8736b345df3bb89226e2314363`，与最终验收分支10ded7ac整树一致，保留Codex联合署名。附注tag和[Release v0.90.1](https://github.com/linhongcun/video-studio/releases/tag/v0.90.1)指向同一提交；Release后[Pages 40804410988](https://github.com/linhongcun/video-studio/actions/runs/40804410988)以同HEAD完成完整构建和部署。

北京时间2026-10-29 10:11:21完成23项规范URL完整GET，共34,905,213字节，全200/pass。四期原视频、新横封、全文字幕12份资产完整SHA匹配；9实际页面包含完整原题、精确四课集合、新版本与真实Release链接，旧learn页面的JS跳转目标/canonical/search/hash保留及fallback/noindex契约按静态完整响应核对，不冒称本轮线上浏览器执行。2份固定合并提交下载的ZIP/preview字节与审定交付一致。实际状态、完整SHA与身份见[online-verification.json](online-verification.json)、[deployment-status.json](deployment-status.json)和[publication.json](publication.json)。

[本系列](https://linhongcun.github.io/video-studio/series/peak/)已显示统一封面，[24张完整素材](../../../../design/peak-covers-20261029/README.md)可领取。本次没有issue写入或平台操作；后续视频沿模板继续。回执仅文档归档，不另升版本或触发部署。
