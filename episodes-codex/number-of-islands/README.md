# 岛屿数量：怎样保证一座岛只数一次？

本轮左上边界反馈已按v0.67.1合并上线，Release后Pages40187760204及10次线上完整核验通过，证据见[边界修订记录](../../docs/number-of-islands-boundaries/README.md)。仅新渲染06，复现按splice-boundary.py和splice-plan.json；原通用render入口仍可重建完整画面，但本次实际交付使用有证据的局部复用流程。

已按持续授权合并并发布[网站版本v0.66.0](https://linhongcun.github.io/video-studio/episodes/number-of-islands/)，Release后Pages40179672105成功，线上39次完整HTTPS核验通过、#82已completed关闭。实际发布、失败过程与能力范围见[交付记录](../../docs/number-of-islands/README.md)。

选自现有[issue #82](https://github.com/linhongcun/video-studio/issues/82)，独立算法系列LC.200，内部排序EP34。开工同步与并行身份预留见startup.json；片内仅展示题号。当前真实配音和分镜已装配，后续阶段以实际QA/发布报告为准，不将本说明当作通过凭据。

## 内容与依据

固定4×5海陆地图，先说明四邻连通与返回岛数，从逐格计数的重复推得整座归属与保留分支，再命名DFS、推导栈。场景始终保留海陆地形，用归属、待展开、当前和已展开不同标记讲真实执行；分析演示与正式扫描之间明确重置。完整26行Python使用迭代栈和seen，不改输入；源码、文章与片尾显示一致。

官方资料和实际读取证据见research.md、research/source-access.json；真实solution.py经AST观测得到99事件demo-trace.json，再原字节复制到remotion/src/lesson.json供动画读取。独立并查集完整分区验证65,852组通过，真实范围见research/algorithm-verification.json，不由动画另算一套结果。

## 重建入口

使用当前remotion/package-lock.json独立npm ci，不依赖已删除工程或其ignored缓存。配音调用episodes/_shared/voice/prep.py、gen.py、build.py，共享起音与整轨逻辑不复制。本片28句为新生成MiMo候选，DFS送模替换和裁尾记录见voice/；字幕保持原文。重建会写文件，检查已发布稿时只执行只读冻结核对。

仓根装配/铺轨/时序检查：

```sh
python3 episodes-codex/number-of-islands/prepare_code_endcard.py
python3 episodes/_shared/place_v2.py --dir episodes-codex/number-of-islands --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/number-of-islands
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/number-of-islands
python3 episodes-codex/number-of-islands/freeze.py
python3 episodes-codex/number-of-islands/freeze.py --verify
```

真实分镜14镜、28句、4章、5783帧/30fps。完整Python卡从5633到5782，共150帧/5秒，旁白PCM为零且无字幕进入；最后旁白提示暂停查看。音轨为实体remotion/public/audio/voice.wav，whole-place与voice.wav字节相同；声音、锁文件、共享依赖、所有src和真实trace均冻结在source-sha256.json。

remotion目录使用本地编译器并按顺序完成封面/真实时序预检，再正式编码：

```sh
npm ci --no-audit --no-fund
./node_modules/.bin/tsc --noEmit
TMPDIR=/workspace/islands-tmp flock /tmp/video-studio-render.lock npm run covers
TMPDIR=/workspace/islands-tmp flock /tmp/video-studio-render.lock npm run stills -- out/qa-measured
TMPDIR=/workspace/islands-tmp flock /tmp/video-studio-render.lock npm run render
```

实际多阶段与连续片原参数见qa-motion-measured.json；08状态文案定向复采见qa-motion-08-fixed.json，最终94点接受范围及来源见qa-motion-final.json；默认stills仅是镜内采样，不能代替本次三段无字幕连续过程。qa脚本递归绑定所有src，支持QA_FRACTIONS/QA_EXTRA_FRAMES/QA_CLIPS/QA_MANIFEST。早期layout-only是明确的占位开发稿；revisions/layout-shore-before保留四陆格交点假水孔的失败图与原源，修后仅补内部海岸连接，真实斜角水隙保留。不得把占位开发图称作真实配音预检。

正式编码先渲染新旁白视频，再用共享Wallpaper BGM混音；复制实际mix-report.json后运行_shared/check_encoded_episode.py和extract_encoded_samples.py（--samples qa-motion-final.json）。源、连续片、声音、封面、成片和网站的实际结果分别在qa-*与docs/number-of-islands/，能力限制按执行报告保留；无逐字ASR或全片人工听辨声明。

## 交付范围

按持续授权合并、附注tag/Release和GitHub Pages交付，网站仅接入最终检查通过的canonical副本。发布前再次同步并核对冻结输入交集、实际版本与其它课程；保留旧6条算法、最新Skills/适配器/P04/P05草稿和旧Agent删除结果。站点构建/两视口播放、字幕、章节、媒体与海报完整HTTP SHA和Release日志核验在实际执行后记录。线上通过后将issue #82以completed关闭。平台新发不在本轮范围。

## 第10批参考资料名单与当前入口

本批只在完整原片之后追加`title-author`参考资料名单，每页最多4项、默认5秒。完整body包含原150帧Python解法卡，参考资料从代码卡结束后开始；solution.py/json、分镜、字幕和音轨均不改写。基线`4213a233c4c242b04453b8c1215031dc421c2398`的Git发布原片已绑定原render-result与总帧数，逐字节保存在`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`；本批直接使用这些原片追加，不寻找旧缓存或重制正文。

原151项历史输入全部现存并按原路径或before快照逐一验证，保留全部原key。当前清单只声明现存真实依赖及本轮资料/入口，不将它当作原MP4已重新编码的证明。旧freezer及清单完整保存在revisions/reference-endcards；旧QA、局部拼接、媒体和算法测试记录保留其历史身份。完整源码入口的静态import、别名及公开音轨核对不依赖缺失缓存，详见[生产入口报告](../../docs/reference-endcards/batch-10/production-entry-check.json)。当前freeze.py保留实质断言，分镜快照/placeholder和代码卡只读核对；不调用原写入型freezer、prepare_code_endcard、装配、TTS或算法测试。

资料负责人停写且来源预检通过后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/number-of-islands
python3 episodes-codex/number-of-islands/freeze.py
python3 episodes-codex/number-of-islands/freeze.py --verify
```

默认`npm run render`接共享bibliography wrapper，先核对来源和冻结，再运行`render:body`及附录。`render:body`保留原voice→mix闭环、编码参数和concurrency=2，仅把mix输出改至`out/body.mp4`，完整Python卡仍由现行源码渲染。`npm run render:references`从该完整body单独追加资料；`npm run verify:references`是后续完整交付检查入口。本批只做来源与只读冻结/入口检查，未运行正文、混音或重复完整解码。最终总帧数以新receipt、render-result及发布metadata为准；[本批进度](../../docs/reference-endcards/batch-10/README.md)不预记未完成的媒体或线上通过。
