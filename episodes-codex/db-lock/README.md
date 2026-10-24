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
