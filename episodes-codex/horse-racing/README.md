# P01 · 25匹马赛跑

当前按用户最新反馈采用简短收尾：视频讲题意、逐次排除和七场安排，16镜32句，在5+1+1=7结束；最少性证明只留文章，视频不展示、不提及，也不引导观众去补证明。

制作目录为本目录，站点读取episodes/horse-racing/。首发v0.55.0；v0.56.4约4分59秒的证明版已被用户否定其复杂与篇幅，技术记录留作历史，不能当作观看认可。当前修订见[short-ending](revisions/short-ending/README.md)。

## 复用与制作

原前5581显示帧与32句源人声复用，补37帧静止结果和小品牌，共5618帧、187.2667秒（约3:07）。最后一句音频结束5557.596875帧，尾后静音约2.0134秒；不调用新TTS，不加速或重新归一化人声。shorten_voice.py只做PCM裁切和时间记录，仍由共享assemble/place/check生成与核对分镜和字幕。原前15镜时序、所有32句PCM严格保留，详见voice/short-ending-preservation.json。

本期freeze.py复用共享冻结器并纳入本轮裁切、baseline和实际渲染编排输入：

```sh
python3 episodes-codex/horse-racing/freeze.py
python3 episodes-codex/horse-racing/freeze.py --verify
```

新末卡与实际快速剪短命令由本期remotion/package.json提供，具体执行结果、原媒体SHA、帧数、编码/音量、实际末态与网页检查见修订报告。封面与主体已验收部分复用，不为小修整片Remotion重渲或重跑数学用例。

## 来源与边界

research-math.md、verify_math.py与article.mdx保存数学来源和完整严证，原程序核验不替代证明，也不要求视频展开全部推导。原版与证明版的检查可从原Git标签及revisions追溯。

未执行逐字ASR、全片人工听辨或初学者实验；句首声学与输入核对按实际能力记录。用户认可原主体、否定证明版篇幅，新剪短版不预记用户已经观看认可。

## 发布

按既有GitHub持续授权完成检查后合并、Release、部署并核对完整线上媒体/字幕/六章；本次修订版本v0.56.5，实际结果见release.md。#205在核验后completed关闭，其他九题和外部平台不在本次范围。
