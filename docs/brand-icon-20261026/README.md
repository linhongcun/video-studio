# 代码小村网站图标

用户确定 01「代码小村」为头像后，要求网站 icon 采用同一图案。本次统一浏览器标签页图标、网站页头标志与 Apple 收藏图标，保存最终头像及原始候选源文件。

小尺寸版保留头像的屋顶、屋身、代码尖括号与斜杠四条原始路径，移除外圆环、辅助短线及金点，将 viewBox 收紧至 `160 160 704 704`。网站页头直接引用 `site/public/favicon.svg`，避免维护两套图形；图标 URL 使用 `?v=code-village` 更新旧书本图标缓存。PNG32 用于兼容，PNG180 用于 Apple 收藏图标。

同步基线为 `c3666b42`（v0.73.0 图文统一）；开工前保护并恢复上一轮头像文件和选型记录，重新安装当前站点锁文件。网站版本升级为 v0.74.0，内容时间、成片与平台链接不变。

已执行检查：

- 按当前锁文件 `npm ci`；完整 `npm run build` 通过，包括日期、参考资料、配套图文检查及47篇搜索索引。
- Chromium 实际检查 1440 / 390 宽度的 light / dark 四种组合：首页与文章页标志正常，页头图标为40 / 35 px，没有横向溢出和 JavaScript 异常；手机菜单可打开和关闭。结果见 `browser-checks.json` 与四张页头截图。
- 独立检查确认四条核心路径与已选头像完全一致，32 / 180 px PNG 与 SVG 在深蓝底的渲染一致，图标引用及读屏名称正确。
- `python3 episodes/_shared/tests/secret_scan.py` 通过（19475文件）；`git diff --check` 通过。

[PR #358](https://github.com/linhongcun/video-studio/pull/358) 已合并，发布提交为 `b77dc7e0d51e4bfffea74571df3254f21ab71638`；[v0.74.0 Release](https://github.com/linhongcun/video-studio/releases/tag/v0.74.0) 于北京时间 2026-10-26 21:20:09 发布。[Pages 40329604429](https://github.com/linhongcun/video-studio/actions/runs/40329604429) 成功，实际构建在 Release 之后执行，部署于 21:26:39 完成。已取消重复待处理的 40329689220。运行、步骤与 Release 元数据见 `deployment.json`、`deployment-job-times.json` 和 `release.json`。

北京时间 2026-10-26 21:33:53、v0.74.0 发布时点的实际 HTTPS 核验共7项全部通过：原始与带缓存参数的 SVG、PNG32、PNG180 均返回200，完整 SHA-256 与发布源文件一致；首页、HTTP 文章页和更新日志均返回200，引用新的 SVG、PNG 后备、Apple 图标和页头标志，页面版本为 v0.74.0；更新日志同时核对本次 Release 正文与版本链接。结果见 `online-verification.json`。

归档时依次整合了制作规范提交 `29dc6461` 和后续 GitHub 导航入口提交 `2cc29a77`（#360、v0.75.0），保留上游全部改动；再次确认品牌 SVG、PNG 字节未变，页头继续引用同一 `brand-mark` 图标。上述7项证据保留 v0.74.0 发布时点的实际结果，不作为后续版本的重复发布记录。仅网站品牌图标更新；没有向外部平台发片或更改账号资料。
