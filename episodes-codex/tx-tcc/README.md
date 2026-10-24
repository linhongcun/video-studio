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

v0.49.1流程导航修订已完成正式编码与独立媒体复核，完整SHA见[render-result.json](render-result.json)，实际范围/限制见[qa-final.md](qa-final.md)。原v0.47.0已被用户观看并提出结构反馈，旧输入通过[历史索引](revisions/v0.47.0.json)追溯；本版不预记用户认可。GitHub发布与线上核验后按#152收尾。
