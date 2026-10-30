# MQ01–MQ04实现原理重制

2026-10-30，北京时间。用户授权重制已发布四期MQ，增加实现深度并保持容易理解，本轮优先于继续MQ05。任务[#443](https://github.com/linhongcun/video-studio/issues/443)，系列[#308](https://github.com/linhongcun/video-studio/issues/308)。四条正式成片与图文已由PR #444合并，随v0.96.1更新原页面；Release后Pages与线上完整文件、原生交互及实际审图均已通过，#443已以completed关闭。

开工从clean最新`923305b49cea1b18d7fc7e4dd8ac70ad830bc673`建立`codex/mq01-04-source-remake-20261030`。保留原EP、slug、题名、创建/首发时间、封面与既有平台链接；新生产目录各为`episodes-codex/<slug>/revisions/source-depth-v2/`。旧#309–#312的completed与原交付保持历史身份，新#443已在本轮上线核验后以completed关闭。

| 身份 | 正文中的实现因果 | 实际成片 | 冻结输入项 |
|---|---|---|---|
| MQ01 / EP10 | 任务数据→分区日志追加→按位置读取→应用另执行业务 | 2:40 / 4811帧 | 182 |
| MQ02 / EP42 | classic Range分配表计算→同步安装→按归属表构造Fetch | 2:49 / 5076帧 | 183 |
| MQ03 / EP43 | 持久恢复值→新内存position→Fetch起点→原日志字节 | 2:38 / 4752帧 | 169 |
| MQ04 / EP44 | 分区批次/在途→同一结果完成；身份与完整序号范围→Broker判重 | 3:00 / 5412帧 | 204 |

[媒体完整SHA与字节](media-summary.json)、[站点安装/派生稿记录](publication-files.json)、[独立闸门](qa/independent-gate-ledger.json)。四片共53镜106句，20051帧，32,126,145字节；每片正文后实际追加150帧原题/机构资料，未把仅正文输出当最终视频。各期冻结清单保持182/183/169/204项，合计738个声明（共享项不冒称唯一文件）。

## 研究、演示与实际范围

固定Apache Kafka/Java4.4.0及官方commit`1156b2752aaa28eafc0b4c4d387e63356793268d`。先读执行结构/判断/更新，再以同一事件逐步解释；必要名称随对象引入，源码短卡按需要出现，核心原因留正文，完整旁支留文章。四期配音前独立审稿见[旁白SHA记录](qa/editorial-approvals.json)。

[最小真实运行](runtime/README.md)由官方分发全量SHA512核对后进行：RF1单KRaft节点观察发送确认早于创建消费者、物理日志保留、classic动态Range组分工与两组独立读取、position/committed分离及重开恢复。首轮静态成员运行29断言与补充动态组21断言分别保留；未重跑的position不追认为动态补轮结果，见[范围补充](runtime/erratum.json)。没有执行通知业务、三副本故障或MQ04丢回应实验。

MQ02另实际编译运行固定版本未修改的RangeAssignor/SubscriptionState，MQ04实际运行ProducerStateEntry/BatchMetadata的精确条件fixture；后者不是Broker/网络或完整记录解码实验。动画仍是官方实现约束的有限教学模型，不能冒充实测终端。各期来源/模型/实验记录在各新制作目录。

## 实际质量检查

来源、模型、最终106句PCM/原始声学边界、真实动态预演和正式MP4分别独立验收。短尾/原始削顶仅对异常句同文补候选，保留原take和最初信号报告，不将信号异常说成听出错字。MQ01 decode→position→poll→应用解析顺序、MQ02协调者隐藏状态、MQ03/04完成态文字抢先均在编码前修正并保留旧源与证据。

四片默认入口实际转换full601→limited709像素、混音并生成同色资料；最终1080p30/H264/limitedBT709/AAC48k、完整解码与附加前后正文/声音保真通过。正式图像以准确整数n复核关键相邻状态、烧录字幕及资料首中末；非作者接受报告分别在新目录`qa-independent/`或`qa-final-independent/`。不以预演或断言通过替代实际编码图读。

16幅JPEG从最终视频按编码前图位整数帧导出，明确limited709→full601矩阵转换，已逐张实际查看。MQ01实际平坦背景样点JPEG与最终视频最大通道差1，见[有限颜色样点](qa/mq01-root-color-sample.json)。生产MDX保持冻结；站点派生稿仅插12个旧锚点别名、将MQ04四个等价相对Figure路径展开为站点要求的绝对前缀，未改正文、原文、图注、回看时间或图片。第一次构建阻止相对路径的[原始日志](site-build-initial-failure.log)及[派生原因](site-derivations/kafka-send-confirmation/correction.json)保留。

fresh npm ci后完整[站点构建](site-build.log)通过52日期/52参考输出、51篇文章/91原文摘录/67有效配图。四页本地原生Chromium共210项动作、80次严格实际PTS及真实截图审读通过，含1440/390、844横屏Fullscreen、播放/字幕/章节/原文/配图/原图/旧锚点。MQ02/04自然初始暂停海报仍见原生加载弧，实际播放和后续交互正常；[本地报告](site-local/)保留该观察，不宣称清洁海报或物理手机已测。没有TLS忽略、HTTP回填或隐藏控件。

## 保护与流程拦截

开工[基线](baseline.json)记录8435个旧冻结实际文件的SHA/mtime与四期1972个原Gitblob。[安装后只读核对](qa/preservation-after-install.json)确认旧生产输入不变，57个既有发布文件是本轮明确替换；旧封面/海报/style与创建/首发/平台身份严格保持，新增发布文件另外记录。

第一次MQ01冻结因新placeholder目录缺失停止，MQ03因可选covers元数据缺失停止，均未启动失败输入的正式编码；仅补canonical所需空目录或与既有board完全相同的covers元数据。MQ03最终QA的111项平铺select触发过滤器递归限制，改共享QA工具为平衡树后以同组整数帧重跑，未改媒体。相关失败与修复记录在本目录qa及各期独立报告。

[密钥复核](qa/secret-review.json)使用未修改的canonical规则；一处官方KafkaApis.scala参数类型产生误报，按完整固定源SHA/行号/公开URL逐项核对，未放宽其他规则。Remotion生成bundle和浏览器下载缓存作为可重建输出忽略，实际来源/图像/短片继续保留。

本批实际交付见[发布回执](publication.json)。没有逐字ASR、全片实时人工语义听辨、物理手机或学习效果实验，也没有新版用户观看认可；仅GitHub与本站，无外部平台重发。

## 实际发布与线上闭环

[PR #444](https://github.com/linhongcun/video-studio/pull/444)合并为`d033d2ba520fe6829caa7c62c95f1c50ee2ccd1b`；远端[附注tag](annotated-tag-verification.json)精确指向该提交。[Release v0.96.1](https://github.com/linhongcun/video-studio/releases/tag/v0.96.1)于2026-10-30T13:44:45Z发出后，[Pages 41065814951](https://github.com/linhongcun/video-studio/actions/runs/41065814951)在同一HEAD成功。只取消本次同HEAD、Release前自动push的41065674817，未改他人运行。

[38项普通canonical完整GET](online-verification.json)通过，未用Range、缓存参数或重试：四条完整MP4（合计32,126,145字节）、四海报、四VTT及16幅JPG与本地完整SHA一致；16章/106cue、旧锚点、四课目录、入口和真实Release/更新日志通过。

线上原生Chromium另完成[MQ01](site-online/message-queue/report.json)52、[MQ02](site-online/kafka-consumer-groups/report.json)50、[MQ03](site-online/kafka-log-replay/report.json)54、[MQ04](site-online/kafka-send-confirmation/report.json)54项动作，各20次严格实际PTS；合计210/80，与本地结果分开留证。四份报告均已实际审图，根代理另[实际打开5图](qa/root-visual-online.json)。HTTPS原生验证，无TLS忽略或HTTP回填；初始海报加载弧/原生控件及早期lazy图状态原样保留，不称清洁初始海报，后续实际播放和交互正常。1440/390/844均为模拟视口，未测物理手机。

线上核验后[#443](issues/443-after.json)以completed关闭，[#308](issues/308-after.json)同步重制交付；仍4/9核心题已交付、5题未制作、14题取消。旧#309–#312及各首发Release/QA保持历史身份，本轮不扩展为外平台重发。没有逐字ASR、全片实时人工语义听辨、学习效果实验或新版用户观看认可。

MQ04新制作README本身属于204项编码前冻结输入，仍保留准备阶段身份；其他三份未冻结README补充当前状态。当前交付状态统一以本批记录及实际回执为准，未修改任何冻结README。

## 上线后反馈（2026-10-30）

用户在本轮交付后，肯定当前表达对实现深度与易懂程度的平衡。后续MQ可延续以源码执行路径支撑同一消息推导、必要术语随动作引入、复杂支线留图文的做法，提炼见[成功经验S023](../../../successful-practices.md#s023-把实现因果变成同一事件的连续推导)。这是定性反馈，未逐期确认四片完整观看，也不是学习效果测量；原发布回执与QA中尚无新观看反馈的声明保持交付当时的身份。
