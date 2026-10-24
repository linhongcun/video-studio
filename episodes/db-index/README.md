# EP.15 数据库索引（db-index）

2026-10-24 经用户观看并批准，将 `episodes-codex/db-index` 的重制成片接入本站。
这次只上站点，不重发视频平台，`meta.json` 的历史平台链接保留。

- 成片为 1920×1080、30 fps、3924 帧，画面时长 130.8 秒；不再追加全局片尾。
- 视频 SHA-256：`1b903ab2b78bb6aea837c0f01db711112df333d0430930c653d23906d57f136e`，与批准的观看版逐字节一致。
- `meta.json.finalVideoFrames` 固定成片长度，避免按旧工程的片尾规则多算两秒。
- `storyboard.json`、`voice.wav`、`words.json` 为制作目录的原样副本；分镜冻结副本 `storyboard.fe81a37e.json` 与主分镜相同。
- `chapters.txt` 按实际镜头起点取整秒（开场、镜 02、04、08、12），对应文章的五个章节锚点。
- 公开依据见 `research.md`，技术正文及片外补充见 `article.mdx`。
- 新版的渲染代码、真实音频边界与独立检查报告都在 [`episodes-codex/db-index`](../../episodes-codex/db-index/README.md)。

本目录原有的 `gen.py`、`frame.py`、`remotion/`、`cover/` 等是旧版历史工程，不是当前成片的渲染入口。重新制作请进入 `episodes-codex/db-index/remotion`，不要用旧工程重新生成本目录的分镜或视频。旧的顶层及 Remotion `timing.json` 已删除，防止被站点误用。

配乐：Kevin MacLeod《Wallpaper》（incompetech.com），CC BY 4.0。
