# 独立短片的句级装配与检查

本目录包含句级装配、检查与参考资料附录工具，下方旧命令保留各自适用范围。不修改既有冻结工程，不复制共享TTS、裁尾、铺轨、起音或混音算法。现行规则在`docs/RULES.md`；脚本和文章需先经技术复核，动画按真实音轨复验后才冻结编码。

## 新期的固定参考资料流程

新制作或重制的视频从调研起准备 `presentation: original-title-quote` 的本期 `references.json`、原题/原文证据和文章出处；默认入口必须覆盖参考资料附录。[新期模板](../_template/README.md)提供待填写JSON、package脚本片段及冻结清单示例。不要把复制旧工程的 `render` 命令当作已接入新流程。

`title` 必须保留文档实际原始题名及其语言、字词与标点，`titleEvidence: {locator, evidence}` 可定位。可选 `quotation: {text, locator, evidence}` 保存需要展示的连续原文，画面标「原文摘录」；无需摘录则省略字段。不自行拼接省略，不用概括或译文替代原题/原文；`displayTitle`、`displaySupport` 禁用，内部 `supports` 不上屏。文章引用区另附翻译或解释时分别标「译文」「编者说明」。

```sh
node site/scripts/check-references.mjs --sources episodes-codex/your-episode
python3 episodes-codex/_shared/render_with_references.py episodes-codex/your-episode
```

入口先只读检查来源/文章链接及本期实际 `source-sha256.json`，再调用本期 `npm run render:body`；该命令应把完整正文和已有代码卡混音到 `remotion/out/body.mp4`。随后使用 `append_references_original.py`，默认每页5秒、最多2项、提示暂停阅读，生成最终 `video.mp4`。新器保留并依赖旧 `append_references.py` 的媒体处理实现，不修改旧引擎字节。资料不全或冻结失效时应在正文渲染前失败。

资料清单、文章、核验/题名/短引证据、package脚本、默认入口、新追加器及其旧引擎依赖/依赖锁、资料预检代码与实际主题都随本期输入冻结；最终视频和生成回执不作为编码前输入。Pillow按 `requirements-reference-appendix.txt` 安装，字体及编码环境按实际生成回执记录。该流程不复制配音、混音或起音算法，不改已经发布的冻结追加器。

生成的两份附录回执放在 `revisions/reference-endcards/`，并复制到本期根目录；`render-result.json` 提供最终SHA和 `publicationMetadata`。发布时复制最终视频、文章、来源及两份回执，按该metadata片段填写 `meta.referenceAppendix`、`meta.finalVideoFrames`，正文分镜和 `words.json` 继续描述实际正文范围。

新回执将 `sourceTitles`、`quotations` 与实际清单逐条绑定，记录新器的生成身份及旧引擎依赖SHA。标题与短引各自最多3行，溢出时明确失败，不自动截断、改写成概括或从 `supports` 合成原文。实际原题/原文、版式及播放器仍须复核，不能把回执存在当作已看过原文。

```sh
python3 episodes-codex/_shared/render_with_references.py episodes-codex/your-episode --verify
npm --prefix site run check:references
```

`--verify` 只读核对冻结与媒体，按帮助信息写QA报告；不重写冻结或重渲正文。发布构建在复制媒体之前自动执行同一附录检查：新视频和更换媒体的旧视频缺附录时阻断；只在固定基线名单且媒体字节未变的未处理旧片允许继续分批。来源原文是否真正支持结论、资料卡可读性、原生字幕和暂停/手机全屏效果仍须实际复核。

以下句级装配示例原用于`tx-2pc`、`tx-tcc`、`tx-saga`、`tx-outbox`正文；不要把正文检查器的帧数规则直接用于追加参考资料后的最终媒体。

各片输入：`episode-config.json`（标题、part、slug、镜数、风格、示例、范围、讨论题）、`plan.json`（镜号/slug/章节/visualType/句首cue）、`script.md`（每镜两句完整旁白）、`voice/build.json`、`voice.wav`和封面配置。镜头顺序、数字、术语范围按当期内容，不能照搬旧期参数。

仓根命令（Python需numpy/scipy/soundfile）：

```sh
python3 episodes/_shared/voice/build.py --dir episodes-codex/tx-2pc
python3 episodes-codex/_shared/assemble_sentence_episode.py episodes-codex/tx-2pc
python3 episodes/_shared/place_v2.py --dir episodes-codex/tx-2pc --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/tx-2pc
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/tx-2pc
```

首现cue只能选真实句首。词时间兼容字段保存整句包络，不是内部逐字对齐；无官方ASR模型时不得伪称逐字ASR或全片人工听辨。术语窗口、声学计算只用`episodes/_shared/onset_rule.py`。

