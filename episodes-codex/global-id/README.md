# EP.20《两个订单，怎么撞成同一个号了？》

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
