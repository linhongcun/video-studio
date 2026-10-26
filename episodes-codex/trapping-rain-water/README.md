# 接雨水：每一列能留下多少水？

## 当前交付状态

真实配音与分镜已冻结，145项输入逐项核对；正式成片5926帧/197.533秒，完整SHA `c0148e14dd513913f2f4c376431d1c5a7d23a56f2a4cde6382d9ad99fb91f648`。算法、审稿、真实动态及六封面、正式MP4独立视觉与媒体检查均已通过，最后150帧为5秒完整Python暂停卡。实际范围与能力限制见`qa-preflight.md`、`qa-audio-preflight.md`、`qa-final.md`与`qa-media-independent.md`。网站发布状态统一见[批次记录](../../docs/leetcode-batch-next/README.md)。本轮未发外部平台，尚无新片用户观看结论。

以下保留阶段1制作交接记录，开发占位分镜和未生成配音的说明只适用于当时，不是当前状态。

开工基线8d037aa3e05ce1ed992df6b758b9b2227dd8b18b，分支codex/leetcode-batch-next，issue #86，LC.42，内部EP37，计划随本批首次Release v0.69.0。独立当前锁文件npm ci已由root完成；不依赖已删除工程或旧ignored目录。本期阶段1为内容/算法与动画源码，实际配音、预检、媒体和上线均未做。

本片只讲**左右最高值预处理**，时间O(n)、辅助空间O(n)。issue旧草案考虑双指针；本次用户授权自选有把握的题目，选择更适合用柱子与不同水位推导的基础方法；原题目标不变，不改旧issue原稿，发布PR会透明说明方法调整，双指针仅作未来进阶候选。

固定教学样例[3,0,2,0,4,0,1]→8；左盆水位3、7格水，右盆水位1、1格水；第三列高2的柱顶上只有1格蓝水。两侧最高值均包含当前柱，首尾水深0明确解释。先题意，再较矮挡水/矮柱淹没/重复寻找推导双向保存，之后才命名前缀/后缀最高值；14镜28句四章，末150帧完整19行Python卡提示暂停。

同源解法/trace：solution.py为唯一程序，solution.json按原始行生成，research/generate_demo_trace.py观察同一AST赋值后的真实状态，research/demo-trace.json与remotion/src/lesson.json完全相同；动画不内置第二求解器。research/verify_algorithm.py用水平逐层合法格oracle检验22257输入，另测2组满约束，21事件不变量通过；这些只证明实现和数据。

```sh
/workspace/.venvs/video-studio/bin/python episodes-codex/trapping-rain-water/research/generate_demo_trace.py
/workspace/.venvs/video-studio/bin/python episodes-codex/trapping-rain-water/research/verify_algorithm.py
cd episodes-codex/trapping-rain-water/remotion
npx tsc --noEmit
```

内容通过独立审查后root才执行共享voice/build.py、prepare_code_endcard.py、place_v2.py、label_onset_strict.py与check_sentence_episode.py；不复制TTS/起音/铺轨实现。真实时序后重新检查场景动作与术语起音，停写冻结，再由root在flock /tmp/video-studio-render.lock且TMPDIR=/workspace/rain-tmp下执行npm run render/covers。当前src/placeholders/storyboard.json显式provisionalTiming/pendingAudio，不是预检或冻结产物。实际音轨存在时Main用audio/voice.wav，正式分镜由别名@storyboard自动切换。

能力边界：未生成TTS，未渲染媒体，未做逐字ASR、人工全听、正式成片或站点核验。GitHub合并/Release/Pages在所有质量检查完成后依持续授权由root处理，外部平台未授权。

## 第10批参考资料名单与当前入口

本批只在完整原片之后追加`title-author`参考资料名单，每页最多4项、默认5秒。完整body包含原150帧Python解法卡，参考资料从代码卡结束后开始；solution.py/json、分镜、字幕和音轨均不改写。基线`4213a233c4c242b04453b8c1215031dc421c2398`的Git发布原片已绑定原render-result与总帧数，逐字节保存在`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`；本批直接使用这些原片追加，不寻找旧缓存或重制正文。

原145项历史输入全部现存并按原路径或before快照逐一验证，保留全部原key。当前清单只声明现存真实依赖及本轮资料/入口，不将它当作原MP4已重新编码的证明。旧freezer及清单完整保存在revisions/reference-endcards；旧QA、局部拼接、媒体和算法测试记录保留其历史身份。完整源码入口的静态import、别名及公开音轨核对不依赖缺失缓存，详见[生产入口报告](../../docs/reference-endcards/batch-10/production-entry-check.json)。当前freeze.py保留实质断言，分镜快照/placeholder和代码卡只读核对；不调用原写入型freezer、prepare_code_endcard、装配、TTS或算法测试。

资料负责人停写且来源预检通过后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/trapping-rain-water
python3 episodes-codex/trapping-rain-water/freeze.py
python3 episodes-codex/trapping-rain-water/freeze.py --verify
```

默认`npm run render`接共享bibliography wrapper，先核对来源和冻结，再运行`render:body`及附录。`render:body`保留原voice→mix闭环、编码参数和concurrency=2，仅把mix输出改至`out/body.mp4`，完整Python卡仍由现行源码渲染。`npm run render:references`从该完整body单独追加资料；`npm run verify:references`是后续完整交付检查入口。本批只做来源与只读冻结/入口检查，未运行正文、混音或重复完整解码。最终总帧数以新receipt、render-result及发布metadata为准；[本批进度](../../docs/reference-endcards/batch-10/README.md)不预记未完成的媒体或线上通过。
