<!-- engineering-algorithms:2026-10-25:ea02 -->

## 状态与定位

**已交付并完成线上核验：Redis 系列 / EP50 / `redis-sentinel`，v0.99.0。** 视频与配套图文已发布至 GitHub 站点；本 issue 以 completed 关闭。

所属系列：**Redis 系列**（`redis`）。首批选题索引：[原工程算法选题总览 #294](https://github.com/linhongcun/video-studio/issues/294)。原 EA02 仅保留为历史策划检索编号，不作为 Redis 系列期号，本次制作分配 EP50 与 `redis-sentinel`，不按旧 EA 号重排 Redis 系列。

2026-11-02 先完成系列归类，随后获授权正式制作。开工已同步最新主干 `01cd181caf24d4a8ce846c0eb8faeeab8f0054e2`，制作分支 `codex/redis-mechanisms-20261102`；工程使用 `episodes/redis/redis-sentinel/{production,publication}`。本期已完成资料、独立脚本/动态/成片检查及 GitHub 站点交付与线上核验。

## 已交付记录（v0.99.0，2026-11-02）

- 内容：沿一主两副本、五个 Sentinel 的固定例子，区分 quorum 故障确认、负责人多数授权、资格筛选、晋升确认和客户端重新发现；异步复制的数据边界另设独立分支。
- 交付物：视频、配套文章、官方参考资料尾页与三比例封面；13镜26句、4章，正文4439帧加150帧资料页，共4589帧 / 152.966667秒（30fps）。成片 SHA-256：`6aa19d3121666ae14b2d4f43f633a54f8961aa0159eef187dd12b913deceeaef`。
- 验证范围：固定 Redis 8.4.0 的本地进程实验分别验证仅两台可达时授权受阻、三台可达时正常换主，以及 priority=0 不获晋升；教学进度数字与产品实验分别记录。 [独立最终媒体 QA](https://github.com/linhongcun/video-studio/blob/main/docs/archive/2026-11/redis-mechanisms/qa/sentinel-encoded-final-decision.json)已在本地通过；技术检查不代表用户已观看认可。
- 发布：[制作 PR #455](https://github.com/linhongcun/video-studio/pull/455)；合并/站点提交 `7971d833e37b145eac5ccf66901773beba5cd0a6`；[Release v0.99.0](https://github.com/linhongcun/video-studio/releases/tag/v0.99.0)（2026-11-02T09:00:16Z）；Release 后[手动 Pages 部署](https://github.com/linhongcun/video-studio/actions/runs/41417179935) completed/success，09:09:33Z 完成。
- 线上交付：[成片与图文](https://linhongcun.github.io/video-studio/episodes/redis-sentinel/)。[原生 Chromium 报告](https://github.com/linhongcun/video-studio/blob/main/docs/archive/2026-11/redis-mechanisms/qa/site-online/redis-sentinel/report.json)本期 50 项检查、18 个严格 PTS 通过；三期合计 176 项/56 PTS。此轮浏览器验收在首轮 Pages 41416454968 成功后执行，早于上述手动部署完成，不记作后者完成后的重跑。
- 最终发布核验：[26 项完整 canonical GET 证据](https://github.com/linhongcun/video-studio/blob/main/docs/archive/2026-11/redis-mechanisms/qa/online-full-get-after-release.json)于上述手动部署成功后、09:09:58Z 检查完成，全部通过：三期 MP4/海报/VTT/七张图 SHA、Redis 六课目录、首页/目录/learn、RSS 与真实 Release/changelog。
- 验收范围：桌面与模拟移动视口、播放/章节/图文回放/引用/字幕及资料尾页；原生控件与视口限制保留在报告中。不宣称物理真机、逐字听审或用户理解反馈。
- 仅本次 GitHub 仓库、Release 与 Pages 范围；无外部平台投稿。下方原始提案与开工前核验清单保留为研究/分类历史，实际完成范围以本节与交付凭据为准。

## 一个核心问题

一个 Sentinel 认为主节点故障，为什么不能立即提升任意副本？“选 Sentinel”与“选新主节点”分别是谁做的？

## 拟讲的因果主线

1. 用 1 主 2 副本与 5 个 Sentinel 建立两类对象：业务数据节点与监控/协调者。
2. 超时形成主观下线 SDOWN；收集达到配置 quorum 的故障判断，形成客观下线 ODOWN。
3. Sentinel 在 epoch 内投票，选出本次执行故障转移的负责人；单独展示授权票数。
4. 负责人先排除不合格副本，再按 priority、复制进度等条件选择副本，提升为新主节点，重新配置其他副本并传播配置。
5. 用“quorum=2、只有2个 Sentinel 可达”的对照说明：确认故障后仍可能因不足多数授权而不能换主。

## 可视化与图文方向

票从 Sentinel 发给候选 Sentinel；选举结束后，负责人再检查 Redis 副本状态。故障确认票数与授权票数分两步展示，不能让副本举票或用一个“票数够了”跳过整个过程。

## 准确性、适用边界与内容增量

- 选票对象是负责故障转移的 Sentinel；Redis 副本不是在这一轮相互投票争当主节点。
- 设 N 为当前已知 Sentinel 总数（含自己），授权门槛为 max(floor(N/2)+1, quorum)，不是以当前在线数重算多数；正式演示记录各节点实际已知成员视图。
- 副本选择先检查可用性、断连时长及 priority=0 等限制，再按较小 priority、较大 replication offset、较小 run ID 排序；不能说数据最新者一定当选。
- Sentinel 与 Redis Cluster 自动故障转移是不同部署和协议。本题不把 Sentinel 描述成完整 Raft 日志共识。
- Redis 异步复制意味着换主可能丢失部分已确认写入；多数授权不提供业务数据零丢失保证。

## 第一方资料初核

访问日期：**2026-10-25（北京时间）**。下列为本轮选题初核，未标发布日期的动态文档如实注明；不将资料阅读等同于产品实测或成片质量通过。

- [Redis Sentinel：Quorum / Configuration epochs / Replica selection](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/)，第一方文档，未标发布日期，本轮已读。短引：“a majority of Sentinels (or more than the majority if the quorum is set to a number greater than the majority).”
- 适用 Sentinel 2，Redis 2.8 起稳定提供；早期 Sentinel 1 不作为本题模型。正式制作重新固定 Redis 版本与配置，不能仅凭版本起点代替当前实测。

## 后续安排制作时的专项核验

- [ ] 核对 SDOWN、ODOWN、epoch、授权门槛及副本筛选的顺序；至少覆盖确认故障但无授权、多数可达正常换主、priority=0 不晋升三种情景。
- [ ] 重新核验第一方资料，固定产品版本、配置与支持主张；按[调研格式](https://github.com/linhongcun/video-studio/blob/main/docs/research-template.md)记录短引、日期和适用边界。
- [ ] 开拍前确认一个可跟随的核心机制及必要前置；按[现行规范](https://github.com/linhongcun/video-studio/blob/main/docs/RULES.md)完成因果动画与正式媒体检查，检查和用户观看结论分别记录。
- [ ] 仅在后续获安排制作、完成交付及核验后，才按届时授权以 completed 关闭，并同步系列总览。
