# MySQL视频正文入口

当前用于EP.15索引、EP.16事务、EP.17锁、EP.18复制。正文和参考资料页读取`../mysql-covers/catalog.json`的墨绿/薄荷绿配色、字体与系列标识；索引/事务/锁明确MySQL 8.4与InnoDB，复制明确MySQL 8.4单主异步示例。普通名词数据库、schema与手册机构署名按实际含义保留。

新视觉副本在各期`remotion/src/mysql-style/`，继续读取原data/分镜/模型，独立清单位于`revisions/mysql-style/`，当前meta.sourcePath指向该修订。旧src/package/音轨/分镜/冻结及database-covers六输入保留历史字节，旧默认render不用于覆盖当前新片。

## 制作与检查

按本期当前package-lock安装npm ci，依赖集合完全相同可复用保留的当前制作工程。备好Chromium、ffmpeg、Pillow、Noto CJK SC。当前四锁非根依赖与保留horse-racing当前安装相同，可共用其ignored node_modules，不能指向已删除旧工程。

基线声音来自旧发布MP4，按revision/baseline-publication.json中的提交、路径及完整SHA从Git恢复到`work/mysql-video-style/baseline/<slug>.mp4`。浅克隆先fetch该历史提交；不得把新版片误当旧基线。新输入包含发布稿快照article.mdx，旧生产稿不改。所有元数据/基线快照在名称与文章更改之前保存，不能改写历史身份。

仓根执行：

```bash
node episodes-codex/_shared/mysql-video/qa.mjs <slug> --out-dir work/mysql-qa/<slug>
python3 episodes-codex/_shared/mysql-video/render.py <slug> --freeze
python3 episodes-codex/_shared/mysql-video/render.py <slug> --render
python3 episodes-codex/_shared/mysql-video/render.py <slug> --verify
```

默认仅plan，正式编码先来源预检和只读冻结核对。新薄wrapper私有复用已验证的puzzles-video媒体核心，不改旧模块或全局；实际依赖及MySQL素材来源/许可一起冻结。无声画面渲染后完整流拷贝基线AAC，逐包、时间戳和PCM核对；参考附录复用原题/作者排版，每页最多4项、5秒，墨绿adapter只注入本系列palette，不改旧引擎。原SQL/数据/运动与解释保持；索引删除旧装饰进度线并澄清逻辑定位，锁的FOR UPDATE旁补显式事务与主键定位前提。

QA仅在截图进程读取真实DOM，不在生产片加入审计Hook。检查实际字体、画布边界、字幕区与中间状态；通过静帧不等于整片动态或听辨。发布日期使用带时区的秒或最多三位毫秒ISO，避免Python默认微秒格式；完整元数据/媒体身份及站点检查通过后再发布。

产物与真实检查记录见docs/archive/2026-10/mysql-video-style；不预记新用户观看认可、ASR、全片人工听辨、真机或canonical线上完整SHA。历史来源实读日期保留，不因范围前置写成新官网GET。
