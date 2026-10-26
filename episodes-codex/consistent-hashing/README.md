# EA01 · 一致性哈希

对应[#295](https://github.com/linhongcun/video-studio/issues/295)，内部EP38，制作PR[#304](https://github.com/linhongcun/video-studio/pull/304)。制作目录为本目录，站点读取`episodes/consistent-hashing/`。实际交付与线上证据见`release.md`，不以本说明预记上线或用户观看认可。

本片围绕同一次缓存扩容：先认识键与确定性哈希，再看直接对节点数取余为什么改变许多旧归属；由保留已有去向的目标推导固定编号环、顺时针首个节点及回绕。保持A20/B50/C85，加入D70，只接管(50,70]。同一批十个示例键取余改变8个、环改变2个，均为这组输入的结果。虚拟节点另用预先配置的示例，并按物理身份着色，区分分配区间、数据迁移和请求热度。

14镜、28句、4章，1920×1080 / 30fps / 5881帧，约3分16秒。没有代码尾卡，工程机制和完整示例实现分工：视频解释连续因果，文章保留Python和边界。资料来自实际读取的NGINX、Cassandra5.0及Redis官方文档；不冒充完整产品实现。

## 可复现入口

所有配音、装配、起音和混音都调用保留的共享实现；`remotion`在本期实体目录按锁文件独立安装。Python声音工具使用`/workspace/.venvs/video-studio/bin/python`，不把系统Python缺失依赖写成已安装。

```sh
python3 episodes-codex/consistent-hashing/verify_model.py
/workspace/.venvs/video-studio/bin/python episodes-codex/consistent-hashing/assemble.py
/workspace/.venvs/video-studio/bin/python episodes/_shared/place_v2.py --dir episodes-codex/consistent-hashing --mode whole
/workspace/.venvs/video-studio/bin/python episodes/_shared/label_onset_strict.py --dir episodes-codex/consistent-hashing
/workspace/.venvs/video-studio/bin/python episodes-codex/_shared/check_sentence_episode.py episodes-codex/consistent-hashing
```

现有音轨从已选择的39份候选中装配，输入请求、原始音频、选段及每句处理证明均在`voice/`。不为复现重新随机请求TTS。句级时序和声学检查不等于逐字ASR、语义听辨或全片人工听辨；本轮没有执行这些能力。

在本期`remotion/`中：

```sh
npm ci --no-audit --no-fund
npx tsc --noEmit
npm run covers
node scripts/qa.mjs out/preview
```

实际`out/timed-preview`使用28句正式时序产出98张PNG、三段无字幕编码片，根与独立审稿的检查范围见`qa-preflight.json`、`qa-motion-independent.md`和`qa-term-onset.json`。封面、标签、物理/虚拟身份的预检失败与定向修订在`qa-revisions/`，不删除失败历史或仅凭静帧宣布整片清楚。

首轮正文制作时，所有写入负责人停止修改、动态检查闭合后采用以下冻结入口；本次引用呈现修订使用文末的`freeze_with_references.py`，不重写首轮146项正文历史：

```sh
python3 episodes-codex/consistent-hashing/freeze.py
python3 episodes-codex/consistent-hashing/freeze.py --verify
```

正式渲染使用本期`npm run render`，在外层取得`/tmp/video-studio-render.lock`并设置有空间的短`TMPDIR`。编码前后核对同一清单；如果输入改变，先停止排队或编码，重新检查与冻结，不拿新清单追认旧媒体。

正式文件完成后运行共享`check_encoded_episode.py`、本期`verify_encoded_voice.py`和独立`verify_video.py`，实际看图并记录能力范围。网站接入使用同一媒体及冻结字幕，完成桌面/手机播放、全部章节seek、图文与新系列检查后，按持续授权合并、Release、再次部署并核验完整线上SHA。完成后才关闭#295；本轮不发外部平台。


## 首版片尾参考资料（历史记录）

以下保留首版资料卡的实际制作记录；命令对应当时的资料清单与旧呈现，不直接用于本轮新`references.json`。当前原题名与短引入口见文末。

发布前整合主干1dacf608/v0.69.1的新要求，只对已验收正文追加150帧资料页。最终6031帧约3分21秒；原14镜28句/5881帧及原AAC保持。正文146项冻结清单不重写，新清单、卡图、源码/字体摘要与追加receipt在`reference-inputs-sha256.json`和`revisions/reference-endcards/`。

原正文媒体的Git来源为`c80faaefa7750dd8facebc0dc65658ca56400a4d:episodes/consistent-hashing/video.mp4`，本地不可变输入为`revisions/reference-endcards/body.mp4`。复验最终整体使用共享追加验证器；原`check_encoded_episode.py`和`verify_video.py`是正文检查器，不把6031帧整体套成5881帧正文或重写旧检查记录。

```sh
/workspace/.venvs/video-studio/bin/python episodes-codex/_shared/append_references.py verify --body episodes-codex/consistent-hashing/revisions/reference-endcards/body.mp4 --references episodes-codex/consistent-hashing/references.json --output episodes-codex/consistent-hashing/video.mp4 --artifacts episodes-codex/consistent-hashing/revisions/reference-endcards
```

首次追加使用同一命令的`append`动作，只编码资料卡，不重做正文。网站meta用6031帧及referenceAppendix，分镜/words保持正文5881帧，字幕严格退出在卡首之前。最终网站来源与媒体一致性由`sync_site.py`的双身份检查及交付清单验证。


## v0.70.0默认入口与冻结（历史记录）

本期在发布前同步了b83a0b04的新默认流程。原正文146项清单原字节保留；旧package在body-remotion-package.json中仅作历史输入重定位，所有145个其余输入原路径摘要相同。当前生产清单157项包含新编排与资料来源，编码前不冻结video/生成receipt/render-result。

```sh
python3 episodes-codex/consistent-hashing/freeze_with_references.py --verify
PATH=/workspace/.venvs/video-studio/bin:$PATH npm --prefix episodes-codex/consistent-hashing/remotion run render
PATH=/workspace/.venvs/video-studio/bin:$PATH npm --prefix episodes-codex/consistent-hashing/remotion run verify:references
```

当前默认render会先检查来源/冻结，渲染out/body.mp4再自动附资料卡；verify:references只检查现有整体，不重新渲染。本轮已编码正文按原真实146输入保留，调用默认流程只读verify闭合当前交付，不假称正文采用后来更新的编排重新渲染。

## 原始题名与原文短引修订（2026-10-25）

本轮资料采用`presentation: original-title-quote`，保留文档实际完整原题名，原文短引逐字对应公开正文及定位；`supports`仅用于内部论点核查，不上屏充当原文。每页最多2项、默认5秒，提示暂停阅读。当前资料及文章由对应负责人核验，完成状态以[本轮记录](../../docs/reference-endcards/original-titles/README.md)和实际交付为准，不预记通过或发布。

正文仍为原14镜28句、5881帧，不改变配音、字幕、分镜或代码。原146项清单保持原字节：旧package继续在`revisions/reference-endcards/body-remotion-package.json`验证；原`article.mdx`与`research.md`分别按`revisions/original-titles/before-article.mdx`和`before-research.md`的字节验证。这两份文稿快照的摘要须等于原146项清单，不能用新引用段覆盖旧正文来源。

当前生产清单由`freeze_with_references.py`生成，单独记录当前文章、调研、package、资料JSON、新`append_references_original.py`、未改动的旧媒体拼接engine、统一wrapper、Pillow版本锁、资料检查器，以及`verification`、`titleEvidence`和可选`quotation`分别声明的全部证据文件；本片新证据为`docs/reference-endcards/original-titles/sources-extra.json`。旧文稿快照与旧package也进入当前清单，明确保留历史与本轮输入的映射。视频、卡图回执和`render-result.json`继续作为输出，不在编码前冻结。

```sh
python3 episodes-codex/consistent-hashing/freeze_with_references.py --check-body
# 来源负责人全部停写后再生成当前输入清单：
python3 episodes-codex/consistent-hashing/freeze_with_references.py
python3 episodes-codex/consistent-hashing/freeze_with_references.py --verify
```

本次仅重出参考资料页并接到无损恢复的`remotion/out/body.mp4`之后，不调用默认正文渲染、不重新混音或请求TTS。正文恢复及最终文件的实际身份由本轮`revisions/original-titles/baseline.json`和媒体保留检查记录；旧容器摘要与恢复后容器摘要可能不同，不能以文件名代替逐帧、时间戳及原AAC/PCM保留证明。

后续确需完整渲染时，既有`npm run render`仍调用统一wrapper，`render:body`沿本期原voice→mix流程输出`out/body.mp4`，wrapper现选用新原题名生成器。实际资料页与最终总帧数以新回执为准；不要把原正文5881帧或旧6031帧整体时长直接当成本轮结果。接齐期根交付回执和`render-result.json.publicationMetadata`后，在本期`remotion/`执行`npm run verify:references`，只验证当前冻结与整体交付，不重渲染。精确资料首帧字幕、各页暂停/全屏和最终线上完整SHA仍需按实际结果独立核验。


## 题名与作者：当前资料入口

本轮资料卡采用`presentation: title-author`，按完整原始题名和作者/机构列示。仅在来源本身已有`author`时使用该字段，否则使用既有`organization`，不补造个人姓名。原题名、机构、原文摘录、定位及核验文件保留在`references.json`和配套文章中；本轮只切换显示方式，不改研究结论或正文。

默认资料渲染器为共享`append_references_bibliography.py`，早先两份渲染器保持历史字节并继续作为冻结依赖。新卡按实际排版分页，每页默认5秒；修前回执、来源清单、入口及输入身份保存在本实际制作目录的`revisions/title-author/`，不重写旧验收结果。候选资料卡同在该修订目录生成，通过检查后再接入既有最终产物与回执位置；本轮进度由根任务记录。

当前冻结入口为`freeze_with_references.py`，加`--verify`只读核对。冻结清单在原有正文、声音、图标、导航和历史来源输入之外收录新渲染器，既有wrapper、发布检查器、两份旧渲染器及证据仍保留。默认正文构建、混音、并发和已有代码卡顺序均沿用实际package；本批只消费基线已验收的完整正文生成资料卡，不运行正文prepare、TTS、重渲或重混音。

原146项正文来源仍以真实历史package及旧文章/研究快照分别验证；当前清单另外声明新资料入口，不改旧核心`freeze.py`或历史输入，也不将当前资料格式追认为旧正文的编码来源。

资料生成后按新回执同步最终总帧数、媒体SHA及发布映射；实际复核题名/署名、分页、首卡字幕边界、暂停及原生全屏。原脚本、配音、字幕、分镜、动作和文章/研究均保持本轮基线字节，旧技术验收只按原体保真范围复用，不预记新版已获观看认可。
