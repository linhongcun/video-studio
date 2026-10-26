# 数据库身份修订（#230）

什么是分布式事务？：保留原配音、字幕与5155帧时长，给真实库角色增加MySQL识别标记，内部记录与提交范围保持。

当前视频完整SHA-256：`ae3f2740f8319d435ee8bcb36351493a16956a1800a758cba2106413f63ab62a`；原混合AAC逐字节保持。正式媒体/预演/fresh复现的实际范围见[本轮QA](qa-mysql-identity.json)。图标来源为Devicon，原始SVG、MIT notice和品牌说明见[共享素材](../_shared/database-identity/source.json)，不称官方授权素材。

[PR #235](https://github.com/linhongcun/video-studio/pull/235)已合并，随[v0.58.1](https://github.com/linhongcun/video-studio/releases/tag/v0.58.1)发布；[Release后Pages部署](https://github.com/linhongcun/video-studio/actions/runs/40147968820)成功。线上10支完整视频SHA、字幕、章节、封面、源链接与实际更新日志核验通过，#230已以completed关闭。仅更新GitHub站点，用户对新版的观看反馈后续另记。

[实际线上证据](../../docs/mysql-database-identity/online-verification.json)。

## 历史发布记录

# 什么是分布式事务？：全流程与局部定位重制

对应[#199](https://github.com/linhongcun/video-studio/issues/199)，本批设计ID与实际站点发布号分别追溯。保留原配音、字幕与5155帧时长，增加适合本片机制的稀疏全局图、局部聚焦、情景重置与结尾回收。

完整视频SHA-256：`23c1e396def6d06b26b98ce0d7a71534a144b7fb9dfbb3814875f9a0ad66845d`。具体动态、独立编辑与正式媒体证据见[最终检查](qa-final.md)。历史媒体与源见[原版索引](revisions/pre-flow-map.json)。

已由[PR #224](https://github.com/linhongcun/video-studio/pull/224)合并，随[v0.56.2](https://github.com/linhongcun/video-studio/releases/tag/v0.56.2)上线，并经[Release后Pages部署](https://github.com/linhongcun/video-studio/actions/runs/40118710238)成功。线上视频完整SHA与上述本地成片一致，字幕、章节、海报和更新日志已核验；#199已以completed关闭，见[线上证据](../../docs/flow-navigation-audit/online-verification.json)。本轮仅更新GitHub站点，用户对新版的观看反馈后续另记。

## 片尾参考资料补齐 · v0.72.1

[PR #348](https://github.com/linhongcun/video-studio/pull/348)合并`e770b29f8832d46d83833f037ffb28bea0e2541e`后发布[v0.72.1](https://github.com/linhongcun/video-studio/releases/tag/v0.72.1)，Release后[Pages40303351556](https://github.com/linhongcun/video-studio/actions/runs/40303351556)成功；2026-10-26T18:02:47+08:00线上核验通过。

本期5项原始题名与作者/机构，2页、每页5秒；最终5455帧，完整SHA-256：`62f24413506dd827620ee98e293e79b0b9672a4674a59e54e92c366ed897ab5a`。原Git正文全帧/PTS、AAC/PCM、原文/脚注及创建/首发信息保持；技术实读24日与26日题名补证分别记录，无新配音、正文重渲或平台重发。

本批11项/4页、503当前冻结/451旧记录、15实际尾帧、6组播放器/8张截图及13项完整GET通过。原存量累计26期，全站27片有资料附录（含新Redis跳表），见[第七批证据](../../docs/reference-endcards/batch-7/README.md)。不预记新版观看认可。
