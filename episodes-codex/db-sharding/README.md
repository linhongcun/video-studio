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


## 第6批资料名单：当前入口与原片保留

本批仅追加`title-author`名单：完整原题名与真实作者/机构，每页最多4条、默认5秒。根已将原Git发布整片保存为`revisions/reference-endcards/body.mp4`，`remotion/out/body.mp4`为同SHA副本；基线、旧30项记录、修前package/文稿及发布身份均归档，不回写旧证据。既有MySQL身份组件、SVG、许可和legacy包装器保留。

本期原工程没有独立freeze.py。新增薄入口先核对归档旧记录，旧package使用before快照映射，再登记当前名单和默认渲染实际输入；旧窄记录不被扩展为“原MP4可按新清单重现”的承诺。freeze不运行assemble/TTS、复制SB或改写words/placeholder。来源资料由独立作者整理本片既有真实实读记录，不在此入口补造新GET、技术事实或署名。

资料停写且`npm run check:references`通过后，从本期目录执行`python3 freeze.py`和`python3 freeze.py --verify`。默认`npm run render`经现行bibliography wrapper，原voice→mix及并发参数保持，只将正文混音输出改为out/body.mp4再追加名单；本批不执行正文构建或重混音，由根消费不可变原片追加并做实际全帧/PTS/AAC/PCM比较。

根级回执、实际总帧数和`render-result.json.publicationMetadata`接齐后可执行`npm run verify:references`；本批只做sourcegate、只读freeze和wrapper.verify_freeze，不重复完整媒体解码。原脚本、声音、字幕、场景、主体程序和既有文章/研究前缀保持。实际状态及范围见[第6批记录](../../docs/reference-endcards/batch-6/README.md)，不预记新卡或线上核验完成。
