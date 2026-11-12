# P06 十二球趣味短片重构

日期：2026-11-12（北京时间）。状态：新版已上线，完整线上文件SHA复验待补；追踪 [#484](https://github.com/linhongcun/video-studio/issues/484)。

从主干 `ed088d557e59512c8b27946af4c3d39f91c48e16` 开工，新修订位于 `episodes/puzzles/twelve-balls/production/revisions/simple-20261112/twelve-balls/`。旧制作、冻结清单和交付证据保留。

原片236.7秒，同时承担容量分析、逐步构造、主例和分支回溯。本轮改为四对四直接入手，走完一个完整实例，再简洁补足必要结果；抽象构造、完整决策表和下界留文章深入层。新版12镜24句，正文4669帧155.633秒，另5秒参考资料，共4819帧160.633秒，减少76.067秒，未加快语速。最终MP4 SHA-256为 `d3ec59265969292324d61ef1f8d3d56bdd943a293d66867a22c059f434e013ef`。

独立稿审、164输入冻结、动态及定向复验、19张正式成片图和两张文章图实审完成。完整解码、-16.0 LUFS／-3.8 dBTP、字幕、资料卡、本地站点build、日期／RSS、目录，以及桌面／手机模拟视口下播放、章节、配图回看、引用和全屏检查通过，见本修订的 `qa-final.md` 与 `qa/`。

## 已发生的交付

[PR485](https://github.com/linhongcun/video-studio/pull/485)合并为 `8d2c03f601238728df5f7a38724f48dac4b4742a`，附注tag与[Release v0.106.1](https://github.com/linhongcun/video-studio/releases/tag/v0.106.1)已发布。Release后[部署43139961657](https://github.com/linhongcun/video-studio/actions/runs/43139961657)成功，build 130925228827、deploy 130928674316均success，Pages artifact 13910025482；日志于北京时间2026-11-12 10:25:56报告成功。预Release的push运行已在checkout阶段取消，正式运行未取消或重触发。

普通页面读取已确认新版导语、46／71秒回看与v0.106.1更新日志。备用浏览器服务确认新版约2:40显示、播放／暂停及71秒定位；它明确不能执行JavaScript计算文件哈希，返回的期望SHA不作为实际测量。执行环境在最终复验时不可用，因此完整canonical GET字节与SHA核对仍待补，#484不提前关闭。状态与边界见本修订 `publication.json`、`qa/github-deployment.json`、`qa/online-service-observation.json`。

## 保留的边界

本地旧ignored依赖目录已原样移入workspace的work保存，当前依赖按现行锁安装。全仓secret scanner的282项既有命中涉及25个文件，均与当时最新main逐字节相同，本任务改动扫描无新增；原报告未抑制或改写。

原期号、标题、URL、创建与首发时间、封面和来源核验日期保持。仅GitHub与本站，无外部平台重发。未声明逐字ASR、语义听辨、实体手机测试或新版用户观看认可。
