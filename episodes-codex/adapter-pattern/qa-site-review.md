# D03业务边界修订：v0.64.1本地站点交付

接入及本地验收通过。EP31、D03顺序3、firstRelease **v0.63.0**、publishedAt **2026-10-25**保留；revisionRelease **v0.64.1**、updatedAt **2026-10-25**。新成片4011帧/133.7图像秒，MP4 SHA `f86d48b91d0bc0a00c3d5f51b69bc4ec57106d2dd422358a1c59d2f296528852`；Java尾卡3861+150帧。

首次全套检查执行1440浅色/390深色四章共8次真实seek和短静音播放，20条字幕逐字逐时核对。Java卡首/中/尾均在showing且已完整加载20cue的轨道中0活动cue，并实际解码暂停。原生SVG computed字号、锚点、bbox、#java、两个完整Java源码依赖链接、无溢出和三期目录/前后课均通过。历史路径回归执行1次；40个已发布页面、5个学习方向，Skills存在、两期退役Agent缺失。D01/D02/Skills/P04核心文件及其他所有metadata逐字节保留，egg-drop仍为草稿。

初验发现三处Markdown粗体未生效。以冻结原稿为输入，站点专用`site-article.mdx`只将这三句的句号移到粗体外；去掉粗体标记后文字逐字相同。原稿SHA `4f2e09feb138a15ad96b613a8f34a64cd8b1f384fb45a6501ce529425323f35b`，派生稿SHA `5c011029db0391a9e16741b2d5c873b045eaee213f0f023202483bc79de5ae65`。原184项冻结输入未被本次派生写入。精确匹配次数与diff见`qa-site-article-derivation.json`，复制映射见`qa-site-copy-manifest.json`。

初验报告/日志/截图按原字节另存`revisions/business-boundary-v2/site-initial-check/`；旧v0.63已发布证据独立保留在`previous-site/`。格式修正后仅追加1次构建与两视口三处strong、无裸`**`、#java、链接、无溢出定验。共2次构建、1次历史回归。player HTML、目录HTML、JSON-LD、VTT、metadata、SB、视频、海报与sourcePath均与初验相同，因此保留原8seek/20cue/Java检查的原身份，未声称重新运行。

- 初验输入指纹：`f538e7f34cebcee9e38dfb4f9105d3ed777c153cb47df2a3372a1396c178a8b5`
- 最终输入指纹：`28c7e466f3a9403dde962573e68cc904efbb400597183cdd689fc66aff30849f`
- 最终构建凭证：`qa-site-format/build-receipt.json`
- 定向验收：`qa-site-format-correction.json`
- 汇总与实际看图范围：`qa-site-static.json`、`qa-site-visual-review.json`

实际看过初验6图与修后7图；范围逐张列明，初验带裸标记的正文截图不作为修后证据。未新增媒体重编码、全片听辨或学习效果判断。

本地构建的GitHub Release API取数失败时使用既有外链回退，不代表新Release核验通过。根完成Release和Pages后再运行`site-verify-online.py`的11个普通canonical GET（完整视频流SHA，不保存远端媒体），线上结果单独记录。
