# MySQL 正式成片独立复核

审核日期：2026-10-28 UTC。审核者：`mysql_content_audit`。本记录对应工作区候选成片；检查时 `HEAD` 仍为 `d7a5d7682080232617a03cc988b7c25cb50446f4`，不能把该提交声称为已包含本次 MySQL 修改的提交。

审核者未实现封面模板、正文 UI、编码或安装。此前仅提供 MySQL 内容范围建议并独立审核封面及正文预检。本轮只读核对实际成片、抽帧和记录，只新增本文件；未修改生产输入、旧冻结资料或运行新 TTS。

## 当前结论

| 期数 | 成片 | 结论 |
| --- | --- | --- |
| EP.15 | `db-index` | 正式成片抽帧、实际文件身份及记录一致性通过 |
| EP.16 | `db-transaction` | 正式成片抽帧、实际文件身份及记录一致性通过 |
| EP.17 | `db-lock` | 正式成片抽帧、实际文件身份及记录一致性通过 |
| EP.18 | `db-replication` | 正式成片抽帧、实际文件身份及记录一致性通过 |

## 实际画面检查

分两轮逐张以 `view_image` 打开下列全部 30 张 PNG，并重新计算每张文件的完整 SHA-256，均匹配各自 `final-media-check.json` 的 sample 记录。它们是正式 MP4 抽帧，本轮未以预检图代替终版图。另为覆盖复制的两个关键条件，从实际发布 MP4 短时 seek 提取并实际查看 2 张临时 PNG，合计实际查看 32 张正式媒体画面。

| 成片 | 实际逐张查看的文件 | 对应帧 |
| --- | --- | --- |
| `db-index` | `final/db-index/frame-01.png` 至 `frame-08.png` | 0、1962、2700、2899、3923、3924、3999、4073 |
| `db-transaction` | `final/db-transaction/frame-01.png` 至 `frame-07.png` | 0、2033、2040、4065、4066、4141、4215 |
| `db-lock` | `final/db-lock/frame-01.png` 至 `frame-08.png` | 0、1728、1806、2220、3456、3457、3532、3606 |
| `db-replication` | `final/db-replication/frame-01.png` 至 `frame-07.png` | 0、1780、2310、3559、3560、3635、3709 |

索引、事务、锁正文均清楚显示 `MySQL 8.4 · InnoDB`；复制正文明确显示 `MySQL 8.4 · 单主异步复制`。四片对应 EP 标识、墨绿底、薄荷绿确认态、琥珀色待处理态、相同细线与圆柱标识，与已独立检查的 MySQL 封面属于同一家族。正文首、中、末以及参考资料首、中、末抽帧未见文字裁切、字幕压住图示或边界不清。

索引的结构镜保留“对应记录（示意）”及“编号表示对应关系”，订单 7042 通过示意编号 06 对应原订单记录，未把编号包装成真实物理地址。查找比较镜的正式帧 2899 已包含之前四坐标修正：两表上移、两条说明上移，说明与字幕之间有可辨间距。示例/结构示意/非性能实测的范围文字可见。资料卡两条原题 `How MySQL Uses Indexes`、`Clustered and Secondary Indexes` 及 `Oracle / MySQL` 署名完整。

事务片显示同一数据库、示例数据、非真实转账的前提，提交结果 800/700 与前序账户示例一致。参考资料卡四条原题及各自 `Oracle · MySQL` 署名完整，最长的第二条也未裁切：

1. `autocommit, Commit, and Rollback`
2. `START TRANSACTION, COMMIT, and ROLLBACK Statements`
3. `InnoDB Recovery`
4. `InnoDB Error Handling`

锁片的正式帧 1806 在 SQL 下完整显示“显式事务 · 主键精确查找已存在记录”，与 `SELECT stock FROM goods WHERE id=7042 FOR UPDATE;` 同时可读，和下方旁白字幕之间有清楚间距。帧 1728 是同一段文字淡入中的状态，并非丢失注记；帧 2220 表达甲持锁、修改待确认，乙仍在等待查询返回。资料卡 `Locking Reads`、`InnoDB Locking` 及各自 `Oracle / MySQL` 署名完整。

复制片正式帧 1780 显示同一条记录在主库为青禾、从库仍为阿青；帧 2310 显示本次更改应用完成后从库才变为青禾。补查的实际 MP4 帧 2285 同时显示“接收更改，还要应用更改”、从库仍为阿青、“已接收 · 待应用”和“待应用：青禾”，接收与应用未混为一谈。实际帧 3007 清楚显示“刚改后，要立刻核对：新查询定向主库”及“本例：主库已提交 · 新查询 · 无旧缓存”。源文件还保留“刚改后的新查询 → 同一主库”，配套文章明确同一已提交主库、新查询、无旧缓存和旧 REPEATABLE READ 快照的边界。

