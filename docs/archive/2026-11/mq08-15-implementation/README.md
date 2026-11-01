# MQ08与MQ15实现机制短片

2026-11-01（北京时间）按#308剩余两题开工；两期已完成源码、独立编辑、真实运行、配音与动态检查，正式成片、八张JPEG、本地原生网页与生产构建验收通过，正进入GitHub发布。当前尚未发布，实际进度见stage.json，最终GitHub/线上结果另记publication.json；只含GitHub与本站。

|题库 / issue|EP / slug|主线|冻结输入|正文帧|
|---|---|---|---:|---:|
|MQ08 / #316|48 / kafka-retry-dead-letter|保存调用预算、进程恢复、死信确认与原进度两个边界|240|6018|
|MQ15 / #323|49 / kafka-replica-acks|本地追加、主已知复制进度、当前ISR与成功回应|344|5460|

MQ15保留稳定题库号。新制作分支基于最新origin/main `8769a592856fe2618e5daf3d84849bf4b052e22b`，使用`episodes/message-queue/<slug>/{production,publication}`，共享入口为`episodes/_shared`；两期依当前锁文件新装依赖，未复用旧目录缓存。编码前再次fetch，主干与冻结依赖无交集，拟定站点版本v0.98.0尚未发布。

26583份既有受控文件（含1314份发布文件）的SHA及mtime基线在baseline.json，旧共享与迁移账本保持。唯一允许的现有episode变动为自动生成索引episodes/README.md。旧ignored缓存保留到仓外，初次layout拦截及处置在qa/legacy-cache-quarantine.json；随后57实体对/11系列检查通过。旧manifest不追认新路径代码，新两期冻结实际Python/JS resolver及当前输入。

## 来源与实际运行

两期固定Kafka4.4.0源码`1156b2752aaa28eafc0b4c4d387e63356793268d`，实读原文、原题与机构，视频四/五项title-author资料从默认入口生成。文章另保留完整定位、短引和边界；四张配图时点在编码前按真实声轨冻结，成片生成后才接受实际JPEG。

真实运行185项断言（MQ08 151 / MQ15 34），与教学模型检查分开。347份原始证据已有只读索引且所有服务停止，见[runtime/README.md](runtime/README.md)。MQ08是实际Kafka客户端及本机状态目录，业务处理为可控fixture；预算包含预留但未完成的调用，不是自动延时Topic、分布式状态库或断电实验。MQ15三节点受控调度分别保留物理日志与主可见进度；原dump文件名校验失败保留，仅以相同33份快照字节按官方合法文件名复核，21批CRC通过，未重跑Broker掩盖失败。

## 配音、动态与冻结

56句首候选与5句同文本替换均保留原始take。MQ08初轨6104帧，3句信号候选后最终6018；MQ15初次配音已生成，但镜头标题格式不符合后续装配器，原失败不改。仅移动13行标题说明、独立确认旁白及全部原take相同，使用原26句恢复5515帧整轨，随后仅2句因收尾/满幅风险换同文本候选，最终5460。格式修正没有重新请求整批声音；两次信号替换是单独步骤。最终两轨信号flags均空，实际-16LUFS、TP约-2.20dBTP；不等于逐字ASR或全片人工语义听辨。

MQ08独立动态报告为D/qa-independent/review.json：128实际PNG/DOM、40可见状态、7段2537帧完整解码，180顺序时点/33联系图按明确分工实际看，4字幕图及4图位另审。旧06锚点与尺寸假设两次QA自身失败原样保留，只纠正预期。

MQ15为D/qa-independent/preflight-final.json：39态、199当前有效采样，7片3227帧完整解码，170顺序时点实际审图。初稿在B2报告后标题仍写等待报告，根及独立审查要求按模型状态切换；唯一标题guard的精确源差异、标题区域像素差、受影响08新帧/字幕/454帧窗另验，未受影响范围按有界证明复用，旧源与全部旧图/片保持。文章单处小于号的MDX格式错误也在冻结前留原文、加两枚行内代码标记并以现行站点parser通过。

冻结器、资料入口、真实所选声音、源码/例程/模型、文章图位、两resolver、新封面模板及字体账本均纳入。只读依赖审查补齐实际初声producer快照与resume链；MQ15缺少的placeholder目标父目录在首次freeze前准备。canonical freeze产生实际board的派生placeholder，未改Main/声音/正文board；两期结果在qa/mq08-freeze-result.json与qa/mq15-freeze-result.json。

六张实际JPEG封面独立审看后按原字节安装，9个字排压力样例通过；旧封面catalog与renderer不改。5实际字体文件/5绑定只读核对通过。公共扫描器原始失败保留，48处公开源码/协议标识按精确路径、整文件SHA与行SHA分类，0未决；未删除原日志或扩宽扫描规则，独立边界审查见qa/public-protocol-identifier-review/independent.json。

## 正式媒体与发布门禁

正式默认入口已生成正文、真实limitedBT709混音及参考资料附录；MQ08实际6168帧/205.6秒，MQ15实际5760帧/192秒，完整SHA见media.json。160/149个最终整数n及全部资料页/字幕边界已独立审读，两支完整视频及AAC解码通过。8张709→601JPEG实际逐张审图，并与同n成片PNG比较；本批未把源PNG当成最终JPEG。已安装同字节草稿并完成SHOW_DRAFTS构建，原生双视口140动作/48严格PTS及具名实际图审已通过；已在实际发布工作流开始时写首发字段，生产构建57资料输出/56当前文章、153页及built日期/RSS通过，GitHub合并、Release与Release后Pages仍待执行。线上普通完整GET与浏览器自身媒体Range分别留证。模拟视口不冒充物理手机，没有全片语义听辨、ASR或学习效果测量，不预记本批用户观看认可。
