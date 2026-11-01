# MQ08 / MQ15 公共入口

本文件说明新脚本的调用契约，不是阶段通过回执。当前只做源码/语法及离线语义检查，未执行TTS、冻结、编码、图像导出、安装、构建、浏览器或线上GET。制作与验收按root的实际信号推进。

两期D分别是`episodes/message-queue/kafka-retry-dead-letter/production`与`episodes/message-queue/kafka-replica-acks/production`；P由`episodes/_shared/episode_paths.py`的`publication_directory(slug)`定位。网页URL继续为`/video-studio/episodes/<slug>/`，系列课数从当前有效P元数据计算，不预填九课通过。文中A指本目录。

## 作者接入

两D具名prepare/assemble/freeze/render等薄包装已建立；作者仍独占src/package/plan/script/article/model，root独占voice参数与授权闸门、字体、封面、最终freeze-inputs声明。prepare只转发共享来源预检与voice/prep，assemble只调用canonical句级装配后补本片palette元数据；根的voice-initial会先核确切编辑批准SHA，再调用这些入口。

建议作者自行将以下脚本写入本期`remotion/package.json`，默认Main字幕仍开启：

```json
{
  "check:references": "python3 ../pipeline-tools.py references",
  "render": "python3 ../render.py ..",
  "render:voice": "remotion render src/index.ts Main out/voice.mp4 --codec=h264 --crf=20 --concurrency=2 --browser-executable=/usr/bin/chromium --bundle-cache=false",
  "render:normalize": "python3 ../normalize-color.py",
  "render:mix": "python3 ../pipeline-tools.py mix",
  "render:body": "npm run render:voice && npm run render:normalize && npm run render:mix",
  "verify:references": "python3 ../render.py .. --verify"
}
```

Main/theme在src层引入共享时相对路径为`../../../../../_shared/…`；Python包装动态寻找AGENTS仓根。参考附录保持真实limited BT.709、原题/机构列表、每页最多4项/5秒。新增回执按本期config.slug记录身份，不沿用MQ01/MQ07回执文字。fresh npm ci与锁文件由作者负责。

root最终冻结前须定好实际board/voice、文章、整数frame/seconds=frame/30及seekTo；freeze.py还要求root补齐freeze-inputs.json。新冻结覆盖实际来源、examples、模型、所选voice与helpers、共享adapter/style、Python/JS resolver和本批字体账本。旧source-sha与旧receipt不复制；已有清单禁止静默覆盖。render-final.sh仅在root放行后使用共同flock执行正式默认入口。

## 独立图像与成片检查

动态PNG/DOM入口：

```sh
node A/qa/render-frames.mjs --dir=D --spec=SPEC.json --name=unique-attempt
```

实际调用时把A、D、SPEC替换成真实路径；spec格式为`{samples:[{frame:整数,expectedState:"可选真实状态",label:"审查点"}]}`。它fresh bundle，inputProps与resolved composition props同时关字幕，保留每张PNG、原始DOM/console/告警；`machinePass`不代替实图复核，raw碰撞或SVG度量告警须逐点核实，不能删掉原报告追认为通过。

最终MP4产生后，root按冻结图位运行`python3 A/export-figures.py D`，精确整数n且真实709→601 JPEG转换；旧输出/回执拒绝覆盖，失败stderr和已生成JPEG保留。新receipt默认visualReviewed=false，必须实际逐张审图才由执行者补真实范围。

非作者最终检查入口为`python3 A/qa/final-independent.py D --spec SPEC.json --out-dir qa-final-independent`。它核MP4/附录/冻结身份、H.264/AAC48k与limited709，全视频/AAC解码同时按整数n抽取；全部原始抽图保留在encoded-evidence/raw，逐镜/四图位/每页资料首中末有联系图。新执行目录必须为空，默认visualReviewed=false；需实际看图后另记结论，不冒充整片语义听辨、ASR或真机检查。

## 草稿预览与正式首发

1. 正式媒体与全部JPEG实际检查通过后，root运行`python3 A/install.py`，把同一字节安装至新P，仍保留draft=true且没有publishedAt/firstRelease；D中的WAV、PNG原稿和生产输入不搬走。
2. root以`SHOW_DRAFTS=1 npm --prefix site run build`构建草稿预览，再对每期运行`python3 A/qa-site.py --preview-drafts --production D --out A/site-local/<slug>`。helper使用独立临时本地端口，保留原生播放器、精确实际PTS、引用、图位和截图；不操作他人的已有server。需实际审看全部所需图像，按真实执行范围补visualReviewed，不能仅把自动pass改写成视觉通过。
3. root确定实际release版本后运行`python3 A/install.py --publish --release vX.Y.Z`；默认逐期读取A/site-local/<slug>/report.json，可用--local-qa-root指定实际根。整批资产、身份、draftPreview/pass/visualReviewed、视频SHA及非空动作/PTS先全部校验，才写实际工作流开始时的publishedAt/firstRelease。这里不声称多文件I/O具备事务性，也不把该时间冒充部署完成时刻。
4. 正式构建、Git/PR/tag/Release/Release后部署由root执行。目录新增及索引更新也归root；不能运行上批旧A脚本或scripts中的EP01–14专用接入入口。
5. 实际部署成功后，root运行`python3 A/online-verify.py --release vX.Y.Z`；已有输出拒绝覆盖，重试须明确新--out。普通canonical GET完整读取至EOF并核全SHA，无Range、cachebust、回填、TLS忽略或隐式重试，另核原文/章节/图位/入口/RSS/实际Release。GET数量由本批实际图数得出，不预写通过。
6. 每期另运行`python3 A/qa-site.py --base https://linhongcun.github.io/video-studio --production D --out A/site-online/<slug>`，使用原生Chromium HTTPS且不带draftpreview。浏览器自身正常媒体Range与普通完整GET是不同证据；verifiedHttpResponses空列表不冒充完整下载。实际图审与模拟视口/原生控件等限制均如实记录，再由root关闭issue并归档。

21项离线回归见`qa/helper-offline-regression.json`，只使用合成HTML及内存中的草稿校验对象，不是本片媒体、浏览器或线上验收。所有真实QA证据保留；bundle/node_modules/out仅作为可重建缓存忽略，全局*.mp4仍需root另核应留实际短片并显式保留。
