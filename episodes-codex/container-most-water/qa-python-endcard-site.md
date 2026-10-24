# LC.11 完整 Python 片尾卡：网站复验

- 结果：通过。站点版本 0.50.2；firstRelease 保持 v0.49.0。
- 正式 `npm run build` 与现有 `node site/scripts/check-learning-path.mjs --complete --built` 通过；73页、27个索引页，Agent与原课程保留。
- 成片6994帧，视频帧时长233.133333秒；两种浏览器状态读取容器时长233.152秒，页面均显示3:53。
- 新视频源、构建副本及本地HTTP响应SHA-256一致：`072ae1db566209c671dfb3819cfbbac1f927098e2b65bfe7df9bd89cf903535b`。
- 四章原始精确起点保持0、44.266666666666666、103.06666666666666、176.2秒，390与1440两尺寸实际点击跳转通过。
- VTT仍为44句，SHA-256 `51a28b58f7ae2d0220fb05cc42737a5c1c32f8af07244b034c3e0a3008bac192` 与v2完全一致，最后一条在218.133秒结束。
- 实际开启原生TextTrack showing：108秒旧旁白段有1条activeCue；225秒代码卡activeCues=0，随后约1秒静音播放及暂停后仍为0。
- 原生controls保留，两尺寸暂停代码卡通过；readyState=4、networkState=1，无脚本错误或页面横向溢出。
- 网站运行时代码和v1/v2既有报告保持不变。

实际截图：

- /tmp/container-python-endcard-site/python-card-frame-390.png
- /tmp/container-python-endcard-site/paused-python-card-player-390-dark.png
- /tmp/container-python-endcard-site/python-card-frame-1440.png
- /tmp/container-python-endcard-site/paused-python-card-player-1440-light.png

范围：仅复验390深色和1440浅色，以及代码卡上约1秒静音播放；未重复32项矩阵、全片听辨或算法验证。本地GitHub Releases读取仍走既有外链降级，发布后的更新日志核验另行执行。
