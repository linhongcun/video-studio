# EP.16 参考资料名单补齐（v0.71.3）

[PR #346](https://github.com/linhongcun/video-studio/pull/346)已合并为`8f97995ec92919df5de4a18d05738c3c31e06b37`，并已创建[Release v0.71.3](https://github.com/linhongcun/video-studio/releases/tag/v0.71.3)。Release后的[Pages部署40291951904](https://github.com/linhongcun/video-studio/actions/runs/40291951904)成功；2026-10-26T16:30:13+08:00完成13项规范URL完整GET，三片完整视频SHA、海报、VTT、资料/章节/日期和更新日志通过，见[线上核验](../../docs/reference-endcards/batch-5/online-verification.json)。

本期追加4项MySQL资料，单页5秒，只显示完整原始题名与作者/机构。沿用2026-10-24的真实实读记录，本轮Git/blob及机构核对不冒称新的官方GET；记录SHA标识保留的研究笔记，不当作完整MySQL响应正文的摘要。来源`checkedAt`仍为2026-10-24，内容修改时间保持`2026-10-26T15:58:45+08:00`，创建/首发时间、首发版本和历史平台链接均保留。

原Git发布主体4066帧完整字节用作追加输入，新增150帧资料卡；最终4216帧（140.533秒），完整SHA-256为`1aa298ef82ec025c72c8545f4fd771177849e5f4d6b5c3731f97b1f8dbb34430`。生产追加器确认全部原帧/PTS、AAC包及PCM保留，未新增配音或音频包，未重渲正文或重新混音。

本批三片共8项资料，当前340项冻结与旧57项窄历史记录分开保留；新薄入口不重写SB、words或placeholder，也不把新增依赖说成旧片已按新清单重现。独立实际尾帧、本地来源与6组浏览器检查通过；3次桌面尾段播放到结束、3次手机原生全屏及必要截图按实际范围记录。没有新ASR、全片人工听辨或本版用户观看结论。

本期生成VTT全文和原章节保持；本批字幕修正仅涉及索引片末cue的1毫秒边界，其余46份VTT字节保持。

实际制作、QA及发布证据见[第5批记录](../../docs/reference-endcards/batch-5/README.md)。累计20片已完成资料卡与正式线上核验。仅GitHub站点，无平台重发。

## 既往主体与身份修订记录

# 数据库身份修订（#230）

扣了钱，对方没到账？：保留原配音、字幕与4066帧时长，给真实库角色增加MySQL识别标记，内部记录与提交范围保持。

当前视频完整SHA-256：`66b2075f55dc68d673ed16347049d2c597949a30f12f803ef6f92f98522cc690`；原混合AAC逐字节保持。正式媒体/预演/fresh复现的实际范围见[本轮QA](qa-mysql-identity.json)。图标来源为Devicon，原始SVG、MIT notice和品牌说明见[共享素材](../_shared/database-identity/source.json)，不称官方授权素材。

[PR #235](https://github.com/linhongcun/video-studio/pull/235)已合并，随[v0.58.1](https://github.com/linhongcun/video-studio/releases/tag/v0.58.1)发布；[Release后Pages部署](https://github.com/linhongcun/video-studio/actions/runs/40147968820)成功。线上10支完整视频SHA、字幕、章节、封面、源链接与实际更新日志核验通过，#230已以completed关闭。仅更新GitHub站点，用户对新版的观看反馈后续另记。

[实际线上证据](../../docs/mysql-database-identity/online-verification.json)。

## 历史发布记录

# EP.16 第二版站点发布记录

2026-10-24（北京时间），用户观看第二版后表示“这次就符合预期了”，随后明确要求“代码给合并到主干分支，然后将视频部署到GitHub上了”。本次按 v0.45.2 发布第16期数据库事务重制，只上站点，不重发平台。

批准视频的 SHA-256：`6aa379dd588eed8f22c9bc832a2175227b01dda2658d5b52d16e1d83af4b0a58`。直接复制批准的第二版，不重新渲染；站点 `episodes/db-transaction/video.mp4` 必须与本工程 `video.mp4` 逐字节一致。

- 成片：1920×1080、30 fps、4066 帧，容器时长135.552秒；综合响度−16.0 LUFS，真峰值−3.7 dBTP。
- 站点更新视频、三种封面、文章、公开资料笔记、冻结分镜和句级字幕；去掉旧版标记、旧比喻及75秒描述。
- 删除旧顶层与 Remotion 的 `timing.json`，避免站点用旧镜长覆盖冻结时序；`meta.finalVideoFrames` 固定4066帧。章节直接使用分镜真实起点，外挂字幕使用31句冻结 `from/to`。
- 制作源码、第一版对照源码及检查记录留在本目录。第一版归档视频和本地第二版观看副本不重复入库。选中的 TTS takes 保留；原始响应、未选候选和可再生缓存不入库。
- 原始 `publishedAt`、`firstRelease` 与平台历史链接保留。平台链接仍指向此前上传版本，不把站点重制当作平台已重发，也不自动关闭 #67 中的平台发布事项。

配音与成片 QA 按各自执行时的范围保留；用户后续质量认可和上线授权记录在此，不将未完成的逐字 ASR 改写为通过。

发布顺序：站点构建与文件一致性检查 → PR 合并 → 附注 tag 与 GitHub Release → 再次部署 Pages → 核对线上视频完整 SHA、海报、31条字幕、章节和更新日志。
