# LC.739 每日温度

## 当前贴题开场修订（2026-10-26）

前轮基础衔接得到定性改善反馈，本轮进一步提前预告方法并把基础融入同题动作。14镜28句、4新24旧，正文4881帧，含简洁资料附录5031帧/2:48；Python与资料各5秒。文稿、真实配音/动态/来源预检及正式成片独立声画检查通过，274输入冻结；网站与发布继续按当前记录验收。最新发布片/正文/QA在revisions/problem-fit-opening-before保留，当前成片与网站状态见[本轮记录](../../docs/daily-monostack-opening/README.md)。

## 栈前置修订交付状态（本轮引用格式修订前）

用户观看v0.69.0后指出默认懂单调栈，现先补栈的同端操作、后放先取、底顶，再演不升与维护，之后才命名。新增4句、复用28句；正文5322帧，最终含参考资料5472帧/182.4秒，Python与参考资料卡各150帧/5秒。190项生产输入核对通过。实际最终视频SHA256：`f3aa4f315770896ef3b3d15d8ad3d38ed5602d07528d9fcc20300bad3d6b3a3b`。实际动态、声音、正式MP4独立视觉与媒体检查均通过，能力范围见当前QA；网站及发布状态见[修订记录](../../docs/daily-temperatures-stack-primer/README.md)。该轮随后收到基础衔接有所改善的反馈，最新节奏优化见上；不扩大为所有细节或新一版认可，无逐字ASR或全片人工听辨。旧片/旧QA完整保留于`revisions/stack-primer-before/`。

现行正式渲染从`remotion/`运行`npm run render`，默认共享入口生成正文和参考资料附录。旧版算法/封面保持，源卡片操作来自真实Python append/pop概念演示，与解题trace分开。
以下保留阶段1制作交接记录，开发占位分镜和未生成配音的说明只适用于当时，不是当前状态。

开工基线8d037aa3e05ce1ed992df6b758b9b2227dd8b18b，issue #80，内部EP35，片内只标LC.739。root已从clean最新主干创建codex/leetcode-batch-next，当前独立锁图已npm ci；不依赖被删除工程。计划批次firstRelease v0.69.0，实际发布由root完成。

本期阶段1已完成14镜28句4章脚本、官方题面实际读取、唯一完整Python、独立oracle验证、同源真实执行trace及原创Remotion源码。当前storyboard明确provisionalTiming/pendingAudio，4303帧约143.43秒只是编辑排布，末150帧静态Python卡。尚未生成TTS、实际静帧或视频，不能预记媒体、起音、听辨及上线通过。

主线：每日气温要返回未来第一个严格更暖的等待天数 → 重复往后找 → 留下未解决日期 → 按温度不升、末尾先检查 → 命名单调栈 → 按日执行 → 相等与末尾0 → 复杂度和完整Python。主例[33,34,35,31,30,32,36,33]，输出[1,1,4,2,1,1,0,0]；相等补例[30,30,31]，输出[2,1,0]。示例无指定单位、非真实预报。

核心文件：script.md、plan.json、article.mdx、research.md、pronunciation.md、visual-direction.md、knoll-props.md、covers.json。research/source-access.json与official-web-response.json是官方网页访问证据，solution.py是唯一算法执行源，solution.json与文章代码同源，research/trace.json由sys.settrace观察真实函数生成。Main.tsx读取事件id，不另写解题器。

阶段1复现（从本目录运行，无媒体）：

```sh
/workspace/.venvs/video-studio/bin/python research/verify_solution.py
/workspace/.venvs/video-studio/bin/python build_draft.py
/workspace/.venvs/video-studio/bin/python research/verify_production_inputs.py
./remotion/node_modules/.bin/tsc --noEmit -p remotion/tsconfig.json
```

算法验证：8个官方/边界样例、21844组穷举、3000组确定随机、2组十万长度输入通过；main35事件、equality13事件。源码SHA256为5f628ef12f8f1fd15c85289eeaabec3b2aa01706df39fa1356afb09a8314b718。静态源检查验证双句、四章、题意与方法命名顺序、同源程序、末卡边界、封面声明安全区及固定字号实测宽度。它不能替代实际图像或动态检查。

root安排独立编辑与算法审稿，审稿闭合后才生成配音。后续只使用共享voice prep/gen/build、共享整轨与起音算法；真实build后执行prepare_code_endcard.py，再铺轨、检查真实时序和动态。build_draft.py不能作为生产时间来源。所有写入停止后freeze.py冻结；使用flock /tmp/video-studio-render.lock与TMPDIR=/workspace/daily-tmp串行渲染。检查合格后按持续授权接入GitHub站点，本期无外部平台发布授权。

本阶段没有ASR、全片人工听辨或用户观看结论。

## 制作海报补齐