算法片尾可显式声明`meta.unvoicedEndCard`（`kind: full-python-solution`、整帧`from`/`durationInFrames`），并在末镜写`codeCardFrom`。字幕在附录前结束，旁白音轨用共享build的尾停参数延长；检查器仍严格核对全部原句和字幕连续性，额外要求附录覆盖视频最后一段、原句音轨不越界、该区间voice PCM全零。它不允许省掉正文字幕或遮住未讲完的句子。LC.11的`prepare_code_endcard.py`只调用共享装配后声明附录，不复制配音/起音实现。

所有写入负责人停写、动态表达独立检查闭合后：

```sh
python3 episodes-codex/_shared/freeze_navigation_episode.py episodes-codex/tx-2pc
```

再到当期remotion执行`npm ci`、`npx tsc --noEmit`、`npm run render`；混音报告从`remotion/out/mix-report.json`复制到当期`mix-report.json`，运行：

```sh
python3 episodes-codex/_shared/check_encoded_episode.py episodes-codex/tx-2pc
```

多人共用机器时完整渲染使用`/tmp/video-studio-render.lock`。冻结包含本目录四份Python文件：第一片冻结后，本批其余片不能再修改共享实现；确需修改时，先停受影响排队/渲染任务，重新冻结、重新编码。编码后的报告不用于重新认可未被旧视频采用的源码。

最终MP4仍须独立查看关键相邻状态、完整媒体解码、响度、字幕、章节和线上完整SHA。通用句级装配已在临时副本复现现有入门片的words、storyboard和SRT字节，与原冻结工程无互相改写。

## 多情景的全局与局部导航

`branch-map/`提供四片共用的流程地图与连续相机；拓扑、镜头绑定及安全变焦时间由各片的`remotion/src/branch-map.ts`确定。图是机制关系，不等于示例依次执行；成功、拒绝、未知、补偿和重试按真实语义区分。字幕在相机外层，原冲突与首现术语需要保持可见。预演须覆盖总览停留、变焦中间态和跨镜头情景切换，不能只做端点图。共享实现修改后，受影响预演须重做；全部停写后再统一冻结。冻结清单会包括实际共享导航生产文件。

本轮v0.50.4沿用v0.47.0旁白与时序（分镜保留原计划v0.47.1导航设计ID），以下检查分别验证主体缩放时留在画面内、以及与实际历史版本的音轨/字幕/镜头边界一致；两者都不能替代实际动态查看：

```sh
node episodes-codex/_shared/check_branch_camera.mjs
python3 episodes-codex/_shared/check_branch_preservation.py --baseline d2e949bbce1835cdc80399f7f7e77ff565f782c3
```

新媒体完成并复制到站点后，加`--encoded`核对四份媒体确为新版、发布副本一致。旧版本通过各片`revisions/v0.47.0.json`指向的Git提交、完整SHA和历史QA追溯，保留用户观看反馈与原检查的适用限制。


规范冻结器本身也被已发布LC.11固定引用，导航片不修改它。当前四片保存编码前实际冻结器的原字节快照和路径迁移记录，摘要完全不变；未来用薄包装加入导航依赖。迁移与独立冒烟验证见[共享冻结器保护报告](../../docs/transaction-branch-freezer-preservation.json)。

## 设计模式的Java暂停卡

D01/D02使用`append_java_endcard.py`在已校验的完整人声正文后附150帧静默Java节选卡。先保存不可变正文和来源身份，再显式声明`meta.javaEndCard`与末镜`javaCardFrom`；字幕和句子时间保持在正文内。`verify`会重建原正文供原句级检查器验证，并校验PCM前缀与零尾，不将Java伪标成Python卡，不改旧共享检查器。

```sh
python3 episodes-codex/_shared/append_java_endcard.py append episodes-codex/observer-pattern --frames 150
python3 episodes-codex/_shared/append_java_endcard.py verify episodes-codex/observer-pattern
python3 episodes-codex/observer-pattern/freeze.py
python3 episodes-codex/observer-pattern/freeze.py --verify
```

两期薄包装转发到新增`freeze_pattern_flow_episode.py`，冻结Java来源、原声正文、复用证明与归档媒体；旧冻结器保持原字节。`audit_sentence_reuse.py`核对复用take和裁切来源。最终派生稿不要再次运行正文装配覆盖尾卡。追加器的异常路径由`test_append_java_endcard.py`验证；实际编码和播放器仍需检查卡首、中、末、无旧字幕及暂停后的解码画面。
