# P08 网站独立检查入口

工具已准备，尚未执行本期验收。运行时读取本期完整媒体、meta、分镜、真实PTS与文章图位，不继承旧P09验收结果；首次本地运行须等根安装最终媒体并完成site build。

```bash
python3 episodes/puzzles/hat-parity/production/qa/site-independent.py --out episodes/puzzles/hat-parity/production/qa/site-local-native
python3 episodes/puzzles/hat-parity/production/qa/site-reading-supplement.py --out episodes/puzzles/hat-parity/production/qa/site-local-reading
```

本地每次独立创建随机空闲端口的RangeHTTPServer，直接读取当前site/dist，先核对dist/publication/production视频完整SHA。不使用旧preview服务。1440×1000、390×844模拟视口实际检查播放器、章节、Figure、28句原生VTT、无重复字幕默认值、资料交界与关键帽子镜头PTS、真实Fullscreen API及844×390横屏、引用交互和明暗阅读位置。自然初始poster不调用load()或先播视频；显式TextTrack API启用另记，不称作点击操作系统字幕菜单。

线上沿用完整入口，只指定实际canonical base及新输出目录；普通完整GET单独执行：

```bash
python3 episodes/puzzles/hat-parity/production/qa/site-independent.py --base https://linhongcun.github.io/video-studio --out episodes/puzzles/hat-parity/production/qa/site-online-native
python3 episodes/puzzles/hat-parity/production/qa/site-reading-supplement.py --base-url https://linhongcun.github.io/video-studio --out episodes/puzzles/hat-parity/production/qa/site-online-reading
python3 episodes/puzzles/hat-parity/production/qa/site-verify-online.py --version ACTUAL_TAG --commit ACTUAL_FULL_SHA
```

普通GET核验完整video/poster/两图、当前VTT、页面meta派生字段、章节、Figure时间、源码入口、列表/RSS与真实Release更新日志；Pages不暴露原始meta/storyboard JSON，另从指定部署提交读取GitHub原始字节比对。无cache-busting、TLS绕过或响应回填。

pass仅代表实际运行的断言；截图须view_image目视后在独立结论中列明实看文件。模拟视口和Fullscreen API不代表物理手机；不声明逐字ASR、全片语义听辨或观众理解效果。真实失败报告保留，重跑使用新的输出路径。
