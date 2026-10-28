# 深浅主题与可读性修复

日期：2026-10-28（北京时间）。基线：`dadb53ede6615aa384b3572f8950e3d449a8870d`。范围：#401–405；仅共享站点样式和站点版本，不改写文章、媒体、内容日期或制作冻结输入。

- #401：原生正文 SVG、图片与 Figure 图片使用主题边框及轻阴影，让深色图板与页底分开；保留图形自身的教学配色及全部图形内容。
- #402：首页首屏、方向卡片、文字与按钮改用主题 token，浅色使用浅底，深色保留抬起的底板及边框，保留布局和村落插画。
- #403：浅色 muted 调深为 `#53666B`，在 bg/surface/surface-2 上的对比度分别为 5.61/6.03/5.23；首屏小字与分隔符沿用主题文字色。语法注释沿用同一 muted token。
- #404：卡片图标使用独立的半透明深色圆底与 overlay 前景，悬停和键盘聚焦均可见；纯白、纯黑及缺图背景实测最低 10.01:1。
- #405：动态 Pagefind 搜索命中使用主题高亮，浅色 7.89:1、深色 8.37:1；代码底色沿用 surface-2，增强层次。

## 验证

全站构建通过，包含日期、参考资料、文章、资源复制、Astro 和 Pagefind；实际抓取 Release 成功。构建后日期和完整学习路径检查通过。

`browser-check.json` 为本地 Chromium 的 44 项检查，覆盖 1440/390 视口与深浅主题、系统偏好、切换、重载及无 JavaScript 的 CSS 回退。首屏实际小字最低对比度为浅色 5.16、深色 6.16；三种表面的 muted、动态搜索结果 mark、封面极端背景与键盘聚焦均通过。Redis 图形属性、文字和子节点与基线一致，仅容器样式调整。24 张工作区截图中选存 6 张代表截图。范围为上述实际样式与交互，手机尺寸使用浏览器视口模拟。

`preservation-baseline.json` 以基线提交及 19,753 项受保护 Git 树摘要保留追溯入口，另记录 196 个发布文件的完整 SHA-256、49 份元数据与 149 份冻结清单。`preservation-check.json` 确认全部一致，受保护路径无新增或修改。详尽树可由基线提交重建，未重复存放全部路径。

```sh
NODE_USE_ENV_PROXY=1 npm --prefix site run build
node site/scripts/check-episode-dates.mjs --built
node site/scripts/check-learning-path.mjs --complete --built
python3 episodes/_shared/tests/secret_scan.py
```

## 上线结果

[PR #406](https://github.com/linhongcun/video-studio/pull/406) 已合并，发布 [v0.83.0](https://github.com/linhongcun/video-studio/releases/tag/v0.83.0)。初次 Pages `40619446002` 和 Release 后 Pages `40619470918` 均成功，发布提交为 `d285ea7121ebacc929a33948fa3ac4d38054a12b`；后者完成后再次确认线上版本、素材提交与日志版本。

`online-browser-check.json` 记录桌面浅色、手机尺寸深色的 24 项生产站点检查，实际小字、三类底色、高亮、图框和封面极端背景的对比度均通过，主题切换与保存正常。使用原生 Chromium TLS 校验和环境代理，未绕过证书校验；12 张线上工作区截图中选存 4 张。`online-verification.json` 确认 98 份线上视频/海报的完整 SHA-256，以及首页、搜索、跳表文章、更新日志和抽查字幕正常。

#401–405 已以 `completed` 关闭，状态快照见 `completed-issues.json`，发布回执见 `publication.json`。本次仅 GitHub 站点，不重发外平台。