两张补查 PNG 仅生成于 `/tmp/mysql-final-independent-crnkegy5/`，未写入生产目录。使用 ffmpeg 输入前 `-ss <frame/30>` 精确 seek、只取 1 帧，未重新做完整视频或音频解码。帧 2285 PNG SHA 为 `a693096e1c0b76cf39abf3e4964a30291b86848292915f58668c9e383b761e3b`；帧 3007 PNG SHA 为 `5e57544a67a99df1dea0fa335b6786c6a989bb101023289ffe043348b544da4f`。两者绑定下表实际发布 MP4 的完整 SHA。

复制资料卡四条原题 `Replication Implementation`、`Replication Threads`、`Using Replication for Scale-Out`、`Semisynchronous Replication` 和各自 `Oracle / MySQL` 署名完整。四片合计 12 条资料原题均实际看过首、中、末资料页画面，未裁切或用概括词代替原题；将半同步资料列为边界来源不改变片头明确的单主异步范围。

`Oracle / MySQL` 或 `Oracle · MySQL` 在此为资料出版方署名，保留它不会把系列范围改回 Oracle Database。

## 实际文件身份与格式

对每片三个真实文件完整计算 SHA-256：`episodes-codex/<slug>/revisions/mysql-style/video.mp4`、制作根目录 `episodes-codex/<slug>/video.mp4`、发布目录 `episodes/<slug>/video.mp4`。同片三者字节数和 SHA 完全相同，并与 `final-media-check.json`、三份 `render-result.json`、三份参考资料 receipt 和 media check 的成片 SHA 一致。

| 成片 | 完整 MP4 SHA-256 | 字节数 | 正文 / 资料页 / 全片帧数 |
| --- | --- | --- | --- |
| `db-index` | `8d50530074cdd2cf5ddc8b14a2c7005fe8ceef1cebc708b12e482661f7254a38` | 7,041,468 | 3924 / 150 / 4074 |
| `db-transaction` | `4f85eecc5fade07a88b1e6dfcb19ede1839a6b3e4e05fe87682654e5491de7e6` | 8,665,552 | 4066 / 150 / 4216 |
| `db-lock` | `31b9cd29e376f42e72676fdfca5fc90b4ef8352190f44488dd9e740cb0c36f6f` | 5,748,644 | 3457 / 150 / 3607 |
| `db-replication` | `e931b5c07c3f21fc4e1e1637149bf6dca7feb1fed57545c090100f5075249223` | 6,644,341 | 3560 / 150 / 3710 |

实际对四个发布 MP4 运行 `ffprobe -show_streams -show_format`：均为 H.264、1920×1080、30/1 fps、视频起点 0、AAC 双声道 48 kHz。索引视频 4074 帧 / 135.800000 秒，音频 6133 包 / 130.816000 秒；事务视频 4216 帧 / 140.533333 秒，音频 6355 包 / 135.552000 秒；锁视频 3607 帧 / 120.233333 秒，音频 5403 包 / 115.242000 秒；复制视频 3710 帧 / 123.666667 秒，音频 5564 包 / 118.677000 秒。每片末尾 150 帧是资料页，未增加音频，与 receipt 叙述一致。

制作 revision、制作根目录、发布目录的 `render-result.json`、`reference-appendix.json`、`reference-appendix-media-check.json` 分别逐字节一致。发布 `meta.json` 的 `sourcePath` 指向实际 `revisions/mysql-style`，`finalVideoFrames`、`referenceAppendix.from`、`durationInFrames` 与实际媒体及 receipt 一致。系列内部稳定 key `database` 仍是路由/目录标识，公开摘要、描述及片内明确使用 MySQL；未把正常通用名词“数据库”批量替换。

| 成片 | final-media-check SHA-256 | 发布 meta.json SHA-256 |
| --- | --- | --- |
| `db-index` | `41efbca4087b60e8e1d2e8215e2137239be565b6f97fcd7e1f2d25d9ba26fbf5` | `5117d0114a7725abc63db3fa88316767146327f4a56d369ac8b13afe5339de86` |
| `db-transaction` | `967dff3b0f42e3faa5eb03078fb75e2ff16c49604633de152bede01254335149` | `92b209796faa4aa3fbccc4d4efba5624e198f9edbdb52aa072fa6b956aac8eb0` |
| `db-lock` | `e4a9c26c71755fa5eb027db9568087341b6331028067ac319f059fb37781ca11` | `73b475189fed658aedc755620bc9d946523f368a2ec69bca8f7214957dc19902` |
| `db-replication` | `732c079887ddf2545b1cd7d3a092aaff686fdd511155fc0aa693f77bdcd0b730` | `06480ee1815531e4c442a7ec63193cb611e85aff6d194e94212496cd11615c10` |

