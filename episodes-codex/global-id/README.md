# EP.20《分布式 ID：两个订单，怎么撞成同一个号了？》


## 当前方案定位补充（2026-10-25）

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
