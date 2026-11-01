# LC.11 去掉装饰进度线：网站复验

- 结果：通过。站点版本 0.50.1，visualRevision 2；firstRelease 仍为 v0.49.0。
- `npm run build` 与 `node site/scripts/check-learning-path.mjs --complete --built` 通过；73 页、27 个搜索索引页，Agent 系列与原课程路由保留。
- 新视频 SHA-256：`6d1e3b4ca5c0094b3d351dad8aa2a1f53348224b3cd4a28d6e6b2afa674c8adb`，源文件、构建副本和本地 HTTP 响应一致。
- VTT 仍为 44 句，SHA-256 `51a28b58f7ae2d0220fb05cc42737a5c1c32f8af07244b034c3e0a3008bac192`，与 v1 一致。
- 390px 深色与 1440px 浅色：原生 controls 存在；真实点击浏览器原生时间轴中点，两次均跳至 109.066666 秒；四章节实际点击跳转通过。
- 两种状态均静音实际播放约 1 秒后暂停：readyState=4、networkState=1、seeking=false；无浏览器脚本错误或页面横向溢出。
- 浏览器直接提取的两张视频原始帧，旧 y1053 进度线区域与相邻背景逐像素一致；原生播放器时间轴保留。
- 播放器、导航、系列与检查脚本无源代码变更；v1 `site-ui-check.json` 原样保留。

实际截图：

- /tmp/container-progress-removal-site/video-frame-no-decoration-390.png
- /tmp/container-progress-removal-site/updated-player-390-dark.png
- /tmp/container-progress-removal-site/video-frame-no-decoration-1440.png
- /tmp/container-progress-removal-site/updated-player-1440-light.png

边界：只复验两种尺寸和约一秒静音播放，未重复完整响应式矩阵或全片听辨；直接向 video 发送 ArrowRight 未触发跳转，最终改为点击实际原生时间轴并验证通过。GitHub Releases 在本地构建仍使用既有外链降级，发布后的更新日志核验另行执行。
