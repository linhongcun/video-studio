# LC.200 岛屿数量交付记录

已完成并上线：[LC.200 岛屿数量：怎样保证一座岛只数一次？](https://linhongcun.github.io/video-studio/episodes/number-of-islands/)。选题为既有issue #82，内部EP34，实际首发v0.66.0。

从同一张海陆地图说明四邻规则，先推导整座归属与保留分支，再命名迭代DFS和栈。14镜28句4章、5783帧/30fps约3分13秒；最后150帧为完整26行Python卡，可暂停查看。真实执行源与动画共用99事件trace，65,852例独立并查集完整分区验证通过。

成片SHA-256：`4c2389bee3dc407e66873c6a2bd061ab6eb8f153f96146651fdfcce7ef0bb44d`，9,306,666字节。完整解码、全部PTS、40个实际成片关键帧、94份同尺寸比较、150帧程序卡、声音与三比例6张封面通过，见[制作侧复核](../../episodes-codex/number-of-islands/qa-final.md)。143项冻结输入保持。

网页实际完成2次构建与2次历史回归。首轮机械检查后追加精确首卡暂停，发现WebVTT向上取整仍激活末句；只修正网站附录边界，复验两视口精确首卡及+0.0001秒均无cue。仅本片及旧两数之和最后结束戳各提前1ms，其余39份VTT字节不变，旧canonical媒体与数据完整保持。修前函数、VTT、receipt/log、机械报告和失败真实值保存在[修前证据](before-card-boundary-fix/README.md)，最终结果见[网页复核](qa-site.md)与[vtt针对性验证](vtt-boundary-validation.json)。

1440亮色/390暗色实际播放/暂停、CC、四章8次定位、28句VTT、完整Python/文章/源码、媒体和海报完整HTTP SHA均通过；8张网页/浏览器解码截图和3张canonical JPG已实际打开。最新canonical保留基线为768c23c0；随后519a0fab的四份文档证据也已合入，网站构建输入不变。P05草稿、最新中间件/Skills/适配器/P04及旧Agent删除结果均保留。

经验更新L010、L020、L041与S004，技术检查不等同用户观看认可或初学者效果实验；没有ASR或全片人工听辨声明。按持续授权只发布GitHub网站，线上核验通过后已将#82以completed关闭。

## 实际发布结果

- [内容PR #277](https://github.com/linhongcun/video-studio/pull/277)合并提交`2da29e20ae411b23d294c83e808089772342fd07`，保留Codex联合署名。
- [附注tag/Release v0.66.0](https://github.com/linhongcun/video-studio/releases/tag/v0.66.0)真实发布后触发[Pages 40179672105](https://github.com/linhongcun/video-studio/actions/runs/40179672105)，结果success。
- 2026-10-25 09:18:04 UTC线上39次完整HTTPS响应、94,123,723字节通过，新MP4/海报全文SHA与制作/canonical/tag一致；28句VTT、四章、完整程序/源码、七片入口/RSS与本期Release日志通过，旧6算法及最新课程媒体保持，旧Agent URL仍404。见[线上核验](online-verification.md)。
- [issue #82](https://github.com/linhongcun/video-studio/issues/82)在09:18:26 UTC以completed关闭，原body与平台复选项保持，见[关闭证据](issue-completion.json)。

首次在线检查因脚本将所有章节href误设为文章锚点而失败；实际VideoPlayer支持`#player`回退，八次真实点击/seek此前已通过。验证器改为逐一核对桌面/移动两组控件、ID/index/时刻及inArticle决定的链接，实际网站和部署保持；原脚本与失败attempt保留在online-harness-correction/和online-verification-attempts.json。第二次全部通过，未用修改网站去迎合错误检查。
