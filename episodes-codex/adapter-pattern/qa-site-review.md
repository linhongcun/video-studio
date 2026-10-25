# D03适配器模式：含Skills主干的v0.63.0站点检查

本轮从合入并行Skills的新树重新接入/构建检查，基线adf0d51208b271c1ec07fe5b4a9f78d2e2c4338d；当前首发身份v0.63.0。旧v0.62.0只是未发布D03候选，实际同名tag属于并行Agent Skills。906cbad1中24份旧QA输出、root图报告、当时非生产QA工具及旧meta已逐字节归档，路径映射见qa-site-candidates/v0.62.0-906cbad1/archive-path-map.json。未拷整份生产源码/配音，也未把旧通过记录改名。

通过显式replace-unpublished-candidate，仅把新D03首发身份从v0.62.0替换为v0.63.0。D01/D02的metadata与核心文件保持原字节；对当前main的元数据差异只含adapter-pattern。Skills元数据未改，原首发仍为v0.62.0。

本候选重新完成1次build、1次当前历史路径回归、1440浅色/390深色两个浏览器用例。四章共8次实际seek并短静音播放，最大误差约0.000000667秒；24句字幕文字和全部时间通过。Java卡5121+150，三个点均为完整载入24cue、mode=showing、activeCues=0，实际解码后可暂停。播放器截图恢复原生字幕默认disabled。

39个发布页与5个学习方向保留，新agent-skills及Agent系列存在，两期已退agent-intro/agent-tool-execution仍无页面/资产。D01→D02→D03及D02前后课、首页/系列/资料库/RSS通过。正文#java与完整Java源码链接、两SVG原生computed字号/锚点/bbox和页面无溢出通过。

当前媒体仍为5271帧/175.7秒，完整SHA25bf61a8521517af488b45cf13b66b27d94b4fd963738ca14b19c3176d4a8fe7；没有重配或正式重编码。发布、构建和HTTP媒体/海报完整SHA一致，当前source/render/mix报告同步。

本次实际重新打开6张当前截图：Java解码卡、两张窄屏SVG、窄屏/桌面播放器及窄屏Java图文。范围与SHA见qa-site-visual-review.json；未声称其他图片新看、全片听辨、ASR、用户认可或学习实验。旧候选本地检查完整保留，当前没有复用旧build或浏览器结论。

本机Release读取仍降级外链，未记成实际Release条目通过。Release之后Pages成功时，继续运行site-verify-online.py：11canonical普通GET、完整媒体流SHA、真实v0.63.0条目及新Skills保留/旧Agent不恢复。
