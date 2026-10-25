# EP.01 HTTP请求：技术细节重制

2026-10-25用户观看旧版后认为内容太简单，要求增加TCP三次握手等机制。当前工程以17镜34句、5406帧（180.2秒）沿同一商品页说明三报文、序号与确认、第三次作用、TCP/TLS/HTTP职责、具体HTTP/1.1报文和页面渲染；连接复用及HTTP/3作为边界。

修前稿、真实技术检查与媒体身份由[修前记录](revisions/technical-depth-v2/startup.json)及Git基线追溯。旧检查通过不代表用户认可旧版深度，新版发布也不等于已获观看认可。

## 本轮生产

配音使用仓内共享voice/prep.py、gen.py、build.py；picks为32个depth与2个depthb，保留24个历史选段。读音和取舍在voice/substitutions.md。整轨与public实体音轨字节一致，句级真实时序与声学起音不冒充逐字ASR或人工听辨。具体报告见voice/depth-timing-report.json。

本期assemble.py将共享整轨的真实边界装配为words、storyboard与字幕，不重剪声音。Remotion按production.json的slug与cueFrames读取，三个报文字段和终态有独立检查。公开来源与版本核对见research.md，独立稿审见qa-editorial-depth.md。

依赖按当前remotion/package-lock.json独立npm ci安装，未复用已删除工程软链。运行环境需FFmpeg、Chromium、Noto Sans CJK SC以及Python numpy/scipy/soundfile；本次Python在/workspace/.venvs/video-studio。

## 冻结、预检与渲染

所有生产源停写、真实动态复核完成后，在仓根执行：

```sh
python3 episodes-codex/http-request/freeze.py
python3 episodes-codex/http-request/freeze.py --verify
python3 episodes-codex/http-request/preflight.py
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/http-request
```

在remotion目录执行npx tsc --noEmit、npm run covers、npm run render。正式渲染使用共享/tmp/video-studio-render.lock。render由本期package先编码H.264再调用共享混音；audit_encoded.py核对冻结输入、5406实际解码帧、格式和响度，并输出正式MP4采样。最终视觉与完整线上文件另验。

本轮无逐字ASR、全片人工听辨或初学者学习实验；所有检查按实际执行范围记录。站点仍使用episodes/http-request，历史平台URL保留，本轮只更新GitHub站点。发布与线上结果见release.md及docs/http-request-depth/，实际状态以最新证据为准。
