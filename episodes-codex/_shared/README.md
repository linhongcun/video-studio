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

所有写入负责人停写、动态表达独立检查闭合后：

```sh
python3 episodes-codex/_shared/freeze_sentence_episode.py episodes-codex/tx-2pc
```

再到当期remotion执行`npm ci`、`npx tsc --noEmit`、`npm run render`；混音报告从`remotion/out/mix-report.json`复制到当期`mix-report.json`，运行：

```sh
python3 episodes-codex/_shared/check_encoded_episode.py episodes-codex/tx-2pc
```

多人共用机器时完整渲染使用`/tmp/video-studio-render.lock`。冻结包含本目录四份Python文件：第一片冻结后，本批其余片不能再修改共享实现；确需修改时，先停受影响排队/渲染任务，重新冻结、重新编码。编码后的报告不用于重新认可未被旧视频采用的源码。

最终MP4仍须独立查看关键相邻状态、完整媒体解码、响度、字幕、章节和线上完整SHA。通用句级装配已在临时副本复现现有入门片的words、storyboard和SRT字节，与原冻结工程无互相改写。
