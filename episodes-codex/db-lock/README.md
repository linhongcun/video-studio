# EP.17《两个人抢最后一件货，听谁的？》

2026-10-24 用户要求选择并开始制作下一期，选定[#69](https://github.com/linhongcun/video-studio/issues/69)，接上EP.16片尾。用户观看后认可并批准合并、GitHub站点发布；v0.45.3使用本目录的观看版原样副本，见[发布记录](release.md)。

- [research.md](research.md)：实际核验的七份MySQL官方正文、主张及边界。
- [script.md](script.md)、[article.mdx](article.mdx)、[pronunciation.md](pronunciation.md)：14镜脚本、28句旁白及片外补充。
- [visual-direction.md](visual-direction.md)：逐镜动态设计；[knoll-props.md](knoll-props.md)：制作说明。
- video.mp4与三种封面：当前观看文件；source-sha256.json为冻结输入，render-result.json记录实际编码核验。
- qa-motion.md与qa-final.md分别记录动态预检及最终编码检查范围，不用机器检查冒充独立人工听辨。

在remotion目录执行npm ci、npx tsc --noEmit、npm run stills、npm run covers、npm run render。系统需要FFmpeg、/usr/bin/chromium和Noto Sans CJK SC。工作区node_modules软链不入库；独立安装使用锁文件。

整轨复现依次运行仓内episodes/_shared/voice/prep.py、gen.py、build.py（加--dir episodes-codex/db-lock），再运行本期assemble.py、共享selfcheck.py、place_v2.py --mode whole及label_onset_strict.py。保留已有选定takes，避免重新请求非确定性TTS。配音选段和能力边界见voice/substitutions.md；Python环境为/workspace/.venvs/video-studio。

动态小样：node scripts/motion-qa.mjs /tmp/ep17-motion --shots=03,05,08,09,10,11,12 --flow=08-12。此模式关闭字幕和声音，只用于观察动作。

配乐：Kevin MacLeod《Wallpaper》，CC BY 4.0，沿用仓库共享混音，目标−16 LUFS。


## 第5批资料名单：当前入口与原片复用

本批仅在既有Git发布MP4后追加资料名单，原片完整字节已保存在`revisions/reference-endcards/body.mp4`，同SHA副本位于`remotion/out/body.mp4`；基线、旧输入清单、文稿、package及发布身份分别归档在同目录。原旁白、字幕、分镜、占位快照、程序、动画与批准版主体保持，不运行prepare、assemble、TTS、正文重渲或重混音。

本期历史工程没有独立`freeze.py`，旧`source-sha256.json`只记录当时列出的有限输入；这些旧key全部保留，不能把新增依赖说成旧片已按新清单重渲。新增薄`freeze.py`先验证已归档旧记录，旧package在修前快照处核对，再登记当前真实源码、选定配音、默认入口和资料生成输入；它不复制或重写SB、words及placeholder，也不承诺源码可逐字节重现已验收MP4。事务片后补MySQL身份组件、素材、许可及旧包装器继续保留。

`references.json`采用现行`title-author`样式，显示完整原题名及作者或机构，每页最多4项、默认5秒。复用本期已有真实实读记录和日期，不把整理资料写成新的GET；不新增技术事实或编造作者姓名。当前来源与实际状态见 [第5批记录](../../docs/reference-endcards/batch-5/README.md)。

全部输入停写、`npm run check:references`通过后，在本期运行`python3 freeze.py`，以`python3 freeze.py --verify`只读核对。默认`npm run render`经bibliography wrapper，保留原`render:voice`→`render:mix`闭环和并发参数，将主体输出到`out/body.mp4`再追加资料；这是后续完整制作入口，本批不执行。根代理直接消费已验收body生成尾卡，并以实际全帧/PTS/AAC/PCM比较验证保留范围。

当前冻结除旧key外还收录新旧三个资料生成器、wrapper、发布检查器、Pillow版本锁、主题及实际引用证据；历史窄清单与当前扩展输入分开记录。最终回执和`render-result.json.publicationMetadata`按新输出接齐后可运行`npm run verify:references`。旧`check-final.py`仅用于其原正文帧数，不能对新附录成片直接套用，也不为本批重复完整解码。

正式接入前实际查看名单、首卡字幕边界及原生暂停/全屏；创建、首发时间和已有平台链接保留。本轮只更新GitHub站点，旧用户观看认可适用于当时主体，不预记新资料卡已获认可。
