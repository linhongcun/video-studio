# EP.04《网站怎么记住你已经登录？》Codex 重制

2026-10-24 用户明确要求将 EP01–14 上一轮 Cursor 制作内容，按当日 Codex 规范与经验全部重制。本目录是本轮独立制作工程；旧站点媒体在完成成片检查前保留。

- research.md 记录实际阅读的公开权威正文、逐镜主张与适用边界。
- script.md、article.mdx、pronunciation.md 为本轮新稿；visual-direction.md 和 knoll-props.md 记录逐镜因果动作与制作要求。
- voice/ 保留共享脚本生成的选定takes、送模文本、选择、参数、拼接和检查报告；冻结音轨 3344帧，111.467秒。
- words.json 为真实句级边界和共享声学起音；不是逐字ASR。source-sha256.json 冻结92项实际输入。
- qa-motion.md 记录多阶段与独立图像复核；qa-final.md、render-result.json 记录实际编码检查完成后的结果。

## 复现

Python 环境：/workspace/.venvs/video-studio。使用仓内 episodes/_shared/voice/prep.py、gen.py、build.py；保留选定takes可复现整轨，不必再次请求不确定TTS。随后运行本期 assemble.py，再运行共享 selfcheck.py、place_v2.py --mode whole、label_onset_strict.py 和本期 preflight.py。

在 remotion/ 执行 npm ci、node_modules/.bin/tsc --noEmit、npm run stills、npm run covers、npm run render。使用 FFmpeg、/usr/bin/chromium 与 Noto Sans CJK SC。工作区 node_modules 软链不入库，独立安装按 package-lock.json。封面 PNG 转 JPG 不改变布局。

正式bundle前运行 python ../freeze.py；冻结后修改输入必须重新冻结并重新编码。python ../freeze.py --verify 可只读校验；check-render.py 对真实MP4执行完整解码、帧数、格式、响度和SHA检查。多组制作时使用 flock /tmp/video-studio-render.lock 串行正式渲染与较大动态小样。

配乐沿用共享 Kevin MacLeod《Wallpaper》、CC BY 4.0；成片目标−16LUFS/真峰值≤−2dBTP。ASR模型在环境中缺失且官方端点被proxy拒绝，本期未执行逐字识别或独立人工全片听辨，能力边界在QA中实录。

发布由root统一接入 episodes/cookie-session/、升级站点修订版本、合并PR、Release、部署并核对线上完整SHA。本目录完成制作不等同于平台已重发；当前只上GitHub站点。