同时核对 publication article 及抽帧配图实际 SHA 均匹配 final-media-check。未重新宣称进行网络 GET 或变更原资料读取日期。

## 输入与既有完整保真证据

重新计算并核对四个新制作 manifest 的全部输入：索引 47 项、事务 52 项、锁 47 项、复制 48 项均与实际工作区文件一致，manifest 本身也匹配 render-result 所绑定的 SHA。补审结束时再次核对四期全部输入与 30 张已归档正式抽帧 SHA，前两期记录与审核时未变。

| 成片 | source-sha256.json 完整 SHA-256 | 实际 body.mp4 SHA-256 |
| --- | --- | --- |
| `db-index` | `367a5c4030bf51c88796c0f1ecf33916005236bd8e74e908c1302f50b65c8748` | `65fbdc163191aed63e450ccbaa17623e009a0389da4de7922447b5e18ae38f41` |
| `db-transaction` | `f7892951c01c9a7d33b4048a123dabaa3cbf7a909a102cfa33472140d4bf5e55` | `f7e584910fce7793e7dd2f4a00140c723d0daedbe26903b6ae2277ad35a0bb81` |
| `db-lock` | `618e15bf51012008221fcf092ce2573f4cf72ede69a0f85a57cc714ae9c9cee2` | `921e648008da0ce057a3685d014d46c39a3f5bdf4164b97fdd7b1c1c8f23242c` |
| `db-replication` | `b1c7ed99d9c1ade161d3b2a63973b13f7e625b6068e03ac0dd9e404c4ed436f3` | `7c3e2d06dc1f80af8d16ac7f6980ab0bfbe9938b5746de01b13ae89f83a09e1e` |

实际 baseline MP4 完整 SHA 也与 baseline-publication / baseline-audio-check 一致：索引 `88af7cc11e10691a70986bdecb29542f394822d95871fb50fe38765f74705e9e`，事务 `1aa298ef82ec025c72c8545f4fd771177849e5f4d6b5c3731f97b1f8dbb34430`，锁 `9796806d8e29d21bcdccbbf25d1d5a0ec091588701d4a9bc8a64d4128a7f554e`，复制 `5bd0683ca3855def55f4b7ef4fc78d53cbbad30afae19f336fe854562989faa8`。

已阅读四期既有 `baseline-audio-check.json` 和 `reference-appendix-media-check.json`，并核对它们在 render-result 中的绑定及 body/final/baseline 文件身份。四片报告均通过全部 AAC payload、PTS/DTS/duration、PCM 等同性检查，以及正文全部解码帧/时间戳保留、视频时间线连续检查。本轮不重复这些全解码工作，不把读取报告说成独立重新执行。

| 成片 | AAC payload+timing SHA-256（报告） | 解码 PCM SHA-256（报告） |
| --- | --- | --- |
| `db-index` | `d451ae31c605dc906e74b6420b370a5aa06b03dcd0fdd522c7c18934889c35e9` | `c946d146ac75a2a46821e1a07e663185e6b283965ba977b11c7dc177d7dcbb0d` |
| `db-transaction` | `877c6b60914a93791c32c05e943549e1b95aecb7aadc19814f0d18fb97f046d8` | `69541d54052d28de8387a8a5d6ac0aa89bb3f681b80fd30001831fecad2c208d` |
| `db-lock` | `5e06b9501caafba2ce6f93b96417e392f5eb8a7ddb1fe441c757dcdc71278802` | `2a702c4876094df43e7daa432c2bd0d0a4d036cd497a95e0243434fb0e5defa5` |
| `db-replication` | `e3fb9f64ab76ef782b125d611499cb91cea44256cb4597cad979ee3db882faa2` | `f26d70a7f71a09546ab0a7612f9db5440c4febfe4ce79ab939f3880896f7c27f` |

边界：这是独立源差异/预检审查之后的四期正式媒体文件及抽帧复核；本轮未运行连续全片播放器观看、听音/ASR、手机端播放或网站浏览器验收。未新增 production render/install。四期本层审核均通过，记录写入完成后停止写入，留给后续编码/发布门禁使用。
