# EP.20 两个订单，怎么撞成同一个号了？（global-id）

2026-10-24 按用户的GitHub持续发布授权，将 `episodes-codex/global-id` 中完成检查的重制成片接入本站，版本v0.45.4。只更新站点，保留原发布日期、首发版本及平台历史链接。

- 成片1920×1080、30fps、4419帧，封装时长147.306秒；不追加全局片尾。
- 视频SHA-256：`14bd428ea60068a454310759cbf329e80e33a3f5aef6deed3761c8bce21da471`，与制作工程通过检查的冻结文件逐字节一致。
- 分镜、冻结副本 `storyboard.2fb344e3.json`、最终音轨和词时间兼容文件原样复制；30句外挂字幕采用冻结的 `from/to`，章节按实际镜长及文章ID匹配。
- `meta.finalVideoFrames` 固定当前成片长度；旧顶层及Remotion的 `timing.json`、`chapters.txt` 已移除，避免旧时序影响本站。
- 技术依据见 [research.md](research.md)，完整适用边界见 [article.mdx](article.mdx)。

当前渲染入口、选定配音与检查报告在 [制作工程](../../episodes-codex/global-id/README.md)，实际命令在 `episodes-codex/global-id/remotion/` 执行。本目录原有 `gen.py`、旧配音/校验脚本、`remotion/`、`cover/`、`assets/` 等为历史工程，不用于重建当前成片。不要从这些旧文件恢复旧版分镜或声音时序。

配乐：Kevin MacLeod《Wallpaper》（incompetech.com），CC BY 4.0。
