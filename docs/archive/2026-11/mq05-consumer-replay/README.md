# MQ05：消费者为何需要幂等

2026-11-02，北京时间。修订任务[#454](https://github.com/linhongcun/video-studio/issues/454)，从`01cd181caf24d4a8ce846c0eb8faeeab8f0054e2`建立`codex/mq05-consumer-replay-20261102`。原#313与系列#308保持历史completed状态；本轮保留EP45、slug、原题、创建/首发时间、firstRelease v0.97.0、平台信息和仍适用的原封面。

旧稿Kafka恢复因果占792/5497正文帧（26.4秒，14.4%）。本轮正文沿唯一E01/P0/offset0解释内存读取位置与消费组恢复位点的差别，展示外部数据库已提交、Kafka位点未提交的故障窗口，再比较无保护重复加分、提前提交漏做，以及简单同事务去重。数据库并发内部细节留文章。源码、教学模型、真实运行与媒体审查分别留证，不以其中一项代替另一项。

新制作目录：`episodes/message-queue/kafka-consumer-idempotency/production/revisions/consumer-replay-v2`。`startup.json`、`baseline.json`、`original-publication.json`及`root-preparation.json`记录开工、29,406份旧文件保护、原发布文件和复用封面的身份。保护排除本期明确授权替换的11份发布数据，保留原制作源、旧四幅文章图及所有其他期；现阶段没有发布或新版观看认可声明。

`stage.json`只记录实际进度。源稿由编剧制作，独立审批确切脚本与旁白SHA后才允许root调用共享TTS/整轨/装配；实际语音时序、独立动态与成片验收后更新现有站点。仅GitHub与本站，不含平台投稿。

## 正式编码输入（2026-11-02 15:58，北京时间）

确切脚本d21acba、旁白935cdf经独立编辑审批后生成24句初始a，仅11-2与12-1的单满幅样本旗标按同文本补b；22句选a与24份原a保持。最终声轨e1fd676b51a059bc6e54b475aff3a696da4f260e1d6c1d2a686705600453622a，4884帧/162.8秒；前9镜3432帧，占70.2703%正文。0关键词cue检查不冒称逐词对齐，无逐字ASR或完整语义听审结论。

新Kafka4.4.0/固定commit与PG18.0三个隔离分支实际91断言通过：无保护20、同事务保护10、提前提交0，均单次应用发送与物理单条记录；重启Fetch实参分别0/0/1。初始0由Admin设置并查询确认，业务后1用consumer commit；原配置拒绝与Fetch见证不足的尝试保持，15 Probe JVM、两服务停/三端口关闭与200证据索引见runtime。教学模型另为36状态94检查，不充当实测。

动画正式声轨自检、96张独立fresh无字幕图/4张真字幕图、34实际渲染态和四图位1815/3040/3946/4872通过。第11镜COMMIT抢跑在冻结前被拦并只调整Main时序，早期源/图保持；安全分支明确压缩复演两个前面已详解的状态，不冒称36全绘。三段同源真实视频/AAC共1868帧完整独立解码，102唯一顺序/邻界点实际图审通过；图源视审与正式JPEG仍分阶段。

独立闭包审查补齐共享铺轨/起音检查器及两份生产回执，267项显式声明与自动项共同冻结469实际输入；manifest ab840ff87feba16d379d30e54de9594e5973fba0e6d39014f401d4731840b7ff。新旧目录解析器、字体账本、同色资料生成器、真实调研/模型/运行、声音生产器与继承封面依赖均覆盖；无ignored输入。冻结后开始默认带参考资料的正式编码，未预记成片或线上验收。

未改canonical secret checker：原始扫描仍报公开源码/协议名位置；精确复核48旧+234新匹配、0未决。新16日志/8官方enum逐文件/行/字面值固定，独立234正例/1639负例护栏通过；首FAIL与原始日志保持。派生浏览器bundle窄ignore不遮实际源、params或runtime。

## 成片与本地网页通过

默认成片cb719590bf400e1e2e7489ba853671ccb7d18a8497ff3bb7f386f2203400fb6b，5034帧167.8秒，正文4884加150帧资料。完整解码、原正文帧/AAC保真、−16LUFS/−3.8dBTP与122实际编码帧、4JPEG及资料首中末独立审通过。所有469冻结文件已逐Git index blob核对，5份有界QA短片随证据保存。

本地正常构建与原生86动作/22严格PTS通过；41UI截图与22canvas共63路径，49唯一图具名实际看过，14重复canvas逐SHA与完整bytes绑定。原机器报告和初次覆盖字段名错误保持；海报加载弧、暂停控件压暗字幕、长面板内部滚动及模拟手机边界如实。仅本地检查不冒称已上线。

默认FFmpeg参考RGB比较因均值1.5超限保留原FAIL。两路独立准确709→RGB24转换对22张native帧使用原阈通过，均值最大0.46344/P95为2/BG为0；实读原YUV与标准矩阵另证参考转换精度差。没有修改视频/原PNG/冻结helper或提高阈值。完整出处见qa/native-color-accurate与site-local具名复核。

本地预览完整备份原20发布文件，保留首发身份与全部旧JPEG；实际发布流程开始时仅updatedAt更新为2026-11-02T17:31:30+08:00，firstRelease仍v0.97.0。当前站点版准备0.98.1，待合并/Release后Pages与线上完整GET及native另验。

## 合入并行主干

提交前origin/main已到b19ae154，保留Redis三期v0.99.0及其收尾#455/#456。3815条上游变更与469冻结输入无交集，MQ成片cb719…、媒体/源审和首发身份保持；站点修订号由未发布候选0.98.1顺延0.99.1，原发布流程开始时间保持。当前记忆/教训合并两边内容，保留上游L061，本轮条目用L062/L063，旧局部记录中的L061指当时草拟号。详见version-resolution.json。

## 交付完成

[PR457](https://github.com/linhongcun/video-studio/pull/457) squash合并8eb1b603，附注tag与[Release v0.99.1](https://github.com/linhongcun/video-studio/releases/tag/v0.99.1)后，手动[Pages41423515242](https://github.com/linhongcun/video-studio/actions/runs/41423515242)与deployment7489083734成功。仅取消本批同head的preRelease push41423370219以释放队列，未取消其他任务。

15次普通canonical完整GET核视频/海报/VTT/四图全部SHA、四章/24cue/10引用、九课及入口、RSS原首发和实际Release。并行Redis新首发使EP45按原首发排序为第8，因此首页验收按真实recent6 href/date而非伪造本期新首发；旧helper/差异与独立17项/5负例保留。

线上native86动作/22严格PTS通过；63PNG路径中10新unique实际打开，53逐SHA和完整bytes绑定39个具名本地已实看代表，共49unique。22实际在线canvas与本地同n图逐字节相等，精确RGB数学证据有界复用，不再重复解码参考。原机器/颜色FAIL保持，未绕TLS/请求回填/Range冒充完整GET。海报加载弧、系列部分初始缩略图占位、暂停控件遮暗字幕、长原文内部滚动、390细字及模拟非真机范围如实保留。

[#454](https://github.com/linhongcun/video-studio/issues/454)已于实际线上验收后completed关闭，#313/#308保持completed历史。publication.json汇总准确提交/媒体/冻结身份与证据SHA。只上GitHub及本站，无平台投稿、完整语义听审/ASR、用户新版认可或学习效果声明。
