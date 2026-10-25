# 分布式事务入门：产品交互入口单期试点

**已合并、发布v0.60.2并上线核验。** 对应[#242](https://github.com/linhongcun/video-studio/issues/242)。用户选择先用《什么是分布式事务？》做单期示范；这不授权把其他视频一并重制，也不表示本版已验收或上线。

本次指导是：**实际APP功能操作 → 页面反馈 → 同一业务对象 → 机制 → 回页面**。先让观众看懂谁在用什么功能、操作后看到什么，再从同一订单和商品展开机制；产品交互不是给原来的内部框套一层装饰外壳。界面为教学重建，不冒充实际操作某个真实平台。

## 基线与范围

基线提交`afe60158b30e29a757b88d961c86ac7a34737bea`。当前站点/制作工程由`episodes/distributed-tx-intro/meta.json`的`sourcePath`定位到`episodes-codex/distributed-tx-intro/remotion`。原版完整媒体SHA为`ae3f2740f8319d435ee8bcb36351493a16956a1800a758cba2106413f63ab62a`；Git路径、完整SHA、脚本及时间边界见[baseline.json](baseline.json)，不复制旧大媒体。

保留分镜的镜头边界与配音/字幕时序，复用原配音、40句字幕及首现cue；仍为20镜5155帧（30fps，约171.83秒）。重绘01/02/04/20共1046帧，其他16镜4109帧保持；04只增加进入机制对照所需的明确重置。20前167帧仍回收全局，后156帧回到产品页面。

| 镜号 | 原帧范围（右端不含） | 本次表达 |
| --- | --- | --- |
| 01 | 0–246 | 商品7042、买1件，实际按钮操作和页面反馈；订单8124已记录但待确认 |
| 02 | 246–482 | 同一订单/商品映射到记订单与扣库存；当前库存4，目标3仍未执行 |
| 04 | 738–979 | 明示“机制对照，回到提交之前”：本单待提交、库存4，随后沿原本地事务过程 |
| 20 | 4832–5155 | 前167帧全局回收，4999帧起回到开头同一订单页，保持待确认并回应需要协作/恢复 |

## 设计与编辑守卫

本记录实际阅读了工作盘的`distributed-tx-intro-design.json`与`intro-product-scene-editorial.json`，提炼以下要求；它们是设计/编辑建议，不是本版成片QA。

- 从提交订单、查看订单的实际功能建立任务，按钮操作须有对应反馈；首屏仍兑现原订单/库存冲突。
- 始终对应订单8124、商品7042、数量1。订单存在与整单业务成功分开，不把“已提交”写成“已完成”。
- 库存4和本单未扣须用独立标注的“后台记录（教学透视）”核对；商品页仍显示4不能直接证明数据库没执行。目标3也不能提前当成已保存值。
- UI到机制保留身份映射；04明确回到提交前的机制对照，避免同一已保存订单又无说明地首次提交，也不暗示真实产品临时切换了数据库架构。
- 结尾回到原问题和待确认页面，不凭刷新自动改成成功；不添加付款、退款、发货、售罄或其他未讲机制。已审全局/局部关系继续保留。

## 检查与发布状态

[23帧独立预检](independent-preflight.json)与[16帧正式成片独立复核](independent-encoded.json)通过；[编码检查](encoded-check.json)、[保护项与原AAC字节核对](preservation.json)、[本地站点40条字幕/5章验证](local-verification.json)、[桌面/手机真实播放](ui-check.json)均已完成。1046帧来自新源，4109帧复用原解码画面，整片H.264重新编码一次，原AAC直接复制；不把图像重编码说成数学无损。线上完整视频SHA、40条字幕、5章、海报、源码链接及真实Release更新日志已核验。未把外部未查看的提取帧复制进仓库或充作本次QA，也未新增音频听辨或ASR结论。

[站点核验脚本](verify-site.py)仅处理`baseline.json`的`selected`入门一片，比较正式制作媒体、海报、历史元数据、源链接、原生控件、精确章节和VTT；live模式另查真实Release更新日志。它须在root完成正式媒体与新站点构建后运行：

```bash
python docs/product-scene-intro/verify-site.py --report /path/to/local-verification.json
python docs/product-scene-intro/verify-site.py --live --report /path/to/online-verification.json
```

脚本准备/语法可用不等于上述核验已经执行。合并、发版、部署、线上结果与用户观看反馈均按实际发生后记录；本试点未授权外部平台重发。

本轮两次画面修正：后台库存卡片中心与内部横线对齐；打开订单明确切换到详情与处理进度，长状态文案放回卡片边界。UI helper首轮在恢复disabled字幕模式后读取空cues报错，未执行到截图；[失败记录](ui-check-helper-v1-failure.json)保留，修为hidden模式加载时先记cue数，恢复后重新实播两视口并实际查看四图。未修改播放器或隐藏浏览器控件。

发布前再同步`8bef491`：保留P02及五片算法修订，180冻结输入交集为空且完整SHA复核通过；新站点v0.60.2构建、媒体/40条VTT/5章和完整学习路径通过。此前v0.60.1真实播放四图按实际版本保留，播放器模板/本片媒体与字幕输入相同，未重贴成v0.60.2；见[协作审计](prepublish-upstream-audit.json)。算法批次已修正旧谜题断言，最终采用上游检查器，不重复提交本地的等价修复。

[PR #249](https://github.com/linhongcun/video-studio/pull/249)已合并，附注tag指向`1135c8ef186016c1f3c47178f10ed343d84e3e61`；[v0.60.2](https://github.com/linhongcun/video-studio/releases/tag/v0.60.2)后重新[部署Pages](https://github.com/linhongcun/video-studio/actions/runs/40151454493)成功。[线上核验](online-verification.json)通过，#242以completed关闭；见[发布凭据](release.json)。本次只改事务入门，用户观看反馈待后续实际收到。
