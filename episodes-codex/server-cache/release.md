# 数据库身份修订（#230）

数据库明明有数据，为什么还要再存一份？：保留原配音、字幕与3491帧时长，给真实库角色增加MySQL识别标记，内部记录与提交范围保持。

当前视频完整SHA-256：`eacd015f1b38c34e32a0b89e0b0efd16fecf07de84d30649d9d36e692c8c258f`；原混合AAC逐字节保持。正式媒体/预演/fresh复现的实际范围见[本轮QA](qa-mysql-identity.json)。图标来源为Devicon，原始SVG、MIT notice和品牌说明见[共享素材](../_shared/database-identity/source.json)，不称官方授权素材。

拟随v0.57.2合并主干、Release后部署；线上完整文件、字幕、章节、封面与日志通过后关闭#230。只上GitHub站点，不预写用户观看认可。

## 历史发布记录

# EP.08 站点发布记录

2026-10-24 19:53:36（北京时间），按用户持续授权发布[v0.48.0](https://github.com/linhongcun/video-studio/releases/tag/v0.48.0)，只上GitHub站点，保留历史平台投稿。

- 媒体[PR](https://github.com/linhongcun/video-studio/pull/151)，合并提交 `81ced01a028827ddff1c66138e2d718031ddfdc1`；Release后再次[部署](https://github.com/linhongcun/video-studio/actions/runs/40091595906)。
- 成片3491帧，完整SHA-256：`185ef935abb55e776ee44a2e5b174e0ce3cbafaf19964e72e807eedbdf3ba456`。
- 本地制作检查、冻结输入、实际编码抽帧、站点构建及浏览器验证见本期QA和批次记录。
- 线上canonical视频、海报完整SHA与字节数、VTT逐字节、HTML章节/标题/源码入口，以及首页版本、更新日志实际Release链接均已核验。
- [完整线上证明](../../docs/codex-remake-ep01-14/online.json)保留逐项GET结果；检查不冒充完整人工播放、逐字ASR或独立完整听辨。

按持续授权自主发布不表示用户已经观看认可。后续反馈应重新冻结受影响输入并检查、发布。
