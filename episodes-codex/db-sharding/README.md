# EP.19《订单太多，一个数据库装不下怎么办？》

对应重制 [issue #71](https://github.com/linhongcun/video-studio/issues/71)。主线：订单写入集中 → 按用户把订单分到多个逻辑分片 → 分片键决定路由。成片14镜、28句、3760帧，约125.3秒。GitHub发布和issue关闭由本批集成者在上线核验后完成。

- [research.md](research.md)：实际阅读的Microsoft与Vitess官方正文、关键主张、日期与边界。
- [script.md](script.md)、[article.mdx](article.mdx)、[pronunciation.md](pronunciation.md)：旁白、文章与读音记录。
- [visual-direction.md](visual-direction.md)、[knoll-props.md](knoll-props.md)：逐镜动作和制作说明。
- video.mp4与三种尺寸JPG/PNG封面为交付媒体；source-sha256.json冻结实际渲染输入，render-result.json记录媒体实测。
- qa-motion.md与qa-final.md区分动态预演、最终编码核验及检查能力边界。

复现：在remotion目录安装锁文件依赖，执行npx tsc --noEmit、npm run covers、npm run stills。全片使用共享锁：`flock /tmp/video-studio-render.lock -c 'npm run render > /tmp/ep19-render.log 2>&1'`。需要FFmpeg、/usr/bin/chromium和Noto Sans CJK SC；工作区node_modules软链不入库。

配音整轨复用仓内episodes/_shared/voice/prep.py、gen.py、build.py（参数--dir episodes-codex/db-sharding），随后运行assemble.py、共享selfcheck.py、place_v2.py --mode whole和label_onset_strict.py。复现应保留选定takes与picks，避免重新请求非确定性的TTS；本期threads为2，Python环境/workspace/.venvs/video-studio。

动态预演：`node scripts/motion-qa.mjs /tmp/ep19-motion --shots=01,03,05,07,08,09,10,11,12,13,14 --flow=08-10`。该模式隐藏字幕与声音，用于观察路由与对象衔接，不能代替配音听辨。

配乐：Kevin MacLeod《Wallpaper》，CC BY 4.0，沿用仓库共享混音，目标−16 LUFS。数据和分配规则均为教学设计，没有吞吐测试承诺。
