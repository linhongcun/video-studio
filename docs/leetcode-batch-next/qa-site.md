# 三片批量网站QA

最终本地验收通过。实际3次build、2次check:dates --built、2次历史回归；第1次因Perm制作稿HTML注释不符合MDX语法失败，第2次在精确卡首发现native字幕残留，第3次机械矩阵通过。两次失败及原稿/日志/receipt均保留，未抹去失败记录。

三片1440浅色/390深色共6组实际播放、暂停、native CC、24次章节点击seek、84句真实SB字幕核对、30次精确卡首/+0.0001/中末卡零cue、全文Python/source/ISO时间、视频与海报完整HTTP SHA均通过。日期45记录和10条算法有序系列、主页/学习入口/库/RSS回归通过。42部既有canonical共785文件SHA完整保持，所有既有built视频与海报保持。

已实际打开全部12个截图路径：6张真实页面关键帧与3组desktop/mobile字节相同的1080p全文Python卡。页面题头、题号、创建/修改秒版本、四章和10课位置正常，无横向溢出；完整程序、暂停提示和无字幕卡正常。重复同SHA图片在工具中偶有文字未重现，已以完整字节/SHA一致及唯一图的实际全文视图澄清；root另独立核像素相同。没有为截图呈现重编码或重复完整矩阵。

共享VTT只对精确卡首的末cue使用严格早于该时刻的最大毫秒值。45片前后比较：只有climbing-stairs、reverse-linked-list、permutations的末cue各提前1ms，其他42片VTT全文SHA不变，字幕文本、起点和其他结束均不变。第三build实际45份VTT与生成器一致；5个针对性真实函数fixture通过。额外只对受影响旧2片做1440 nativeCC精确卡首/+0.0001短检，均0cue，没有重跑旧片完整矩阵或下载旧线上电影。

Daily文章字节同源；Perm/Rain使用具备原稿快照、冻结SHA、精确diff和确定性transform的站点派生稿。制作源、431冻结输入、正式视频和封面保持验收身份。Perm两个不可见生成标记转MDX注释，讲解与Python代码未改。

本地GitHub Release fetch真实失败并降级外链。本次Release自身li关联3新片、3视频/海报完整HTTPS及旧2小VTT实际发布仍需发布后的显式tag/run核验；当前未声称这些生产检查已通过。实际范围与所有截图SHA见qa-site.json，失败经过见qa-site-attempts.json。未声称全片听辨、ASR或学习效果。

发布前证据同步：整合上游d515f0d4a136667766e5201217e6e5fb746ea861，仅新增旧观察者的QA JSON；网站实际输入与431媒体冻结项未变。原build/browser基线42d49c743bb48bf41c7c4151e5288ef32b53e8ce及receipt不改，保留实际3/2/2次数；另以新主干逐字节核验全部旧canonical，见qa-preservation-final.json，未重复构建或交互。
