# Kafka MQ01 新修订制作入口审查

日期：2026-10-28（北京时间）。只读基线 `d7a5d7682080232617a03cc988b7c25cb50446f4`。本审查未调用TTS或渲染、未改旧工程。

## 正确目录与最小基础设施

当前发布meta.sourcePath为 `episodes-codex/message-queue/revisions/mq-intro/message-queue/remotion`，并非旧根工程。新建同层 sibling `episodes-codex/message-queue/revisions/kafka-intro/message-queue/`；相同深度让既有 shared imports/package相对路径保持准确。旧根工程和mq-intro全部输入、媒体、来源、冻结及QA保留。

可复制基础设施：`prepare.py`、`assemble.py`、`freeze.py`、`verify.py`、`render-final.sh`；Remotion `package.json`/`package-lock.json`、`remotion.config.ts`、`tsconfig.json`、`src/index.ts`/`Root.tsx`/`data.ts`（审读是否含旧参数）、`scripts/stills.mjs`。不得整目录复制旧MP4、语音整轨、storyboard/words/sentences/build、source-sha256、旧QA/发布回执；新脚本、文章、来源、plan、covers、config、Main/theme与输入provenance另建。

`remotion/scripts/review.mjs`有硬编码12镜、旧ACK术语与对应局部时点，**不是通用检查器**，应按新模型和真实句时重新写或定向改。`stills.mjs`只取每镜65%/半分辨率，且没有收集COPYFIT日志，不能以此冒充完整动态检查。

旧episode-config曾保留 `series: peak`，这是历史输入，不应照抄为当前元数据；新config用 message-queue，并保留slug message-queue、EP.10。Kafka新正文/封面共用独立不可变 `episodes-codex/_shared/kafka-covers/style-v1.json`，不依赖会随新集增长的catalog；该文件需冻结。原pageTheme仅给实际功能页面使用，canvas外底可用Kafka系列色。

## 实际环境与依赖

本机 `/workspace/.venvs/video-studio/bin/python` 存在，numpy/scipy/soundfile存在但Pillow未装；默认python有numpy/scipy/Pillow但soundfile缺失。使用视频venv并按仓库锁安装附录依赖：

```bash
/workspace/.venvs/video-studio/bin/python -m pip install -r episodes-codex/_shared/requirements-reference-appendix.txt
```

Remotion依赖必须在新目录按其锁fresh npm ci，不能软链旧工程node_modules。原实际版本Remotion4.0.534/React18.3.1/TypeScript锁提供；浏览器 `/usr/bin/chromium`，无bundle-cache。默认npm缓存不可写，命令显式使用work缓存：

```bash
npm --prefix episodes-codex/message-queue/revisions/kafka-intro/message-queue/remotion ci --cache /workspace/work/kafka-intro-npm-cache --no-audit --no-fund
npm --prefix episodes-codex/message-queue/revisions/kafka-intro/message-queue/remotion run check:types
```

## 声源候选及绝不能复用的语义

已逐条读取24句、选take与送模文本，完整路径/SHA在同目录 `reuse-candidates.json`。13句只是**条件候选**，最终新script逐字一致且新场景正确才复制选定 `.wav/.raw.wav/.txt.json` 三文件；不能因为原来已验收就自动批准。可保留：01-submit两句、02-burst两句、03-roles-2、04-accepted-2、06-resume两句、07-work-1、09-result两句、11-growth-1、12-recap-1。

必须新配：03-roles-1泛称队列改Kafka分区日志；04-accepted-1生产者确认前提；05-pause两句“取走/留在队列”；07-work-2“已经送出”；08-ack两句Rabbit处理确认；10-drain两句“队列排空”；11-growth-2队列计数；12-recap-2总边界。尤其Kafka消费者读取后日志记录仍在；commit是消费组位点，不是Rabbit逐条ACK/删除；积压减少不等于日志排空。页面业务完成仍来自业务结果查询，不能从commit直接连到页面。生产者写成功也不是消费者业务成功。

