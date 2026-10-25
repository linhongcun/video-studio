# LC.200 左上边界解释修订

修订已完成并上线：[岛屿数量](https://linhongcun.github.io/video-studio/episodes/number-of-islands/)。制作、独立复核、本地网站及线上完整核验均通过。原v0.66.0交付证据保持，当前首发身份仍为v0.66.0，本轮实际补丁v0.67.1。

用户实际观看后指出：第一行第一列为什么不向左、向上访问未解释，会让人误以为只向右下。代码与真实trace已有四向边界检查，缺的是讲解。06只新录第二句：“四个方向都要检查，右边和下面先标记入栈，左边和上边越出地图边界，就直接跳过。”画面实际演右、下之后的左12、上13，箭头止于网格边框，各停48帧；不画外部格，不读取/标记/入栈，14才完成首格展开。

仅06启用新增边界绘制，其他分支及地图默认行为可逐字节还原旧源；其余13镜局部时长、字幕、cue、代码卡时序全等，后段全局平移62帧。27句旧take的81个来源文件保持，只有06-2选新boundary-b。新句保留355464样本，旧为257264，添加1000个零样本使变化99200样本恰好62帧，约2.067秒；没有加速或重录其他句。

只正式渲染新06的487帧，其他已验画面按原片索引通过FFmpeg解码/重新编码组合，非无损bitstream复制；声音使用新整轨及共享BGM重新混音，非旧AAC复用。完整复现入口为制作目录splice-boundary.py、splice-plan.json，旧v66视频/脚本/分镜/源/QA在revisions/boundary-before保留。完整程序、99事件trace和6张封面按精确源与输出SHA复用，未重跑65852个算法案例或重做封面。

新片5845帧/30fps，194.837秒，1080p、AAC48kHz，8787142字节；完整SHA-256 `67bf3a409bae9ab78e845cdf21b456953958d92ef5f2d671676e7729bdb248c6`。完整解码、−16.0LUFS/−3.9dBTP、151输入冻结通过。06预演独立实际26时点、最终20时点/两拼接点通过；95唯一帧与96份同尺寸接受预览比较maxMAE3.266261<8。全部5845个PTS连续、末150帧5695..5844完整Python卡实际打开通过，原人声卡段240000样本为零，最终有BGM另记。

实际报告：[06预检](../../episodes-codex/number-of-islands/qa-boundary-preflight.md)、[声音](../../episodes-codex/number-of-islands/qa-boundary-audio.md)、[正式视觉](../../episodes-codex/number-of-islands/qa-boundary-video.md)、[媒体](../../episodes-codex/number-of-islands/qa-boundary-media.md)。这些检查不代表逐字ASR、全片人耳听辨或用户认可修订。经验L045，范围收敛延续L020；网站和发布结果随后按实际记录。

## 本地网页复核

一次真实构建与一次历史回归；1440亮色/390暗色实际播放、四章8次定位、28句VTT、完整程序、海报/媒体全文SHA通过。网页分别捕获约81.4秒左边界与82.98秒上边界，6张页面图及6张解码图实际打开确认；首卡189.833333秒及+0.0001秒、中末卡全部0 activeCues。其他41个canonical目录/779文件、三封面与程序trace保持；首发v66/ep34/题号200/原publishedAt不变，只加updatedAt和修订媒体时序。准备期harness漏声明config的失败保留，修正后attempt2通过，没有因该错误重建。详见[网站报告](qa-site.md)。

## 实际发布

[PR #282](https://github.com/linhongcun/video-studio/pull/282)已合并为40adfbf4f6a266a8b2a189e89dc5496146f0b199，附注tag及[Release v0.67.1](https://github.com/linhongcun/video-studio/releases/tag/v0.67.1)发布后，[Pages40187760204](https://github.com/linhongcun/video-studio/actions/runs/40187760204)成功。线上首次核验10次完整HTTPS、9,322,681字节全部通过；新MP4/海报全文SHA、28句VTT、四章、完整Python/源码/算法入口及本次Release条目一致，实际记录见[线上报告](online-verification.md)。原issue82保持completed关闭，不重开或改动未执行的平台清单。

新内容约1:20开始明确展示左/上边界。原始用户反馈与v66检查范围保留，尚无用户观看本次修订的结论。
