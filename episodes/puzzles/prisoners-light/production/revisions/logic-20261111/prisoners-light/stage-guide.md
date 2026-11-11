# P10 logic-20261111 发布接入指引

本文件只记录本修订的接入方案，不执行publication写入、冻结、编码或发布。当前实测旁白/分镜正文为6362帧（212.0666667秒），默认另追加150帧参考列表，预计最终6512帧（217.0666667秒）。最终帧数、媒体SHA、字节数和资料区间必须读取真实 `render-result.json`、`reference-appendix.json` 及 `reference-appendix-media-check.json`，本指引不预填或推定最终SHA。

## 五章时间

章节取本目录 `storyboard.json` 的场景起点；站点从分镜生成时间，不手工取一位小数代替精确帧。标题及id保持：

| id | 标题 | 起始帧 | 起始秒 |
|---|---|---:|---:|
| problem | 条件与要确认的事 | 0 | 0 |
| protocol | 约定谁发送、谁接收 | 895 | 895/30＝29.833333… |
| walkthrough | 四个人完整走一遍 | 2076 | 69.2 |
| guarantee | 为什么安全、为什么会结束 | 4809 | 160.3 |
| conclusion | 每个人只贡献一次 | 5869 | 5869/30＝195.633333… |

## 两处文章图位

当前文章按已维护的publication稿派生，仅改两个 `seekTo` 值，正文、标题结构、SourceQuote及出处均保持；差异计划见 `qa/article-timing-plan.json`。

| 图片 | 原帧/秒 | 保持的镜内位置 | 新精确帧 | 新seekTo |
|---|---|---|---:|---:|
| article/01.jpg | 2325 / 77.5 | 06镜local149 | 2631 | 87.7 |
| article/02.jpg | 4380 / 146 | 11镜local332 | 4686 | 156.2 |

文章基线完整SHA为 `30bf8b5589b98e87b9b5100773ad6a91c129c9c06a6602f9694e5f10be156666`，两处seek派生后的SHA为 `947f6cf9b947eb5fdb945663cc28ab9df2fd977acbf0992f170b76481428d568`。接入时再次核对，不能把后续未记录的正文变化并入本轮。

正式MP4通过检查后，运行本目录 `export-article.py`。它从帧零完整解码并选择2631、4686精确帧，用limited BT.709→full-range BT.601矩阵实际转换JPEG，仅输出本目录 `article/01.jpg`、`article/02.jpg` 和 `qa/article-image-export.json`；回执记旧发布图片SHA。图片须实际查看后再复制，生成成功不等于视觉验收。

## 发布副本和元数据

目标为仓根 `episodes/puzzles/prisoners-light/publication/`。主agent统一接入前先复核最新主干、本期当前发布身份与版本占用，保留其他人的变更。需要更新的文件：

- 本目录最终 `video.mp4`，不得使用 `remotion/out/body.mp4`；完整SHA须与真实render结果及两份附录回执一致。
- 本目录 `storyboard.json`、`script.md`、`article.mdx`。旁白身份是3句新take＋25句复用take，实际证据在 `input-provenance.json` 和本轮声音回执；不冒称全片重新配音或整条旧声轨保持。
- 本目录 `references.json`、`reference-appendix.json`、`reference-appendix-media-check.json`。来源证据仍指向原production的已核验研究身份；现有publication的 `research.md`、`research-evidence.json` 若同步，须核对与本修订复用文件同SHA，不另改核验日期或来源结论。
- 本目录经实际查看的 `article/01.jpg`、`article/02.jpg`。JPG封面、poster及cover-style保持当前原字节，不因本轮补逻辑重新渲染或覆盖。

`meta.json` 保留原 `slug`、`ep`、`episodePart`、`title`、`createdAt`、`publishedAt`、`firstRelease`、`series`、`related`、`platforms` 与封面路径。创建时间仍为 `2026-11-04T21:36:10+08:00`，首发时间 `2026-11-04T23:53:03+08:00`，首发版本 `v0.105.0`。仅将 `updatedAt` 设为实际接入时的北京时间ISO值，并设置：

- `sourcePath`：`episodes/puzzles/prisoners-light/production/revisions/logic-20261111/prisoners-light/remotion`。
- `finalVideoFrames`、`referenceAppendix`：完整采用真实 `render-result.json.publicationMetadata`。当前计划区间为正文 `[0,6362)`、资料 `[6362,6512)`，不得拿预计值覆盖不一致的实测回执。
- `targetDuration`：真实render结果的 `seconds`；保持实际烧录字幕事实 `burnedInCaptions: true`。

VTT由新分镜生成，预期28条字幕；章节、图片回看及深链均按上表核对。部署后核对canonical视频、海报、两图、VTT的完整SHA，以及页面版本、绑定实际构建提交的sourcePath、五章时间、两处图片回看和更新日志。本地浏览器动作与线上HTTP身份检查分别留证，不相互冒称。GitHub发布由主agent统一处理，不包含外部平台重发或本轮用户观看认可。

## 实际编码结果（2026-11-11）

默认入口已完成：最终6512帧／217.0666666667秒，11,313,057字节；完整SHA为 `a8bfe657f39ff9b08688ffd410775829ef593c116deb54cdb7612b825b4e018d`。实际正文/资料区间与上方计划相同，采用本目录render-result.json.publicationMetadata。完整解码和媒体身份、两图导出及制作者实看已完成，独立实际MP4的29帧视看已通过，见docs/archive/2026-11/puzzles-followup-logic/motion/prisoners-light/encoded-visual-review.json；本段不表示已接入或发布。