旧Root/data/音频流程不会自动保证这些技术语义；需要新模型、职责图、剧情及独立动态审。

## 经核对的实际顺序和命令

以下EPDIR统一指新Kafka目录。先定稿script/references/article/plan/config/visual-direction/pronunciation/knoll-props/covers，引用清单原题与真实作者/机构、固定原文证据及文章来源全换Kafka；稿件独立技术审后才TTS。

```bash
/workspace/.venvs/video-studio/bin/python EPDIR/prepare.py
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/gen.py --dir EPDIR --jobs EPDIR/voice/jobs-new.json
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/build.py --dir EPDIR
/workspace/.venvs/video-studio/bin/python EPDIR/assemble.py
/workspace/.venvs/video-studio/bin/python episodes/_shared/place_v2.py --dir EPDIR --mode whole
/workspace/.venvs/video-studio/bin/python episodes/_shared/label_onset_strict.py --dir EPDIR
/workspace/.venvs/video-studio/bin/python EPDIR/verify.py
node site/scripts/check-references.mjs --sources EPDIR
```

`--jobs`是绝对路径或相对EPDIR/voice的路径；若在仓根传EPDIR相对路径需用绝对值，避免common.chdir后路径错误。共享prep按完整script分句并加辅助“好。”供裁尾；显示字幕仍是原文。每镜恰好两句、plan镜数等于config.shotCount；cue必须是真实句首且至少63帧可读。`voice/params.json`旧03额外1.7秒属于原作参数，不能无脑继承；新真实动作/句时再确定。

所有源码/语音/引用/文章停写、预检和动态独立审闭合后：

```bash
/workspace/.venvs/video-studio/bin/python EPDIR/freeze.py
/workspace/.venvs/video-studio/bin/python EPDIR/freeze.py --verify
bash EPDIR/render-final.sh
/workspace/.venvs/video-studio/bin/python EPDIR/verify.py --final
/workspace/.venvs/video-studio/bin/python episodes-codex/_shared/render_with_references.py EPDIR --verify
```

`render-final.sh`已用set -euo pipefail、冻结verify、类型检查、`flock /tmp/video-studio-render.lock`串行正式编码；默认npm render调用共享入口先来源/冻结再正文混音，再追加title-author参考卡。最终使用 `EPDIR/video.mp4`，不发布remotion/out/body.mp4。`verify --final`核对bodyFrames、附录起点/finalFrames、H264/AAC/1920x1080/30fps/48kHz、完整SHA、−16±.3LUFS/≤−2.0dBTP并全解码；它不代替技术/动态图义/真实听辨/播放器审。资料每页最多4项、默认5秒，原题与机构真实完整；新色资料卡若要延续Kafka系列色需新adapter（见puzzles-video做法），不能改被冻结旧附录引擎。

freeze.py已有freeze-inputs.json扩展入口，可加入style-v1、Kafka实际图标与license/source、模型和研究证据等；当前自动shared-component枚举只列branch-map/middleware-identity，新增共享Kafka模板必须显式纳入，不得假定rglob覆盖仓外路径。最终freeze manifest不含MP4/生成receipt，生产输入与输出身份分开。

成片后从实际新片生成文章预定图位并实看；冻结制作文章若需改只做有前后SHA的站点派生稿。复制到episodes/message-queue时同步新article/script/storyboard/words/references/附录receipt、video、poster，按render-result.publicationMetadata更新meta.frame数/附录和sourcePath，保留EP、URL、createdAt/publishedAt/firstRelease与原平台链接；updatedAt按真实完成时间。

然后完整站点build（含dates/references/articles）、学习路径、桌面/手机播放器暂停/全屏/字幕/图回看/来源浮层和海报。新增共享工具代码需独立验证，旧共享字节不改。Release后部署并对线上完整媒体/海报/VTT/页面/更新日志实际GET核对；未做ASR、全片人工听辨或真机操作须如实限定。
