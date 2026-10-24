# LC.704 网站接入与实际验证

- 结果：通过。当前站点版本 `0.56.0`，本片实际首发版本 `v0.56.0`，公开标签LC.704，内部期号24。
- 本次基于含P01的新主干 `5a41a16ebaadb8339e4bc592edf325a407e74295` 重新构建一次通过：91个HTML文件、31个搜索索引页。`check-learning-path.mjs --complete --built` 本次执行一次通过，保留五个学习方向、既有课程与历史Release身份。
- 1440浅色和390深色均实际打开本片页；标题、LC.704、页脚v0.56.0、2:38时长、Remotion源码入口、同源完整Python图文、上一课链接、原生controls正确，无页面脚本错误或横向溢出。实际查看了本次生成的两张页面截图。
- 四章实际起点为0、21、78.6666666667、127.5666666667秒；两个尺寸均实际点击章节seek并核对当前位置。
- 28句VTT逐句匹配冻结分镜，HTTP与构建字节一致；正文开启CC后有activeCue，5秒代码卡内activeCues为0；卡内约1秒静音播放与暂停通过。
- 成片仍为4748帧，画面时长158.266667秒，浏览器读取158.272秒；本次没有重做、重编码或更改媒体。源、构建与HTTP完整视频SHA一致：`9faef1baf76695937c252b0e56cebe7a06c12f252451d30aa1e721d11ee660ae`。海报完整SHA也一致：`f4a4daecaf847bce60021b34d7768b808357166a01b4187d4b1da9686e793b31`。
- LeetCode系列仍为LC.11→LC.3→LC.704三期；首页入口、资料库LeetCode筛选三条及学习顺序、RSS LC.704条目通过；并行P01页面实际HTTP200且题名正确，保留其首发v0.55.0身份。
- 本次结束后只读核对137项冻结制作输入，全部保持原哈希，没有修改分镜、文章、配音或动画输入。

旧站点QA报告以v0.55.0作为本片拟首发版本。当时另一台机器的P01已占用该标签，实际tag树未包含本片，因此本轮更正站点和本片首发为v0.56.0，并对新版本和新主干身份重新检查。旧报告及旧pager断言修正记录保存在[Git提交5a41a16的qa-site.md](https://github.com/linhongcun/video-studio/blob/5a41a16ebaadb8339e4bc592edf325a407e74295/episodes-codex/binary-search/qa-site.md)与[qa-site.json](https://github.com/linhongcun/video-studio/blob/5a41a16ebaadb8339e4bc592edf325a407e74295/episodes-codex/binary-search/qa-site.json)，本报告覆盖当前顶层文件，不改写历史检查结论。本次默认运行QA脚本，一次新构建后全部通过，没有复用旧构建。

实际截图与哈希见 [qa-site.json](qa-site.json)，执行脚本为 [qa-site.cjs](qa-site.cjs)。本轮只复核受影响的站点交付，不表示全片人工听辨、ASR或重新测量算法与学习效果；生产Release、Pages及线上完整媒体核验由发布流程另行记录。
