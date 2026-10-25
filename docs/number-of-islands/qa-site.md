# LC.200 岛屿数量：网站检查

实际检查：2026-10-25T09:04:18.150Z；首次发布v0.66.0，结果通过。2次真实构建和2次历史回归（首轮因首卡原生CC阻塞，修正站点VTT后重建）；1440亮色/390暗色两组，四章共8次真实点击/seek。28句VTT逐字与真实SB帧时一致，正式片5783帧/192.767秒。原生CC激活后恢复默认；每视口实际播放开头约4秒、代码卡约1秒再暂停。150帧/5秒代码卡精确首卡、+0.0001秒与中末卡五个采样无cue，完整Python/文章/源码同源，完整MP4与海报HTTP SHA一致，三封面canonical与production相同。

此前6条算法完整canonical SHA及所有非任务canonical与768c23c0df976ec2247cd4d07d7f188bf4c34624保持，当前已发布媒体在同次构建中逐字节复制；P04、Agent Skills、Adapter均保留，撤下的旧两期Agent没有恢复。首页算法方向、学习入口、七片系列、资料库及RSS可达。新片firstRelease为本次显式tag，内部ep从最终meta读取，不把暂定编号当影片题号。

已实际打开第二次构建后的全部8份页面/浏览器解码图，以及3份最终JPG封面，共11份；题号、标题、3:12时长、四章、完整26行Python与暂停提示正常，未见意外溢出或裁切。具体路径/SHA见actualVisualReview。构建Release提示：[changelog] 拉取 GitHub Releases 失败（fetch failed），降级为外链。新片自身Release/changelog及生产HTTPS待发布后核验，不预记通过；不声称全片听辨、ASR或观众学习效果。详见[机器报告](qa-site.json)。

首卡修复与真实过程：前三次机械attempt及随后精确首卡activeCues=1的blocked补测全部保留在[原始快照](before-card-boundary-fix/README.md)和attempts。站点buildVtt仅对有效静卡的精确末cue结束帧向下取毫秒，执行第二次真实build/回归。修后两视口精确187.7666667s（Chrome currentTime187.766666）、+0.0001s（187.766766）、+.1/中/末卡全部activeCues=0。9项针对性函数验证通过；41份VTT比较仅本片和Two Sum末句提前1ms，39份字节不变，文字/起点/其他结束不变，所有旧canonical完整SHA保持。具体见[vtt差异](vtt-boundary-comparison.json)。MP4/声轨/SB及143制作冻结输入没有因此改动。
