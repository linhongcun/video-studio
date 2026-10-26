# 配套图文统一

本轮将视频下方文章的精确原文引用与有效正文配图作为共同交付要求，并统一模块、图注和来源区样式。规范见 [RULES](../RULES.md#配套图文)，写作入口见 [article-style](../article-style.md)。

## 基线与范围

开工工作区干净，先 fetch 后快进主干至 `4213a233c4c242b04453b8c1215031dc421c2398`，在 `codex/unified-articles` 制作。重新读取现行规范、调研与发布手册、站点源码入口和当前锁文件；依赖使用 `site/package-lock.json`，没有从已删除工程借用依赖。

基线共48篇：47篇当前文章、1篇历史归档（`distributed-tx`），没有草稿。当前文章18篇含精确摘录、16篇有独立引用块、5篇有正文SVG共8幅，27篇两项均无；独立引用与配图兼具1篇。基线文章和既有发布文件的完整SHA见 [baseline.json](baseline.json)。

本轮只对当前47篇发布文章补图与引用、统一来源标题和阅读模块，保留正文论证、完整代码、章节锚点与既有出处；历史归档保留原稿。制作目录的冻结文章、已编码视频与旧输入清单保持原身份。引用先复用实际核对的历史原文，缺失时实际阅读并保存新证据，历史访问日期与新访问日期分别保留。截图从实际发布MP4抽取，图注描述所选状态并带准确秒数。

## 验证与交付

47篇当前文章全部具有精确引用和有效正文图，共67处 `SourceQuote`、50幅配图（42张新增实际视频关键帧、8幅既有SVG）。来源区统一命名，原文就近放置；原始代码块、章节锚点及既有HTTPS链接全部保留。47篇更新时间反映本轮配套讲解变化，创建与首发时间保持。逐篇编辑与看图证据见 [A组](group-a.json)、[B组](group-b.json)、[C组](group-c.json)，跨组来源/语义独立复核见 [B组复核](independent-b.json)、[C组复核](independent-c.json)。

文章独有来源保存实际实读证据。TinyFish提供的是页面提取正文及规范化阅读文本，不是原HTTP响应字节；Stripe无关认证示例已省略并标注，短引和上下文保留。doocs题面明确为第三方镜像，只支撑题意/限制，不冒充官方题解或正确性证明。未重新访问的资料保留原核验日期。

- [构建](build.log)：当前锁文件 `npm ci` 后完整 `npm run build` 成功，47篇进入搜索。首次真实构建发现打包后 `import.meta.url` 的目录变化，修正为查找实际仓根；[失败记录](build-attempt-1.log)保留。后续[成功构建](build-attempt-2.log)后，手机看图增加原图入口，再完成最终构建。
- [测试](tests.log)：91项全部通过，覆盖实际引用解析、准确证据、来源身份、路径边界、时间范围、隐藏/代码/无slot子内容不计数及既有参考附录检查。
- [浏览器](browser-review.json)：真实Chromium桌面1440亮色/手机390暗色共94页面通过，所有实际引用与源数据相同，42图加载并与原文件同SHA，无横向溢出；三篇各双视口共6次精确时间回看，另双视口实际点击原图通过。16张[代表截图](screenshots/)记录引用卡、视频图与原生SVG；另有[四组合独立检查](components-review.json)。模拟视口不扩大为真机或阅读效果测量。
- [保留核对](preservation.json)：48篇的原代码、锚点和旧链接保持；869项既有发布文件逐一比较，除47项 `updatedAt` 外无变化，包含全部原MP4、海报、分镜、资料及旧回执。制作冻结稿未修改，归档全文未修改。
- [密钥检查](secret-scan.log)通过，`git diff --check` 通过。

[PR #356](https://github.com/linhongcun/video-studio/pull/356) 已合并至 `c3666b42fe7e6ddcc01430d5d5d807dddcf5aa0e`，发布 [v0.73.0](https://github.com/linhongcun/video-studio/releases/tag/v0.73.0)，[Pages 40327319665](https://github.com/linhongcun/video-studio/actions/runs/40327319665) 成功。Release于13:03:48 UTC发布，成功构建任务于13:03:56 UTC开始，因此实际构建已读取Release；线上更新日志已确认包含此版本，取消了相同提交的冗余排队手动运行40327399053。完整身份见 [publication.json](publication.json)。

2026-10-26T21:10:22.947449+08:00完成96项规范URL核验：47篇线上原文/出处/图片/回看时间/日期与当前构建一致，42张新增图片完整SHA一致，另核对3条原视频与海报的完整SHA、更新日志。详细响应摘要及范围见 [online-verification.json](online-verification.json)，脚本见 [verify-online.py](verify-online.py)。原视频未改变，本轮未重复全站成片解码或配音复核。检查说明实际交付范围，不代表用户已观看认可。
