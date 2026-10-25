# LC.200 边界说明修订：网站检查

实际检查：2026-10-25T11:03:14.538Z；修订v0.67.1，结果通过。一次构建和一次历史回归；1440亮色/390暗色两组，四章共8次实际点击/seek。28句VTT逐字与新SB帧时一致，正式片5845帧/194.833秒。实际播放06第二句边界画面约1秒后暂停，以及完整程序卡约1秒；原生CC测完恢复默认，精确首卡、+0.0001秒与中末卡采样activeCues全0。完整Python/source/文章及MP4/海报HTTP SHA匹配。

本片ep34/LC200/首发v0.66.0/原publishedAt保留，仅当前补丁tag与updatedAt表示此次修订。三封面、程序/trace及所有其他canonical与17effcf6c18e4277d13178960f065ea82c904f6d保持，七片算法series顺序不变，P05当前已发表状态保留。首页算法方向、学习入口、系列/库/RSS可达，不要求旧片挤进首页近期卡。

已实际打开全部12份新截图/1080p解码帧：两视口的06左边界、上边界和完整Python卡。左/上红箭头及挡线均实际停在地图边界，明确“越界→跳过，不标记、不入栈”；题头/LC200/3:14/四章和完整代码正常，未见意外溢出或裁切。构建Release提示：[changelog] 拉取 GitHub Releases 失败（fetch failed），降级为外链；该补丁自身changelog与生产HTTPS在发布后按显式身份核验，不预记通过。不声称全片听辨、ASR或观众学习效果。详见[机器报告](qa-site.json)。

本轮实际构建1次、历史回归1次。首次harness准备检查因缺少config读取而在构建前退出，修复后第二次attempt完整通过；失败经过保留在qa-site-attempts.json，没有第二次构建或重编码。左边界取样目标2441帧、上边界2489帧，实际捕获时间与窗口记录在boundaryScene；精确首卡及+.0001/中末卡的actual currentTime与零cue记录在captions.silentSamples。
