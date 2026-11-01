# D02 观察者模式：模式主线修订

用户观看v0.68.4后指出MQ占据主要篇幅，偏离设计模式。当前从同一订单17、摘要和变化记录解释观察者的动机、角色与共同约定、订阅/通知/退出、收益成本；MQ仅第09镜13.53秒实践对应，结尾回到模式。不能把上一轮技术和部署检查当作用户认可主题。

新正文10镜20句、4292帧/143.07秒，其中模式129.53秒（90.54%），MQ13.53秒（9.46%）；静默Java原理卡150帧，总4442帧/148.07秒。代码不逐行讲语法，完整原例仍在demo-java。旧v0.68.4源码与身份在revisions/observer-first/baseline，原12镜源在revisions/mq-practice/baseline，旧检查范围按其版本保留。

01产品操作；02说明接收需求变化时分开来源与响应的动机；03逐节点角色；04明确回看付款前再登记；05先改来源、收到后各自响应；06关闭摘要并取消；07同一订单发货只到记录；08收益与成本；09框架事件/MQ短应用映射；10回原例的模式核心。原例最终订单已发货、记录两条、摘要已退出且最后值已付款；09独立映射不改变它，10回到同一最终结构。

## 实际生产入口

Python使用/workspace/.venvs/video-studio/bin/python。当前锁文件npm ci安装257包，node_modules为本期实体目录。共享voice/prep.py、gen.py、build.py→assemble_sentence_episode.py→place_v2.py→label_onset_strict.py负责配音、分镜与3句首标签；不复制裁音/起音算法。新配10句pattern take，旧10句按observer-first-reuse.json逐字/原字节映射到flow/reuse，选段见picks.json。

独立配音检查见qa-observer-first-voice.json，20句原始转换、模型文字、共享裁尾与正文PCM通过，内部低信号flags为空；没有逐字ASR或全片人工听辨。原理Java完整程序与真实节选另行校验，不把其运行当成MQ集成测试。

Java附录用共享append_java_endcard.py append/verify，必须指定--body-dir revisions/observer-first/voiced-body；正文真实快照不可覆盖，字幕不进入附录，音轨前缀一致且附录PCM全零。本期freeze.py先验证新正文派生，再调用标准冻结器并纳入真实当前take、程序、源码、共享图标、公开研究旧证据和拒绝版基线；核对加--verify。

预演使用remotion内npm run qa；关键采样入口由motion.events提供，需检查新动机、合并通知的完整收发、关闭与下一次通知、短应用映射到模式回收及Java卡边界。所有写入者停写、预检通过、冻结核对成功后才允许npm run render，使用短TMPDIR和共享渲染锁。正式成片用check_encoded_episode.py核对完整解码、帧数、音频、响度和冻结输入。

site-integrate.py直接复制当前文稿和通过验收的媒体，保留slug、创建与首发身份，仅更新内容修改时间、时长、描述和revisionIssue。verify-online.py检查线上完整视频/海报/VTT、20句、5章、模式主线和真正Release条目。实际交付见docs/observer-pattern-first/README.md及本期release.md；平台未新发，不预写用户观看认可。

## 首版参考资料附录（2026-10-25历史记录）

完整讲解与Java原理卡仍为video.mp4：4442帧/148.07秒、SHA23b49bf1…beb64be7，181项冻结输入与旧检查保持。新增一张参考资料卡由共享episodes-codex/_shared/append_references.py单独生成150帧，输出video-with-references.mp4：4592帧/153.07秒、SHA5b98a0bc…cea67d0。只有后者用于发布，site-integrate.py明确记录其到episodes/observer-pattern/video.mp4的字节复制映射；原render-result.json是核心报告，发布映射改用render-result-final.json。不要用核心帧数检查器把派生文件与4442帧的分镜误比。

references.json的两项资料分别支持模式主体和唯一实战镜，来源正文/日期沿用同日已保存证据，不冒称重新联网。完整链接及论点映射已在原article.mdx脚注中，因此保持原冻结文章不改。生成器、字体、主题、资料清单和核心媒体SHA都在revisions/observer-first/reference-appendix/reference-appendix.json中记录，独立媒体校验保存全部4442解码帧/PTS、AAC包/时间戳和PCM完全一致的证明；参考段无新增音频包，原音频在原端点结束。

旧回执与原始资料输入现归档于`revisions/original-titles/`；本轮新器入口见下节，不再对当前资料清单执行旧生成器。正式参考卡独立抽4441/4442/4517/4591四帧及全尺寸PNG，机构、资料名/版本、暂停提示和正文/附录边界通过；原47核心状态检查按全前缀保真继续适用。完整检查见qa-observer-first-references-independent.json及reference-appendix-media-check.json。Java字幕边界在4292帧优先，后面的4442帧参考卡不覆盖它。


