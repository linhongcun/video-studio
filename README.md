# IT小村 · 技术可视化学习站

把技术原理，一步步看明白。

IT小村用代码生成的动画短片、配套图文和可运行示例，讲清技术怎样工作、为什么这样设计，以及适用条件与取舍。`video-studio` 是学习站与内容制作系统的仓库，包含已发布内容、Remotion 动画源码、配音与媒体工具，以及资料核验、渲染和发布流程。

[进入学习站](https://linhongcun.github.io/video-studio/) · [浏览学习内容](https://linhongcun.github.io/video-studio/library/) · [搜索知识点](https://linhongcun.github.io/video-studio/search/) · [更新日志](https://linhongcun.github.io/video-studio/changelog/) · [RSS 订阅](https://linhongcun.github.io/video-studio/rss.xml)

## 学习内容

[学习内容页](https://linhongcun.github.io/video-studio/library/)集中展示系列目录与全部内容，可以按系列、知识标签筛选，并按最新发布或学习顺序排列。完整目录、发布状态和内容日期由站点读取各期元数据生成。

| 系列 | 内容方向 |
| --- | --- |
| [高并发、高可用、高性能](https://linhongcun.github.io/video-studio/series/peak/) | 限流、幂等、熔断与降级，理解流量、重复请求和服务故障的处理过程。 |
| [Agent 开发](https://linhongcun.github.io/video-studio/series/agent/) | 从已发布的 Skills 专题出发，理解 Agent 能力的组织方式与设计取舍。 |
| [LeetCode · 算法可视化](https://linhongcun.github.io/video-studio/series/leetcode/) | 从题意和方法选择依据，走到算法的完整执行过程与 Python 实现。 |
| [设计模式](https://linhongcun.github.io/video-studio/series/design-patterns/) | 从策略、观察者与适配器等模式理解职责拆分、变化隔离和对象协作，默认以 Java 展示实现。 |
| [趣味推理](https://linhongcun.github.io/video-studio/series/puzzles/) | 赛马、过桥、倒水、三门与鸡蛋掉落，用连续过程解释判断和排除的依据。 |
| [Kafka · 消息队列](https://linhongcun.github.io/video-studio/series/message-queue/) | 从 Kafka 入门到消费组与日志重放，理解记录写入、任务处理、消费者分工与重读边界。 |
| [MySQL](https://linhongcun.github.io/video-studio/series/database/) | 以 MySQL 8.4 为背景，理解 InnoDB 索引、事务、锁与单主异步复制。 |
| [Redis 系列](https://linhongcun.github.io/video-studio/series/redis/) | 从商品查询缓存与缓存一致性，深入跳表等内部机制。 |
| [分布式](https://linhongcun.github.io/video-studio/series/distributed/) | 分库分表、分布式 ID，以及事务入门、两阶段提交、TCC、Saga 和 Outbox。 |
| [计算机网络](https://linhongcun.github.io/video-studio/series/request/) | 沿网页请求理解 HTTP、HTTPS、DNS、登录态、CDN、负载均衡与浏览器缓存。 |
| [其他](https://linhongcun.github.io/video-studio/series/engineering-algorithms/) | 一致性哈希、布隆过滤器等独立专题；以后没有明确系列的内容统一归入这里。 |

各系列直接组织自己的视频与图文，可以按需要选择学习方向。系列名称与说明维护在 [`series.json`](site/src/content/series.json)，单期归属和发布信息维护在 `episodes/<slug>/meta.json`。

## 视频、图文与源码一起看

- **按问题查找**：站内搜索使用 Pagefind，检索标题、摘要与文章正文；首页展示最近发布的内容。
- **边看边读**：视频章节、文章目录与配图时间点相互连接，可以从文章或截图回到对应视频片段；代码示例支持复制。
- **核对资料**：文章中的“原文”入口可查看引用、出处与来源链接，配图支持放大；视频片尾列出参考资料原题与作者或机构。
- **查看制作过程**：每篇的“幕后”提供脚本、分镜和动画源码，链接固定到该次站点构建的 Git 提交，便于追溯对应版本。
- **在不同设备阅读**：响应式布局、中文字幕、章节操作，以及浅色、深色和跟随系统的主题模式。
- **跟进更新**：通过 RSS 订阅新内容，通过站点更新日志与 [GitHub Releases](https://github.com/linhongcun/video-studio/releases)查看版本变化。

## 系统结构

站点使用 **Astro + MDX** 构建，**Pagefind** 生成搜索索引，部署在 **GitHub Pages**。动画使用 **Remotion + React / TypeScript**，配音与媒体处理复用 Python、MiMo TTS 和 FFmpeg 工具。发布数据与制作工程分别维护，通过各期 `meta.json` 的 `sourcePath` 关联。

```text
site/
  src/pages/              首页、学习内容、系列、文章、搜索与更新日志
  src/components/         播放器、章节、原文引用、配图等共享组件
  src/content/            系列与标签配置
  scripts/                日期、资料、图文检查及媒体复制工具
episodes/
  <slug>/                 发布元数据、MDX、分镜、最终 MP4、封面与资料回执
    article/              文章配图与来源证据
  _shared/                配音、起音、混音与基础主题工具
episodes-codex/
  <slug>/                 制作文稿、配音、动画、冻结清单与修订记录
  _shared/                系列视觉模板、句级装配、冻结与渲染工具
  _template/              新期说明、图文骨架与参考资料接入片段
design/                   品牌、封面等设计素材与制作记录
docs/                     规范、手册、经验、项目记忆与历史归档
AGENTS.md                 制作与协作入口
CREDITS.md                第三方素材与署名
```

`episodes/<slug>/` 是站点发布入口；当前制作源码的位置以 `meta.json.sourcePath` 及对应工程 README 为准。音频原稿、动画工程和冻结输入保留在制作目录，构建生成的站点媒体副本不提交到仓库。

## 本地运行站点

使用 Node.js 与 npm；建议使用 Node.js 22 或 24 LTS。仓库中的 `episodes/` 发布媒体需要完整保留，站点预览使用已有成片，无需配置 TTS 密钥。

在仓库根目录执行：

```sh
npm --prefix site ci
npm --prefix site run dev
```

打开终端提示的地址，默认是 <http://localhost:4321/video-studio/>。

构建与预览：

```sh
npm --prefix site run build
npm --prefix site run preview
```

`dev` 会先检查图文并复制媒体。`build` 依次检查内容日期、参考资料与图文，再复制视频、海报和文章图片，构建 Astro 页面与 Pagefind 索引，输出到 `site/dist/`。构建入口和依赖以 [`site/package.json`](site/package.json) 与锁文件为准。

## 制作与维护

开始制作或修订前，先读 [AGENTS.md](AGENTS.md)，保护工作区并同步最新主干，再从[文档索引](docs/README.md)进入对应手册。现行规范以 [RULES.md](docs/RULES.md) 为准，完整步骤见[制作流程](docs/pipeline.md)。

1. **调研与定稿**：核对公开来源，建立 `references.json`，同步编写脚本、配套图文、发音说明与分镜；明确题意、讲解主线、前置概念和适用边界。
2. **配音与动画**：使用共享配音与时序工具，沿用对应系列的封面和正文视觉体系，先验证关键连续过程，再展开完整制作。
3. **检查与冻结**：核验资料、配音、时序、版面和动态表达，冻结实际输入并记录 SHA-256；保留旧制作稿与历史证据的原路径和字节。
4. **生成最终媒体**：按当前单期工程的入口渲染正文、适用的代码卡和参考资料附录，检查成片、字幕、章节、封面与媒体记录。
5. **接入与发布**：将通过检查的产物接入 `episodes/`，验证站点阅读、视频回看和来源链接，按发布手册完成版本、部署及线上文件核验。

新制作或重制的视频默认包含经核验的参考资料附录；配套文章包含原文引用与有效正文配图。新期从[模板说明](episodes-codex/_template/README.md)进入，渲染命令、依赖和系列模板按当前工程及[渲染手册](docs/render.md)选择。

视频制作还需要 FFmpeg / ffprobe、Python 依赖、浏览器与字体环境，具体版本见对应制作工具和单期工程。MiMo TTS 使用 `MIMO_API_KEY`，密钥按[配音手册](docs/voice.md)配置。

| 要做的事 | 入口 |
| --- | --- |
| 查规范、现行任务与授权范围 | [AGENTS.md](AGENTS.md) · [RULES.md](docs/RULES.md) |
| 开新期或重制 | [制作流程](docs/pipeline.md) · [新期模板](episodes-codex/_template/README.md) |
| 写图文、核对引用与配图 | [调研模板](docs/research-template.md) · [图文写作说明](docs/article-style.md) |
| 做配音、动画、封面与资料附录 | [配音](docs/voice.md) · [渲染](docs/render.md) · [共享制作工具](episodes-codex/_shared/README.md) |
| 质检与上线 | [校验](docs/validate.md) · [质检清单](docs/qa.md) · [发布](docs/publish.md) |
| 查已有经验和当前偏好 | [教训](docs/lessons-learned.md) · [成功经验](docs/successful-practices.md) · [项目制作记忆](docs/production-memory.md) |
| 查重制、资料补齐与站点改版记录 | [历史归档索引](docs/archive/README.md) |

## 版本与发布

站点版本记在 [`site/package.json`](site/package.json)。视频或图文内容修订升 patch；新增一期、新功能或站点改动升 minor。发布使用对应 tag 与 GitHub Release，更新日志在构建时读取 Releases；完整发版步骤见[发布手册](docs/publish.md)。

每期分别记录创建时间、最近一次实质内容修改时间和首次公开时间；更新已有内容时保留原 slug 与首发身份。历史版本和归档内容可通过发布记录与 Git 历史追溯。

GitHub 主干与站点按现行授权和质量流程发布；B站、抖音等外部平台投稿另行授权，实际播放入口以各期页面的真实平台链接为准。

## 署名与来源

音乐、配音及其他第三方素材的出处与署名见 [CREDITS.md](CREDITS.md) 和对应工程说明；技术资料的完整来源见各期文章与研究记录。
