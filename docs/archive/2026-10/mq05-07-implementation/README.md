# MQ05–MQ07实现机制短片

2026-10-30，北京时间。用户在前四期重制后肯定实现深度与可理解性的平衡，并授权继续数期。本批按题库顺序制作三期，固定源码、独立配音前审稿、最小运行和声音信号检查已完成，三期独立动态复核后已冻结并完成正式编码，实际成片与12幅JPEG已全部通过非作者复核，本地网页226项动作/66严格PTS和实际图审通过，正式构建55份媒体附录、54篇文章与日期/RSS检查通过；当前准备合并发布，线上核验尚未执行，不预记交付完成。

| 选题 | 新身份 | 核心实现因果 |
|---|---|---|
| [MQ05 / #313](https://github.com/linhongcun/video-studio/issues/313) | EP45 / kafka-consumer-idempotency | 同一逻辑键的唯一约束仲裁，去重与积分同一本地事务 |
| [MQ06 / #314](https://github.com/linhongcun/video-studio/issues/314) | EP46 / kafka-message-ordering | 同Key路由、分区日志与应用完成顺序的连接 |
| [MQ07 / #315](https://github.com/linhongcun/video-studio/issues/315) | EP47 / kafka-message-backlog | 分区归属、受限业务步骤与按分区计算的积压变化 |

每期独立建立对象与必要条件，同一事件贯穿推导，短代码服务因果，复杂支线放图文。固定Kafka/Java4.4.0 commit `1156b2752aaa28eafc0b4c4d387e63356793268d`；MQ05另核PostgreSQL18.0 commit `3d6a828938a5fa0444275d3d2f67b64ec3199eb7`。源码事实、有限模型、真实最小运行和媒体/站点检查分别留证，配音前独立审确切旁白版本。

开工clean最新主干`f01411f7e2a2d1cef480cd0f6b73d4c29d7169f3`，分支`codex/mq05-07-implementation-20261030`。[基线](baseline.json)保护1348份既有发布Gitblob与9051份旧MQ冻结实际文件的SHA/mtime；仅新增三个发布目录，不覆盖旧片。新依赖按当前保留工程锁文件fresh安装，系统字体在[本批账本](font-environment.json)单独记录。

原封面catalog与renderer已在旧冻结中，因此以[独立输入](../../../../episodes-codex/_shared/kafka-covers-mq05-07/README.md)扩展本批，沿原不可变Kafka风格，不修改旧目录或重生成旧封面。封面图、实际声音、时序、文章原文与图位均须在正式冻结前定稿。

[编辑闸门](qa/editorial-matrix.json)记录14/14/12镜、28/28/24句的确切旁白与全稿SHA。三套正式封面已经9张实际JPEG独立审图、12字体压力布局与严格安装核对；MQ07初版缺少同组条件，已保留旧证据并定向补字，MQ05/06的18份SVG/PNG/JPG逐字节保持。字体账本另补封面数字实际使用的DejaVu Sans Bold，原四个字体文件及绑定不变。

本批实际运行分别完成MQ05的89项、MQ06的12项、MQ07的20项断言，按各run的真实范围留证。MQ05为本地Kafka与PostgreSQL的恢复及并发事务；MQ06投影是实际Java调度，不执行支付；MQ07的稳定分配与独立单成员poll门控分开，不是吞吐benchmark。媒体、声音信号和逐镜动态仍须各自验收，不能用实验数量替代讲解质量。

最终声音为5497/4966/6058正文帧，共80句，身份和实际信号范围见[声音闸门](qa/voice-stage-final.json)。7个新增同文候选请求最终替换6句，原take/初始候选与失败信号报告保持；未做逐字ASR或全片实时人工语义听辨。初次MQ05装配缺userScope元数据被canonical拦截，补字段后复用同一声轨、words字节相同；封面元数据与MQ06本体图像的等价范围也另行留证，未为元数据错误重配声音。

仅GitHub与本站。总览[#308](https://github.com/linhongcun/video-studio/issues/308)当前仍4/9已交付，本批3题制作中，MQ08/MQ15未开工，原14题取消保持；完成Release后部署、完整线上文件与原生交互核验，再关闭对应制作issue。既有用户正向反馈针对上轮当前表达，不追认为本批已获观看认可或学习效果测量。


正式编码为5647/5116/6208帧（各含150帧原题/机构资料列表），实际媒体身份见[媒体清单](media-summary.json)。三个新清单分别218/253/189项，共660项声明，逐期只读验证通过；编码后再次核对9051份旧冻结输入与1348份既有发布文件不变。新增QA bundle缓存明确忽略，源码、原始take、失败/候选记录与实际复核证据保留。

最终12幅文章JPEG已由根代理逐张实际查看，记录在[额外图像复核](qa/root-final-jpegs.json)；每期仍由非作者分别核实际MP4和全部4张JPEG，不能用额外审图替代该闸门。本地安装先保持draft并用SHOW_DRAFTS预览，首发时间只在正式发布工作流开始时写入，实际发布以Release后成功部署与线上核验为准。

正式首发元数据在实际工作流开始时写入，预览媒体/图文/运行代码逐SHA不变，见[发布阶段记录](publication.json)。本地原生控件在暂停截图遮暗底部字幕、受控preload/load海报出现加载弧等观察均保留，不宣称清洁海报或暂停字幕完全无遮挡。
