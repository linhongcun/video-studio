# 数据库身份修订（#230）

可靠消息：Outbox怎样把通知送出去？：保留原配音、字幕与3499帧时长，给真实库角色增加MySQL识别标记，内部记录与提交范围保持。

当前视频完整SHA-256：`4a27553f8e60c53702425e3523f1c4c6f0728d6688c8c78320f18fb09d89f0e4`；原混合AAC逐字节保持。正式媒体/预演/fresh复现的实际范围见[本轮QA](qa-mysql-identity.json)。图标来源为Devicon，原始SVG、MIT notice和品牌说明见[共享素材](../_shared/database-identity/source.json)，不称官方授权素材。

拟随v0.56.5合并主干、Release后部署；线上完整文件、字幕、章节、封面与日志通过后关闭#230。只上GitHub站点，不预写用户观看认可。

## 历史发布记录

# v0.51.0：EP.21 · 可靠消息全局流程与缩放导航

14镜28句，3499帧，约116.6秒。成片完整SHA256：`1cb505dfe2dc5f4780a11e729c910feb4f920e5781590380766d88c5acf58dfb`。

发送与消费回边分层，消费三出口前提互斥。HUD进入/退出统一表达“必须共同保存”的要求，完成状态只在2373实际提交后出现；修前198954aa…未发布。

原配音、字幕与时长保持，制作/独立预演、最终MP4实际查看、干净构建和能力限制见qa-final.md与本批独立报告。旧v0.47.0已被用户观看并反馈缺全局定位；新检查不预记用户认可。

实际站点版本v0.51.0，完整保留至v0.50.5的协作主干；分镜内v0.47.1仅保留最初导航设计ID。历史源和媒体见revisions/v0.47.0.json。

已由[PR #186](https://github.com/linhongcun/video-studio/pull/186)合并，发布[v0.51.0](https://github.com/linhongcun/video-studio/releases/tag/v0.51.0)，Release后[部署40103321270](https://github.com/linhongcun/video-studio/actions/runs/40103321270)成功。线上四片完整SHA/字节、海报、112句字幕、18章、学习顺序、原入门与旧合集、更新日志及协作主干视频核验通过，[#152](https://github.com/linhongcun/video-studio/issues/152)已以completed关闭。完整证据见[线上报告](../../docs/transaction-branch-online-verification.json)。只上GitHub站点；未预写用户对新版的观看认可。
