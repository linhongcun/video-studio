# 从模板开一期

先读仓库根上的 [AGENTS.md](../../AGENTS.md)、[docs/RULES.md](../../docs/RULES.md) 和 [docs/pipeline.md](../../docs/pipeline.md)。本目录提供制作说明、待填写的资料清单和参考资料渲染脚本片段，没有完整的 Remotion 工程。

## 当前授权范围

按 [docs/RULES.md](../../docs/RULES.md) 的 STATUS 推进用户交办或已确定的选题。2026-10-24 用户已持续授权：做好并完成检查后可自主合并 GitHub 主干、发布 Release、部署 Pages，收到反馈再修改重发，无需每期等待 widget 批准。资料、动画动态复核、时序、媒体和线上完整 SHA 检查继续执行，能力限制如实记录；平台新发须另行明确授权。

## 最短路径

先按根AGENTS的“开工前同步”检查工作区并同步最新主干，记录基线、删除/移动和依赖变化，再复制现行工程。当前机的旧node_modules缓存或软链不代表删除后的工程仍可从零构建；至少在保留的当前制作目录按锁文件安装依赖，其他新期再共享该有效位置。

参考当前制作工程 `episodes-codex/db-lock/`、`episodes-codex/db-transaction/`（已认可的第二版），以及本轮各期 README。创建 `episodes-codex/<slug>/`；站点目录仍为 `episodes/<slug>/`。只复用配音、冻结和渲染基础设施，按本期主题重新设计动作，镜数与时长不照搬前一期。

新目录不继承上期的成片、资料回执、`render-result.json` 或冻结清单作为已验收产物；这些文件须由本期真实输入重新产生。新来源清单也不能继承上期的 `verified` 状态。

