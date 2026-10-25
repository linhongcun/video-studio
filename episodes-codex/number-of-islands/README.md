# 岛屿数量：怎样保证一座岛只数一次？

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
