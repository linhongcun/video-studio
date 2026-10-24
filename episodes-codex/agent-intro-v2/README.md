# EP.22 / A01 V2：AI智能体，下一步怎么选？

制作issue：[#131](https://github.com/linhongcun/video-studio/issues/131)。用户观看V1后指出主线模糊、开头流水账，要求直接给悬念或方向。V2只回答：**返回结果怎样改变智能体的下一步？** 首镜以“查着订单却突然反问”为悬念，第二镜进入首次查询，结尾回扣使用情况缺口。

11镜22句，旁白431字（含标点）。同一合成订单8124贯穿：签收3天、使用未知→查询示例7天政策→因使用情况仍未知而询问→用户补充后形成申请建议。没有执行退款。首词cue为01“智能体”、02“模型”；不添加装饰进度条、假应用壳或隐藏思考文字。

本目录为新版生产输入；canonical站点仍为`episodes/agent-intro/`，EP.22、A01及issue不变。V1在`episodes-codex/agent-intro/`和GitHub `v0.50.0`保留，不用新版文件覆盖其冻结记录。

正文与依据见`script.md`、`plan.json`、`article.mdx`、`research.md`、`pronunciation.md`。原4项官方来源已于2026-10-24重读正文。实际成片为2864帧、95.466667秒、5,945,472字节，完整SHA-256：`f9cdfa3b10e0d26baa57ad64a71b34e31860a0304ad6b619a92f346bf3e8ec15`。冻结、媒体及独立复核范围见`qa-final.md`和各专项报告。

## 可复现流程

以下路径从仓根执行；Python需要numpy/scipy/soundfile，渲染需要Node、npm、ffmpeg与`/usr/bin/chromium`。首次生成音频还需要已配置的`MIMO_API_KEY`；不得输出或提交密钥。已有选定takes时重建从`build.py`开始，不重新请求TTS。

```sh
python3 episodes/_shared/voice/prep.py --dir episodes-codex/agent-intro-v2
python3 episodes/_shared/voice/gen.py --dir episodes-codex/agent-intro-v2 --jobs jobs-a.json
python3 episodes/_shared/voice/build.py --dir episodes-codex/agent-intro-v2
python3 episodes-codex/agent-intro-v2/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes-codex/agent-intro-v2 --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/agent-intro-v2
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/agent-intro-v2
```

生成候选、检查风险与确定`voice/picks.json`在build前完成，具体候选批次以`voice/jobs-*.json`和音频记录为准。`assemble.py`是root维护的薄包装，复用共享句级装配；不得另写TTS、裁尾、起音或铺轨算法。真实句边界决定`words.json`、`storyboard.json`及字幕。

在本期`remotion/`运行实际脚本，先安装与检查，再用真实音轨时序预演。以下目录均写入本期输出，不占用较小临时盘存放大批抽帧。

```sh
npm ci
npx tsc --noEmit
node scripts/qa.mjs out/qa-captioned
node scripts/qa.mjs out/qa-no-captions --shots=01,02,06,07,08,11 --motion --no-captions
npm run covers
```

独立复核首2/5秒的主题与悬念、15秒内进入正片首次查询（开头预览不计），以及“结果→缺口→选择”的无字幕连续动作。通过后保留最终带字幕报告的真实图片路径，将其记录为本期`qa-motion-samples.json`，供编码后采样比较。预演参数不等于实际输出已合格。

所有输入负责人停写、预检闭合后，从仓根冻结；不要在旁白尚未定稿或动画仍修改时提前运行。

```sh
python3 episodes-codex/agent-intro-v2/freeze.py
```

再从本期`remotion/`编码，使用共享锁避免多个正式渲染争用资源：

```sh
flock /tmp/video-studio-render.lock npm run render
```

编码后回到仓根，保存实际混音报告并运行共享媒体检查和编码采样：

```sh
cp episodes-codex/agent-intro-v2/remotion/out/mix-report.json episodes-codex/agent-intro-v2/mix-report.json
python3 episodes-codex/_shared/check_encoded_episode.py episodes-codex/agent-intro-v2
python3 episodes-codex/_shared/extract_encoded_samples.py episodes-codex/agent-intro-v2
```

媒体检查包括冻结输入、帧数、格式、响度与完整解码；抽帧相似度不能代替教学表达复核。源冻结后若要修改任何生产输入，先停止本期排队/执行的编码，再复验、重冻结和重新完整编码，不能用新清单认可旧视频。

## 检查与发布边界

本轮不能声称已经完成逐字ASR或全片人工听辨；句级边界、信号检查和句首声学cue不代替这些能力。所有执行者、已完成项目与能力限制据实记录。

干净重建须等root确认最终`source-sha256.json`已冻结后，才复制该清单内输入，在独立目录执行`npm ci`、TypeScript和frame0静帧匹配。本文建立时未执行这项检查，不预写通过。

成片与封面经实际编码复核后，再按当前`docs/RULES.md`发布到canonical站点，并核对完整媒体SHA、字幕和章节。平台新发仍需单独授权。配乐沿用Kevin MacLeod《Wallpaper》，CC BY 4.0，最终发布保留署名。

## 干净重建结果

独立镜像检查已完成，详见[qa-clean-build.json](qa-clean-build.json)。当前冻结清单SHA为`32607f64c97d6cdb7762d16d55b19d34723e530d37f4daf3948fb21c6a0c0df9`，120项原输入与镜像输入均逐项匹配，保留相对共享路径，未复用`node_modules`。全新`npm ci`安装257包，TypeScript检查与相同QA接口的20个开头状态样本渲染完成（01镜17个，02镜显式闸门3个）；captioned frame0与原预演PNG完整字节一致，SHA均为`ac3304c5660aea13409f91a48ea51cf692d72a90bcb7abbb41a2144cef9edc2a`。

合入main后仅共享句级检查器改变；镜像已更新该文件并按新120项清单复核，实际运行新检查器通过。依赖锁、渲染源码、分镜与音频均未变，因此保留同一干净安装和首帧结果，未重复无变化的渲染。旧清单证据单独保存在`qa-clean-build.pre-main-00f43cf4.json`，不作当前清单认定。Node为24.19.0，npm为11.9.0，Remotion为4.0.534；详细版本和命令见报告。

本项复用同一主机的系统Chromium与字体，包下载缓存可能共用；不代表跨系统复现、全片教学检查、逐字ASR或全片人工听辨。实际成片检查和媒体SHA另记。
