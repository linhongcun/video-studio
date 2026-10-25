# 设计模式 D02 · 观察者模式

制作 issue 为 [#164](https://github.com/linhongcun/video-studio/issues/164)，系列总览为 [#161](https://github.com/linhongcun/video-studio/issues/161)。先解释语言无关的设计关系：变化来源、订阅者、共同通知约定与可调整的订阅集合；具体语言实现仅作配套图文拓展。当前真实音轨为12镜24句、5章、4979帧，约2分46秒；思想/动态预检、正式成片、本地站点及实际上线核验均通过，首发v0.58.0；见[发布记录](release.md)，不预记用户已观看认可。

## 配音与装配

Python 工具环境为 `/workspace/.venvs/video-studio/bin/python`，已具有 numpy、scipy 和 soundfile。音色冰糖、模型 mimo-v2.5-tts；用共享工具生成逐句候选并裁掉隔离尾词“好。”，不进行合成后变速。口播稿通过审读且明确冻结后才请求 TTS。

```sh
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/prep.py --dir episodes-codex/observer-pattern
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/gen.py --dir episodes-codex/observer-pattern --jobs jobs-production.json
/workspace/.venvs/video-studio/bin/python episodes-codex/observer-pattern/voice/signal-audit.py
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/build.py --dir episodes-codex/observer-pattern
/workspace/.venvs/video-studio/bin/python episodes-codex/_shared/assemble_sentence_episode.py episodes-codex/observer-pattern
/workspace/.venvs/video-studio/bin/python episodes/_shared/place_v2.py --dir episodes-codex/observer-pattern --mode whole
/workspace/.venvs/video-studio/bin/python episodes/_shared/label_onset_strict.py --dir episodes-codex/observer-pattern
/workspace/.venvs/video-studio/bin/python episodes-codex/_shared/check_sentence_episode.py episodes-codex/observer-pattern
```

上述生成入口只在制作和明确重建时运行；已发布输入的复核使用只读检查，`place_v2` 加 `--no-copy`，报告写到临时目录，不重写清单追认旧媒体。新 take 不覆盖旧 take，选段写在 `voice/picks.json`，文本与声学检查见 `voice/substitutions.md`、`voice/candidate-audit.json` 和 `voice/audio-qa.json`。

本轮24句均选择首轮a候选，文本/48kHz转换逐样本一致，共享裁尾检查无硬警报、候选与归一后整轨均无≥0.50秒句内低信号标记；没有合成后变速。整轨−16.0 LUFS，4倍采样真峰值−2.2 dBTP，whole铺轨最大偏移0帧，三个句首术语窗口全部通过。配音SHA-256为 `6a8c262ee470a7da2228658de027fa95a236ecd275534ca5aab9e6d06d06ffde`。

本轮没有可用 ASR 模型库、模型缓存或音频转写工具，未执行逐字 ASR、发音听辨或全片人工听辨。`words.json` 的兼容字符字段仅为句包络；只有句首起音按共享 `onset_rule.py` 测量，不能将其描述成内部词级时间或已验证读音。完整能力边界见 `voice/runtime-readiness.json`。

## 冻结与正式编码

以下冻结命令从**仓库根目录**运行；先确认独立动态预检通过、全部生产负责人停写。共享冻结器要求placeholders目录存在。本轮实际清单为119项，包含选定takes、分镜、音轨、渲染源码和共享依赖。

```sh
mkdir -p episodes-codex/observer-pattern/remotion/src/placeholders
/workspace/.venvs/video-studio/bin/python episodes-codex/_shared/freeze_sentence_episode.py episodes-codex/observer-pattern
```

读取冻结成功结果后，再从**本期remotion目录**单独启动编码；不要把渲染放在一个前置失败后仍会继续的独立shell行里。本轮输出为`../video.mp4`，日志和混音报告位于`out/`。

```sh
set -e
mkdir -p /workspace/obs-tmp
PATH=/workspace/.venvs/video-studio/bin:$PATH TMPDIR=/workspace/obs-tmp flock /tmp/video-studio-render.lock npm run render
```

首次误启动因工作目录错误而立即中止，未采用其输出；正确冻结后重新从头编码，实际记录见`qa-render-environment.json`，相关教训为L034。编码完成后只读核对清单并运行共享`check_encoded_episode.py`，不重新冻结去追认旧输出。

## 检查与交付

文稿审查、实际连续动画预演、源冻结、正式 MP4 复核与上线核验各自记录实际执行范围。冻结后任何生产输入修改须先停止受影响编码，再重新检查和冻结；生产清单不能在编码完成后重写来追认未被采用的源码。站点只接入检查通过的同一份 MP4、JPG 和必要文本数据，不复制制作 WAV、PNG 或 Remotion 工程。

GitHub 主干合并、Release、Pages 部署及线上完整 SHA 检查在现行持续授权内完成，成功后以 completed 关闭 #164；外部平台没有新发授权。实际版本、部署与线上结论以后续 `release.md` 为准，不将制作检查写成用户观看认可或初学者学习效果测量。

站点图文使用`article-site.mdx`：它由冻结`article.mdx`仅转换原生SVG属性名，原文/派生SHA与转换次数记录在`site-article-derivation.json`。这项发布格式修复不改变已编码119项输入，不重渲视频；实际网页验证见`site-svg-correction.json`，具体教训L035。
