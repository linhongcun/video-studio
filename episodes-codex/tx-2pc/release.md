# 数据库身份修订（#230）

两阶段提交，两个库怎么共同确认？：保留原配音、字幕与3398帧时长，给真实库角色增加MySQL识别标记，内部记录与提交范围保持。

当前视频完整SHA-256：`7c919e72f48096b3d6bf71b79be02a791955b64de41d3fdff9e37c26f6b107b6`；原混合AAC逐字节保持。正式媒体/预演/fresh复现的实际范围见[本轮QA](qa-mysql-identity.json)。图标来源为Devicon，原始SVG、MIT notice和品牌说明见[共享素材](../_shared/database-identity/source.json)，不称官方授权素材。

拟随v0.56.5合并主干、Release后部署；线上完整文件、字幕、章节、封面与日志通过后关闭#230。只上GitHub站点，不预写用户观看认可。

## 历史发布记录

# v0.51.0：EP.21 · 2PC全局流程与缩放导航

14镜28句，3398帧，约113.3秒。成片完整SHA256：`7f3666ea053489b4d6b5b65fb1afed67fabc287d61ca1a97624b49d37271b7ca`。

三种分别演示的情景：正常保存、准备拒绝、决定未知。恢复查回原决定，不重新选择；03请求39→70在相机落点后完整出现。

原配音、字幕与时长保持，制作/独立预演、最终MP4实际查看、干净构建和能力限制见qa-final.md与本批独立报告。旧v0.47.0已被用户观看并反馈缺全局定位；新检查不预记用户认可。

实际站点版本v0.51.0，完整保留至v0.50.5的协作主干；分镜内v0.47.1仅保留最初导航设计ID。历史源和媒体见revisions/v0.47.0.json。

已由[PR #186](https://github.com/linhongcun/video-studio/pull/186)合并，发布[v0.51.0](https://github.com/linhongcun/video-studio/releases/tag/v0.51.0)，Release后[部署40103321270](https://github.com/linhongcun/video-studio/actions/runs/40103321270)成功。线上四片完整SHA/字节、海报、112句字幕、18章、学习顺序、原入门与旧合集、更新日志及协作主干视频核验通过，[#152](https://github.com/linhongcun/video-studio/issues/152)已以completed关闭。完整证据见[线上报告](../../docs/transaction-branch-online-verification.json)。只上GitHub站点；未预写用户对新版的观看认可。
