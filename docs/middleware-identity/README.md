# 缓存与消息中间件身份标记（#271，v0.64.2已上线）

基线为 `f5327fdf90dea765d6e1d2f086fcd1a1789970ff`。本轮只给实际中间件对象补产品身份，保留原机制、配音、字幕、分镜与导航时序、封面；不把通用机制改成某个产品的定义。发版号在最终整合最新主干后确定。

当前按已发布 `meta.json` 的真实 `sourcePath` 核对：41 份元数据中有 39 期非草稿、非归档；`egg-drop` 是草稿，旧 `distributed-tx` 是归档。选择以下 4 期，其余 35 期保留。完整目录判定、基线媒体 SHA 与源码定位摘要在 [index.json](index.json)；仓库外逐镜源码审计是 `/workspace/.video-studio-middleware-icon/catalog-audit.json`，这份盘点没有声称实际观看成片。

| 视频 | 标记位置 | 身份与边界 |
| --- | --- | --- |
| 服务端缓存 | 06–12 的真实共享缓存 K | 明确“本例：Redis 共享缓存”。04/05 泛型副本与本地/共享说明不贴，应用本地内存不贴 Redis。 |
| 缓存一致性 | 01–12 的真实缓存 K | Redis 作为本例选型；数据库、价格值与检查/删除/回填操作节点保持原身份。 |
| 消息队列 | 03–11 的真实队列 broker | RabbitMQ 示例，与原手动处理确认、断连未确认重投机制对应；任务卡、应用、处理者不贴。 |
| Outbox | 07–09 的真实外部 broker | Kafka 示例；本地待发表、E8124 事件、库存和消费去重标记不贴。 |

浏览器缓存、DNS 解析器缓存、CDN 边缘副本不标 Redis。会话记录、限流额度、幂等处理记录、数据库行锁与复制日志，也不因“可能用某产品实现”而加品牌。观察者的同程序通知与适配器服务返回“已排队”，没有建立实际消息中间件对象。

本期采用的现有机制依据分别在四期 `research.md`：缓存是应用管理的副本，MQ 是 RabbitMQ 手动确认示例，Outbox 是本地待办与独立发送流程。标记素材来自固定 Devicon commit 的原始 SVG；共享模块的 [来源记录](../../episodes-codex/_shared/middleware-identity/source.json)、[MIT notice](../../episodes-codex/_shared/middleware-identity/LICENSE.txt) 与 [品牌说明](../../episodes-codex/_shared/middleware-identity/NOTICE.md) 随输入保留。素材来源和其他执行者的官方资料阅读记录不等同本文件作者重新阅读全部官方正文，也不表示官方授权或背书。

`index.json` 固定四支原片、610 项原声/字幕/镜头/封面/导航及既有共享输入，另列 6 个允许修改的期内源文件与 8 个新模块文件。原 AAC 从可寻址的基线 MP4 实际流复制到 ADTS 后计算完整 SHA；这只是历史基线，不是新片通过的结论。

生产输入停写后运行：

```bash
python3 docs/middleware-identity/check-preservation.py --report /workspace/.video-studio-middleware-icon/preservation-source.json
# 正式编码和站点副本更新后再加 --encoded；若整合了新主干，传入实际 --upstream SHA。
python3 docs/middleware-identity/check-preservation.py --encoded --upstream ACTUAL_UPSTREAM_SHA --report /workspace/.video-studio-middleware-icon/preservation-final.json
python3 docs/middleware-identity/verify-site.py --report /workspace/.video-studio-middleware-icon/site-verification.json
# Release 与实际部署完成后：
python3 docs/middleware-identity/verify-site.py --live --report /workspace/.video-studio-middleware-icon/online-verification.json
```

检查器核对真实输入和原 AAC 字节；站点检查器核对完整媒体、字幕、章节、海报、源码链接及历史身份。实际预演/正式代表帧、干净输入复现、编码与网页检查分别记录执行者和有限范围，不以静帧代替连续动作、听辨或用户观看反馈。

当前状态：目录源码盘点与历史保护基线已建立；独立实际查看 25 张有字幕、1920×1080 预演，新增身份标记在泛型/选型切换、空缓存、变焦中态与回全局时均无可见阻断，见 [有限范围预检](preflight-review.json)。正式成片另实看 30 张实际 MP4 抽帧（四片分别 7/7/8/8），核对改制/复用边界、变焦和品牌对象，四支完整成片 SHA 独立匹配，见 [正式媒体采样复核](review-encoded.json)。这些是静态采样，无连续播放、听辨或用户认可声明；完整媒体/原 AAC 保护由根制作任务另验，网站与上线状态等待实际结果。原 MySQL 批次的历史记录不改写。

本次8523帧从新冻结源重绘，5031帧复用旧解码画面；保留原AAC流。缓存一致性全帧有标识增量，直接CRF20；其他片按连续受影响镜头组合CRF1中间片、与旧解码画面拼接后统一CRF20。不把图像重新编码说成数学无损，见[渲染计划](render-plan.json)。新依赖仅复用当前相同锁包图，并用干净安装/输入复制复现两个代表PNG，见[fresh检查](fresh-build.json)。

发布前同步包含D03的v0.64.1重制与LC200预留，所有484冻结输入交集为零；本批顺延v0.64.2，不覆盖旧tag。四选中页面在相同版本下与UI实播构建字节相同，最终除精确版本号外也逐字节一致；既有0.64.1八次实播按实际版本保留，最终0.64.2媒体/字幕/章节/封面核验通过。见[协作审计](prepublish-upstream-audit.json)。旧全库检查把preview算法链硬写成六课，新增draft LC200后失效；生产导航原本已正确隔离，现只修检查器并显式检查预览完整七课、公开六课与构建草稿隔离，[完整检查](learning-path-final.log)通过。

[PR #275](https://github.com/linhongcun/video-studio/pull/275)已合并，附注tag指向`768c23c0df976ec2247cd4d07d7f188bf4c34624`；[Release](https://github.com/linhongcun/video-studio/releases/tag/v0.64.2)后[Pages部署40178059672](https://github.com/linhongcun/video-studio/actions/runs/40178059672)成功。[线上核验](online-verification.json)通过，#271以completed关闭；[发布凭据](release.json)记录各片完整SHA。本批尚无用户观看反馈。
