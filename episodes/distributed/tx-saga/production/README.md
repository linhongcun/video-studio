# EP.21 · Saga：扣款成功，缺货了怎么办？

本期独立短片只讲Saga：各步本地提交，明确后续失败后用新业务动作补偿。14镜28句、3478帧，约115.9秒；成功/缺货/退款失败分支都有明确起点，原扣款流水不被抹掉。实际媒体指标由root编码后记录。

导航修订按用户新反馈加入同一张全局流程图：先总览，换分支时缩回定位并重置示例，再放大当前步骤，结尾回图。配音、字幕和总时长保持v0.47.0原字节；详细映射见[navigation.md](navigation.md)，本轮真实采样与检查限制见[qa-motion.md](qa-motion.md)。

制作入口为本目录remotion。脚本、plan、episode-config、research/article/pronunciation与视觉说明对应；配音复用episodes/_shared/voice，句级边界与句首声学实测不冒充逐字ASR。所选28句b、原始raw、送模记录与picks保留。

从仓根运行共享assemble/check：

```sh
python3 episodes/_shared/voice/build.py --dir episodes-codex/tx-saga
python3 episodes-codex/_shared/assemble_sentence_episode.py episodes-codex/tx-saga
python3 episodes/_shared/place_v2.py --dir episodes-codex/tx-saga --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/tx-saga
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/tx-saga
```

新环境在remotion/运行npm ci，再npx tsc --noEmit。导航预演用`TMPDIR=/workspace/.video-studio-tmp node scripts/branch-qa.mjs /workspace/.video-studio-branch-qa/tx-saga`，跨任务通过`/tmp/video-studio-render.lock`串行；封面未变无需重渲染。依赖目录/软链接不跟踪。完整编码由root在输入停写且独立预检收敛后，先运行共享freeze_sentence_episode.py，再通过同一锁执行npm run render；禁止更新清单去认可旧媒体。

三构图4:3核心x315..1125、底部<918，poster与3:4 JPEG一致。没有额外全局片尾。配乐Kevin MacLeod《Wallpaper》，CC BY4.0。当前环境未执行逐字ASR或全片人工听辨；检查范围和用户观看反馈分开记录。


## 成片与发布记录

v0.51.0流程导航修订已完成正式编码与独立媒体复核，完整SHA见[render-result.json](render-result.json)，实际范围/限制见[qa-final.md](qa-final.md)。原v0.47.0已被用户观看并提出结构反馈，旧输入通过[历史索引](revisions/v0.47.0.json)追溯；本版不预记用户认可。GitHub发布与线上核验后按#152收尾。

## 第8批参考资料名单与当前入口

本批为已验收的完整原片追加`title-author`参考资料名单，每页最多4项、默认5秒，仅显示完整原题与明确作者或机构。原旁白、字幕、分镜及现有视觉依赖保持；不运行装配、TTS、正文渲染或混音。基线`61d3b984a594578a67bc34aa374cccd0326cd9d6`的Git完整原片已逐字节保存在`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`，本批直接消费该body并另做实际追加媒体保真检查。

当前冻结入口为本期`freeze.py`，保留旧清单全部140个key与既有共享依赖；旧article/research/package记录通过`revisions/reference-endcards/`下before快照核对，其余按原路径核对。当前清单声明实际资料与新入口依赖，不声称它已重现旧MP4。原实质输入校验保留；storyboard、words、带SHA的分镜快照及placeholder只读检查，不再重写。来源JSON及其中记录的原始补证文件分别按完整SHA纳入冻结，技术实读日期与本轮题名/署名补查范围按来源记录区分。

资料负责人停写且来源预检通过后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/tx-saga
python3 episodes-codex/tx-saga/freeze.py
python3 episodes-codex/tx-saga/freeze.py --verify
```

默认`npm run render`调用共享bibliography wrapper，先核对来源和冻结，再运行`render:body`及附录。`render:body`保留本期原voice→mix闭环、编码参数与concurrency=2，只把mix输出改到`out/body.mp4`；`npm run render:references`从该完整body单独追加名单。`npm run verify:references`用于后续完整交付核验，会检查最终媒体；本批入口审计只执行只读freeze与wrapper.verify_freeze，不重复整片解码。旧正文QA和发布事实按原记录保留，最终总帧数以新receipt、render-result和发布metadata为准。进度见[第8批记录](../../docs/reference-endcards/batch-8/README.md)，不预记尚未完成的媒体或线上结果。
