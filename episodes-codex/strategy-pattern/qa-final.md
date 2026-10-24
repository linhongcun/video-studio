# 策略模式新手版：最终本地交付检查

2026-10-25（北京时间）。用户授权据新手理解反馈调整并上线；本报告只对应13镜26句的新手版，旧16镜与章节桥接报告保留于revisions/v0.52.0和revisions/v0.54.1。

## 结果

本地制作、真实时序、独立正式成片与站点验收通过，可以合并并发布GitHub站点。当前发布目标v0.54.4，线上结果待Release后部署实际核验，再补release.md与online-verification.json；本地通过不预写成已上线或用户认可。

- 视频：4895帧，画面163.1667秒、容器163.178秒，1920×1080、30fps、H264、48kHz AAC。
- 文件：8,674,537字节；完整SHA-256为a7056ae8ccfe6783063b6c679174fa5d15ab410cac0628fe5de12e7fcc9e6696。
- 共享混音实测-16.0LUFS、-3.7dBTP；完整解码、全部4895显示PTS、视频DTS/AAC包连续性通过，见render-result.json、mix-report.json、qa-encoded-media.json。
- 137项生产输入冻结核对通过，26条新录音，未沿用旧13镜PCM或旧拼接基线。主WAV SHA为1abd9781d2b417644bd2671d753629aa6fcb284cbc942a0cb7210b9e33dba2fa。

## 教学结构与实际画面

只讲会员/活动两种办法，100元分别得90/80元。先建立一个具体函数再命名策略；补齐传函数而非结果、pricing本次关联所选函数、调用以后才计算，换一次办法时先清旧90并从100元重算。改价、新客注册和完整校验移到配套图文拓展。

根与独立质检先按六个理解问题审读，随后用最终真实时序生成130全片预演图、53关键图和06–10五段无字幕连续编码。COPYFIT零、无临时时序、最终字幕隐藏参数正确；独立实际查看全13镜25图、从五段MP4自行提取16中间态。根另实际查看6张最终源预演图。范围和实际源SHA见qa-motion.md、qa-motion-samples.json及qa-teaching-beginner.md。

正式混音MP4上，根精确抽13帧并实际查看8帧，覆盖首帧、选择、未算、参数对应、90返回、清旧、80返回及末尾成本；完整索引与原图见qa-root-beginner-encoded.json、revisions/beginner/frames。独立质检另从正式1080p文件精确抽取并实际查看16帧，核对新章入口、函数身份、计算/返回顺序、原价重算、字幕与结尾，无发布阻塞。实际范围见qa-teaching-beginner.md及当前qa-independent.md，不声称逐帧人工看完整片。

预检发现并修复的Python前导缩进被pre-line吞掉、顶栏章名未传入问题，均在最终预检与正式编码前关闭；本轮所有最终检查对应修订后的源。三个原封面保持完整SHA一致，见qa-beginner-cover-reuse.json，不重复生成。

## 网站

站点副本使用同一视频、文章、SB/words/script/research，firstRelease仍v0.52.0，slug和四章ID保留。新标题为《策略模式：结算怎样换一种算价办法？》，updatedAt为2026-10-25，版本0.54.4。

生产构建及静态检查通过。1440/390两视口各四章共8次真实seek及随后播放均通过，最大误差6.67e-7秒，readyState4、无video.error、时间实际前进。26条VTT载入，网页播放器时长163.178秒，与画面差0.011秒；整页无横向溢出，新图无需横向滚动，封面、四章、源码、首页/系列/RSS通过。证据位于episodes/strategy-pattern/site-beginner-{copy-manifest,static-check,browser-check}.json。VTT完整SHA为a47f04c6a0d9ec4a4cf6790bd33f503ada13ba1e31e97171dc42179b81ca4a25。

## 能力与发布边界

配音候选文本/PCM及共享句边界、声学首词、整轨/混音测量完成；保留一条候选0.61秒低信号停顿复核标记，整轨测量与范围见voice/audio-qa.json及beginner报告。当前无可用逐字ASR/直接音频听辨，未把上述检查写成逐字识别或完整人工听辨。

独立六问与画面复核支持本轮编辑判断，不是新手理解实验，也不代表用户已观看认可新版。平台新发未执行。GitHub合并、Release后部署、线上完整SHA与issue关闭由release.md记录真实结果。
