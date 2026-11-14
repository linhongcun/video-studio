# 从模板开一期

先读仓库根上的 [AGENTS.md](../../AGENTS.md)、[docs/RULES.md](../../docs/RULES.md) 和 [docs/pipeline.md](../../docs/pipeline.md)，再按[制作环境与跨工具接手](../../docs/production-setup.md)准备本机依赖与交接记录。制作说明使用[通用模板](../../docs/production-notes.template.md)，骨架可由 `episodes/_shared/make_production_notes.py` 生成。本目录提供制作说明、待填写的资料清单和参考资料渲染脚本片段，没有完整的 Remotion 工程。

## 当前授权范围

按 [docs/RULES.md](../../docs/RULES.md) 的 STATUS 推进用户交办或已确定的选题。2026-10-24 用户已持续授权：做好并完成检查后可自主合并 GitHub 主干、发布 Release、部署 Pages，收到反馈再修改重发，无需每期重复申请批准。资料、动画动态复核、时序、媒体和线上完整 SHA 检查继续执行，能力限制如实记录；平台新发须另行明确授权。

## 最短路径

先按根AGENTS的“开工前同步”检查工作区并同步最新主干，记录基线、删除/移动和依赖变化，再复制现行工程。当前机的旧node_modules缓存或软链不代表删除后的工程仍可从零构建；至少在保留的当前制作目录按锁文件安装依赖，其他新期再共享该有效位置。

先在 `site/src/content/series.json` 中确认有效系列键，再创建 `episodes/<series>/<slug>/production/` 与同级 `publication/`：制作文稿、配音、动画、修订及冻结输入放前者，站点发布稿、媒体和元数据放后者。在发布 `meta.json` 中填写相同的 `series`、稳定 `slug` 以及当前动画修订的实际 `sourcePath`，不要新增按工具区分的根目录。

新期的元数据与源码入口建立后，在仓根运行 `python3 scripts/check-layout.py --write-index` 更新[系列工程索引](../README.md)，再运行 `python3 scripts/check-layout.py` 检查实体目录与索引；发布前待视频、海报等交付齐全后再次检查并一同提交索引。草稿元数据按实际状态使用 `draft: true`，尚未产出的 `video`、`poster` 字段先省略，不填写不存在的媒体路径。调整系列归属时同时移动本期实体目录、更新 `meta.series` 与 `sourcePath`，并重新生成索引；部署会检查索引是否过期。

先按发布 `meta.json.sourcePath` 定位当前动画修订，再读该制作目录的 README。完整新期可参考 [LC347](../leetcode/top-k-frequent-elements/production/README.md)，按影响范围补录和复用可参考 [P09 倒推动机修订](../puzzles/pirate-gold/production/revisions/motivation-20261107/pirate-gold/README.md)。共享工具与模板统一使用 `episodes/_shared/`、`episodes/_template/`。只复用配音、冻结和渲染基础设施，按本期主题重新设计动作，镜数、时长、机器专属路径与已验收状态不照搬前一期；系列视觉入口仍按下方对应模板选择。

现有工程已按用户授权实体迁移，旧清单、来源JSON、QA和回执保留原字节，旧路径通过[迁移记录](../../docs/archive/2026-11/episode-layout/README.md)及固定基线 `28dfb2fa` 追溯。复制的旧冻结清单不能证明已适配新路径的源码；新期或后续重渲必须冻结本期当前实际输入，不把目录整理当作重新制作验收。

新目录不继承上期的成片、资料回执、`render-result.json` 或冻结清单作为已验收产物；这些文件须由本期真实输入重新产生。新来源清单也不能继承上期的 `verified` 状态。

