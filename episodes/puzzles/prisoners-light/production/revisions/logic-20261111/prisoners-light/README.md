# P10 囚徒与灯 · 2026-11-11 方法动机修订

本独立修订从主干 `27329c38aae4e8388a9999ab1c357fa9c8783fd9` 的已发布 P10 建立，保留题面、协议模型、固定12访主例、14镜结构与既有封面。最小补录03第一句及04两句，说明为何把累计放在同一人的记忆里、每人只贡献一次，以及亮灯不能再留下第二份、也不能破坏待收信号或用掉尚未成功发送者的资格。原制作、冻结、媒体与QA保留历史身份，本目录不继承旧检查结论。

`input-provenance.json` 记录基线、复制输入完整SHA及旧冻结身份。25句保留文本、TTS文本、选定take与WAV/文本/raw文件按完整SHA核对；03/04的3个替换句默认使用新 `logic` 标签，原3个take未复制。整条新WAV与全部句级时序由共享工具重建，不要求和旧声轨字节相同，也不把输入take复用宣称为整轨PCM保持。

当前Remotion依赖以本目录现有 `package-lock.json` 为准。若缺少安装目录，从 `remotion/` 运行 `npm ci --no-audit --no-fund`；不得借用被删除工程或不同锁文件的缓存。声音工具依赖numpy、scipy、soundfile与FFmpeg，任务可使用已经准备的 `/workspace/work/pirate-motivation-20261107/.venv/bin/python`；实际使用的解释器与版本在本轮声音记录中另记，不复制该venv。

## 先定稿，再配音和装配

以下命令从本目录执行。脚本及草分镜先通过独立四问审读；本工具准备阶段不会自行请求TTS。

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

`prepare.py` 调用原共享 `voice/prep.py` 并记录当前脚本/旁白SHA。`gen.py` 默认只把 `voice/jobs-logic.json` 中3项03/04任务交给原共享 `voice/gen.py`，不生成25句已选take；任务标签须与picks一致，文本取自准备好的句子。需要候选重录时使用新标签和对应jobs/picks，不覆盖已选take。`build.py`、`assemble.py` 分别调用共享整轨和句级装配，后者仅补回系列palette及元数据，不复制任何裁尾、归一化、起音或铺轨算法。

`voice_reuse.py` 检查25句的文字、TTS文字、选中标签及全部take字节。新3句须改动旧文并使用新标签；生成后及正式冻结时还须有真实的新WAV与文本。共享整轨重新测量全部句长、静音、响度与真峰值；按实际句级结果生成分镜、字幕与章节，不能给后段机械加一个统一整数帧差。无成功ASR或语义听辨时继续明确能力边界，不重试已确认Unsupported的识别模型。

## 预检、冻结与完整渲染

完成新03/04声音与动态预检，并核对后段主例及章节的时序影响后，先绑定本轮文章两处精确图位，再停止输入写入并冻结。`freeze-inputs.json` 只列本轮实际输入，不读取旧QA为新片背书。协议数据与旧有限模型报告是保持原字节的复用输入，不表示本轮已经重新执行独立协议检查。

```sh
python3 freeze.py
python3 freeze.py --verify
bash render-final.sh
python3 verify.py --final
python3 render.py . --verify
python3 export-article.py
```

默认渲染使用全局高清编码锁 `/tmp/video-studio-render.lock`，完整执行Remotion正文、full-range BT.601→limited BT.709真实像素转换、共享背景音乐混音，再追加同紫色原题/作者或机构参考列表。资料页默认150帧，最终帧数、SHA及音频来源按新 `render-result.json` 与实际回执确认，不能沿用旧6206帧。最终交付是本目录 `video.mp4`，不是 `remotion/out/body.mp4`；正式媒体生成后冻结器拒绝重写本目录清单。

封面JPG与poster按复制时SHA原样复用。`cover-style.json` 仍描述它们原来的生成身份，不要求已扩充的当前共享catalog重新匹配旧源哈希；新冻结记录实际复用图片字节、旧冻结身份及本轮实际视频与资料引擎输入。来源清单继续指向原已核验研究证据并一并冻结，字段预检不冒称本轮已重新读取来源。

## 文章截图与发布接入

本轮不重构已认可文章正文；按新分镜为两处Figure绑定精确帧，必要时补与新旁白同义的短说明。`export-article.py` 从本目录最终MP4完整解码、精确选取整数帧，按原limited709→full601矩阵真实转换JPEG，**只输出本目录 `article/`**及 `qa/article-image-export.json`，不写publication。回执记录旧发布图片SHA；生成成功不等于图片已被实际查看。

完成独立实际媒体、资料页、两图和播放器检查后，由主agent统一接入原publication。接入须复制本轮最终视频、分镜、字幕相关数据、资料清单与两份附录回执，更新sourcePath到本目录remotion；保留原EP、slug、题名、创建和首发身份，仅实质修改更新updatedAt。精确帧、章节起点、图位及文章差异以本轮真实记录为准，GitHub持续授权不扩展为外部平台重发。

本文只记录修订范围、基础工具与默认流程，不预记新声音、动态、成片、网站、上线或用户认可通过。
