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

按既有GitHub持续授权完成检查后合并、Release、部署并核对完整线上媒体/字幕/六章；本次修订版本v0.57.1，实际结果见release.md。#205在核验后completed关闭，其他九题和外部平台不在本次范围。

## 第11批参考资料名单与当前入口

本批只在完整原片后追加`title-author`参考资料名单，每页最多4项、默认5秒；本片无Python或Java代码卡，原有收尾、旁白、字幕、场景和配图保持。基线`a1a9821845c83a61a57fbb3f0e10461ef4c55238`的Git发布原片已核对原render-result与总帧数，逐字节保存为`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`。本批直接使用该完整原片追加，不寻找缓存、不重制正文。

原157项历史输入全部现存并按原路径或before快照逐一验证，保留全部原key。当前清单只声明真实现存依赖及本轮资料/入口，不能用作原MP4已重渲的证明。旧freezer、清单和修前文稿/入口完整归档；数学检查、旧渲染编排和媒体QA保留历史身份，本批不重跑。当前freeze.py保留原实质输入约束，并只读核对分镜快照和placeholder；不调用共享写入型freezer、装配、TTS或数学程序。完整源码静态import、别名和公开音轨的实际结果见[入口报告](../../docs/reference-endcards/batch-11/production-entry-check.json)。

资料负责人停写且来源预检通过后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/horse-racing
python3 episodes-codex/horse-racing/freeze.py
python3 episodes-codex/horse-racing/freeze.py --verify
```

默认`npm run render`经共享bibliography wrapper核对来源和冻结后，执行`render:body`并追加参考资料。`render:body`保留原voice→mix命令、H.264/CRF20、concurrency=2及Chromium参数，仅把默认mix输出改至`out/body.mp4`；旧特别修订命令保留历史用途，交付需通过当前参考资料检查。`npm run render:references`从完整body单独追加名单；`npm run verify:references`用于后续完整交付复核。本批只执行来源和只读冻结/入口检查，不运行正文、混音、数学重验或重复全片解码。最终总帧数以新receipt、render-result及发布metadata为准；[本批记录](../../docs/reference-endcards/batch-11/README.md)不预记媒体和线上通过。