建立新期时在 `meta.json` 记录实际 `createdAt` 与 `updatedAt`（初始相同），首次公开再写 `publishedAt`；新时间使用含时区的 ISO 8601 值。修改既有期保留创建与首发时间，实质内容修改才刷新 `updatedAt`，对外以北京时间日期区分版本，同日多版带时分秒，不累加“重制版”名字。历史时间不补造精度，纯站点调整不改视频修改时间；完整口径见 [视频时间与版本](../../docs/publish.md#视频时间与版本)。

1. 实际读取核心公开资料，按 [docs/research-template.md](../../docs/research-template.md) 记录主张、访问日期和边界，同时建立本期 `references.json`。先确认观众需要的前置概念；术语与支线按本期范围取舍，不沿用上期的来源或已通过状态。
2. 编写 `script.md`、`article.mdx`、`pronunciation.md` 和 `visual-direction.md`；文章同步提供片尾各项的完整标题、链接和对应知识点。完成下面的资料预检后，再开始配音和昂贵的正式渲染。同一对象、渐进揭示，让动作解释因果；先做关键连续过程的小样，再展开全片。
3. 生成本期 `storyboard.json`、`covers.json` 和 `knoll-props.md`。主线收束后明确安排参考资料附录；如有完整代码卡，参考资料放在代码卡之后，每页默认5秒。结构参照 [分镜字段](../../docs/storyboard-schema.md)，画面与封面依当前 [RULES](../../docs/RULES.md)。
4. 用共享 `episodes/_shared/voice/` 的 prep、gen、build 等真实脚本生成冰糖配音、比较候选并保留 picks。按本期组装脚本写入真实句级区间，使用共享起音与 `place_v2.py --mode whole`；public/audio/voice.wav 是实体副本。ASR或听辨未执行时如实记录，不把字符兼容包络当作逐字识别，也不伪造共享自检结果。
5. 完成预检与独立动态复核，停止写入后冻结实际输入（含选中takes、共享实现、全部渲染源码，以及下述资料清单/证据/渲染入口）。在编码前后只读核对同一份清单，不把视频或生成的附录回执当作编码前输入冻结。
6. 按下面的默认入口接通 `npm run render`：资料预检 → 正文及代码卡 → 参考资料 → 最终媒体。完成完整解码、媒体指标、实际编码中间态及跨镜接续复核，另外实际查看所有资料页和原生播放器的暂停/全屏效果。记录执行者、具体范围和能力边界。
7. 将检查通过的同一份媒体、来源清单和附录回执接入站点，按实际渲染结果写入发布元数据；执行 `npm --prefix site run check:references`。新制作或重制的公开视频缺资料附录时，构建会阻止发布。文章章节、字幕及线上完整SHA仍按 [publish.md](../../docs/publish.md) 核验；平台授权范围保持原约定。

## 新期默认接入参考资料

先将 [references.example.json](references.example.json) 复制为本期 `references.json`，填写本期slug、实际核验日期、真实来源、支持论点与仓内证据路径。示例中的空字段和 `pending` 会使预检失败；只有实际读取并保存核验记录后，才能填写 `verified`。不能从上期复制一个已通过的资料清单。

在本期配套文章已有完整出处后，从仓根检查：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/your-episode
```

将 [reference-scripts.json](reference-scripts.json) 中的 `scripts` 合并到本期 `remotion/package.json`，保留本期实际的 `render:voice`、封面和类型检查命令。片段使用现有共享混音工具，输出改为 `out/body.mp4`；`render:body` 包含讲解及已有代码卡，默认 `render` 再自动生成参考资料。不要把 `render:body` 指回 `render`。

本期冻结器仍须保留全部真实正文、声音、时序和封面输入，再在其文件清单中加入以下资料生产输入（`D` 为本期目录）：

```python
ROOT = Path(__file__).resolve().parents[2]
files += [D / 'references.json', D / 'article.mdx',
          ROOT / 'episodes-codex/_shared/render_with_references.py',
          ROOT / 'episodes-codex/_shared/append_references.py',
          ROOT / 'episodes-codex/_shared/requirements-reference-appendix.txt',
          ROOT / 'site/scripts/check-references.mjs',
          ROOT / 'episodes/_shared/theme/pageTheme.ts']
for source in json.loads((D / 'references.json').read_text())['sources']:
    files.append(ROOT / source['verification']['evidence'])
```

`remotion/package.json` 也须冻结。按本期真实冻结器写入清单，停止写入后再从本期 `remotion/` 执行 `npm run render`。入口会在正文开始前检查资料与冻结，在正文后调用既有追加器；不重写原旁白、分镜或 `words.json`。Python依赖先按 `_shared/requirements-reference-appendix.txt` 安装。当前追加器用于已有16:9、至少1280×720的H.264/AAC恒定帧率工程，其他格式另做适配与检查。

渲染完成后，`video.mp4` 是包含资料附录的最终视频；本期根目录另有 `references.json`、`reference-appendix.json`、`reference-appendix-media-check.json`。`render-result.json.publicationMetadata` 给出应写入发布 `meta.json` 的 `referenceAppendix` 和 `finalVideoFrames`。接入时复制这些文件及文章，保留原创建/首发时间，按真实内容更新修改时间。不要发布 `out/body.mp4`，也不要省掉附录的元数据和回执。

```sh
python3 episodes-codex/_shared/render_with_references.py episodes-codex/your-episode --verify
npm --prefix site run check:references
```

发布检查只证明录入资料与输出身份一致，不代替原文审读或实际审片。存量豁免名单只保护引入流程时仍未补齐、媒体字节未变的旧片；新片或旧片后续重制都要带齐参考资料。

历史 EP.14 的20镜/5152帧回归输入固定在 `episodes/_shared/tests/fixtures/`，旧制作说明保留在 `docs/examples/`；不要用已更换为新片的 live 站点目录重跑旧golden。

算法题的顺序为题意→入手分析与选择依据→方法名称→完整过程→5秒Python卡→参考资料附录。独立审稿分别复述“题目要什么”与“为何选择此法”，不能把两项合成一个题意检查；无需固定先讲暴力。见L039。

原题自带楼梯等具体场景时，优先用其对象、空间和动作解释规则与推导，再把计数或程序映射回对应位置。不能把“不用无关比喻”扩大为拒绝原题场景，也不能只在数字框后放装饰图；先按L041检查真正的动作与落点。
