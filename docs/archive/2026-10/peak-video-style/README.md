# 高并发、高可用、高性能正文延续封面

2026-10-29。范围为EP.11限流、EP.12幂等、EP.13熔断、EP.14降级，让正文和资料页延续现行深青蓝、亮青、暖黄封面。当前完成独立来源/源码审查、126逐镜取样、42镜中段预演审读与四条正式媒体生成。完整原AAC包/PTS/DTS/duration和解码PCM、原片全部presentationPTS/duration、新正文附加资料后的全部解码画面与时序均通过；最终桌面/手机八组页面检查通过；发布身份与部署结果通过Release回执另据实记录。

从clean最新`eea5d8fab1037cb9630a14647cbada564082a74b`/v0.91.0建立制作分支。保留最新学习内容目录、当前peak归类、真实EP、完整原题、URL、创建/首发身份与外平台链接。既有60封面相关资产与266历史source-sha256清单按完整SHA保护；四个未冻结的根README仅补当前入口。原模型、分镜、字幕、资料原题/署名、来源核验日期与文章发布MDX字节保持。

新入口为各期`remotion/src/peak-style/index.ts`，共享[制作入口](../../../../episodes-codex/_shared/peak-video/README.md)与不可变style-v1，新媒体独立放`revisions/peak-style/`。正文3271/2998/2926/3134帧，片尾仍各150帧，完整片3421/3148/3076/3284帧。新冻结47/51/48/50仓内输入、每期6字体文件/8绑定。原完整AAC复用，不重新配音或混音；默认流程真实转换full-rangeBT601→limitedBT709像素，并以setparams明确逐帧颜色，正文与资料同编码。

独立历史保护审计覆盖871原路径：498已落盘文件按Gitblob和全文SHA核对，373稀疏缺省文件保留Git身份和缺省状态。原四份制作冻结400个声明中，304现存文件SHA相符，96未落盘音频等不冒称实核；四个根README为明确且未冻结的文档例外。详见`independent/source-audit.json`及其配套清单。

原四片完整helpers/Scene和Main尾部逐字节相同，继续调用原shot-data；熔断继续调用原导航状态与运动窗口，只在新导航渲染器适配配色。系列头标不提前添加单集术语，不改变原术语引入时刻；导航HUD位置保持，头标在其上方。配色以亮青表示活动/通过，暖黄表示判断/强调，珊瑚表示拒绝/失败，具体条件与数值不变。

初次预览发现系列标题bbox上边19px，制作将baseline58改60。该修改发生在首次逐镜采样期间，四次运行均被输入SHA变化守卫中止；原报告、源码身份和日志保留在[初次记录](initial-preflight/README.md)，没有将未聚合的零违规写为通过。稳定源码重新完成36+30+30+30采样，零违规、字体/边界/字幕审计通过。独立实际查看8张合辑覆盖全部42镜中段，另直接查看幂等1421与熔断1084，确认标记、流程、字幕和导航可见；见[independent](independent/)。本次沿S022/L055–57执行，后续截图导出问题另记L059。

当前来源审查核对保留的实际原文与历史核验记录，没有将本轮视觉修改写为重新访问官网。完整音轨、时序、实际媒体与网页验证各按其真实记录声明；不预记全片听辨、ASR、真机、新观看认可或学习效果。本次仅GitHub站点，不向外平台重新投稿。

## 文章JPEG导出修正

完整66张正式PNG审读通过后，根复核发现默认MJPEG截图的亮青偏绿。保留首次候选3cbc97dd、四张原JPEG和首次站点构建/部分交互，不将它们写为最终验收；仅以同MP4同一精确帧进行limitedBT709→fullBT601 JPEG像素转换。四张新JPEG对同帧PNG的全文RGB误差均降低、色块偏差收敛；视频、原配音、冻结源、文章MDX与66张PNG全部不变。前后像素、完整SHA和准确命令见[纠正记录](figure-export-correction.json)，独立终审与最终站点另外记录；教训见L059。

## 交付包

四条高清成片与12张现行封面打成17文件ZIP，逐项CRC/全文SHA、520输入字节/SHA/mtime保护通过；文件25,750,420字节，SHA-256 `96c3c372a8e8664a9c76217c0d8e290dc1e4aea13bd1385fe609d106d89be878`。由独立delivery分支保存，不把ZIP放main；[不可变下载](https://raw.githubusercontent.com/linhongcun/video-studio/e5e090b0ff5425b6e8cbf09c4ade570357f0e273/design/peak-video-style-20261029/peak-video-style-20261029.zip)已完整HTTPS GET并逐字节散列核验，见`delivery-download-verification.json`。

## 最终网站与发布范围

最终网站候选为`1a26027d7d6e2f4c50574604b8f37b56ecb7b7b4`，后续文档提交的site/episodes/episodes-codex树保持此候选。两次完整构建分别保留旧JPEG与纠正JPEG身份；四集1440×1000和390×844播放、K暂停、全屏、章节、原文浮层、亮暗Figure与实际图像取色检查通过，16份本地完整HTTP媒体响应SHA相符。默认原生字幕关闭，烧录字幕可见；显式启用VTT后资料区无活动cue，返回正文恢复。

稀疏检出缺少两张已跟踪站点图标，验收中按候选Gitblob补齐并对public/dist/完整HTTP三方SHA核验；五份public静态资产均实核，Git无变更。独立原图JPG文档触发浏览器对origin-root `/favicon.ico` 的404，作为非阻塞附带请求保留，未为此修改站点base或视频。手机原图查看器保留自然缩放，其滚动不当作文章溢出；应用页面单独检查。初次候选、失败/中断假设与有界复用范围见`site-final/`。

仅GitHub站点，原外平台链接保持。计划版本v0.91.1，实际合并、附注tag、Release与Release后Pages身份、canonical完整GET能力限制以[正式Release](https://github.com/linhongcun/video-studio/releases/tag/v0.91.1)所链发布回执为准，不用本地媒体SHA代替线上完整验证；本记录不预记最终部署。

最终网站实核34次视频章节、24次文章章节、16组Figure主题/回看/原图、12组原文与来源键盘访问、8组播放/K/全屏/字幕生命周期；实际查看42张网站PNG，保留70份浏览器截图。Video→Canvas对ffmpeg同帧背景最大通道差1，纠正Figure网页像素与JPEG相同、对PNG差1。完整报告见[最终网站验收](site-final/README.md)。
