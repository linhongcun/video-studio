# EP.16《扣了钱，对方没到账？》重制工程

2026-10-24 用户要求从未关闭的 issue 选择下一期制作，本轮选择 #67，接续已上线 EP.15 的片尾预告。用户观看并认可第二版后，明确批准合并主干并部署 GitHub。本站使用本目录批准版的原样副本，发布说明见 [release.md](release.md)。

## 内容与资料

用同一数据库内的两个教学账户，解释两步分开确认为什么可能只完成一半，以及一笔事务如何一起提交或回滚。第二版通过原确认值锚点、当前修改预览、焦点移动、共同落位与撤除过程建立状态区别；不再常驻两层大表。应用主动回滚与提交前数据库崩溃恢复分别演示，不把所有语句错误说成自动整笔回滚，也不把例子当作真实跨行支付流程。

用户观看第一版后指出信息密集、主要变化集中在字幕。本轮重做全部视觉调度，见 `visual-direction-v2.md`；动态验收见 `qa-motion-v2.md`。第一版源码与检查记录保存在 `revisions/v1/`，归档视频仅保留在工作区、不入库；它们用于对照，不作为当前视觉方案的合格证明。

- `script.md`、`pronunciation.md`：16 镜旁白和读音表。
- `research.md`：实际核验的 MySQL 官方正文、主张和适用边界。
- `article.mdx`：正文及 ACID、自动提交、错误处理、恢复、脏读的片外补充。
- `storyboard.json`、冻结副本：配音决定的真实镜长、句级字幕和术语挂词。
- `video.mp4`：第二版批准成片；本地用于区分版本的 `video-v2.mp4` 与它逐字节一致，不重复入库。三种封面、`captions.srt` 同目录保留。
- `render-result.json`、`qa-final.md`、`qa-independent.md`：实际检查范围与结果。

## 重现方式

从仓库根目录运行。保留选定 takes；已有 take 时不要重新请求不确定的 TTS。

```sh
python3 episodes/_shared/voice/prep.py --dir episodes-codex/db-transaction
python3 episodes/_shared/voice/gen.py --dir episodes-codex/db-transaction
# 追加候选配音时使用 voice/jobs_b.json；最终选段由 voice/picks.json 决定。
python3 episodes/_shared/voice/build.py --dir episodes-codex/db-transaction
python3 episodes-codex/db-transaction/assemble.py
python3 episodes/_shared/voice/selfcheck.py --dir episodes-codex/db-transaction
python3 episodes/_shared/place_v2.py --dir episodes-codex/db-transaction --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/db-transaction
```

```sh
cd episodes-codex/db-transaction/remotion
npm ci
npx tsc --noEmit
npm run stills
# 动态检查：连续阶段无字幕/无旁白预演
node scripts/motion-qa.mjs /tmp/ep16-motion --shots=03,07,08,09,11 --flow=07-09
npm run covers
npm run render
```

Python 需要 numpy、scipy、soundfile，本环境位于 `/workspace/.venvs/video-studio`；渲染需要 FFmpeg、Chromium 和 Noto Sans CJK SC。配乐沿用仓库的 Kevin MacLeod《Wallpaper》，CC BY 4.0。

## 时序和检查边界

本轮重新检查后，官方 ASR 模型下载仍被环境网络策略拒绝，未绕过限制。`words.json` 明确记录无 ASR、无逐字对齐；字符携带的是整句区间，不能用来生成句中逐字挂词。字幕依据真实句子音频边界；三个首次术语各自位于独立句首，复用共享声学起音规则检查。

本期 `assemble.py` 仅整理已铺好的音轨、镜头时序和元数据，不另写配音铺轨或起音算法。完整视觉布局以 `remotion/src/Main.tsx` 为准，分镜 `elements` 记录需要校验的术语挂词，并非完整 UI 元素清单。

预检、独立样张复核、编码后抽帧和自动媒体检查各有明确范围，不将其中一项通过说成已完成所有读音听辨或人工审片。此次用户明确批准 GitHub 站点发布，平台历史投稿保持原样。


## 第5批资料名单：当前入口与原片复用

本批仅在既有Git发布MP4后追加资料名单，原片完整字节已保存在`revisions/reference-endcards/body.mp4`，同SHA副本位于`remotion/out/body.mp4`；基线、旧输入清单、文稿、package及发布身份分别归档在同目录。原旁白、字幕、分镜、占位快照、程序、动画与批准版主体保持，不运行prepare、assemble、TTS、正文重渲或重混音。

本期历史工程没有独立`freeze.py`，旧`source-sha256.json`只记录当时列出的有限输入；这些旧key全部保留，不能把新增依赖说成旧片已按新清单重渲。新增薄`freeze.py`先验证已归档旧记录，旧package在修前快照处核对，再登记当前真实源码、选定配音、默认入口和资料生成输入；它不复制或重写SB、words及placeholder，也不承诺源码可逐字节重现已验收MP4。事务片后补MySQL身份组件、素材、许可及旧包装器继续保留。

`references.json`采用现行`title-author`样式，显示完整原题名及作者或机构，每页最多4项、默认5秒。复用本期已有真实实读记录和日期，不把整理资料写成新的GET；不新增技术事实或编造作者姓名。当前来源与实际状态见 [第5批记录](../../docs/reference-endcards/batch-5/README.md)。

全部输入停写、`npm run check:references`通过后，在本期运行`python3 freeze.py`，以`python3 freeze.py --verify`只读核对。默认`npm run render`经bibliography wrapper，保留原`render:voice`→`render:mix`闭环和并发参数，将主体输出到`out/body.mp4`再追加资料；这是后续完整制作入口，本批不执行。根代理直接消费已验收body生成尾卡，并以实际全帧/PTS/AAC/PCM比较验证保留范围。

当前冻结除旧key外还收录新旧三个资料生成器、wrapper、发布检查器、Pillow版本锁、主题及实际引用证据；历史窄清单与当前扩展输入分开记录。最终回执和`render-result.json.publicationMetadata`按新输出接齐后可运行`npm run verify:references`。旧`check-final.py`仅用于其原正文帧数，不能对新附录成片直接套用，也不为本批重复完整解码。

正式接入前实际查看名单、首卡字幕边界及原生暂停/全屏；创建、首发时间和已有平台链接保留。本轮只更新GitHub站点，旧用户观看认可适用于当时主体，不预记新资料卡已获认可。
