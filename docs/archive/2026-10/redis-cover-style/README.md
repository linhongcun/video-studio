# Redis系列封面统一

日期：2026-10-28（北京时间）。本地制作、独立安装与最终站点验收已通过，已按v0.86.1发布并完成线上核验。

从clean最新2b418a9d/v0.85.1开工，已保留其他线程的LeetCode正文样式与字幕更新。现有Redis独立系列仅redis-skiplist / EP.40，原完整题为《Redis 跳表：怎样跳过一段，找到插入位置？》。本轮仅更换封面，不重制视频，不改变课号、meta/sourcePath、内容日期、URL或原始冻结。

冷银灰/Redis红/石墨文字、原始Redis标记和真实EP编号组成独立系列模板。背景图像生成仅用于无事实边角装饰；题名与具体机制图由SVG绘制。跳表图沿本片前向链接教学示例，目标55在50/60之间，在40原地下降而非前进到70；不将小集合示意当作Redis默认实际内存布局。

三种尺寸为1920×1080、1080×1440、1440×1080，4:3使用完整竖版缩放居中并检查内容x315..1125、底边<918。水印随版式。新增视频沿[共享模板](../../../../episodes-codex/_shared/redis-covers/README.md)扩展题名、EP与机制图。

仅GitHub站点更新，外平台作品封面未修改；未来候选没有开工。无新用户观看反馈或辨识度、观看效果实测结论。

## 已完成的本地检查

- 独立逐图查看三比例PNG，12项输入、9份SVG/PNG/JPG产物身份与尺寸匹配，3份SVG独立重生逐字节相同；9份合成文字压力样例只验证排版，不是未来选题或成片。
- 按当前sourcePath安装11张图与2份配对sidecar，全部与审定候选一致；两份poster.jpg为3:4 JPG副本，原meta.poster仍为cover-16x9.jpg。
- 2883保护路径、全部49份发布元数据与三套139/146/151共436冻结声明保持；源当前修订原本无本地video.mp4，媒体核对实际发布片与保留render-result，不重建或伪造源片。
- 完整站点构建通过49参考输出、48文章、74精确摘录与55配图；独立学习路径检查通过。当前任务只换封面，没有重新执行声音或动画制作检查。

## 发布前主干整合

再次fetch发现分布式系统独立系列新主干`a442ab1c8d67aa1e2df12dfe4aeac782d2fcd120` / v0.86.0，本轮从候选v0.85.2顺延v0.86.1。Redis封面提交`edcf720e`与新上游整合为`16e2576f`，仅两份版本JSON有冲突，完整采用新上游对象后改version；归档索引自动保留双方。

24个上游路径与2883保护/436冻结零交集，21个非重叠文件完整字节及mode等新上游，索引保留双方非空行，依赖图不变。整合后重新完整build与学习路径通过；旧本地v0.85.2检查与0网络的线上计划按历史身份保留，不冒充实际发布。证明见[整合报告](upstream-integration/integration-report.json)。

## 最终站点验收

最终v0.86.1重新执行1440×1000与390×844双视口14项检查/14截图，11个代表原资产逐字节保持；Redis单课筛选、首页与学习入口、列表新图、播放器海报、短播放暂停及Fullscreen API通过。独立复核实看全部14截图合辑与3原图，root实看桌面library、手机poster与home。原v0.85.2整轮证据保持，不用旧UI结果替代变化后的runtime。

手机series缩略图按现有CSS隐藏，library封面完整显示；原生暂停控件会盖住播放器海报下部问题文字，不能把图片安全区检查扩大成所有控件状态无遮挡。实际HTTP keepalive reset保留，浏览器pageerror为0。最初两次静态文件路径假设在浏览器启动前失败，按真实发布树修正QA脚本，没有改产品或放宽字节判断。非物理手机测试，未重复已保真正文的动画、声音或逐字听辨。完整报告与实际截图见[site-qa](site-qa/report.json)。

最后fetch还取得分布式发布回执`453747f7`，仅8份任务归档文件，全部原字节整合。相对最终UI检查head16e2576f，site/episodes/episodes-codex三棵树完全相同，不重复构建或媒体检查；记录见[最新回执整合](latest-upstream-receipt.json)。

## 发布与线上核验

[PR #416](https://github.com/linhongcun/video-studio/pull/416)合并为`43259b689a25d6df490c3cc488c0d351f37ef087`，与已验收分支树相同，Codex联合署名保留。附注tag与[Release v0.86.1](https://github.com/linhongcun/video-studio/releases/tag/v0.86.1)指向该提交；Release后手动[Pages 40670831777](https://github.com/linhongcun/video-studio/actions/runs/40670831777)以相同HEAD完成构建和部署。

北京时间2026-10-28 18:21:17，11项规范URL完整GET通过，共10,407,453字节。原视频、新横封、全文字幕、6个实际页面及2个固定合并提交下载均匹配；页面包含Redis完整题、独立系列、实际版本与Release链接。原视频完整SHA仍为`0edf23150bb3a3a00950ebb99547e09e9ede6ba9326e22d46e73d5e2e50f24f9`。实际响应、HTTP状态、完整SHA及部署身份见[online-verification.json](online-verification.json)、[deployment-status.json](deployment-status.json)和[publication.json](publication.json)。

[Redis系列](https://linhongcun.github.io/video-studio/series/redis/)已显示新封面，[三比例素材](../../../../design/redis-covers-20261028/README.md)可领取。没有对应开放封面issue，旧已关闭制作记录及未来候选未修改；外平台作品封面未修改。发布回执仅文档归档，不另升版本或部署。
