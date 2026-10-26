# EP.21 · TCC：先预留，再确认

按用户“每种常见实现独立短视频”指导制作，14镜28句、3618帧、120.6秒，只讲业务预留的一成功一失败。先看[分布式事务入门](../distributed-tx-intro/README.md)，本期不重复方案总览。

- script.md / research.md / article.mdx：单一主线、实际官方正文核验与工程边界。
- plan.json / episode-config.json / visual-direction.md / knoll-props.md：固定示例、分支重置与时序动作。
- voice/qa.json / voice/selected-take-audit.json / voice/substitutions.md：25b+2c+1d，实际送模与信号/格式/原始转换来源。无逐字ASR或全片人工听辨结论。
- qa-motion-samples.json与qa-continuous-samples.json在实际预演后生成；只有实际检查才记录通过。

音轨SHA256：2063df3b6d39a6ee2b2f7403135ce0cd94cae209bc2a3605aabe2bbfc6ea5f0e，48k单声道PCM16，共5,788,800样本。正确数量4/0/0→3/1/0→3/0/1；另起取消分支回到4/0/0，重复请求不再更改数量。

整轨和声学实现复用episodes/_shared/voice；本期通过共享episodes-codex/_shared/assemble_sentence_episode.py按真实句级边界生成分镜、words和字幕，后接共享place_v2 whole、label_onset_strict及check_sentence_episode.py。禁止用本期参数另造裁尾/起音算法。

```sh
cd episodes-codex/tx-tcc/remotion
npm ci
npx tsc --noEmit
node scripts/qa.mjs /tmp/tx-tcc-preview
node scripts/qa.mjs /tmp/tx-tcc-motion --shots=04,07,11 --motion --no-captions
npm run covers
```

完成独立检查并所有负责人停写后，由root统一冻结并通过共享渲染锁正式编码；不能在排队或编码后继续改输入。成片指标以render-result.json为准，预演不等于实际媒体通过。三构图封面4:3核心x315..1125/y<918，poster取3:4 JPEG。最终不追加额外全局片尾；配乐Kevin MacLeod Wallpaper(CC BY 4.0)。


## 成片与发布记录

v0.51.0流程导航修订已完成正式编码与独立媒体复核，完整SHA见[render-result.json](render-result.json)，实际范围/限制见[qa-final.md](qa-final.md)。原v0.47.0已被用户观看并提出结构反馈，旧输入通过[历史索引](revisions/v0.47.0.json)追溯；本版不预记用户认可。GitHub发布与线上核验后按#152收尾。

## 第7批参考资料名单与当前入口

本批为已验收的完整原片追加`title-author`参考资料名单，每页最多4项、默认5秒，仅显示完整原题与明确作者或机构。原旁白、字幕、分镜、导航和身份图形保持；本批不运行装配、TTS或正文渲染。Git基线`656b525f533037f1c0dff6383c4afa69926e612c`的完整原片已逐字节保存在`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`，由本批直接消费并另做实际追加媒体保真检查。

当前使用本期`freeze.py`。它保留旧清单全部131个key和既有共享依赖；旧article/research/package的记录通过`revisions/reference-endcards/`下before快照核对，其他历史输入按原路径核对。当前清单声明实际资料与新入口依赖，不声称它已重现旧MP4。原输入校验保留；storyboard、words、带SHA的分镜快照及placeholder只读核对，不重写。

资料负责人停写且来源预检通过后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/tx-tcc
python3 episodes-codex/tx-tcc/freeze.py
python3 episodes-codex/tx-tcc/freeze.py --verify
```

默认`npm run render`现调用共享bibliography wrapper，先核对来源和冻结，再运行`render:body`及附录。`render:body`保留原voice→mix与并发参数，只把mix输出改到`out/body.mp4`；`npm run render:references`从该完整body单独追加名单。`npm run verify:references`用于后续完整交付核验，会做最终媒体验证；本批入口检查只做只读freeze和wrapper.verify_freeze，不重复整片解码。旧正文范围内的QA和历史发布事实按原记录保留，最终总帧数以新receipt、render-result和发布metadata为准。进度见[第7批记录](../../docs/reference-endcards/batch-7/README.md)，不预记尚未完成的媒体或线上结果。
