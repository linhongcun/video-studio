# EP.20《分布式 ID：两个订单，怎么撞成同一个号了？》


## 当前顺序与取舍修订（2026-10-25）

用户观看上一轮补充后认为，开头先说“雪花只是一种”突兀，要求UUID→Redis自增→雪花逐项讲述，并补充每项实际优缺点。本轮16直接从随机UUIDv4本地生成进入，再说明非递增作为MySQL InnoDB主键的分散插入、缓存与页分裂代价；17演Redis共同计数、异步复制未到达的主从切换回退重号，再切换到事先可靠预留1001—1200号段、停号隔离旧主后放弃旧段从1201继续的条件方案。最后才过渡到原雪花详细讲解，去掉开头的三方案总览及提前点名雪花。

本轮新小段8句1227帧40.9秒，替换上一轮5句24.7秒；全片5646帧188.2秒，17镜38句8章。原15镜局部画面和30句人声PCM继续从不可变methods-before基线精确复用。上一轮实际成片和165项冻结输入已按固定Git `2ca6e1e0661bbb2b9683f7909de5c0949272ec04`核验并保存文稿/QA快照于revisions/tradeoffs-before，当前启动主干为`9834e2cd84b1081f8ab41ade369cf46b8b6ddf62`。

当前执行使用assembly-profiles.json选择tradeoffs：共享voice prep/gen/build的--dir为`episodes-codex/global-id/revisions/tradeoffs-insert`，随后运行`assemble-methods.py --profile tradeoffs`。预检通过后用`freeze.py --profile tradeoffs`冻结，`freeze.py --verify --profile tradeoffs`只读核对，再运行`render-methods.py --profile tradeoffs`局部渲染并重混。methods只支持历史时序装配；旧视觉/成片须从固定提交复现，当前renderer明确拒绝拿新视觉重渲旧profile。

本轮依据与实际检查见research.md、tradeoffs-reuse-proof.json及qa-tradeoffs-*报告。UUID只讨论随机v4，文章说明v7的时间布局；页分裂仅作页空间不足时的机制示例，不声称每条必分裂。跳号是有可靠号段记录与旧主停止发号前提的治理思路，非Redis默认功能或任意固定加N的唯一性保证。未做逐字ASR或人工逐字听辨，不声称其通过。

## 上一轮方案定位补充（2026-10-25，历史）

用户指出只有雪花算法会让观众误以为它就是分布式ID。当前在原06/07之间新增16-options、17-redis两镜5句：先点明多种实现，再用随机UUID本地生成与Redis共同计数器取号作简短示例，保留碰撞概率/随机源与故障回退边界，最后回到雪花主线。新增741帧24.7秒，全片5160帧172秒，17镜35句7章；标题、slug、创建/首发时间保持，按实质内容修改更新修改时间。

制作基线`11dd6fbb0109c6e18321e8bc2ecb5e65516e98f7`，原媒体与声音存于`revisions/methods-before/`。上一轮仅改文章命名，导致旧105项冻结清单中article一项与原编码输入不同；104项声音和视觉等来源仍一致，已在baseline.json如实记录。旧清单不回写。原30句PCM前后段精确复用，原15镜局部数据完全不变，全局时间只平移741帧；见methods-reuse-proof.json与qa-methods-technical.json。

当前复现入口：

```sh
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/prep.py --dir episodes-codex/global-id/revisions/methods-insert
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/gen.py --dir episodes-codex/global-id/revisions/methods-insert
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/build.py --dir episodes-codex/global-id/revisions/methods-insert
/workspace/.venvs/video-studio/bin/python episodes-codex/global-id/assemble-methods.py
```

已有选定takes会被复用。新增镜头预检通过后调用freeze.py，再以freeze.py --verify只读核对，运行render-methods.py：只渲染新增镜头，原编码画面由FFmpeg解码重编码拼接，使用完整人声及共享混音的连续配乐，不声称无损流拷贝。原成片全量render入口仍用于原理复现，当前交付按render-methods.py与实际splice报告追溯。新增术语起音、原声复用与最终媒体检查按本轮QA记录；未做逐字ASR或人工逐字听辨，不声称其通过。

以下为原15镜制作记录，保留历史参数，不作为当前帧数。