## 原始题名与原文短引（历史资料样式）

本轮使用 `presentation: original-title-quote`，保留资料实际完整原题名及原语言；短引采用连续原文并标明位置，不把内部 `supports` 当成文献原句。每页最多2项、默认5秒，最终时长以新回执为准。本轮修前资料/文章/研究/冻结与回执均保存在 `revisions/original-titles/`，不得覆盖；旧附录的SHA和核验只表示当时实际结果。详见 [原题名修订](../../docs/reference-endcards/original-titles/README.md)。

本期继续区分两个视频身份：`video.mp4`为讲解加Java卡的4442帧核心，`render-result.json`是核心报告；最终发布媒体为另名 `video-with-references.mp4`，使用 `render-result-final.json` 记录最终身份。不能把普通wrapper输出到`video.mp4`的策略直接套到本期，更不能把含旧资料附录的最终文件当成原核心继续叠加。

在 `remotion/` 运行 `npm run check:references`，全部输入停写后使用本期 `freeze.py`（仍先核验真实Java派生和原声/分镜）冻结；加`--verify`只读核对。清单保留原核心真实输入，并收录新原题名渲染器、未改字节的旧媒体引擎、默认wrapper、发布检查器、资料/文章/package、Pillow版本锁、主题及三类证据路径：`verification.evidence`、`titleEvidence.evidence`与可选`quotation.evidence`。当前文献段更新不冒充旧核心已采用的新来源，旧核心完整SHA与修前清单单独追溯。

后续完整制作的默认 `npm run render` 执行来源/冻结预检，再以 `render:body`沿用原`render:voice`→`render:mix`生成核心`../video.mp4`，最后自动执行新`render:references`。本次仅复用已核验核心，运行尾卡入口，不重渲正文、不重配音：

```sh
# 本期 remotion/ 目录；原核心 video.mp4 必须已在位并通过核验。
npm run render:references
npm run verify:references
```

尾卡入口使用 `append_references_original.py`，明确指定`--body ../video.mp4 --output ../video-with-references.mp4 --artifacts ../revisions/observer-first/reference-appendix`。`verify:references`执行当前来源与本期冻结检查，再由同一新器验证该独立核心/最终媒体和资料回执；它不会调用普通wrapper覆盖核心，也不会自动更新最终发布元数据。`site-integrate.py`的发布映射仍要求最终报告与实际最终媒体一致，接入前必须按新回执更新并另行复核`render-result-final.json`。

Java卡仍自4292帧开始150帧，参考卡从完整核心4442帧之后开始，两段字幕边界分别检查。最后实际查看所有资料页、精确首卡和桌面/手机暂停/全屏；原核心QA只在完整正文/Java卡及原AAC确证保持的范围复用，不预记当前附录或发布已经通过。


## 题名与作者：当前资料入口

本轮资料卡采用`presentation: title-author`，按完整原始题名和作者/机构列示。仅在来源本身已有`author`时使用该字段，否则使用既有`organization`，不补造个人姓名。原题名、机构、原文摘录、定位及核验文件保留在`references.json`和配套文章中；本轮只切换显示方式，不改研究结论或正文。

默认资料渲染器为共享`append_references_bibliography.py`，早先两份渲染器保持历史字节并继续作为冻结依赖。新卡按实际排版分页，每页默认5秒；修前回执、来源清单、入口及输入身份保存在本实际制作目录的`revisions/title-author/`，不重写旧验收结果。候选资料卡同在该修订目录生成，通过检查后再接入既有最终产物与回执位置；本轮进度由根任务记录。

当前冻结入口为`freeze.py`，加`--verify`只读核对。冻结清单在原有正文、声音、图标、导航和历史来源输入之外收录新渲染器，既有wrapper、发布检查器、两份旧渲染器及证据仍保留。默认正文构建、混音、并发和已有代码卡顺序均沿用实际package；本批只消费基线已验收的完整正文生成资料卡，不运行正文prepare、TTS、重渲或重混音。

本期`video.mp4`仍是4442帧讲解加Java卡核心，最终附录输出仍为独立`video-with-references.mp4`，核心报告不覆盖。当前尾卡append/verify入口明确区分两者，不能改用普通wrapper覆盖核心；正式发布继续按独立最终报告和实际媒体映射核对。

资料生成后按新回执同步最终总帧数、媒体SHA及发布映射；实际复核题名/署名、分页、首卡字幕边界、暂停及原生全屏。原脚本、配音、字幕、分镜、动作和文章/研究均保持本轮基线字节，旧技术验收只按原体保真范围复用，不预记新版已获观看认可。
