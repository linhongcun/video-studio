# P02 · 四人过桥

本期用1、2、5、10分钟四人的同一组数据，对照最快者逐一接送的19分钟与另一种17分钟安排。视频先交代条件，再连续展示往返和累计时间，最后回收整体代价；完整最短性核验留在文章，视频不展示或提及证明。独立系列为趣味推理，内部EP29；不属于LeetCode，不追加程序代码卡。

## 开工与依赖

最新主干基线、工作区保护、实际依赖入口见[startup.json](startup.json)。制作目录为本目录，站点读取`episodes/bridge-torch/`。Remotion在本期按现行锁文件`npm ci`安装，不软链已删除工程；配音、声学起音、句级装配、主题和混音均调用仓内共享实现，不复制算法。

## 制作入口

脚本经编辑与数学复核后，使用`episodes/_shared/voice/`准备句子、生成并选择冰糖takes、构建整轨。实际选段与参数保存在`voice/`。

```sh
python3 episodes-codex/bridge-torch/verify_math.py
python3 episodes/_shared/voice/build.py --dir episodes-codex/bridge-torch
python3 episodes-codex/bridge-torch/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes-codex/bridge-torch --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/bridge-torch
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/bridge-torch
```

`assemble.py`只调用共享装配并复制字幕名称，不实现另一套时序。人声必须以实体文件从第0帧铺放。实际`words.json`记录整份`script.md`和`voice.wav`的完整SHA；句级时间包络与声学起音不代表逐字识别或内部词对齐。

停止输入写入、完成关键无字幕过程复核后冻结；渲染前后均只读核对同一清单：

```sh
python3 episodes-codex/bridge-torch/freeze.py
python3 episodes-codex/bridge-torch/freeze.py --verify
```

本期Remotion的真实入口：

```sh
cd episodes-codex/bridge-torch/remotion
npm ci
npx tsc --noEmit
npm run qa:state
npm run stills -- out/preview
npm run covers
```

`QA_FRAMES`可指定全片帧号，`QA_HIDE_SUBTITLES=1`关闭旁白字幕，`QA_CLIPS`指定连续区间；实际输出与源SHA记录在各次samples.json。正式`npm run render`仅在冻结与独立预检通过后启动；多人共享`/tmp/video-studio-render.lock`，TMPDIR使用有空间的短路径。混音前输出`remotion/out/voice.mp4`，最终成片为本目录`video.mp4`。

当前真实人声为6025帧（200.8333秒，约3分21秒）、32句、4章，正常语速。并行制作期间保留已上线的观察者EP28/v0.58.0，本期非口播身份顺延EP29，最终首发v0.60.0；全部原人声与句窗复用，见voice/metadata-sync-ep29.json、upstream-before-encoding.json和upstream-before-release.json。

数学核验、预检、实际编码、响度和网页证据按真实执行范围记录，不用生成参数代替输出检查。正式媒体与发布结果见`qa-final.md`及`release.md`，其中未完成的检查不得预写通过。

## 发布范围

按已有持续授权完成GitHub主干、Release与Pages交付，核验线上完整视频/海报SHA、字幕、章节和真实更新日志后，以`completed`关闭#206并同步#204。外部平台未获本次授权。已发布与用户已观看认可分别记录。

当前已按v0.60.0完成PR #243、附注tag/Release与Pages交付，首轮10次线上核验通过，#206已completed关闭。实际媒体、检查边界与证据见[交付记录](release.md)。

## 第11批参考资料名单与当前入口

本批只在完整原片后追加`title-author`参考资料名单，每页最多4项、默认5秒；本片无Python或Java代码卡，原有收尾、旁白、字幕、场景和配图保持。基线`a1a9821845c83a61a57fbb3f0e10461ef4c55238`的Git发布原片已核对原render-result与总帧数，逐字节保存为`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`。本批直接使用该完整原片追加，不寻找缓存、不重制正文。

原154项历史输入全部现存并按原路径或before快照逐一验证，保留全部原key。当前清单只声明真实现存依赖及本轮资料/入口，不能用作原MP4已重渲的证明。旧freezer、清单和修前文稿/入口完整归档；数学检查、旧渲染编排和媒体QA保留历史身份，本批不重跑。当前freeze.py保留原实质输入约束，并只读核对分镜快照和placeholder；不调用共享写入型freezer、装配、TTS或数学程序。完整源码静态import、别名和公开音轨的实际结果见[入口报告](../../docs/reference-endcards/batch-11/production-entry-check.json)。

资料负责人停写且来源预检通过后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/bridge-torch
python3 episodes-codex/bridge-torch/freeze.py
python3 episodes-codex/bridge-torch/freeze.py --verify
```

默认`npm run render`经共享bibliography wrapper核对来源和冻结后，执行`render:body`并追加参考资料。`render:body`保留原voice→mix命令、H.264/CRF20、concurrency=2及Chromium参数，仅把默认mix输出改至`out/body.mp4`；旧特别修订命令保留历史用途，交付需通过当前参考资料检查。`npm run render:references`从完整body单独追加名单；`npm run verify:references`用于后续完整交付复核。本批只执行来源和只读冻结/入口检查，不运行正文、混音、数学重验或重复全片解码。最终总帧数以新receipt、render-result及发布metadata为准；[本批记录](../../docs/reference-endcards/batch-11/README.md)不预记媒体和线上通过。
