# P08 / EP55 制作验收

本期选择[#212](https://github.com/linhongcun/video-studio/issues/212)，从main `60f92e6f7550b1ef4a450b6ebdae67d1888733f2`新建。本期已按v0.103.0交付，Release后Pages及canonical线上终验完成；#212已以completed关闭，#204同步为8/10。实际交付身份见[publication.json](publication.json)。

两份大学公开材料已实读，原题、个人署名、版本／日期及颜色映射见[研究](research.md)、[来源证据](research-evidence.json)和[来源清单](references.json)。R1支持100人规则、奇偶协议与上界，R2交叉支持五人递推；两份连续短引为16／15词，不把署名作者称作谜题发明者。

本期独立Python穷举n=1..16，共131,070种完整分配、1,835,012个后续回合、65,535对首帽翻转；独立V8穷举n=1..14，共32,766种分配、393,220个后续回合、16,383对翻转。各自另跑204个确定性100人夹具与负向控制。任意100人分配的完整保证来自不变量证明，未把夹具称作2¹⁰⁰穷举、随机试验或现实实验。

14镜28句、4章的实测正文4876帧／162.533秒。冰糖整轨SHA `de9a74c834a58e10c4297226624da4e81519f77e85eef3cc09cab35a89f415a6`；独立用未改共享build在临时副本重建，28选定句及整轨全文字节一致。28次共享Rule句首起音、PCM原位、全零间隙和实体public音轨一致。07镜第2句a候选抛弃尾段过短，仅同文追加b；风险、旧候选与实际取舍保留。没有执行逐字ASR、句内词对齐或全片语义听辨。[声音独立证据](qa/voice-independent.json)。

最终动画Main SHA `6f35d9a3b75d044d27854a0024c9c261f88fdb705e015b12769c4510222e6ac4`。[独立动态预检](qa/preflight-v2.json)含136个真实DOM／PNG状态点和5段连续编码预演；独立实际查看23静帧、5片段中的30采样帧及28句字幕crop合辑。视野、首消息独立、已听真实答案、扣黑翻转／扣白不变、0偶及只翻首帽的双局面通过；这属于有界采样，未声称全实时观看。旧layout-v1布局失败、被04改源取代的preflight-v1、临时重建EXDEV失败均保留原结果，没有改哈希追认。

04配对卡移除重复的自帽图形，仅显示合计2／3顶黑帽；问号明确为看不见，与听答推知分开。三比例封面经过实际图审与独立DOM检查，旧七期119个相关文件SHA不变。[封面证据](qa/covers-review.json)。

176个输入冻结清单SHA `702f19542c968e99c718db8ae3a4f7e6a5bb1ec3940bb21526e5f4201b998af5`。文章图位编码前绑定1740帧／58秒和3375帧／112.5秒，正式JPEG待从实际最终媒体准确帧导出。默认完整流程包含实际full601→limited709像素转换、共享混音及5秒原题／作者列表，交付不得使用body.mp4。

原始全仓secret_scan实际失败于282处既有公开fixture标记；25份对应文件与开工基线SHA一致。当前变更范围使用原检查器规则复核；最新提交前按原规则复核本期变更为0标记，不将全仓结果称为通过。

本轮范围为GitHub站点，平台新发未获授权。尚无用户对本期的观看结论或学习效果测量。

首次预提交完整git diff --check报告5处新文件末尾空行：3份已冻结研究文件与2份逐字发布副本；非其他代码行空白错误。为保留本次编码输入SHA保持原字节，完整检查未宣称通过，其余路径检查通过；逐文件身份和范围见[空白审计](qa/whitespace-review.json)。

## 正式成片与本地网页

最终5026帧／167.533秒，含4876正文帧与150帧参考资料；媒体SHA `7cdfa6173cd7fc407aa141730931145188121dba1b6e63642adc6f6fd37bca4e`。生产核验与独立全5026帧PTS／色彩／解码、4876正文decoded-frameMD5、AAC／PCM包与时序均通过。独立136同帧按full1920 limited709→GBR、相同Pillow960网格比较，原3／.015／8界限保持，最大coreMAE2.53928；28句AAC相关最小0.9999719。独立响度−16.01 LUFS／−3.75 dBTP。已实际审13正式合辑、准确首参考卡和两张Figure，首卡无原字幕残留；根另实际查看精确首卡与首中末边界合辑。[独立正式媒体](qa/media-final-independent.json)。

站点完整build通过dates／references／articles／copy／Astro／Pagefind：63日期、63参考输出、62公开文章。原生60动作／38精确PTS、阅读12项及nativeRGB38对照通过；native full1920原界限1.5／3／3保持，最大均值0.59433、P95为2、背景点差1。手机390、桌面1440与实际Fullscreen API的844横屏资料题名作者完整；默认原生字幕关闭，显式开启／关闭、章节、58／112.5秒Figure回看、引用与无JS原生popover通过。根另实看手机自然海报和横屏资料图。[本地网站结论](qa/site-local-acceptance.json)。这是Chromium模拟视口，未声称实体手机或旧浏览器实测。

第一次媒体QA因words顶层schema假设失败；环境短暂starting→ready后，第二个旧会话句柄失效、报告仅running头，未获得媒体指标。均保留原文件与失败记录，恢复后用v2完整执行；未重用不存在的通过结果或改生产输入。阅读首轮未严格证明dark的触摸位移，保留旧范围，v2分别从0到24的真实位移闭合。所有工具修正与生产文件分开。

最终全差异样式审计另保留原始site-build.log的行末空白，未清洗执行日志；完整diff检查仍为FAIL，仅5份EOF文件和1份原始构建日志属于精确分类范围，其余源码与文档路径检查通过。[最终样式范围](qa/whitespace-final-review.json)保留原输出gzip及SHA。

## 线上终验与完成状态

核心PR467合并142a2d97b319aef46ea7f6e490849e9fbf6853e1；附注tag对象14c358e61aed606e139ee662c2c4d2ae5354dec2指向相同提交，公开Release v0.103.0于2026-11-04T00:04:38Z发布。Release后Pages41744074130实际success；本任务原先的pre-Release41743916355在部署前正常取消，以优先包含新changelog的那次构建，不作为媒体失败。

该次post-Release部署上的原生60动作／38精确PTS、阅读12项、nativeRGB38次及12完整GET（10个canonical Pages文件／页面＋2个指定部署commit JSON）通过。5026帧视频全SHA、28cue／4章、海报、两Figure、实际Release与changelog一致。独立实际查看12张线上图，根另实看两种正文全屏状态。[线上结论](qa/site-online-acceptance.json)、[完整GET](qa/site-online-http-verification.json)。

额外三张844横屏暂停图确认：原生控件显示时，其黑渐变会明显压暗底部烧录字幕；主要机制区与参考资料清楚。正常播放、controls仍为true且原生控件自然收起后，最长句字幕白字清楚。没有把暂停字幕写成完全无遮挡，也没有改媒体、CSS或共享播放器。全屏补验最初的paused rVFC等待和微秒分数相等断言失败保留，后续按Fullscreen前后实际currentTime相等复核，主PTS及颜色门限未放宽。

#212已按实际制作／发布／线上核验完成关闭，总览#204为8/10，P06／P10仍待后续安排。本轮仅GitHub站点，无新外平台投稿；尚无用户本期观看认可或学习效果实验。[事项收尾](qa/issue-completion.json)。
