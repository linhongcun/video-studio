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
