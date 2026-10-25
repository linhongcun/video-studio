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
