# 爬楼梯：为什么只要记住前两个数？

当前制作工程为本目录，站点只读取episodes/climbing-stairs/。用户指出原片没有利用题目自带的楼梯场景；本轮将横排数字框换成台阶上的实际走法、最后一步来源和计数位置。当前实际制作/检查/发布状态见[楼梯场景记录](../../docs/climbing-stairs-scene/README.md)，本文件不将旧媒体QA当作新画面已通过。

原24句旁白、12镜/4章、4779帧（30fps，159.3秒）、真实句级时序和完整Python保留。末150帧（4629..4778）仍为5秒静态代码卡，提示暂停，无人声PCM与正文字幕。代码卡、执行源和文章代码字节相同，旧算法执行证据按相同程序保留，不冒充新跑过算法测试。

## 实际依赖与来源

Python环境/workspace/.venvs/video-studio包含numpy、scipy、soundfile、Pillow；Remotion/React依赖按本期锁文件，新锁图与保留的two-sum实体node_modules相同。依赖软链不指向已删除的Agent或旧工程。原媒体来源为固定Git bb9b4e97，before/和来源身份保存在revisions/stair-scene。历史MP4不重复保存到制作输入。

本轮最终声音直接复用已验证的原成片AAC，冻结输入为revisions/stair-scene/inputs/original-audio.m4a，来源提取、7469包时间戳/内容与解码PCM身份见audio-extraction.json。此修订不新合成声音、不改配乐或重算语速；script/words/SB仅刷新视觉说明和整脚本哈希封套，真实句窗及音轨保持。freeze.py会递归覆盖Staircase.tsx，并额外包含上述M4A。

## 检查与预演

```sh
/workspace/.venvs/video-studio/bin/python episodes-codex/_shared/check_sentence_episode.py episodes-codex/climbing-stairs
/workspace/.venvs/video-studio/bin/python episodes-codex/climbing-stairs/freeze.py --verify
```

仅在输入真正定稿后执行不带--verify的freeze.py。正式媒体完成后只读核对，不能重写清单追认旧媒体。原126项预检清单与初次真实预演保留；01/03/04飞行过程遮挡说明的实际失败帧及源保存在before-layout-fix，修后源清单与精确四处位置替换见layout-fixed-source-sha256.json、layout-fix.json。未改05–09连续片按源分支不变和真实时点证据复用，不称为修后重渲。

remotion/scripts/qa.mjs用实际句级时序，支持QA_FRACTIONS、QA_EXTRA_FRAMES、QA_SCALE、QA_MANIFEST与QA_CLIPS；静帧默认带字幕，连续片强制hideSubtitles=true并写入记录。第一轮qa-motion-scene.json；修后全12镜字幕静帧及01–04无字幕连续片为qa-motion-scene-fixed.json，后者用于正式编码同帧对照。报告以实际独立预检与成片结果为准，不声称全片人工听辨、逐字ASR或真实新手实验。

## 正式画面与声音

所有渲染共用/tmp/video-studio-render.lock，2CPU并发2；TMPDIR用/workspace/cs-scene-tmp等短路径。输入冻结、动态预检通过后，从remotion目录执行：

```sh
node_modules/.bin/remotion render src/index.ts Main out/voice-stair-scene.mp4 --codec=h264 --crf=20 --concurrency=2 --browser-executable=/usr/bin/chromium --bundle-cache=false
ffmpeg -nostdin -y -i out/voice-stair-scene.mp4 -i ../revisions/stair-scene/inputs/original-audio.m4a -map 0:v:0 -map 1:a:0 -c copy -movflags +faststart ../video.mp4
```

最终只采用新画面与原AAC，丢弃Remotion中间文件音轨。正式音量重新测量，记录mix-report.json与revisions/stair-scene/final-ebur128.txt；共享check_encoded_episode.py检查完整解码/帧数/音轨，extract_encoded_samples.py --samples qa-motion-scene-fixed.json比较实际正式MP4与修后字幕预演。原npm run render仍可重新合成全片声音，但其输出不应声称逐字节等于本次复用原AAC的发布文件。

三尺寸封面由npm run covers生成；这轮换成同题楼梯、人物和最后一/两阶弧线，安全区/标题位置原样。发布只复制已验MP4/JPG与必要站点数据，不复制WAV、PNG或制作工程。实际版本、部署、线上完整SHA见本轮发布记录。

本轮已随[v0.61.1](https://github.com/linhongcun/video-studio/releases/tag/v0.61.1)发布，PR #260、Release后单次手动部署40156242220及首次28响应线上核验通过。原制作issue #81保持历史completed，本轮未重复关闭；实际媒体、tag和部署身份统一见[发布记录](../../docs/climbing-stairs-scene/release.md)。交付证据提交晚于媒体tag，不变更成片或网站构建输入。

## 第9批参考资料名单与当前入口

本批只在完整原片后追加`title-author`参考资料名单，每页最多4项、默认5秒。原body包括已设计的150帧完整Python解法卡，参考资料从该卡结束之后开始；代码卡、旁白、字幕、分镜和执行/显示代码均不改写。制作目录的video.mp4初始缺失，本批直接使用Git发布原片；该完整MP4已与保留的render-result完整SHA及总帧数核对，保存为`revisions/reference-endcards/body.mp4`和同SHA的`remotion/out/body.mp4`，不查找旧ignored缓存或重制正文。

旧冻结清单及修前article/research/freezer/package已完整存档。本期当前`freeze.py`只读核对原实质输入约束、分镜快照与placeholder、代码卡范围和solution.py/json哈希；不调用旧共享写入型freezer、prepare_code_endcard、装配或TTS。历史记录和当前实际输入的核验范围在[生产入口报告](../../docs/reference-endcards/batch-9/production-entry-check.json)分列，不以新清单追认原MP4重现；旧QA、局部拼接与算法执行记录保留历史身份，本批不新跑算法测试。

资料负责人停写且来源预检通过后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/climbing-stairs
python3 episodes-codex/climbing-stairs/freeze.py
python3 episodes-codex/climbing-stairs/freeze.py --verify
```

默认`npm run render`经共享bibliography wrapper核对来源和冻结，再执行`render:body`及参考资料附录。`render:body`保留原voice→mix闭环、H.264/CRF20、concurrency=2及Chromium参数，只把mix输出改至`out/body.mp4`；该完整body包含原Python卡。`npm run render:references`供本批直接从不可变Git body追加资料，不覆盖代码卡；`npm run verify:references`是后续完整交付验证入口。本批仅做来源/冻结/入口及输入字节核对，不运行正文、混音或重复完整解码，最终总帧数以新receipt、render-result与发布metadata为准。实际进度见[第9批记录](../../docs/reference-endcards/batch-9/README.md)，不预记媒体或线上通过。

本期原126项历史输入均现存并逐项核对；当前清单保留全部原key，并增加本轮真实资料输入。旧局部拼接器仅保留历史用途；现行默认完整源码入口的静态import及public音轨核对不依赖这些历史缓存。
