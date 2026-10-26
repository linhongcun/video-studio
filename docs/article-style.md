# 图文写作说明

规范以 [RULES 的配套图文](RULES.md#配套图文) 为准。本文说明如何在现有站点落实；起稿用 [article.mdx 模板](../episodes-codex/_template/article.mdx)。

## 阅读结构

开头用一两段说明问题、教学示例与主线，随后按机制或推导分节，必要时解释限制和失败情景，末尾回顾，最后列「参考资料」。保留原有章节锚点；完整程序、证明与拓展有需要就保留，不要求同篇幅、同章数。文章应当能够独立阅读，少用制作流程提示和夸张评价。

统一使用站点标题、正文、代码、提示、引用和图注样式。`Callout` 用于提示或边界，`SourceQuote` 用于真正的外部原文，避免把作者自己的提醒显示成来源证据。

## 就近放置精确引用

先阅读原文，选取足以支持当前论点的连续语段，核对上下文、题名、署名、位置与适用版本。文稿中直接写：

```mdx
<SourceQuote sourceId="R1" supports="说明这段原文实际支持的具体论点，保留必要条件。" />
```

组件从同一期 `references.json` 读取原文与出处，不必在MDX重复抄写。若文章需要的视频外来源，新增 `article-sources.json`，与视频资料合并读取，id 使用 `A1` 等避免重名：

```json
{
  "schemaVersion": 1,
  "episode": "your-episode",
  "sources": [{
    "id": "A1",
    "organization": "实际发布机构",
    "title": "实际文档原题",
    "version": "实际版本，未标时说明未标",
    "url": "https://example.org/source",
    "supports": ["实际支持的具体论点"],
    "verification": {
      "status": "verified",
      "checkedAt": "实际阅读日期",
      "evidence": "episodes/your-episode/article/source-evidence.md"
    },
    "quotation": {
      "text": "从实读文档复制的连续原文",
      "locator": "真实小标题、段落或页码",
      "evidence": "episodes/your-episode/article/source-evidence.md"
    }
  }]
}
```

以上只是字段示例，不能作为真实来源发布。证据文件应保存实读原文及必要上下文、公开URL、实际读取日期；不能把 `supports`、搜索摘要、旧中文核验概括当作原句。固定版本链接可写 `verification.sourceUrl`。核验补充来源的机构、原题和署名，有明确个人署名才填写 `author`。引用旧证据保留历史访问日期，新增来源用本轮实际阅读日期；无需为了更换卡片样式重新访问不变的原文。

可用 `translation="……"` 附译文。原文不会因译文或编者解释而改写。短引只支持其中实际写出的部分：题意可说明输入与限制，不能代替算法正确性证明；教学假设不能冒充真实系统记录。

## 配图和回看

优先复用清楚的正文示意图，或从最终视频提取与邻近文字一致的关键状态。选择动作已完成、标注可读的时刻，避免空白、淡入淡出和片尾资料页。示例命令中的时间、路径都须按本期实际替换：

```sh
mkdir -p episodes/your-episode/article
ffmpeg -ss 42.5 -i episodes/your-episode/video.mp4 -frames:v 1 -q:v 2 episodes/your-episode/article/01.jpg
```

```mdx
<Figure src="/video-studio/episodes/your-episode/article/01.jpg"
  alt="图中关键对象、状态和关系的准确描述"
  caption="教学示例：解释这一状态说明什么。"
  seekTo={42.5} chapter="existing-chapter-id" />
```

必须实际查看抽出的图片；图注解释图意，时间链接负责回看；图片和「查看大图」链接可打开原图，方便手机放大查看细节。自制示意图用 `figure` / `figcaption` 包裹，SVG有 `aria-label` 或 `title`，注明「示意图」以及必要的数据来源。外部图片保留来源及使用依据，不把生成图伪装成截图。所有图紧邻相关解释，宽度、留白和图注复用站点样式。

## 冻结与成片后配图

制作目录的 `article.mdx` 是编码前冻结输入。分镜和时序定稿后，先写好并启用 `Figure` 的图片路径、预定秒数、章节、图注及alt，随文章一起冻结；此时图片文件可以尚未生成，不能标记为已经看图验收。冻结前已有的 `article-sources.json` 及其原文/核验依据也纳入本期实际输入清单，因为MDX中的sourceId并不包含真正引文内容。

成片后按预定图位生成截图、实际查看并核对图意与回看时间，只增加图片文件，不修改冻结制作稿。若实际选图需要更换时间、图注或其他文稿内容，保留原制作稿和冻结清单，另存站点发布派生稿，再接入 `episodes/<slug>/article.mdx`；本期记录写明制作稿SHA、发布稿SHA、实际差异与原因。成片后新增或调整的文章来源、证据和图片也保存各文件SHA，不追认为原编码输入。来源更正若影响视频内容，应按实际影响返工视频，不能只改图文记录。

## 接入与验收

最终媒体产生后补图，将发布稿、文章独有资料JSON及 `article/` 中图片与证据接入 `episodes/<slug>/`。运行：

```sh
npm --prefix site run check:articles
npm --prefix site run build
```

机器检查确认引用确实用于正文、短引和本地证据一致、出处字段与图片齐全。编辑再确认论点支持关系、上下文与图意；浏览器分别查看桌面/手机、亮暗主题，确认图片清楚、长英文可换行、原始链接和截图时间可操作。至少一处引用与一幅图是最低线，不能代替对正文质量的判断。

修改存量站点文章时记录前后全文SHA和改动范围，制作目录的冻结文章、已编码媒体、旧回执及旧冻结清单保留。站点衍生稿不是对旧渲染输入的追认；不为新增图文重渲未变视频。修改了配套讲解内容时按 [时间与版本口径](publish.md#视频时间与版本) 维护当前更新时间，保留创建和首发时间。
