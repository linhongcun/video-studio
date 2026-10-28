# MySQL四期正文与系列范围统一

日期：2026-10-28。四期正式制作、独立媒体复核和最终网站验收已完成；GitHub发布身份与部署结果见下方Release链接的publication.json。

范围为EP15索引、EP16事务、EP17锁、EP18主从复制；从d7a5d768/v0.83.1最新main开工，先保存原发布MP4和metadata/receipt/cover-style身份。系列显示名、封面与文章开头统一为MySQL，内部database ID、旧URL、原问题式标题与历史身份保留。索引/事务/锁明确MySQL 8.4 InnoDB，复制明确MySQL 8.4单主异步；四期原技术依据已适用，不须新录旁白。通用数据库名词与Oracle / MySQL机构署名保留。

新封面为`episodes-codex/_shared/mysql-covers/`，正文为`_shared/mysql-video/`与各期`src/mysql-style/`，独立冻结位于`revisions/mysql-style/`。旧database-covers、原模型、制作稿、字幕/分镜/声音及旧冻结保留历史字节；54项保护记录见[preservation-baseline.json](preservation-baseline.json)。四篇发布稿只增加范围与摘要，原引文、图位、回看时间保留；[稿件派生](site-article-derivation.json)与[最终安装](final-media-summary.json)分别记录文字和媒体身份。

## 已完成的制作检查

- 12个三比例封面实际独立查看、字体/边界与安全区检查通过，见[封面复核](independent-cover-review.md)。封面另建六输入，不重写旧模板。
- 174个唯一逐镜预检帧通过，共实际渲染177次；索引两条标签首次距字幕不足，严格限定4处坐标后补查3帧，原失败图和报告保留，见[预检摘要](preflight-summary.json)与[正文审查](independent-body-preflight.md)。
- 四片独立输入47/52/47/48项，完整AAC载荷/时间戳/PCM与旧片相同，正式片正文帧及PTS在追加原题参考页后保持。30张正式归档图及复制2张额外条件帧逐张独立查看通过，见[正式终审](independent-final-review.md)及[最终媒体报告](final-media-summary.json)。
- 共享媒体核心只通过私有薄adapter复用，旧脚本未修改；合成小样追加、实际生产索引片只读verify及生产SHA/大小/mtime不变检查通过，见[工具复核](independent-tool-review.md)与[生产verify](production-verify.json)。未对其余三片重复全解码。

版本为v0.84.0，因本轮同时更新站点系列名称、标签与学习介绍。最终网站检查针对候选`c213222d6f0fc1d652206c46a1b367602ea82de2`完成一次完整构建：49日期/附录、48文章/73引文/55配图、133生成页与48 Pagefind页通过。双视口（1440/390）实际检查4期播放/暂停/全屏/原生字幕正文与参考页、24视频章节、21正文锚点、8关联目标、4幅图回看与原文键盘浮层，0页面/控制台错误和横向溢出；完整媒体/海报/配图HTTP SHA匹配。QA过程修正了章节锚点子集、seek hash数值精度与合成截图等待等脚本误判，未改变生产文件或重复构建；最终报告与截图见[网站验收](site-final/)。发布只限GitHub本站。正式Release入口为[v0.84.0](https://github.com/linhongcun/video-studio/releases/tag/v0.84.0)，实际发布身份/部署运行与网络能力边界以该Release链接的publication.json为准，未写入前不表示已发布。最终QA后的补充仅为文档与检查证据，生产路径与被验候选一致。

本轮没有新的用户观看反馈、全片人工听辨、ASR或真机验证；2026-10-24来源实读身份保留，不声称新官网GET。当前环境阻止canonical域名，若发布后仍受限，独立记录失败，不将本地HTTP/GitHub源SHA称为canonical线上完整SHA。
