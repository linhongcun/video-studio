# P09 海盗分金币 · 2026-11-07 倒推动机修订

本修订从最新主干 `570d4f86c2304dfdae38820075bf34b33d8f124b` 的已发布 `clarity-20261106` 版本建立，仅补充第04镜的倒推动机。保留原14镜结构、原投票模型、其余26句已选配音takes和既有封面；第04镜两句新配，整轨由原共享工具重新生成，后续镜头、章节与截图时间随实际新增时长顺移。原修订的冻结清单、媒体与QA保留历史身份。

`input-provenance.json` 记录基线、复制输入SHA、旧冻结身份，以及26句保留文本、选定take和WAV/原始WAV/文本文件的完整SHA。第04镜原take未复制，默认新take标签为 `motivation`；旧整WAV、words、storyboard、build、字幕、QA、冻结清单、成片与输出目录均未复制。保留的 Remotion placeholder 仅是源码回退输入，不能当作本轮实际时序。

依赖使用原锁文件，当前锁与仍保留的 `clarity-20261106/pirate-gold/remotion/package-lock.json` 完全相同，因此本地 `node_modules` 软链到该现行修订的真实安装目录。该软链不提交、不作为冻结输入，也不指向已退休工程；换环境时从本目录 `remotion` 运行 `npm ci --no-audit --no-fund`。

当前默认Python缺少soundfile，首次生成在导入阶段停止，尚未发出TTS请求。随后在 `/workspace/work/pirate-motivation-20261107/.venv` 建立任务局部环境，安装官方PyPI的soundfile0.14.0并复用现有NumPy/SciPy，成功运行两句生成。实际Python、依赖版本及恢复范围记录于 `voice/runtime-provenance.json`；换环境按共享voice工具依赖准备对应解释器，不复制此venv。

## 定稿后的配音与时序

所有命令从本目录运行。先定稿 `script.md`、`plan.json`、画面及配置，再准备句子；本轮实际定稿后执行如下共享流程；仅两个04任务会请求TTS，其余26句由守卫保持。

```sh
VOICE_PYTHON=/workspace/work/pirate-motivation-20261107/.venv/bin/python
"$VOICE_PYTHON" voice_reuse.py --setup-only
"$VOICE_PYTHON" prepare.py
"$VOICE_PYTHON" gen.py
"$VOICE_PYTHON" build.py
"$VOICE_PYTHON" assemble.py
"$VOICE_PYTHON" ../../../../../../_shared/place_v2.py --dir . --mode whole
"$VOICE_PYTHON" verify.py
npm --prefix remotion run check:types
npm --prefix remotion run check:references
```

`prepare.py` 只调用原共享 `voice/prep.py`，随后记录脚本与旁白SHA。`gen.py` 默认仅将 `voice/jobs-motivation.json` 中两项04任务交给原共享 `voice/gen.py`；它拒绝将其他句子加入生成任务。需要另一轮04take时，可用新jobs文件并相应调整04的 `picks.json`，保留未选take身份。`build.py`、`assemble.py` 分别调用原共享整轨和句级装配，不复制其算法。`assemble.py` 只在共享结果上补回紫色palette与系列元数据。

`voice_reuse.py` 检查其余26句的文本、TTS文本、选定标签和每份take字节保持。新的04必须使用新标签且改变原文；生成或冻结阶段还会检查实际新take存在。整WAV不再要求与旧版相同：共享整轨会重新测量句长、静音、整体响度和真峰值，并重建全部时序；复用输入take不意味着新整轨对应片段的PCM增益或旧时间戳保持不变。

本轮在两句定稿后仅生成04的两个 `motivation` takes，再运行共享build/assemble/place与时序检查；26句原选take的52份WAV/文本文件及对应原始WAV完整SHA保持。新正文5227帧，04从1077帧开始、720帧（24秒）；其后句子样本统一顺移681124样本，即425.7025帧，所以镜头起点取整后各自偏移425或426帧。原3000/4365图位保持镜内位置时对应新3426/4790帧，不能统一加一个整数时差。实际报告为 `qa/voice-reuse-and-timing.json`，仅证明输入身份、信号和时序，不代替新旁白语义听辨或动画验收。

## 预检、冻结与默认渲染

先完成新04的声学与视觉检查、其余镜头相对时序差异复核，输入定稿后再冻结；setup不生成新冻结或编码许可。

```sh
python3 freeze.py
python3 freeze.py --verify
bash render-final.sh
python3 verify.py --final
python3 render.py . --verify
```

默认入口保持统一高清编码锁，完整Remotion正文、真实full601→limited709像素转换、共享混音及紫色原题/机构参考列表。最终帧数使用新 `render-result.json`，不沿用旧4951帧。参考列表仍默认150帧；实际旁白、正文、资料页、字幕与播放器另行审查。产生本轮 `video.mp4` 后，冻结器拒绝覆盖本目录清单。

`article.mdx` 已在编码前同步倒推起点的理由，并按新分镜绑定两处图位：3420帧／114秒、4785帧／159.5秒。两个时间均对应已经确认的局内结果；实际图像须在正式MP4后精确导出并实看，旧文章及图片SHA保留在发布派生记录中。保留原EP、slug、标题、创建和首发时间，实质修改只更新updatedAt；GitHub持续授权继续，不扩展为外部平台重发。

## 局部渲染可行性

只读检查确认旧04区间为 `[1077,1371)`：起点是关键帧，结束后的1371是P帧，后一个闭合GOP关键帧为1577。因此不能只渲新04后直接从1371无损流拷贝后段；旧AAC包也不与这些边界对齐，新整轨需重新混音和编码。

若选择仅用Remotion渲04，可精确解码旧前后画面后拼接统一编码；这能省Remotion渲染但会使其余画面多一代编码，不能称原码流无损复用。最大限度流拷贝还需把旧1371–1576的206帧重编码为桥段，并验证SPS、B帧DTS、时间基和接缝。当前默认未启用这两条媒体复用路线；若改用旧MP4作为实际生产输入，必须另行明确冻结基线媒体SHA与拼接工具，不能绕过现有禁止输出MP4充当输入的断言。

本文件记录基础设施、实际两句TTS及共享装配和剪切边界。新动态、成片、上线以各阶段实际回执为准，不预记用户观看认可。
