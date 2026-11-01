# EP.23 · 设计模式 D01：策略模式

制作 issue [#163](https://github.com/linhongcun/video-studio/issues/163)，系列总览 [#161](https://github.com/linhongcun/video-studio/issues/161)。用户授权从设计模式选题中选择一期制作，完成后部署 GitHub 网站，本次选择策略模式。

一笔100元示例订单贯穿：普通100、会员90、活动80；算法从结算内部拆成可替换函数，由调用方选择，再将原金额交给规则并接回结果。活动八折改七五折得到75，新增新客减10元得到90。各次独立计算，优惠不叠加。数字、规则与舍入都是教学设定，完整代码及实际运行证据在 `demo/`。

16镜32句、四章；具体帧数、媒体指标及最终SHA见 `qa-timing.json` 与 `render-result.json`。旁白采用冰糖自然配音，不加速。代码画面仅03、14；其余用规则实际拆出、选中引用、金额调用与返回、修改范围说明设计，不加装饰进度条。

## 当前修订：章节口头衔接

用户观看v0.52.0后认为整体问题不大，指出章节入口缺少承接与方向说明。本次只改04、11、15的六句与对应动作：先说清下一段要看什么，第二句再展开。旧版工程和媒体以Git tag `v0.52.0`为不可变基线，历史检查报告存于`revisions/v0.52.0/`。

当前5292帧、176.4秒，比原版增加94帧、约3.13秒。其余十三镜的原PCM、局部字幕/cue及镜长逐项严格保持，见`chapter-bridge-assembly.json`。只重渲三个镜头；其余画面从原版精确取帧，统一快速H.264编码与共享混音，码流字节不声明相同。

本次修订的复现入口（仓根；使用仓库已有的v0.52.0 tag）：

```sh
python3 episodes-codex/strategy-pattern/revise_chapter_bridges.py archive
python3 episodes-codex/strategy-pattern/revise_chapter_bridges.py assemble
python3 episodes-codex/strategy-pattern/freeze.py
python3 episodes-codex/strategy-pattern/revise_chapter_bridges.py render
python3 episodes-codex/strategy-pattern/verify_chapter_picture_reuse.py
```

`archive`从不可变tag恢复忽略目录中的旧基线，`assemble`调用共享配音和时序实现，只替换三镜PCM；全量配音重建命令作为原版历史步骤保留在下文。当前冻结清单包括局部拼接脚本与真实基线输入，冷检前先恢复这些基线。

## 内容与运行证据

- `research.md`：实际查阅的课程和官方文档、短引、日期、使用位置与边界；未取得的GoF全书不伪称已读。
- `script.md`、`article.mdx`、`pronunciation.md`：同一主线的脚本、图文与读音。
- `demo/pricing.py`、`demo/verify_demo.py`：整数分计算、重构对照、选择与返回值契约、金额舍入和边界检查。
- `demo/`的版本快照与diff：同名活动函数只改80→75的真实补丁证据；单文件V1/V2模拟另行标明。
- `qa-editorial.md`、后续动态与成片报告：检查执行者、范围和限制，以实际存在的产物为准，不将机器通过写成用户已观看认可。

仓根运行：

```sh
python3 episodes-codex/strategy-pattern/demo/pricing.py
python3 episodes-codex/strategy-pattern/demo/verify_demo.py
```

## 配音与真实句级装配

使用共享 `episodes/_shared/voice/` 的prep/gen/build，不复制TTS、裁尾、铺轨或起音算法。重建已有takes无需再次请求TTS：

```sh
python3 episodes/_shared/voice/build.py --dir episodes-codex/strategy-pattern
python3 episodes-codex/_shared/assemble_sentence_episode.py episodes-codex/strategy-pattern
python3 episodes/_shared/place_v2.py --dir episodes-codex/strategy-pattern --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/strategy-pattern
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/strategy-pattern
```

首次术语“策略模式”在06句首，使用共享Rule的实测声学起音；句包络兼容字段不是逐字对齐。本次ASR能力、候选选择和实际执行的声音检查见 `voice/` 的报告，缺失的逐字ASR或全片人工听辨不声称通过。

## 动画、冻结与正式编码

在本期 `remotion/` 运行：

```sh
npm ci
npx tsc --noEmit
node scripts/qa.mjs out/qa-stills
node scripts/qa.mjs out/qa-motion --shots=04,07,08,09,10,11,13 --motion --no-captions
npm run covers
```

QA目录应使用本期已忽略的 `remotion/out/` 路径或工作盘的临时目录，避免填满独立 `/tmp`。具体执行路径见检查报告。无字幕样片必须检查最终composition参数及实际输出，不能仅凭传参认定。

所有生产输入负责人停写、关键动作独立复核闭合后，从仓根冻结：

```sh
python3 episodes-codex/strategy-pattern/freeze.py
python3 episodes-codex/strategy-pattern/freeze.py --verify
```

`freeze.py`调用共享冻结器，并将本期可运行代码、版本快照、示例结果及渲染辅助脚本补入同一清单。它不复制起音或时序算法。正式编码在本期 `remotion/` 运行 `npm run render`；多人共用时以 `/tmp/video-studio-render.lock` 串行编码，`TMPDIR`使用工作盘上的短路径，本期为`/workspace/strategy-tmp`；路径过长会使Chromium的SingletonSocket无法创建，首次失败和修正见`qa-render-environment.json`。修改冻结输入前必须停止本期排队或渲染，重新复核、冻结并编码。

复制混音报告后，从仓根执行：

```sh
python3 episodes-codex/strategy-pattern/freeze.py --verify
python3 episodes-codex/_shared/check_encoded_episode.py episodes-codex/strategy-pattern
```

最终还需实际编码的状态与中间态复核。站点副本位于 `episodes/strategy-pattern/`，不得重生成另一个未经检查的媒体；视频、海报、字幕、四章起点、源码入口、系列与更新日志按完整SHA和实际HTTP GET核验。发布记录见 `release.md` 与线上核验JSON。

配乐：Kevin MacLeod《Wallpaper》，CC BY 4.0。发布按仓库现行规范与用户授权执行。
