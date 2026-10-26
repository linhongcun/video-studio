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


## 第6批资料名单：当前入口与原片保留

本批仅追加`title-author`名单：完整原题名与真实作者/机构，每页最多4条、默认5秒。根已将原Git发布整片保存为`revisions/reference-endcards/body.mp4`，`remotion/out/body.mp4`为同SHA副本；基线、旧30项记录、修前package/文稿及发布身份均归档，不回写旧证据。既有MySQL身份组件、SVG、许可和legacy包装器保留。

本期原工程没有独立freeze.py。新增薄入口先核对归档旧记录，旧package使用before快照映射，再登记当前名单和默认渲染实际输入；旧窄记录不被扩展为“原MP4可按新清单重现”的承诺。freeze不运行assemble/TTS、复制SB或改写words/placeholder。来源资料由独立作者整理本片既有真实实读记录，不在此入口补造新GET、技术事实或署名。

资料停写且`npm run check:references`通过后，从本期目录执行`python3 freeze.py`和`python3 freeze.py --verify`。默认`npm run render`经现行bibliography wrapper，原voice→mix及并发参数保持，只将正文混音输出改为out/body.mp4再追加名单；本批不执行正文构建或重混音，由根消费不可变原片追加并做实际全帧/PTS/AAC/PCM比较。

根级回执、实际总帧数和`render-result.json.publicationMetadata`接齐后可执行`npm run verify:references`；本批只做sourcegate、只读freeze和wrapper.verify_freeze，不重复完整媒体解码。原脚本、声音、字幕、场景、主体程序和既有文章/研究前缀保持。实际状态及范围见[第6批记录](../../docs/reference-endcards/batch-6/README.md)，不预记新卡或线上核验完成。