建立新期时在 `meta.json` 记录实际 `createdAt` 与 `updatedAt`（初始相同），首次公开再写 `publishedAt`；新时间使用含时区的 ISO 8601 值。修改既有期保留创建与首发时间，实质内容修改才刷新 `updatedAt`，对外以北京时间日期区分版本，同日多版带时分秒，不累加“重制版”名字。历史时间不补造精度，纯站点调整不改视频修改时间；完整口径见 [视频时间与版本](../../docs/publish.md#视频时间与版本)。

1. 实际读取核心公开资料，按 [docs/research-template.md](../../docs/research-template.md) 记录原始题名、题名证据、主张、访问日期和边界，同时建立 `presentation: title-author` 的本期 `references.json`。核对公开作者或维护机构；明确个人署名填非空 `author`，否则省略并用 `organization`。原文摘录留图文/研究，不上视频，不用概括或译文冒充原题。先确认观众需要的前置概念；术语与支线按本期范围取舍，不沿用上期的来源或已通过状态。
2. 编写 `script.md`、`article.mdx`、`pronunciation.md` 和 `visual-direction.md`；文章先按下方「配套图文起稿与接入」定提纲，再展开正文，同步提供片尾各项的完整标题、链接和对应知识点。文稿定稿时完成结构审读，资料预检通过后再开始配音和昂贵的正式渲染。同一对象、渐进揭示，让动作解释因果；先做关键连续过程的小样，再展开全片。
3. 生成本期 `storyboard.json`、`covers.json` 和制作说明（`knoll-props.md` 是现有工具兼容文件名，不代表特定角色）。主线收束后明确安排原题与作者/机构的参考资料简表；如有完整代码卡，参考资料放在代码卡之后，每页最多4项、默认5秒。结构参照 [分镜字段](../../docs/storyboard-schema.md)，画面与封面依当前 [RULES](../../docs/RULES.md)。
   LeetCode新题封面默认沿用已认可的[共享系列模板](../_shared/leetcode-covers/README.md)：按本题元数据扩展catalog和对应题图，统一生成并检查三比例，不从旧期复制另一套封面样式。趣味推理使用[本系列共享模板](../_shared/puzzles-covers/README.md)，按同一规则扩展题图。MySQL使用[本系列共享模板](../_shared/mysql-covers/README.md)，以真实EP和本片机制扩展单集封面。设计模式使用[本系列共享模板](../_shared/design-pattern-covers/README.md)，核对D编号、EP和职责关系，沿同一布局扩展。Kafka消息队列使用[共享模板](../_shared/kafka-covers/README.md)，MQ号取规划索引，正文与封面共用不可变style-v1，参考资料走[Kafka同色入口](../_shared/kafka-video/README.md)。Redis封面使用[本系列共享模板](../_shared/redis-covers-v2/README.md)，核对真实EP与完整题名，按单集机制扩展，保留旧冻结源。高并发、高可用、高性能使用[本系列共享模板](../_shared/peak-covers/README.md)，以真实EP、完整原问题和单集机制图扩展三比例。
4. 用共享 `episodes/_shared/voice/` 的 prep、gen、build 等真实脚本生成冰糖配音、比较候选并保留 picks。按本期组装脚本写入真实句级区间，使用共享起音与 `place_v2.py --mode whole`；public/audio/voice.wav 是实体副本。ASR或听辨未执行时如实记录，不把字符兼容包络当作逐字识别，也不伪造共享自检结果。
5. 完成预检与独立动态复核，停止写入后冻结实际输入（含选中takes、共享实现、全部渲染源码，以及下述资料清单/证据/渲染入口）。在编码前后只读核对同一份清单，不把视频或生成的附录回执当作编码前输入冻结。
6. 按下面的默认入口接通 `npm run render`：资料预检 → 正文及代码卡 → 参考资料 → 最终媒体。完成完整解码、媒体指标、实际编码中间态及跨镜接续复核，另外实际查看所有资料页和原生播放器的暂停/全屏效果。记录执行者、具体范围和能力边界。
7. 将检查通过的同一份媒体、来源清单和附录回执接入站点，按实际渲染结果写入发布元数据；执行 `npm --prefix site run check:references` 和 `npm --prefix site run check:articles`，实际复核引用支持关系、图片信息价值、手机/桌面阅读、回看和原图入口。新制作或重制的公开视频缺资料附录时，构建会阻止发布。文章章节、字幕及线上完整SHA仍按 [publish.md](../../docs/publish.md) 核验；平台授权范围保持原约定。

## 配套图文起稿与接入

先在已有研究、制作记录或模板注释中确定目标读者、必要前提、核心问题、贯穿示例、预期判断及深入内容，无需另建必交文档。按[阅读结构](../../docs/article-style.md#阅读结构)组织问题开场、可见方向、同例推导、图文代码对照、深入分层与结尾收束；根据题材重写标题和安排层级，不套固定章数或篇幅。文章应独立读懂，关键依据与条件留主线，代码有用途和结果解释；详略与段落、列表、表格的选择见[写作说明](../../docs/article-style.md#详略与排版)。

冻结前按[文稿定稿审读](../../docs/qa.md#文稿定稿审读冻结前)确认开头与小结回答同一问题、每步推导能由文内信息接上，再冻结制作稿。发布前复核实际页面的目录、手机排版、引用、图片和回看；文章独有标题不写成不存在的视频章节或时码。

从 [article.mdx](article.mdx) 复制骨架，按 [图文写作说明](../../docs/article-style.md) 替换所有占位内容。调研时核对原文、位置和对应论点，文稿中放置 `SourceQuote`；编码前按已定分镜时序写好并启用 `Figure` 图位（路径、预定秒数、章节、图注和alt），随文章、已有文章独有来源和实读证据一起冻结；最终媒体生成后只生成并核验截图，不把尚未生成的图记为已验收。实际选图需改时间或文稿时，保留冻结制作稿，只做记录前后SHA及差异的站点发布派生稿；新增来源、证据和图片也记录各自SHA。至少一处核心原文与一幅有效配图，发布前运行 `npm --prefix site run check:articles` 并实际复核阅读和回看操作。文章独有来源可存 `article-sources.json`，随发布稿和 `article/` 图片、证据一起接入 `episodes/<series>/<slug>/publication/`。

`SourceQuote` 的写法与来源数据保持不变，后续新期自动共享段末「原文」入口和按需浮层，不逐篇另写交互。默认折叠仍须通过真实调用与原文证据检查；实际查看桌面悬停/点击、手机点按、键盘及关闭操作、长面板与来源链接，边界和降级要求见 [写作说明](../../docs/article-style.md#接入与验收)。

## 新期默认接入参考资料

先将 [references.example.json](references.example.json) 复制为本期 `references.json`，填写本期slug、实际核验日期、真实来源、文档原始 `title`、`titleEvidence: {locator, evidence}`、`organization`、内部支持论点与仓内证据路径。有明确公开个人署名时另加非空字符串 `author`，没有时省略；不得用空值占位，也不从Git提交者或维护账号推断作者。署名依据保留于关联核验记录。`presentation` 使用 `title-author`，不填写 `displayTitle` 或 `displaySupport`。示例中的空字段和 `pending` 会使预检失败；只有实际读取并保存核验记录后，才能填写 `verified`。不能从上期复制一个已通过的资料清单。

片尾只显示原题与作者/机构，采用简洁列表，不显示摘录、位置、年份/版本、核验日期、链接、暂停提示或其他卡片说明。完整出处和实际原文保留于文章或研究，需要时可在source保留 `quotation: {text, locator, evidence}`，但它不上视频；`text` 仍须为连续原文，位置与证据齐全，不改词、拼接或添加省略。译文与解释在文章中分别标「译文」「编者说明」，内部 `supports` 也不上屏。

在本期配套文章已有完整出处后，从仓根检查：

```sh
node site/scripts/check-references.mjs --sources episodes/request/your-episode/production
```

将 [reference-scripts.json](reference-scripts.json) 中的 `scripts` 合并到本期 `remotion/package.json`，保留本期实际的 `render:voice`、封面和类型检查命令。片段使用现有共享混音工具，输出改为 `out/body.mp4`；`render:body` 包含讲解及已有代码卡，默认 `render` 再自动生成参考资料。不要把 `render:body` 指回 `render`。

本期冻结器仍须保留全部真实正文、声音、时序和封面输入，再在其文件清单中加入以下资料生产输入（`D` 为本期目录）：

```python
ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'AGENTS.md').is_file() and (p / 'site/package.json').is_file())
files += [D / 'references.json', D / 'article.mdx',
          ROOT / 'episodes/_shared/episode_paths.py',
          ROOT / 'episodes/_shared/render_with_references.py',
          ROOT / 'episodes/_shared/append_references_bibliography.py',
          ROOT / 'episodes/_shared/append_references_original.py',
          ROOT / 'episodes/_shared/append_references.py',
          ROOT / 'episodes/_shared/requirements-reference-appendix.txt',
          ROOT / 'site/scripts/check-references.mjs',
          ROOT / 'site/scripts/episode-paths.mjs',
          ROOT / 'episodes/_shared/theme/pageTheme.ts']
for source in json.loads((D / 'references.json').read_text())['sources']:
    files.append(ROOT / source['verification']['evidence'])
    files.append(ROOT / source['titleEvidence']['evidence'])
    if source.get('quotation'):
        files.append(ROOT / source['quotation']['evidence'])
article_sources = D / 'article-sources.json'
if article_sources.exists():
    files.append(article_sources)
    for source in json.loads(article_sources.read_text())['sources']:
        files.append(ROOT / source['verification']['evidence'])
        files.append(ROOT / source['quotation']['evidence'])
        if source.get('titleEvidence'):
            files.append(ROOT / source['titleEvidence']['evidence'])
```

`remotion/package.json` 也须冻结。按本期真实冻结器写入清单，停止写入后再从本期 `remotion/` 执行 `npm run render`。入口会在正文开始前检查资料与冻结，在正文后调用 `append_references_bibliography.py`；它通过保留的两个旧追加器完成媒体操作，不修改旧文件字节，也不重写原旁白、分镜或 `words.json`。Python依赖先按 `_shared/requirements-reference-appendix.txt` 安装。新模式每页最多4项、默认5秒，原题和署名溢出会报COPYFIT，不能靠截断、缩写题名或杜撰作者过关。当前追加器用于已有16:9、至少1280×720的H.264/AAC恒定帧率工程，其他格式另做适配与检查。

渲染完成后，`video.mp4` 是包含资料附录的最终视频；本期根目录另有 `references.json`、`reference-appendix.json`、`reference-appendix-media-check.json`。新回执的 `bibliography` 记录实际显示的 `title` 与 `credit`，`layout` 为单列且只渲染这两项，`quotesRendered` 为false；每页5秒记在 `inputs.secondsPerPage`。`render-result.json.publicationMetadata` 给出应写入发布 `meta.json` 的 `referenceAppendix` 和 `finalVideoFrames`。接入时复制这些文件及文章，保留原创建/首发时间，按真实内容更新修改时间。不要发布 `out/body.mp4`，也不要省掉附录的元数据和回执。

```sh
python3 episodes/_shared/render_with_references.py episodes/request/your-episode/production --verify
npm --prefix site run check:references
npm --prefix site run check:articles
```

发布检查只证明录入资料与输出身份一致，不代替原文审读或实际审片。存量豁免名单只保护引入流程时仍未补齐、媒体字节未变的旧片；新片或旧片后续重制都要带齐参考资料。

历史 EP.14 的20镜/5152帧回归输入固定在 `episodes/_shared/tests/fixtures/`，旧制作说明保留在 `docs/examples/`；不要用已更换为新片的 live 站点目录重跑旧golden。

算法题的顺序为题意→入手分析与选择依据→方法名称→完整过程→5秒Python卡→参考资料附录。独立审稿分别复述“题目要什么”与“为何选择此法”，不能把两项合成一个题意检查；无需固定先讲暴力。见L039。

原题自带楼梯等具体场景时，优先用其对象、空间和动作解释规则与推导，再把计数或程序映射回对应位置。不能把“不用无关比喻”扩大为拒绝原题场景，也不能只在数字框后放装饰图；先按L041检查真正的动作与落点。
