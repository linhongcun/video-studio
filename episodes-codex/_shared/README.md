# 独立短片的句级装配与检查

本目录服务本批`tx-2pc`、`tx-tcc`、`tx-saga`、`tx-outbox`。不修改既有冻结工程，不复制共享TTS、裁尾、铺轨、起音或混音算法。现行规则在`docs/RULES.md`；脚本和文章需先经技术复核，动画按真实音轨复验后才冻结编码。

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
