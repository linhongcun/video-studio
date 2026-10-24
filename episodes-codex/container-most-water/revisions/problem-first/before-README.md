# LC.11 · 盛最多水的容器

标题：《盛最多水的容器：为什么每次都移动短边？》。对应[#78](https://github.com/linhongcun/video-studio/issues/78)，站点展示LC.11，独立LeetCode系列。

当前修订4按用户最新要求，把完整Python解法卡从15秒缩短为5秒，保留“暂停查看完整代码”提示。原讲解6544帧，其后150帧静态卡，共6694帧、30fps、223.133秒，约3分43秒；代码与画面内容不改。用户对原主体的认可、15秒过长的反馈和新版技术检查分开记录。

22镜44句、四章起点保持：0、44.2666666667、103.0666666667、176.2秒。正文字幕止于6543，代码卡6544..6693无人声、无旧字幕。完整16行`solution.py`与文章及`solution.json`逐字相同；程序检查沿用v0.50.2已通过结果。

本次复用已验收的编码画面，经FFmpeg准确截短并沿用共享混音调整结尾，不整条重渲动画。人声使用共享`episodes/_shared/voice/build.py`生成5秒尾段，原44句时间及人声PCM前缀逐样本保持；检查聚焦新总长、末帧/展示PTS、代码可读、尾音与网站新时长。生产输入仍冻结，具体执行与旧证据继承范围见`qa-codecard-five-seconds.json`、`qa-codecard-five-seconds-independent.json`与`qa-final.md`。

完整重建仍使用本期`remotion/package.json`；共享配音build后运行`prepare_code_endcard.py`，同步public音轨、冻结输入，再运行`npm run render`。本轮快速修订另记录实际FFmpeg输入SHA与参数。站点实际读取`episodes/container-most-water/`逐字节副本。

v0.50.2的15秒版本证据见旧提交及`qa-python-endcard-independent.md/json`、`qa-python-endcard-site.md/json`，不将历史时长当作当前状态。各版合并、Release与线上结果见`release.md`。未新增逐字ASR或全片人工听辨，不含外部平台投稿。
