# EP39 布隆过滤器：单位置主线修订

公开课程保持`bloom-filter`、EP39、工程算法第二期。该目录是本次独立制作工程；旧`episodes-codex/bloom-filter`的v0.71.0冻结输入、配音和媒体保留原字节。站点发布副本仍为`episodes/bloom-filter`，元数据`sourcePath`指向本目录的`remotion`。

主线为8位、一个元素计算一个位置：A/B共享3，D在7读0可排除，C在3读1却从未加入。错误清位说明共享边界；片尾仅用另建、完整重插A/B的双位置对照解释如何排除C的这次误判，不据此估算误判率或声称增加次数必定更好。

资料、脚本与模型先独立审查。所有旁白重新生成，使用共享冰糖TTS/整轨/起音工具；句包络不是逐字ASR。实际时序、动态、冻结、编码与发布状态以本目录各阶段QA为准，文件存在不表示检查已完成。

仓库根路径记为`ROOT`，本目录记为`D`。依次执行共享`voice/prep.py`、`voice/gen.py`、`voice/build.py`、`assemble_sentence_episode.py`、`place_v2.py`和`label_onset_strict.py`；在实际时序上完成动态与版式预检后，运行本期`freeze.py`，然后在`remotion`运行默认`npm run render`。默认入口包含正文混音和题名、作者参考资料附录，最终交付`D/video.mp4`。

`freeze.py --verify`只读核对本期冻结；旧版的验证入口和结果仍适用于旧版，不能用新清单追认旧编码。`sync_site.py`同步通过检查的最终媒体，保留创建、首发时间和首发版本，仅更新内容修改时间；`verify_published.py`在Release后的Pages成功后核验普通线上GET与完整SHA。外部平台未获本轮新发授权。

修订追踪：[issue #342](https://github.com/linhongcun/video-studio/issues/342)、[PR #343](https://github.com/linhongcun/video-studio/pull/343)。反馈以原因和改进的总结记录，不摘录对话；检查通过不代表已获新版观看认可。

## 实际交付

已由[PR #343](https://github.com/linhongcun/video-studio/pull/343)合并`47e27a7b`，随[v0.71.1](https://github.com/linhongcun/video-studio/releases/tag/v0.71.1)发布。[课程页面](https://linhongcun.github.io/video-studio/episodes/bloom-filter/)保持原URL、EP39与首发身份，修改时间为2026-10-26T10:15:31+08:00。

最终4720帧、157.333333秒，完整SHA-256：`e47e4cb2707d108f739232fc4f763aea6a459e45e30a6d8f8bb75b3444cfe2dd`。130项冻结输入的清单SHA：`06632c370fe18c66636221cd04f31413d6c5042352ddb8cfdc19888f6f673dcb`。

独立模型/审稿、真实动态/DOM、56张实际MP4图及完整解码/音轨数值检查通过；桌面/窄屏84项本地检查及代码滚动、完整复制/执行可达性通过。最新[Pages40262765700](https://github.com/linhongcun/video-studio/actions/runs/40262765700)成功，2026-10-26T11:16:49.910345+08:00的10个普通canonical GET核对完整媒体SHA、海报、VTT、四章及实际Release/更新日志通过；线上两视口实际播放、章跳转、4570首资料帧paint与无active cue通过。

实际阶段结果见[最终QA](qa-final.md)、[动态预检](qa-motion-independent.md)、[实际成片](qa-video-independent.md)、[网页审查](qa-site-visual-independent.md)、[发布证据](publication-evidence.json)。Release首轮识别检查发现说明缺课程URL，补齐后重新部署同步日志，原失败记录保留；没有重配或替换成片。旧150项冻结和原媒体、其他902份发布文件保持。没有全片人工听辨、逐字ASR或新版用户观看认可；窄屏为headless视口，非真机。仅GitHub站点，无外部平台新发。


## 题名与作者：当前资料入口

本轮资料卡采用`presentation: title-author`，按完整原始题名和作者/机构列示。仅在来源本身已有`author`时使用该字段，否则使用既有`organization`，不补造个人姓名。原题名、机构、原文摘录、定位及核验文件保留在`references.json`和配套文章中；本轮只切换显示方式，不改研究结论或正文。

默认资料渲染器为共享`append_references_bibliography.py`，早先两份渲染器保持历史字节并继续作为冻结依赖。新卡按实际排版分页，每页默认5秒；修前回执、来源清单、入口及输入身份保存在本实际制作目录的`revisions/title-author/`，不重写旧验收结果。候选资料卡同在该修订目录生成，通过检查后再接入既有最终产物与回执位置；本轮进度由根任务记录。

当前冻结入口为`freeze.py`，加`--verify`只读核对。冻结清单在原有正文、声音、图标、导航和历史来源输入之外收录新渲染器，既有wrapper、发布检查器、两份旧渲染器及证据仍保留。默认正文构建、混音、并发和已有代码卡顺序均沿用实际package；本批只消费基线已验收的完整正文生成资料卡，不运行正文prepare、TTS、重渲或重混音。

本片当前实际工程为`episodes-codex/bloom-filter/revisions/single-hash-core/bloom-filter/`，主线正文4570帧。只维护本目录的refs、入口和冻结，产物为本目录`video.mp4`；上层旧5741帧工程及其媒体保持历史身份，不能作为本轮正文或发布来源。

资料生成后按新回执同步最终总帧数、媒体SHA及发布映射；实际复核题名/署名、分页、首卡字幕边界、暂停及原生全屏。原脚本、配音、字幕、分镜、动作和文章/研究均保持本轮基线字节，旧技术验收只按原体保真范围复用，不预记新版已获观看认可。
