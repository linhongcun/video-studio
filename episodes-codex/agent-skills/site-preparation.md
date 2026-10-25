# Skills 站点接入准备

2026-10-25（北京时间）。**根代理已锁定EP.31/v0.62.0并授权正式本地接入；15项发布副本、完整构建及双视口站点QA已执行通过。尚未GitHub发布，仍等待根代理的最终成片审读与发行收尾。** 实际结果见`qa-site.json`、`qa-site-build.json`和`qa-site.md`，本地更新日志请求降级情况已单独注明。

- 内部EP.31，slug `agent-skills`，series `agent`，`lessonOrder: 0`。并行主干P03已使用EP.30，本片顺延，不修改旁白、画面或音轨。当前已撤下的 `agent-intro` / `agent-tool-execution` 不恢复、不作依赖。
- 制作源码入口固定为 `episodes-codex/agent-skills/remotion`；文章四章为 `problem`、`loading`、`resources`、`boundaries`，开始帧从正式分镜累计计算，不从临时预览估算。
- `sync_site.py` 导入只读。它核验冻结输入、正式MP4完整SHA、配音文本与字幕、文章锚点之后，才接受显式 `--publish --release <根锁定版本> --date <北京时间日期>` 创建发布副本。版本必须等于当时 `site/package.json`。
- 复制范围为站点需要的文章、制作说明/分镜/字幕/字时及渲染数据、正式MP4和三张JPG封面，共15项；WAV、PNG、Remotion及demo源码留在制作目录。
- 根代理完成正式接入、完整Astro/Pagefind构建并启动本地preview后，运行 `python3 episodes-codex/agent-skills/verify_site.py --base http://127.0.0.1:4331/video-studio/`。脚本不会自动构建、复制、冻结、渲染或发行。
- QA计划为1440×1000与390×844真实Chromium：标题、源码入口、唯一Agent目录、四章播放器/文章seek、所有VTT文字与帧级时间、字幕实际激活、起始播放与自然结束、图文窄屏、主页/学习入口/系列/资料库、Pagefind搜索，以及完整媒体字节副本。
- 实际结果仅在完整执行后写入 `qa-site.json` / `qa-site.md`；截图在ignored的 `qa/site/`。真实浏览器检查不能冒充完整人工听辨或学习效果测量。

本轮本地候选锁定为v0.62.0，最终发行与线上核验由根代理收尾；本地没有执行GitHub合并、Release或Pages部署。
