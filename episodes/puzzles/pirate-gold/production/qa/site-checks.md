# P09 网站独立检查入口

状态：工具准备完成，尚未执行本期本地或线上网站验收。本期检查只读取实际冻结媒体、发布副本和构建站点；不继承P07的QA结果。工具语法与帮助入口已检查，媒体、稿件、meta、动画和Git状态未被这些工具修改。

根代理安装最终媒体并完成站点build后：

```sh
python3 episodes/puzzles/pirate-gold/production/qa/site-independent.py --out episodes/puzzles/pirate-gold/production/qa/site-local
python3 episodes/puzzles/pirate-gold/production/qa/site-reading-supplement.py --out episodes/puzzles/pirate-gold/production/qa/site-local-reading
```

主入口核对全片真实解码PTS为连续1/30秒，然后实际操作1440×1000及390×844 Chromium视口：播放和暂停、章节、Figure加载及回看、默认烧录字幕/原生TextTrack状态、当前全部VTT、资料首中末、五个海盗关键镜头准确帧、Fullscreen API、原图入口、R1/R2引用点击/键盘/移动端触摸及明暗主题边界。补验入口直接拍摄“小结”和“参考资料”的实际阅读位置，并在引用面板真实溢出时执行触摸滚动；不溢出时如实记录未发生滚动。

线上浏览器操作沿用同一入口，只改base和输出目录：

```sh
python3 episodes/puzzles/pirate-gold/production/qa/site-independent.py --base https://linhongcun.github.io/video-studio --out episodes/puzzles/pirate-gold/production/qa/site-online
python3 episodes/puzzles/pirate-gold/production/qa/site-reading-supplement.py --base-url https://linhongcun.github.io/video-studio --out episodes/puzzles/pirate-gold/production/qa/site-online-reading
```

浏览器使用原生canonical HTTPS，无TLS绕过、响应回填或cache-busting。普通canonical GET及完整媒体SHA由根代理单独执行；为其准备的`verify-online.py --version TAG --commit FULL_SHA`只写`qa/online-http-verification.json`。

脚本的`pass`表示实际动作及断言，截图仍须通过view_image目视后，才按实际查看文件和范围填写`visualReviewed`。真实视口/触屏模拟与Fullscreen API不能写成物理手机测试；没有执行的全片听辨、逐字ASR或学习效果实验也不计为通过。旧失败报告与图片保留，定向修工具时使用新的输出目录，不覆盖失败记录。