对应重制 issue [#72](https://github.com/linhongcun/video-studio/issues/72)。从两个独立订单表各自生成42开始，用时间、生成器的机器编号和同毫秒序号说明雪花算法；保留条件错误仍撞号的反例。片尾接EP.21《下单成功了，库存怎么没扣？》。

- research.md记录实际查阅的MySQL、Twitter原始代码、Apache当前文档与实现、MDN正文及适用边界。
- script.md、article.mdx、pronunciation.md为15镜、30句旁白和片外补充；visual-direction.md说明动画意图。
- video.mp4是1920×1080、30fps的成片；三尺寸PNG/JPG封面和poster.jpg为本期媒体。
- storyboard.<sha8>.json与storyboard.json逐字节相同；source-sha256.json冻结实际输入，render-result.json记录实际编码结果。
- qa-motion.md、qa-final.md分别记录动态预检与最终编码检查、执行者和能力限制。

工程入口在remotion目录。安装使用npm ci，检查使用npx tsc --noEmit；npm run stills、npm run covers、npm run render分别生成截图、封面和带配乐成片。环境需要FFmpeg、/usr/bin/chromium、Noto Sans CJK SC和Noto Sans Mono。工作区node_modules软链不入库。

配音复现使用仓内episodes/_shared/voice/prep.py、gen.py、build.py，参数--dir episodes-codex/global-id，再运行assemble.py、共享voice/selfcheck.py、place_v2.py --mode whole和label_onset_strict.py。本期保留首轮a的30条选择和takes；不必重新请求非确定性TTS。Python环境为/workspace/.venvs/video-studio。voice/substitutions.md说明裁切与检查范围。

动态预演命令：node scripts/motion-qa.mjs /tmp/ep20-final-motion --shots=01,03,05,07,08,09,10,11,12,13,14,15 --flow=08-10。该模式关闭字幕和声音，用于检查字段变化和对象接续。

实际长编号均在sample-data.ts中用BigInt运算并转字符串，不能先转Number。最终全片渲染使用共享锁：flock /tmp/video-studio-render.lock -c 'npm run render > /tmp/ep20-render.log 2>&1'。

配乐：Kevin MacLeod《Wallpaper》，CC BY 4.0，沿用共享混音，目标−16 LUFS。按用户的持续授权，由主任务统一接入站点、合并、发布并核验，完成后关闭对应issue；本目录制作代理不单独操作Git。


## 第6批资料名单与当前冻结入口

本批只为已验收的tradeoffs完整原片追加`title-author`名单，不重做UUID/Redis/雪花正文、配音或拼接。根已将Git发布原片保存为`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`；基线、原200项清单和修前文稿/freezer/package分别存档。引用完整原题名与真实作者/机构，每页最多4项、默认5秒，技术主张沿用本片2026-10-24/25实际实读记录；2026-10-26补查的RFC题名/署名和Sentinel完整题名另记范围，不冒充技术正文重读。

现有freeze.py的profile、完整时序SHA、WAV样本数、逐镜/字幕/配音位置校验全部保留。当前只验证已装配的storyboard.<sha>.json与placeholder字节相同，不再重写它们；不运行assemble-methods、TTS、render-methods或正文渲染。旧200项按article/research/freezer/package四份before快照映射及其他原路径独立核对，原methods/tradeoffs历史输入不回滚。

资料作者停写、`npm run check:references`通过后，运行`freeze.py --profile tradeoffs`及`freeze.py --verify --profile tradeoffs`；新清单保留原200个key，并登记当前名单、实际wrapper/三个渲染器、发布检查器和引用证据，包括3份逐字节保存的题名/署名原文件。新清单声明当前入口/附录输入，不能据此声称原MP4已按新引用重现。

默认render现经bibliography wrapper；render:body严格保留本期原voice→mix闭环及并发参数，mix输出到out/body.mp4后追加名单。根本批直接消费不可变body执行新卡和完整帧/PTS/AAC/PCM保真检查，接齐当前交付回执/总帧数后再发布；不重复fullwrapper解码。`npm run verify:references`是后续完整交付验证入口。实际进度见[第6批记录](../../docs/reference-endcards/batch-6/README.md)，不预记新版名单或线上验证通过。
