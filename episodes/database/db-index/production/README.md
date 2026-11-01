# EP.15《加个索引，为啥就快了？》重制工程

2026-10-24 用户明确授权制作 issue #66。本期工程与已上线的
`episodes/db-index` 分开保存；不改变其他期的暂停状态。

## 观看与资料

- `video.mp4`：1920×1080，30 fps，130.8 秒，旁白、字幕与背景音乐。
- `cover-16x9.*`、`cover-4x3.*`、`cover-3x4.*`：三种封面。
- `captions.srt`：与真实 TTS 句子边界对应的字幕。
- `script.md`、`pronunciation.md`：脚本与读音表。
- `research.md`：实际核验的 MySQL 官方资料及主张对应关系。
- `article.mdx`：正文与片外深入阅读。
- `qa-independent.md`：独立技术与关键静帧检查，非正式上线批准。

## 重现

先安装 Python numpy、scipy、soundfile；本环境可用
`/workspace/.venvs/video-studio/bin/python`。TTS 只从环境变量读取密钥。

```sh
# 在仓库根目录，已有 takes 时不要重新请求配音。
python3 episodes/_shared/voice/prep.py --dir episodes-codex/db-index
python3 episodes/_shared/voice/gen.py --dir episodes-codex/db-index
python3 episodes/_shared/voice/build.py --dir episodes-codex/db-index
python3 episodes-codex/db-index/assemble.py
python3 episodes/_shared/voice/selfcheck.py --dir episodes-codex/db-index
python3 episodes/_shared/place_v2.py --dir episodes-codex/db-index --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/db-index
```

```sh
cd episodes-codex/db-index/remotion
npm ci
npx tsc --noEmit
npm run render
npm run covers
```

## 时序与审查边界

本次模型下载被环境网络策略拒绝，因此没有自动 ASR。`words.json`
明确写 `asrModel: none`、`wordAlignment: false`；`chars` 内每个字携带的是
**整句边界**，不能用作逐字高亮或句中挂词。整句边界来自实际生成的音频，
句首起音复用共享 `onset_rule.py`。两个首次术语都位于独立句首，已用共享
`label_onset_strict.py` 实测验证，未豁免窗口。

共享 `selfcheck.py` 只证明帧长、句首挂词和最短镜长等检查通过；其 ASR 差异
列表因未识别而为空匹配，不能解读成读音已通过。最终观看与听辨仍是上线前
的一环，制作阶段仅交付本地观看版。2026-10-24 用户观看后已批准合并代码与 GitHub 站点部署；本次按 v0.45.1 只上站点，详细记录见 `release.md`。

本期使用程序绘制 canvas。`storyboard.json` 保留真实镜长、旁白、字幕、
音频位置和术语挂词；其 `elements` 是挂词记录，完整视觉布局以
`remotion/src/Main.tsx` 为准。现行通用 storyboard 生成器面向浏览器组件的
完整元素 schema，本期未冒称通过该生成器的所有布局检查。


## 第5批资料名单：当前入口与原片复用

本批仅在既有Git发布MP4后追加资料名单，原片完整字节已保存在`revisions/reference-endcards/body.mp4`，同SHA副本位于`remotion/out/body.mp4`；基线、旧输入清单、文稿、package及发布身份分别归档在同目录。原旁白、字幕、分镜、占位快照、程序、动画与批准版主体保持，不运行prepare、assemble、TTS、正文重渲或重混音。

本期历史工程没有独立`freeze.py`，旧`source-sha256.json`只记录当时列出的有限输入；这些旧key全部保留，不能把新增依赖说成旧片已按新清单重渲。新增薄`freeze.py`先验证已归档旧记录，旧package在修前快照处核对，再登记当前真实源码、选定配音、默认入口和资料生成输入；它不复制或重写SB、words及placeholder，也不承诺源码可逐字节重现已验收MP4。事务片后补MySQL身份组件、素材、许可及旧包装器继续保留。

`references.json`采用现行`title-author`样式，显示完整原题名及作者或机构，每页最多4项、默认5秒。复用本期已有真实实读记录和日期，不把整理资料写成新的GET；不新增技术事实或编造作者姓名。当前来源与实际状态见 [第5批记录](../../docs/reference-endcards/batch-5/README.md)。

全部输入停写、`npm run check:references`通过后，在本期运行`python3 freeze.py`，以`python3 freeze.py --verify`只读核对。默认`npm run render`经bibliography wrapper，保留原`render:voice`→`render:mix`闭环和并发参数，将主体输出到`out/body.mp4`再追加资料；这是后续完整制作入口，本批不执行。根代理直接消费已验收body生成尾卡，并以实际全帧/PTS/AAC/PCM比较验证保留范围。

当前冻结除旧key外还收录新旧三个资料生成器、wrapper、发布检查器、Pillow版本锁、主题及实际引用证据；历史窄清单与当前扩展输入分开记录。最终回执和`render-result.json.publicationMetadata`按新输出接齐后可运行`npm run verify:references`。旧`check-final.py`仅用于其原正文帧数，不能对新附录成片直接套用，也不为本批重复完整解码。

正式接入前实际查看名单、首卡字幕边界及原生暂停/全屏；创建、首发时间和已有平台链接保留。本轮只更新GitHub站点，旧用户观看认可适用于当时主体，不预记新资料卡已获认可。
