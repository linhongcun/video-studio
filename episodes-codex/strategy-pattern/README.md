# EP.23 · 设计模式D01：策略模式新手版

制作issue [#163](https://github.com/linhongcun/video-studio/issues/163)，系列总览[#161](https://github.com/linhongcun/video-studio/issues/161)。用户2026-10-25明确授权按新手理解反馈重排视频并完成网站上线。

## 当前内容

《策略模式：结算怎样换一种算价办法？》采用13镜26句、四章，一笔原价100元的示例订单贯穿。先认识会员九折与活动八折两个函数，再明确传入函数本身、pricing本次对应所选函数、调用之后才产生结果。会员返回90元，重新从100元开始改传活动函数得到80元；只切换一次，优惠不叠加。

观众前置为简单函数调用与条件判断，函数可以作为参数在片中补齐。三问为为什么考虑拆分、具体怎样替换和执行、何时值得用。七五折变更、新客注册、类型和校验留在文章拓展。依据与新手检查问题见[参考拆解](../../docs/strategy-beginner-reference.md)；真实帧数和媒体SHA以qa-timing.json、render-result.json与release.md为准。

## 历史边界

v0.52.0首发16镜，v0.54.1仅补三处章节入口。两版技术报告分别保留在revisions/v0.52.0与revisions/v0.54.1；原媒体、音轨和工程均可从各自不可变Git tag恢复。本轮完整重做，不使用旧三镜拼接结果或旧版局部检查给新版结论。历史revise_chapter_bridges.py仍保留，但不是当前重建入口。

## 真实配音与装配

共享实现为episodes/_shared/voice及episodes-codex/_shared，不复制TTS、裁尾、铺轨、起音或混音算法。当前新take使用beginner后缀，旧a/b/c不覆盖。候选选择、文本一致性、信号边界与实际能力限制见voice下本轮报告。

从仓根用已选定录音重建，无需再次请求TTS：

```sh
python3 episodes/_shared/voice/build.py --dir episodes-codex/strategy-pattern
python3 episodes-codex/_shared/assemble_sentence_episode.py episodes-codex/strategy-pattern
python3 episodes/_shared/place_v2.py --dir episodes-codex/strategy-pattern --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/strategy-pattern
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/strategy-pattern
```

词兼容字段使用句包络，不是逐字时间戳。首次策略模式位于04第一句，以共享声学起音对齐；缺失的逐字ASR或全片人工听辨不得写成通过。

## 动画预检与冻结

本期remotion下运行npx tsc --noEmit，再以scripts/qa.mjs生成全13镜真实时序预演；06–10需要连续无字幕过程，检查尚未执行、参数绑定、执行返回、清旧结果及同原价重算。报告必须含源SHA、provisional:false和最终hideSubtitles/showSubtitles参数，实际图像仍须查看。

根任务与独立复核确认生产输入停写后，从仓根冻结：

```sh
python3 episodes-codex/strategy-pattern/freeze.py
python3 episodes-codex/strategy-pattern/freeze.py --verify
```

冻结包含选定新录音、真实SB/words、生产源码和共享实现、本期可执行demo及实际使用的mjs脚本；不再自动依赖历史chapterbridge/out/base文件。原封面三尺寸内容仍符合主题，复用已上线原件并核对完整SHA。

## 完整编码与发布

正式渲染由本期remotion/package.json调用Remotion和共享Wallpaper混音工具。使用短TMPDIR=/workspace/strategy-tmp和/tmp/video-studio-render.lock；输入变化必须停止当前渲染、重新检查并冻结。随后执行：

```sh
python3 episodes-codex/strategy-pattern/freeze.py --verify
python3 episodes-codex/_shared/check_encoded_episode.py episodes-codex/strategy-pattern
```

正式MP4还要完整解码、实际关键帧与跨镜过程复核。站点复制同一媒体及字幕/章节数据，保留slug、四个章ID和firstRelease v0.52.0。合并、Release后Pages部署，再执行verify-online.py的8个canonical普通GET，流式完整核对视频、海报、VTT和章节/系列/RSS/更新日志；核验通过后completed关闭#163。平台新发未授权。

配乐Kevin MacLeod《Wallpaper》，CC BY4.0。最终执行结果与未完成能力以实际QA/release记录为准，不将制作验收当成用户已观看认可。
