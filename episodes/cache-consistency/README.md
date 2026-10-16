# EP.22 缓存与数据库一致性（cache-consistency）
- storyboard.json（sha a329e86e…）：8 章 13 段 22 镜头，6698 帧 @30fps（含 5 张章节卡 card-1～5 各 78 帧停顿，第 3–7 章各一张；开头钩子、第 2 章、结尾不放卡）；meta.finalVideoFrames = 6728
- 成片 = 分镜 6698 + ending-2 片尾停留 30 帧 = 6728 帧（约 3 分 44 秒）。**EP.22 起不再追加全局 60 帧「IT小村 · 原创」片尾卡**：片尾 = ending-1（讨论问题卡）+ ending-2（关注提醒卡 + 关注·点赞·收藏图标行），长度跟随结尾旁白，文字见 endcard.txt；改动只在本期 remotion/src/Main.tsx（TAIL_HOLD）和 Root.tsx，episodes/_shared 未改
- 停顿：holds_applied.json；build_voice.py 在下一句开口前 0.1 s 的句间静音里插章节卡静音，末尾补 30 帧，整轨 voice.wav = 6728 帧
- 配音：MiMo 冰糖（/workspace/share/ep22，整轨 narration.wav sha 0badc4af…，6309 帧；「看｜台上空了」看后 0.2 s 停顿，用自然停顿底噪填充）；voice.wav sha 4cd976b0…
- 术语标签 10 个，完整显示均 ≥69 帧（最短 删缓存）
- 制作：`cd remotion && npm ci && npm run render`；mix_bgm.py（Wallpaper，−16 LUFS）；成片 sha 506d7dd1…（r3）
- 检查：`node site/scripts/check-frames.mjs cache-consistency`
- 封面：Miyazaki 设计稿 cover/ep22-*.png → cover-*.jpg（同 EP.21；不取视频帧）
