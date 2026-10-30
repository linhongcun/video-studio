# MQ05–MQ07实现机制短片

2026-10-30开工，2026-10-31北京时间完成交付。三期正式视频、配套图文与封面已随[PR #447](https://github.com/linhongcun/video-studio/pull/447)合并`dcaafde2e30c7fde688e0744d45f2e4e1131c46e`，附注tag/[Release v0.97.0](https://github.com/linhongcun/video-studio/releases/tag/v0.97.0)发布后[Pages41100736996](https://github.com/linhongcun/video-studio/actions/runs/41100736996)成功。31次普通canonical完整GET及线上原生226动作/66严格PTS和实际图审通过；#313/#314/#315在完成线上验收后以completed关闭。系列现7/9，MQ08/MQ15未开工，原14项取消保持。仅GitHub与本站，无外部平台新发。

| 已交付 | 制作issue | 最终帧数 / 时长（30fps） | 完整MP4 SHA-256 |
|---|---|---|---|
| [MQ05 / EP45 · 消费幂等](https://linhongcun.github.io/video-studio/episodes/kafka-consumer-idempotency/) | #313 | 5647 / 188.2333秒 | `5d14be81eed533acea8738e0c883b3c44b298789e74a53d1b7a24a0624f66328` |
| [MQ06 / EP46 · 消息保序](https://linhongcun.github.io/video-studio/episodes/kafka-message-ordering/) | #314 | 5116 / 170.5333秒 | `6e05b178ce8f183e475d0f2aac260988b7f056cf2ddd27ae17188c95b6dca4d8` |
| [MQ07 / EP47 · 消息积压](https://linhongcun.github.io/video-studio/episodes/kafka-message-backlog/) | #315 | 6208 / 206.9333秒 | `81781a4d0973c4e2ec1d90505e3f5d009c1c07eb10b664a5e7ec9497da111bcf` |

每片含150帧原题/机构资料列表，共12幅从正式成片精确整数帧导出的正文图与80句旁白。[媒体清单](media-summary.json)、[发布记录](publication.json)、[issue关闭回执](issues-completed.json)记录确切身份。创建时间保留2026-10-30T23:02:51+08:00，实质内容安装时间为10-31T01:26:41+08:00；首发元数据在真实发布工作流开始10-31T01:36:34+08:00写入，明确不冒充实际部署完成时刻。

用户在上轮四期重制后肯定实现深度与可理解性的平衡，本批据此继续三题；此反馈针对上轮表达，不追认为本批已获观看认可或已测量学习效果。每期独立建立对象与条件，同一事件贯穿“结构保存什么→何时判断→状态为何变化”，必要术语随动作引入，完整旁支留文章。

## 实现与运行的实际范围

固定Kafka/Java4.4.0 commit `1156b2752aaa28eafc0b4c4d387e63356793268d`；MQ05另核PostgreSQL18.0 commit `3d6a828938a5fa0444275d3d2f67b64ec3199eb7`。确切旁白版本先过[独立编辑闸门](qa/editorial-matrix.json)才进入TTS；原题、署名、原文和永久定位留在各期sources、references及article-sources中。

- MQ05：同一逻辑业务与E01竞争非空、立即唯一键；冲突先等待未决事务结局再重查，只有本次RETURNING新行才放行业务增量，登记与积分在同一本地事务提交或回滚。Kafka恢复只解释重读前提。真实运行89断言核对退出/重启、并发提交/回滚及目标更新失败；先查后写等错误分支是教学反例，不声称全部另跑过真实实验。
- MQ06：沿同Key路由、分区缓冲/日志、客户端收集到应用交付，再对照异步晚写与按订单串行完成。真实运行12断言使用实际Kafka记录和Java状态投影，不执行支付/退款。源码一次收集两条的合法路径，与实测两次poll各一条再聚合的范围分别说明。
- MQ07：两分区、十二同组成员按member.id排序形成两份非空与十份空列表；实际Fetch/poll之后仍要等待本例串行业务。真实运行20断言分别核稳定分配与独立单成员组的业务门控，不是十二成员通知接口benchmark。教学逐分区账目以明确流入/完成假设推导增长与十步排空，不把已拉取、提交lag或日志长度冒充业务完成数。

共121项真实运行断言，[运行记录](runtime/)与有限模型/媒体检查分别留证；临时业务服务已停止并清理。MQ07 C01…C12是排序后教学别名，不冒充实际client.id或加入次序。

## 冻结与成片

开工已从clean最新`origin/main`的`f01411f7e2a2d1cef480cd0f6b73d4c29d7169f3`建立制作分支；正式编码、发布及环境恢复后再次核对。[基线保护](baseline.json)中的1348份既有发布Gitblob和9051份旧冻结实际文件SHA/mtime均保持，三期新增218/253/189项冻结声明，共660项，所有声明路径均已提交且与core blob一致。默认入口完成正文、真实limitedBT709转换、混音与资料附录；5个实际字体文件及绑定单列[环境账本](font-environment.json)。

[声音闸门](qa/voice-stage-final.json)绑定5497/4966/6058正文帧。7个新增同文候选请求最终替换6句，原take、初始声音和失败信号报告保持；未做逐字ASR或全片实时人工语义听辨。初次装配缺userScope被canonical拦截，补元数据后复用同一声轨；MQ05初次冻结缺substitutions说明，未产生清单或开始编码，补生产说明后重走闸门，失败日志保留。MQ06封面元数据修正的等价范围另留证，没有为元数据错误重配声音。

各期非作者独立完成实际动态、最终MP4完整视频/AAC解码与精确抽帧、所有四张JPEG审图。MQ05标题完成态抢先在编码前修正，MQ07真实排序输入及SVG/圆形边角误报逐点实核；原源、失败观察、局部复用证明与短片保持，不扩大DOM规则豁免。根代理另实际查看12张JPEG、三片实际资料首帧及本地/线上各6张关键页面图。

原共享Kafka封面catalog/renderer已在旧冻结中，本批使用[独立封面输入](../../../../episodes-codex/_shared/kafka-covers-mq05-07/README.md)，保留原style-v1视觉。9张最终JPEG实审、12项字体压力布局通过；MQ07初版缺同组条件已定向修正并保留旧证据，MQ05/06原18份SVG/PNG/JPG逐字节不变。最终JPEG截图做真实tv709→pc601转换；默认8bit正文转换有已测的小幅舍入色差，状态色与对比清楚，不宣称与源PNG逐像素相等。

## 网站与实际线上验收

先安装为draft并SHOW_DRAFTS预览，三期各自保持无publishedAt/firstRelease；本地原生Chromium226动作/66严格实际PTS及图审通过后才整批准备正式首发。正式构建通过55份媒体附录、54篇文章/113原文/79正文图、55条日期及构建页/RSS核验；三期预览与正式发布媒体/文章字节一致。新期本次共22原文模块、12章与80条VTT。

[31完整GET](online-verification.json)无Range、cachebuster、重试或TLS绕过，三支完整MP4、3海报、3VTT和12图的SHA均与已验收文件一致，并检查实际入口、引用原文/URL、图位回看、七课目录、首发RSS和真实Release。此为完整传输证据，浏览器helper的空verifiedHttpResponses不冒充下载核验。

[线上原生验收](qa/online-site-accepted.json)每期均重新执行实际播放推进/暂停、章节/四图回放、原文悬停/点击或点按/键盘、出处滚动可达、资料与正文Fullscreen、原图导航及主题边界。图像由实际查看或逐文件SHA与已实看本地图完全相同后有界复用；1440/390及844×390为模拟视口，不是物理手机。受控preload/load后海报加载弧、暂停原生控件/渐变遮暗底部字幕、手机细字小与长引用内部滚动如实记录，不宣称清洁首载或暂停字幕完全无遮挡，也未隐藏控件。

GitHub曾出现502/504读取失败以及run/suite/单项检查/部署状态不一致、时间回填异常，[原回执](qa/github-deployment-state-diagnosis/)保留；只对本批重复push任务发起取消，没有重复dispatch或取消他人任务。随后实际workflow与Pages成功，加上完整GET与原生线上检查确认交付；不把控制面滞后归因为源码错误或未经核实的服务事件。环境恢复后旧输入保护和660声明再次验证通过。额外Release附件上传通道Forbidden，实际0份附件；三支正式MP4在main与本站，不能称已上传Release附件。

提交前使用不变canonical密钥规则并逐项审查5个确切SHA/行号绑定的公开源码标识符，无未解决匹配；不宣称原始扫描器直接无告警。生成bundle与node_modules不提交，实际source/take/失败记录及已审16段短片保留。冻结制作README保持当时身份，当前交付以本归档为准。