真实封面复核发现`covers.json`声明的竖版`poster.jpg`缺失，六张比例封面本身已通过。保留原阻塞记录于`revisions/missing-poster-before/`，仅执行`cp cover-3x4.jpg poster.jpg`补齐声明产物，二者逐字节相同。网站另由`episodes/daily-temperatures/meta.json`明确选择`cover-16x9.jpg`。新增竖版已独立实际查看，详见`qa-covers.md/json`；未重渲不变封面，未改覆盖源码、分镜、声音或其他冻结输入。

## 原始题名与原文短引：当前参考资料入口

本轮保留刚上线的栈前置讲解及完整Python卡：主体仍为5322帧，其中Python卡自5172帧开始150帧。仅将其后的资料卡迁移为 `presentation: original-title-quote`，显示真实完整原题名、原语言和带位置的连续原文短引，不把内部 `supports` 当作文献原句上屏。每页最多2项、默认5秒，最终帧数和区间按实际新回执计算。修前资料、文章、研究、冻结与回执已保存于 `revisions/original-titles/`；前节5472帧及SHA仅表示此前单页资料卡的历史结果，不预记新卡已验收。当前范围与后续发布见 [原题名修订](../../docs/reference-endcards/original-titles/README.md)。

在本期 `remotion/` 运行 `npm run check:references`，所有生产输入停写后用本期 `freeze.py` 冻结，加 `--verify` 只读核对。冻结保留原句级、声音、程序、拼接计划和全部旧/新画面素材依赖，再录入新原题名生成器、未改字节的旧媒体引擎、wrapper、发布检查器、Pillow版本锁、主题、资料/文章/package，以及 `verification.evidence`、`titleEvidence.evidence` 和可选 `quotation.evidence` 的实际JSON文件。本轮资料证据在 `docs/reference-endcards/original-titles/sources-algorithms.json`，不覆盖旧证据。

默认 `npm run render` 继续使用统一wrapper；其 `render:body` 必须保留 `python3 ../render_stack_primer.py`，不能机械替换为普通 `render:voice`→`render:mix`。该薄入口按 `stack-primer-remix-plan.json` 的真实原/新片段与PCM生成主体 `out/body.mp4`，wrapper随后用 `append_references_original.py`追加资料。本期拼接计划不消费文章或研究文件，package也维持原计划已核验的完整SHA；当前文献段落和新尾卡输入不冒充旧主体来源。

本次只复用从最新5322帧主体恢复并核验的 `remotion/out/body.mp4`，单独生成资料尾卡，不重渲讲解、Python卡或重新混音，不从此前版本覆盖新的栈教学。最终视频为本期 `video.mp4`，附录记录在 `revisions/reference-endcards/`，交付副本在期根；接齐新回执及 `render-result.json.publicationMetadata` 后，运行 `npm run verify:references` 只读核对来源、冻结和最终媒体。原旁白、字幕、分镜及 `words.json` 仍表示5322帧主体，Python卡与参考资料起点分别核验；旧QA仅在原画面/声音确证保持的范围复用。实际查看每张新卡、精确首卡字幕以及桌面/手机暂停与全屏后再发布，不将自动检查当作人工听辨或用户观看认可。


## 题名与作者：当前资料入口

本轮资料卡采用`presentation: title-author`，按完整原始题名和作者/机构列示。仅在来源本身已有`author`时使用该字段，否则使用既有`organization`，不补造个人姓名。原题名、机构、原文摘录、定位及核验文件保留在`references.json`和配套文章中；本轮只切换显示方式，不改研究结论或正文。

默认资料渲染器为共享`append_references_bibliography.py`，早先两份渲染器保持历史字节并继续作为冻结依赖。新卡按实际排版分页，每页默认5秒；修前回执、来源清单、入口及输入身份保存在本实际制作目录的`revisions/title-author/`，不重写旧验收结果。候选资料卡同在该修订目录生成，通过检查后再接入既有最终产物与回执位置；本轮进度由根任务记录。

当前冻结入口为`freeze.py`，加`--verify`只读核对。冻结清单在原有正文、声音、图标、导航和历史来源输入之外收录新渲染器，既有wrapper、发布检查器、两份旧渲染器及证据仍保留。默认正文构建、混音、并发和已有代码卡顺序均沿用实际package；本批只消费基线已验收的完整正文生成资料卡，不运行正文prepare、TTS、重渲或重混音。

本期保留`render:body=python3 ../render_stack_primer.py`的局部拼接闭环与package原字节，不换成通用voice→mix命令；栈教学与Python代码卡完整保留。

资料生成后按新回执同步最终总帧数、媒体SHA及发布映射；实际复核题名/署名、分页、首卡字幕边界、暂停及原生全屏。原脚本、配音、字幕、分镜、动作和文章/研究均保持本轮基线字节，旧技术验收只按原体保真范围复用，不预记新版已获观看认可。
