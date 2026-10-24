# EP.18《刚改的昵称，怎么又变回去了？》

对应[#70](https://github.com/linhongcun/video-studio/issues/70)。本工程重制同一条昵称记录的主库、从库和读取路径，按用户既有GitHub持续发布授权制作；最终站点接入与issue收尾由主任务统一执行。

- research.md：实际核验的六份MySQL官方正文、主张与边界；article.mdx为配套技术文章。
- script.md、pronunciation.md：14镜28句旁白与读音表；visual-direction.md、knoll-props.md记录逐步动画。
- storyboard.json和sha副本：实测句级时序与挂词；voice.wav、words.json、voice/picks.json及选定takes可重现当前音轨。
- video.mp4、三尺寸JPG/PNG、poster.jpg：最终媒体；source-sha256.json固定实际输入，render-result.json和mix-report.json记录编码/混音检查。
- qa-motion.md、qa-final.md：检查执行范围、证据与能力限制，不冒称逐字ASR或完整人工听辨。

在remotion目录使用npm ci（工作区依赖软链不入库）、npx tsc --noEmit、npm run covers、npm run stills、npm run render。机器环境Node20+、FFmpeg、/usr/bin/chromium、Noto Sans CJK SC；Python工作区为/workspace/.venvs/video-studio。批量全片渲染使用共享/tmp/video-studio-render.lock，避免多期同时占满资源。

配音复现顺序：仓库共享voice/prep.py、gen.py、build.py（均加--dir episodes-codex/db-replication），然后本期assemble.py，再共享selfcheck.py、place_v2.py --mode whole、label_onset_strict.py。已保留takes应直接复用，不重新请求非确定性TTS。全部首次术语在句首，起音由唯一共享Rule测量；字符字段只是整句包络，不作句内逐字挂词。

动态检查在remotion目录：node scripts/motion-qa.mjs /tmp/ep18-motion --shots=05,07,09,10,12 --flow=09-11。该模式关闭字幕和声音；正式输出默认保留字幕和配音。

配乐：Kevin MacLeod《Wallpaper》，CC BY 4.0，沿用共享混音脚本，目标−16 LUFS。
