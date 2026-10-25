# EP.01 HTTP请求：技术细节重制

2026-10-25用户观看旧版后认为内容太简单，要求增加TCP三次握手等机制。现有正文以17镜34句、5406帧（180.2秒）沿同一商品页说明三报文、序号与确认、第三次作用、TCP/TLS/HTTP职责、具体HTTP/1.1报文和页面渲染；连接复用及HTTP/3作为边界。

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


## 参考资料默认入口与本批存量接入（2026-10-25）

本期已接入统一的 `render_with_references.py` 默认入口。调研时同步维护 `references.json`，配套文章保留正式链接、固定实读版本和对应论点；先在本期 `remotion/` 运行 `npm run check:references`。Python附录依赖按 `../_shared/requirements-reference-appendix.txt` 固定版本安装，字体与FFmpeg按共享工具的真实环境要求准备。

所有生产输入停写后运行本期 `freeze.py`，以 `freeze.py --verify` 只读核对。清单保留原正文、声音、时序、封面及本期素材依赖，并收录参考资料、默认wrapper、追加器、Pillow版本锁、发布资料检查器和每项来源声明的实际核验JSON；文章、package与共享主题也属于冻结输入。渲染前后核对同一份清单，不把视频或生成回执当作编码前输入。

后续需要重新制作正文时，在 `remotion/` 运行 `npm run render`：默认wrapper先检查来源与冻结，随后调用 `render:body`，沿用本期既有的 `render:voice` → `render:mix`，将完整正文输出到 `out/body.mp4`，再自动追加参考资料得到 `../video.mp4`。`render:body`不调用默认`render`，避免递归。

本次存量补齐采用 [第2批记录](../../docs/reference-endcards/batch-2/README.md) 中的固定Git基线：原已发布MP4放到 `remotion/out/body.mp4`，只生成并追加资料卡，每页默认5秒、可暂停阅读，不执行正文重渲、重混音或重新请求配音。基线与原冻结/媒体身份分别保存于 `revisions/reference-endcards/baseline.json`、`body-source-sha256.json`、`body-render-result.json`；旧QA仍只证明原来执行过的检查范围。

原脚本、分镜、`words.json`、人声与字幕继续描述正文；最终总帧数、正文终点和资料页范围由实际 `reference-appendix.json` 及发布元数据声明。附录回执先由共享工具写入 `revisions/reference-endcards/`，交付副本位于本期根目录；`render-result.json.publicationMetadata`给出应同步到发布`meta.json`的`finalVideoFrames`与`referenceAppendix`。本批手动复用正文后也必须按实际结果接齐这些交付文件，不能用旧时长/旧哈希代替最终身份。

接齐后在 `remotion/` 运行 `npm run verify:references`：统一wrapper只读核对来源、冻结、真实最终媒体及交付回执，不重新渲染正文。旧正文编码检查器的帧数断言只用于对应正文副本，不直接用它判断已追加附录的最终`video.mp4`。实际查看所有资料页、精确首卡字幕边界以及桌面/手机原生播放器暂停和全屏效果，再同步发布副本；保留原URL、创建/首发时间、已有平台链接及未执行ASR/人工听辨的能力边界。本批制作和上线状态以批次证据为准，不预记已通过或已发布。
