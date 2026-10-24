# EP.17 数据库锁（db-lock）

2026-10-24 经用户观看并认可，将 `episodes-codex/db-lock` 的重制成片接入本站，发布版本 v0.45.3。本次只上站点，保留历史平台链接。

- 成片1920×1080、30fps、3457帧，画面115.233秒、容器115.242秒；不追加全局片尾。
- 视频 SHA-256：`93804b4838a9e414a930c91e15bd6e835cba2913d6aea747195ac624f46b4299`，与用户观看版逐字节一致。
- 分镜及冻结副本 `storyboard.34fe0cd8.json`、音轨和词时间兼容文件原样复制；28句字幕使用冻结的 `from/to`，章节直接按镜长和文章ID匹配。
- `meta.finalVideoFrames` 固定成片长度；顶层及 Remotion 的两份旧 `timing.json` 已删除，避免旧数据覆盖新镜长。
- 公开依据见 [research.md](research.md)，技术边界及补充见 [article.mdx](article.mdx)。

当前渲染入口、选定配音、动态检查及发布记录在[制作工程](../../episodes-codex/db-lock/README.md)。本目录原有 `gen.py`、`build_shot_audio.py`、`map_timing.py`、`common_split.py`、`validate.py`、`realign.sh`、`shotlist.md`、`remotion/`、`cover/` 和 `assets/` 是旧版历史工程，不用于重建当前视频。

配乐：Kevin MacLeod《Wallpaper》（incompetech.com），CC BY 4.0。
