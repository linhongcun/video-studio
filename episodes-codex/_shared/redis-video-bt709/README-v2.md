# Redis limited-range BT.709 派生

原`redis-style`冻结、预检、正文、资料与成片全部保持。此次只修实际Chromium播放时的色彩解释：将原4557帧正文由full-range BT.601转换为limited-range BT.709，完整AAC流拷贝；再用原资料图生成器和相同题名/机构，按limited BT.709编码150帧资料并追加。新产物独立位于`revisions/redis-style-bt709-v2/`。

```bash
python3 episodes-codex/_shared/redis-video-bt709/render-v2.py
python3 episodes-codex/_shared/redis-video-bt709/render-v2.py --freeze
python3 episodes-codex/_shared/redis-video-bt709/render-v2.py --render
python3 episodes-codex/_shared/redis-video-bt709/render-v2.py --verify
```

先完成来源/原视觉预检与独立色彩试验，再冻结并渲染。新清单绑定原61份输入、实际6字体、原冻结与完整输入视频/回执、本工具和实际ffmpeg/Python版本；旧清单不改写追认。正文转换为有损图像，不能宣称与转换前逐像素相等；全4557帧PTS/duration及完整AAC包、解码PCM保持。原append核心检查新正文在最终片中的全部解码帧和PTS、4707帧连续性及完整声音保真。实际浏览器取色和可读性仍需独立验收。

第一份BT.709转换在4557帧正文后被严格检查拦截：矩阵与范围正确，但实际输出缺primaries/trc。其工具、78项冻结、失败正文和日志保留；v2在scale转换后加入setparams，明确每帧范围、矩阵、primaries/trc，资料图编码同样设置。两帧正文/资料小样的实际ffprobe均显示全部5项颜色参数后才允许本次新冻结。新清单也绑定失败的第一份清单、正文及其工具身份，不覆盖旧证据。
