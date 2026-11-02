# MQ05修订入口

本次只处理EP45的`consumer-replay-v2`。11个具名包装从自身位置找到仓库根，调用现行`episodes/_shared`；配音装配、起音、混音、冻结和附录算法仍使用共享实现。未复制旧takes、冻结清单或通过回执。

```sh
A=docs/archive/2026-11/mq05-consumer-replay
D=episodes/message-queue/kafka-consumer-idempotency/production/revisions/consumer-replay-v2
```

作者独占Remotion package/config/src，root控制声音、正式冻结/编码、安装/构建和远程发布。本文是操作契约，不表示这些阶段已经执行。

## 工程接入

`prepare.py`只转调共享voice/prep；`assemble.py`只转调共享句级装配并补当前Kafka配色等元数据。脚本镜头标题必须是独占整行的`### 01 english-slug`，中文说明另行；每镜保留一条`旁白：`行，同镜多句放在该行。不能只满足prep的前缀解析却违反assemble的整行解析。

Remotion建议脚本：

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

正式Main默认烧录字幕。预声音入口另设composition，不能把placeholder当作真实board。独立无字幕采样同时向selectComposition和renderStill传入隐藏字幕props，并检查resolved props。`render-final.sh`使用现行渲染锁；它不是冻结放行授权。

`freeze-inputs.json`由root最终填写，缺失即拒绝冻结。声明实际用到的新A生产脚本、字体账本/校验器、运行证据及额外共享依赖。新包装自动纳入本地helpers、Python/JS路径resolver、实际sources/examples/model/文章来源、共享渲染/参考资料实现和root复制的旧封面。共享freeze另纳入真实声音、锁文件、起音和混音依赖。不能只冻本地wrapper而漏掉实际导入的共享文件。

四幅图位先按真实声音定为整数`frame`、`seconds=frame/30`。图片路径必须是`article/consumer-replay-*.jpg`；文章使用`/video-studio/episodes/kafka-consumer-idempotency/article/consumer-replay-*.jpg`，保留旧发布JPEG。

## 成片与本地修订预览

root正式编码后使用新A入口，旧A不执行：

```sh
python "$A/qa/final-independent.py" "$D"
python "$A/export-figures.py" "$D"
```

前者一次完整视频与AAC解码并精确整数n抽图，默认逐镜/图位/资料页首中末，raw全部保留。需要关键状态前后邻帧时，独立QA先准备真实点位JSON再传`--spec`。后者只从最终MP4按冻结整数n导出真实709→601 JPEG。两份初始报告均不声称视觉通过；实际审图后记录具名范围。

独立final review须包含真实`pass: true`、`visualReviewed: true`、`videoSHA256`和`frozenManifestSHA256`。JPEG出口回执必须实际四图审过。全部通过后由root执行：

```sh
python "$A/install.py" --stage --final-review "$D/qa-final-independent/review.json"
```

`--stage`先完整核验，后将原P全文件以copy2备份到仓外`/workspace/.video-studio-preview-backups/mq05-consumer-replay-<baseline12>`（可显式`--backup-dir`），再装入新媒体/文稿和四幅新图。它保留EP、slug、原题、创建/首发时间、首发v0.97.0、平台信息、旧updatedAt、五份封面与全部旧JPEG。只有本地P的媒体和sourcePath变为新修订；未执行Git或网络发布。失败保留逐项回执，不宣称多文件I/O原子提交。

root随后正常构建站点，再运行：

```sh
python "$A/qa-site.py" --revision-preview --production "$D" --out "$A/site-local"
```

本地模式使用独立临时端口服务root已有dist；不启动构建、不干预别人的server。实际测试当前全部MQ课、章节/图回看、原文、播放暂停、严格RVFC-PTS、正文/资料边界和原生Fullscreen。输出必须新且空；初始`report.json`字节自动另存`report.machine-only.json`。完整实际图审闭合后才注释visualReviewed，保留原生加载弧/暂停控件等真实状态和模拟手机限制。

发布前由root执行：

```sh
python "$A/install.py" --publish --release vX.Y.Z --local-qa "$A/site-local/report.json"
```

该步要求实际本地revisionPreview/pass/visualReviewed、媒体与全部暂存资产不变，release匹配当前site版本。它只把`updatedAt`改为实际发布工作流开始时间；firstRelease仍为v0.97.0，publishedAt和createdAt原样。root再重建正式站点、提交/Release/部署。发布前若明确放弃本地预览，可在没有后续资产改动时`install.py --restore`恢复原P完整字节与mtime；不会自动覆盖意外新改动。

## 部署后的检查

只在root确认目标Release后Pages成功后执行：

```sh
python "$A/online-verify.py" --release vX.Y.Z --out "$A/online-verification.json"
python "$A/qa-site.py" --base https://linhongcun.github.io/video-studio --production "$D" --out "$A/site-online"
```

普通GET完整读到EOF，核完整媒体/海报/VTT/四图SHA、当前章节/原文/入口/RSS历史首发时间及真实Release更新日志。原生浏览器HTTPS另外核播放器操作与实际解码；它的正常媒体Range不冒充完整GET，不忽略TLS、不回填HTTP、不cachebust。只对字节完全一致且有具名实际审图的代表图限定复用，其余新图实际打开。动作/PTS/页数按真实结果记录。

`secret-review.py`只使用未改的canonical规则及前批SHA固定的具体公开源码/协议名证据；输出必须是新A新文件。新运行若有额外命中，需具体定位和窄查，不泛化allowlist。当前只准备入口，不在sources仍写入时运行最终扫描。
