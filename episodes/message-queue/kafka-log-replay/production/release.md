# MQ03 / EP43 发布记录

2026-10-30（北京时间），制作issue#311，总览#308。当前状态：v0.95.0已合并发布并完成Pages与线上核验，#311已以completed关闭。

## 实际制作与复核

清洁工作区fetch后从9e44109511cac1b0fb54d8aa9383b9d7dfe9074b开工，制作中再fetch并ff整合72b841c1/v0.94.0，保留其他分类与新站点规范。13条上游文件变动与本期模型/声音/动画/封面/共享渲染输入零交集，候选版本顺延v0.95.0；实际记录qa/upstream-integration.json。

Kafka4.4.0固定提交1156b2752aaa28eafc0b4c4d387e63356793268d官方来源本轮重新GET并实读。Introduction、Design、Basic Kafka Operations、Topic Configs原题/机构/精确引文通过来源预检；API/工具/TopicConfig源码交叉核对position、commit、inactive reset与旧段清理。有限模型137项检查与独立模型审读通过，未启动真实Broker或执行CLI、通知/积分副作用。

11镜22句、4章，正文3943帧/131.4333秒，预留150帧原题机构资料页。配音06-retained-2原a候选附加尾过短仅0.09秒，保留原失败源/报告，仅同文追加并选b，尾0.38秒；其余21原take保持。整轨SHA为0f75a80c027bc2ce786434489cd5a9a422f6cfa1ca436a5c0376ec1f3dbd7d10。独立22句来源/裁尾/PCM/静音信号检查无旗标，最短抛弃尾0.345秒，最大句内静音0.42秒；铺轨偏差0，0cue/0fail如实记录，不冒称逐字ASR或全片人工语义听辨。

独立真实动态预检95PNG/DOM覆盖21模型状态，63处源高亮身份核对，三段真无字幕MP4与56张逐秒顺序抽帧实际查看；0COPYFIT/越界/运动压字/模型不符。正式预演前修正重放第一条时提前称两条已处理、第二条源焦点未及时切换，以及02过早展示03组拓扑。均为源码审查拦截，非已发布事故，实际证据见qa/preflight-v1.json。

三比例封面实际生成/字体/4:3安全区及独立审图通过，mutable输入逐字快照纳入本期冻结，旧MQ01/MQ02冻结保持。真实10帧正文pc601→limitedBT709与四资料150帧附录短窗验证通过。正式冻结清单170项，SHA0a036ad58b41d547f1afecb13066db5e566a1251ad368f4e7630293541205800；编码后只读复验，不重写追认。

本期引用文章四图在编码前固定1445/2900/3251/3572整数帧；最终媒体后按limitedBT709→fullBT601生成JPEG并实际核验，不改冻结制作稿。

## 交付范围

沿RULES STATUS持续授权，只上GitHub主干、Release与Pages；平台无本轮新发。实际成片/本地网页/线上结果见下文；已在完整文件与原生浏览器核验后completed关闭311并同步308。没有逐字ASR、全片人工语义听辨、物理手机或学习效果实验，不预记用户观看认可。

正式编码后再次fetch并ff整合4f631ca7的README重写，保留新的学习站与制作系统文档结构，仅补MQ系列含日志重放的范围说明；实际170冻结输入与site运行代码无交集，见qa/upstream-after-freeze.json。

## 正式成片与本地接入

成片4093帧/136.4333秒、7,023,582字节，SHA-256 `0baa057bfa08635e97ce6e19b75fcd198ece292072bc401c23ea971218baa637`；资料页3943–4092共150帧，四项原题/机构。完整解码、limitedBT709/实际帧属性、正文/资料AAC与PCM及图片前缀保真通过，混音实测-16LUFS/-3.8dBTP，编码后170项冻结只读复验通过。独立实际编码55帧与7张合辑、所有状态关键边界/4图位/资料首中尾通过，见qa/encoded-independent.json。

按预定1445/2900/3251/3572整数帧抽取四图，明确limitedBT709→fullBT601 JPEG像素转换，root实际看完四张，图意与回看时点匹配，冻结文章未改。

临时封面identity-only元数据首次触发正式安装的首发保护，未作为有效发布数据构建；已留存临时身份，换成正式媒体/日期/附录元数据后构建通过。安装器仅对完全匹配本期身份的7键封面暂存记录作识别，真实已发布创建/首发日期保护仍在。新期fresh site依赖与完整build通过：51日期/资料输出（含1归档），50当前文章、80原文、62配图。

本地46项实际浏览器和20次严格PTS检查通过，覆盖22条原生字幕默认off、4章/4图回看、四处引用的桌面hover/点击/手机tap/键盘关闭、实际播放/暂停及Fullscreen API、三课MQ系列。实际图像阅读结论与能力限制见qa/site-independent/report.json。

本期复盘沿用既有短尾、渐进引入、结果状态与元数据闸门经验，不新增重复的通用规范条目。最终线上结果见publication.json与下节。

## 实际发布与线上核验

[PR438](https://github.com/linhongcun/video-studio/pull/438)已squash合并e21e14570db934af7ede110e95b627d7b4190cdb，附注tag与[Release v0.95.0](https://github.com/linhongcun/video-studio/releases/tag/v0.95.0)发布后[Pages40991181077](https://github.com/linhongcun/video-studio/actions/runs/40991181077)成功。同SHA首push40991042825为避免重复部署主动取消，非媒体或构建故障，不改工作流、不取消其他提交的运行。

北京时间2026-10-30T10:27:34开始的14项普通canonical GET通过，线上完整MP4、16:9海报、22cue VTT、四图SHA与审片版相同，4章/三课系列/内容库/首页/旧learn兼容/实际Release更新日志齐全。随后原生Chromium直接HTTPS完成46项交互、20次严格PTS解码和实际截图阅读，未用TLS绕过或HTTP回填。已实际查看桌面资料页、手机R3/R4原文、844模拟手机横屏资料页，四项题名署名完整且不被原生暂停控件遮挡；所看截图未见等待圈，不扩大为所有状态/物理手机结论。

[#311](https://github.com/linhongcun/video-studio/issues/311)已于2026-10-30T02:33:27Z以completed关闭，[#308](https://github.com/linhongcun/video-studio/issues/308)为3/9交付，其余6题未开工、原14题取消保持。本轮收尾只补文档与检查证据，不改变已发布的媒体、文章、站点运行代码或170冻结输入。机器证据见[publication.json](publication.json)、[HTTP](online-verification.json)、[线上原生浏览器](qa/site-online-native/report.json)。
