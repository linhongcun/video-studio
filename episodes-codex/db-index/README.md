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
