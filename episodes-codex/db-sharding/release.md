# 数据库身份修订（#230）

订单太多，一个数据库装不下怎么办？：保留原配音、字幕与3760帧时长，给真实库角色增加MySQL识别标记，内部记录与提交范围保持。

当前视频完整SHA-256：`17f048ef7071e2c5d9ad7b53976c47c3cf0f1419253970fc811be8b3f366668d`；原混合AAC逐字节保持。正式媒体/预演/fresh复现的实际范围见[本轮QA](qa-mysql-identity.json)。图标来源为Devicon，原始SVG、MIT notice和品牌说明见[共享素材](../_shared/database-identity/source.json)，不称官方授权素材。

[PR #235](https://github.com/linhongcun/video-studio/pull/235)已合并，随[v0.58.1](https://github.com/linhongcun/video-studio/releases/tag/v0.58.1)发布；[Release后Pages部署](https://github.com/linhongcun/video-studio/actions/runs/40147968820)成功。线上10支完整视频SHA、字幕、章节、封面、源链接与实际更新日志核验通过，#230已以completed关闭。仅更新GitHub站点，用户对新版的观看反馈后续另记。

[实际线上证据](../../docs/mysql-database-identity/online-verification.json)。

## 历史发布记录

# EP.19 站点发布记录

2026-10-24，按用户已授权的旧版重制任务及GitHub持续发布流程，将本期纳入v0.45.4的EP.18–21批次。只上站点，不重发平台。本期按制作和独立检查结果发布，没有将其记为用户已经观看认可。

视频SHA-256：`ff3d0ba1bcb8969b4f22ebbc7d0f09bc9f9567cf494b3f9a345a3ba89cccf3b7`，规格1920×1080、30fps、3760帧、125.333秒。`episodes/db-sharding/video.mp4` 使用同一份冻结成片，不在发布阶段重新生成音频或画面。

站点同步文章、研究、脚本、封面、海报、冻结分镜 `storyboard.4a97df30.json` 与28句字幕，设置实际 `finalVideoFrames`，移除旧时序与旧版标记。保留原发布日期、首发版本和平台链接。当前入口见 [README.md](README.md)。

制作检查证据见 [qa-motion.md](qa-motion.md)、[qa-final.md](qa-final.md)、[source-sha256.json](source-sha256.json) 与 [render-result.json](render-result.json)。检查包括真实编码抽帧、全部字幕/冻结输入核对及完整媒体解码；没有可用官方ASR权重，不声称已做逐字ASR或全片人工听辨。

发布顺序：本地站点构建与逐项核验 → PR合并 → 附注tag及Release → Release后再次部署Pages → 核验线上完整视频SHA、海报、全部VTT、章节、时长及更新日志 → 将对应 [#71](https://github.com/linhongcun/video-studio/issues/71) 以 `completed` 关闭。未执行的平台新发事项不勾选完成。
