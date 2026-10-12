# Video Studio 科普站 UI 设计稿 v0.2.0

> 作者：Hayao Miyazaki（分镜/UI）｜依据：site-plan.md、episodes/http-request/article.mdx、http-request/storyboard.json、docs/index.html（v0.1 作品页）
> 原则：延续片中深色科技风；**视频是入口，图文是主体**；内容优先、组件少而稳，便于 Astro + MDX 落地。

---

## 1. 设计令牌（Design Tokens）

以 CSS 变量形式落在 `src/styles/tokens.css`，组件只引用变量，不写裸色值。

### 1.1 颜色

| 变量 | 值 | 语义用途 |
|---|---|---|
| `--c-bg` | `#0B1020` | 页面底色（与片子背景一致） |
| `--c-surface` | `#111827` | 卡片、导航、代码块、播放器外框（片中 panel） |
| `--c-surface-2` | `#1F2937` | 悬停态卡片、chip 底、表格斑马纹 |
| `--c-border` | `#243045` | 1px 分隔线、卡片描边 |
| `--c-text` | `#E5E7EB` | 正文、标题 |
| `--c-text-2` | `#9CA3AF` | 次要文字：简介、元信息、页脚、时间戳 |
| `--c-muted` | `#6B7280` | **仅用于装饰/禁用态/图标线条**，不承载需要阅读的文字 |
| `--c-primary` | `#22D3EE` | 品牌主色：链接、当前章节高亮、焦点环、主按钮底 |
| `--c-secondary` | `#3B82F6` | 次级强调：标签 chip、请求方向箭头、信息类 Callout |
| `--c-success` | `#22C55E` | 成功/状态码 2xx、提示类 Callout |
| `--c-accent` | `#F59E0B` | 警示/注意类 Callout、“新”角标 |
| `--c-danger` | `#F87171` | 错误类 Callout、4xx/5xx 状态码 |
| `--c-on-primary` | `#0B1020` | 主色按钮上的文字 |

**对比度（WCAG 2.1 AA：正文 ≥ 4.5:1，大字/UI 部件 ≥ 3:1），均以 `--c-bg #0B1020` 为底估算：**

| 前景 | 对比度 | 结论 |
|---|---|---|
| text `#E5E7EB` | ≈ 15.6:1 | AAA |
| text-2 `#9CA3AF` | ≈ 7.6:1 | AAA，可做次要正文 |
| muted `#6B7280` | ≈ 3.9:1 | **不足 4.5，禁止用于正文**；可用于图标/边框（≥3:1） |
| primary `#22D3EE` | ≈ 11:1 | 链接、小字均可 |
| secondary `#3B82F6` | ≈ 5.0:1 | 正文可用（AA），在 surface 上 ≈ 4.6:1 仍过线 |
| success `#22C55E` | ≈ 8.3:1 | OK |
| accent `#F59E0B` | ≈ 9.4:1 | OK |
| on-primary `#0B1020` 置于 `#22D3EE` | ≈ 11:1 | 主按钮 OK |

- 链接除颜色外加下划线（hover 时加粗下划线），不只靠颜色区分。
- 当前章节高亮 = 主色左边框/底色 + 粗体 + `aria-current`，不只靠颜色。

### 1.2 字体栈

```css
--font-sans: system-ui, -apple-system, "PingFang SC", "Hiragino Sans GB",
             "Noto Sans SC", "Microsoft YaHei", "Segoe UI", Roboto, sans-serif;
--font-mono: ui-monospace, "JetBrains Mono", "SF Mono", Menlo, Consolas,
             "Noto Sans Mono CJK SC", monospace;
```
- 不强制加载 Web 字体（中文字体包太大）；系统字体优先，Noto Sans SC 作为 Linux/安卓兜底。
- 数字（时长、期号、时间戳）使用 `font-variant-numeric: tabular-nums`。

### 1.3 字号阶梯（基准 16px，比例约 1.25）

| 令牌 | 桌面 | 手机 ≤767 | 行高 | 用途 |
|---|---|---|---|---|
| `--fs-display` | 48px | 32px | 1.2 | 首页 Hero 标题 |
| `--fs-h1` | 36px | 28px | 1.25 | 单期页标题 |
| `--fs-h2` | 28px | 22px | 1.35 | 正文章节标题 |
| `--fs-h3` | 22px | 19px | 1.4 | 小节、卡片标题 |
| `--fs-body` | 17px | 16px | 1.8 | 正文（中文行高放宽） |
| `--fs-small` | 14px | 14px | 1.6 | 简介、元信息、chip |
| `--fs-xs` | 12px | 12px | 1.5 | 角标、时长徽章 |
| `--fs-code` | 14px | 13px | 1.65 | 代码块 |

字重：400 正文 / 600 标题与强调 / 700 Hero。

### 1.4 间距（4px 基准）

`--sp-1:4px --sp-2:8px --sp-3:12px --sp-4:16px --sp-5:24px --sp-6:32px --sp-7:48px --sp-8:64px --sp-9:96px`
- 页面左右边距：手机 16、平板 24、桌面 32。
- 正文段间距 `--sp-4`；章节之间 `--sp-8`；首页区块之间 `--sp-9`（手机 `--sp-7`）。

### 1.5 圆角

`--r-sm:6px`（chip、按钮、行内代码）`--r-md:10px`（代码块、Callout）`--r-lg:16px`（卡片、播放器）`--r-full:999px`（标签 pill、头像）

### 1.6 阴影 / 光晕

```css
--shadow-1: 0 1px 2px rgba(0,0,0,.4);
--shadow-2: 0 8px 24px rgba(0,0,0,.45);              /* 卡片 hover */
--glow-primary: 0 0 0 1px rgba(34,211,238,.35), 0 0 24px rgba(34,211,238,.15); /* 当前章节/焦点卡片 */
--focus-ring: 0 0 0 2px var(--c-bg), 0 0 0 4px var(--c-primary);
```
深色底上阴影弱，层级主要靠 `surface` 明度 + 描边 + 主色光晕表达。

### 1.7 断点与容器

| 名称 | 媒体查询 | 典型设备 | 容器宽 |
|---|---|---|---|
| mobile | `< 768px`（设计基准 390） | 手机 | 100% − 32 |
| tablet | `≥ 768px` | 平板竖屏 | 100% − 48 |
| desktop | `≥ 1280px` | 笔记本 | 1200px |
| wide | `≥ 1440px` | 大屏 | 1320px |

- 正文阅读宽 `--measure: 720px`（约 40 个汉字一行）。
- 动效：`--dur-fast:120ms --dur:200ms --ease: cubic-bezier(.2,.8,.2,1)`。

---

## 2. 首页 `/`

### 2.1 线框（桌面 1280）

```
┌──────────────────────────────────────────────────────────────────┐
│ ▣ Video Studio      期数   专题▾   关于            [GitHub ↗]     │ ← SiteHeader 64px 吸顶
├──────────────────────────────────────────────────────────────────┤
│  HERO（最新一期）                                                  │
│ ┌───────────────────────────────┐  EP.01 · 网络基础 · 0:33       │
│ │                               │  一次 HTTP 请求是如何完成的？   │
│ │       poster.jpg  16:9        │  半分钟看懂一次 HTTP 请求……     │
│ │            ( ▶ )              │  [▶ 看视频 + 图文]  [源码 ↗]    │
│ └───────────────────────────────┘                                 │
├──────────────────────────────────────────────────────────────────┤
│ 全部期数                                                          │
│ [全部] [网络基础] [前端] [后端] [数据库] …        ← TagFilter     │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               │
│ │ poster  0:33 │ │ poster  1:02 │ │ poster  0:45 │  ← 3 列       │
│ │ EP.01        │ │ EP.02        │ │ EP.03        │               │
│ │ 标题两行截断 │ │ 标题         │ │ 标题         │               │
│ │ 简介两行截断 │ │ 简介         │ │ 简介         │               │
│ │ #网络基础    │ │ #前端        │ │ #后端        │               │
│ └──────────────┘ └──────────────┘ └──────────────┘               │
├──────────────────────────────────────────────────────────────────┤
│ Video Studio · 用代码拍科普 │ GitHub · RSS · 关于 │ v0.2.0 © 2026 │ ← SiteFooter
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 规格
- **SiteHeader**：高 64（手机 56），`surface` 半透明 + `backdrop-filter: blur(8px)`，底 1px border。Logo 左，导航居中/右，当前页链接主色 + 2px 底线。手机折叠为汉堡按钮 → 全屏抽屉。
- **Hero**：桌面左右 7:5 两栏；平板/手机上下堆叠。封面 16:9、`--r-lg`，中央 64px 圆形播放图标（主色描边）。点击封面或主按钮进入单期页（不在首页播放，避免重复加载 mp4）。背景可加极淡的主色径向渐变。
- **EpisodeCard**：整卡为单个 `<a>`。封面 16:9 `loading="lazy"`，右下角时长徽章（`rgba(11,16,32,.8)` 底 + `--fs-xs`）；期号 `EP.01` 主色等宽小字；标题 `--fs-h3` 两行截断；简介 `text-2` 两行截断；底部标签 pill（最多 3 个）。
- **网格**：`grid-template-columns: repeat(3,1fr)`（≥1280）/ 2 列（768–1279）/ 1 列（<768），gap 24（手机 16）。
- **TagFilter**：横向 pill 组，选中 = 主色底 + `on-primary` 字；客户端过滤（React 岛或原生 JS），同时同步到 URL `?tag=前端`；无 JS 时每个 pill 退化为跳转 `/tags/<tag>/` 的链接。手机端横向滚动。过滤结果为空显示 EmptyState“这个标签还没有片子”。
- **SiteFooter**：三段式，`text-2` 小字；版本号读 package.json。

---

## 3. 单期页 `/episodes/<slug>/`

### 3.1 线框（桌面 1280）

```
┌──────────────────────────────────────────────────────────────────┐
│ SiteHeader                                                        │
├──────────────────────────────────────────────────────────────────┤
│ 首页 / 网络基础 / EP.01                        ← Breadcrumb       │
│ 一次 HTTP 请求是如何完成的？                   ← h1              │
│ 2026-10-12 · 0:33 · #网络基础 #HTTP                               │
│ ┌──────────────────────────────────────┐ ┌─────────────────────┐ │
│ │                                      │ │ 章节                │ │
│ │          <video> 16:9                │ │▌0:00 按下回车之后   │ │← 当前高亮
│ │          poster=开场问号帧            │ │ 0:04 浏览器发出请求 │ │
│ │                                      │ │ 0:11 服务器处理请求 │ │
│ │ ▶ ━━━━━●━━━━━━━━━━  0:05 / 0:33  ⛶   │ │ 0:17 服务器返回响应 │ │
│ └──────────────────────────────────────┘ │ 0:24 浏览器画出页面 │ │
│        （8 列）                           └─────────────────────┘ │
│                                             （4 列，与视频等高）  │
├──────────────────────────────────────────────────────────────────┤
│              ┌──────────── 720px ────────────┐   ┌──────────┐    │
│              │ 导语段落……                     │   │ 本页目录 │    │← ≥1440 才显示
│              │ ┌ Callout(info) ────────────┐  │   │ · 1 …    │    │
│              │ │ ℹ 本文不展开 DNS/TCP/TLS │  │   │ · 2 …    │    │
│              │ └──────────────────────────┘  │   └──────────┘    │
│              │ ## 1. 按下回车之后  [▶ 从这里看]│                   │
│              │ ┌ Figure ──────────────────┐  │                   │
│              │ │   图 / 帧截图            │  │                   │
│              │ └ 图1 地址栏与问号 ────────┘  │                   │
│              │ 正文……                         │                   │
│              │ ## 2. 浏览器发出请求 [▶ 从这里看]│                  │
│              │ ┌ CodeBlock  HTTP · 请求 [复制]┐│                   │
│              │ │ GET /index.html HTTP/1.1    ││                   │
│              │ │ Host: example.com           ││                   │
│              │ └─────────────────────────────┘│                   │
│              │ …… 3 / 4 / 5 ……                │                   │
│              │ ┌ Summary 小结 ───────────────┐│                   │
│              │ │ ✓ 要点1  ✓ 要点2  ✓ 要点3  ││                   │
│              │ └─────────────────────────────┘│                   │
│              │ 幕后  [📄 脚本] [🎞 分镜] [</> 源码]│                │
│              │ ┌ ← 上一期 ─────┐┌─── 下一期 → ┐│                   │
│              │ └───────────────┘└─────────────┘│                   │
│              └────────────────────────────────┘                   │
├──────────────────────────────────────────────────────────────────┤
│ SiteFooter                                                        │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 视频区：VideoPlayer + ChapterList
- 使用原生 `<video controls preload="metadata" playsinline poster>`，保证全浏览器可播、零依赖；章节逻辑为一个 React 岛（`client:visible`）。
- 布局：桌面 `grid 8fr 4fr`，章节面板与视频等高、内部可滚动；平板/手机章节移到视频下方（见 §5）。
- **章节项**：`时间戳(等宽, text-2) + 标题`，高 44+（触控目标）。点击 → `video.currentTime = start; video.play()`，并 `history.replaceState` 写入 `#t=11`。
- **高亮**：监听 `timeupdate`，当前章节 = 最后一个 `start ≤ currentTime` 的章节；样式 = 3px 主色左边框 + `surface-2` 底 + 600 字重 + `aria-current="true"`；项内可显示进度细条（当前章节已播放比例，主色 2px）。
- 同步高亮正文：当前章节对应的 `h2` 旁按钮变为“▶ 正在播放”（不自动滚动正文，避免打断阅读）。
- **深链**：URL `?t=17` 或 `#t=17` 进入时自动定位；`#request` 等正文锚点只滚动正文。
- 章节数据单一来源：article.mdx frontmatter `chapters`（id/title/start），由 meta 构建期注入；制作按实际渲染时间校准 start。

### 3.3 图文正文（ArticleBody）
- 容器 `max-width: var(--measure)` 居中；正文 `--fs-body` / 行高 1.8；段落 `text`；行内代码 `surface-2` 底 `--r-sm`，主色字。
- **章节标题 ChapterHeading**：`<h2 id="request">` 与 frontmatter id 一一对应；左侧序号主色；右侧 `▶ 从这里看` 小按钮（ghost 样式，主色描边，`--fs-small`）。点击 → 滚动到播放器（`scrollIntoView({block:'start'})`，手机吸顶时无需滚动）并跳转播放。标题 hover 时出现 `#` 复制锚点链接。
- `scroll-margin-top: 80px`（手机有吸顶视频时 = 视频高 + 16）。
- 宽屏 ≥1440 右侧可显示“本页目录”TOC，滚动联动；<1440 隐藏。

### 3.4 内容组件规范
**CodeBlock / 报文**
- `surface` 底、1px border、`--r-md`，内边距 16；顶部条：语言/标题（如“HTTP · 请求”）+ 复制按钮（复制后变“已复制 ✓” 2s，`aria-live="polite"`）。
- 等宽 `--fs-code`；横向溢出 `overflow-x:auto`，不折行（报文格式不应被折断）；可选行号。
- **HTTP 报文高亮**：方法（GET/POST）= secondary；路径 = text；协议版本 = text-2；状态码 2xx = success、3xx = secondary、4xx/5xx = danger；头字段名 = primary，值 = text；空行用淡色 `↵` 标出（教学意义：头与体的分隔）。由 Shiki 自定义主题实现，构建期着色、零运行时。
- 可选 `variant="request|response"`：左侧 3px 色条（请求 secondary / 响应 success），呼应片中左右箭头。

**Figure**
- `<figure>`：图片 `--r-md`、1px border、宽 100% 阅读宽；可选 `wide` 超出到 960px。图注 `figcaption` `text-2` `--fs-small` 居中，前缀“图 N”。
- 必填 `alt`；`loading="lazy"`、显式 width/height 防布局抖动。
- 可选 `frame` 属性：直接引用片中帧（如 `frames/frame_0500_server_fixed.png`），并带“▶ 在视频中查看 0:11”链接 → 跳转播放。

**Callout**
- 类型 `info`(secondary) / `tip`(success) / `warn`(accent) / `danger`(danger)：左 3px 色条 + 该色 10% 透明底 + 图标 + 可选标题；正文仍用 `text` 色保证对比度。`role="note"`。
- 文中 `>` 引用默认渲染为 `info` Callout。

**Steps**（可选）：带序号圆点的竖向步骤，用于“浏览器为每个资源再发请求”这类流程。

### 3.5 小结 Summary
- `surface` 卡片 + 顶部主色 2px 线；标题“小结”；列表项前用 success 色 ✓ 图标；之后是“动手试试”引导（tip Callout：打开开发者工具 → 网络面板）。

### 3.6 幕后链接 BehindTheScenes
- 三个等宽按钮卡片（桌面一行 3 个、手机竖排）：📄 脚本 script.md / 🎞 分镜 storyboard.json / `</>` 源码 remotion/；链接指向 GitHub 对应路径，外链加 ↗ 与 `rel="noopener"`。可附一行“这部片子完全由代码生成”。

### 3.7 上一期 / 下一期 EpisodePager
- 两栏卡片：左“← 上一期 + 标题”，右“下一期 → + 标题”（右对齐）；不存在时该位置留空占位（保持布局）。手机端上下堆叠。按发布日期排序。

---

## 4. 标签专题页 `/tags/<tag>/`（及 `/tags/` 总览）

```
┌──────────────────────────────────────────────────────────┐
│ SiteHeader                                                │
├──────────────────────────────────────────────────────────┤
│ 首页 / 专题                                               │
│ #网络基础                                   共 3 期       │
│ 从一次请求出发，看懂浏览器与服务器怎么对话。 ← 专题简介   │
│ 其他专题：[前端] [后端] [数据库]                          │
├──────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐                   │
│ │ Card     │ │ Card     │ │ Card     │ ← 同首页网格       │
│ └──────────┘ └──────────┘ └──────────┘                   │
│ （可选）推荐观看顺序：1 → 2 → 3                           │
├──────────────────────────────────────────────────────────┤
│ SiteFooter                                                │
└──────────────────────────────────────────────────────────┘
```
- 专题元数据（标题、简介、排序）放 `src/content/tags.json`；未配置的标签用默认文案。
- `/tags/` 总览：每个专题一张宽卡（名称、简介、期数、最近 3 期小封面）。
- 列表默认按“推荐顺序”（若配置）否则按发布时间倒序。

---

## 5. 手机版（基准 390）

### 5.1 首页
```
┌──────────────────────┐
│ ▣ Video Studio    ☰  │ 56px
├──────────────────────┤
│ ┌──────────────────┐ │
│ │ poster 16:9  ▶   │ │
│ └──────────────────┘ │
│ EP.01 · 0:33         │
│ 一次 HTTP 请求是如何 │
│ 完成的？             │
│ [▶ 看视频 + 图文]    │
├──────────────────────┤
│ [全部][网络基础][前端→│ ← 横滑
│ ┌──────────────────┐ │
│ │ Card（1 列）      │ │
│ └──────────────────┘ │
│ ┌──────────────────┐ │
│ │ Card             │ │
│ └──────────────────┘ │
├──────────────────────┤
│ Footer（竖排）        │
└──────────────────────┘
```

### 5.2 单期页
```
┌──────────────────────┐
│ ▣ Video Studio    ☰  │
├──────────────────────┤
│ 一次 HTTP 请求是如何 │
│ 完成的？ 0:33 #网络  │
│ ┌──────────────────┐ │ ← 可选吸顶（滚动后 sticky top:0）
│ │  <video> 16:9    │ │
│ └──────────────────┘ │
│ (●0:00 按下回车)(0:04│ ← 章节 chips 横向滚动，当前项自动滚入视野
├──────────────────────┤
│ 正文（左右 16 边距）  │
│ ## 1. 按下回车之后    │
│ [▶ 从这里看]          │ ← 标题下方换行显示
│ CodeBlock 横向滚动 →  │
│ …                     │
│ 小结 / 幕后（竖排）   │
│ ← 上一期             │
│ 下一期 →             │
└──────────────────────┘
```
- **视频吸顶（可选，默认开启，可关闭）**：仅在视频正在播放时吸顶；吸顶态宽 100%、无圆角，下方紧贴 chips；右上角 “×” 取消吸顶（记忆到 localStorage）。暂停超过 3s 或用户关闭则恢复正常流。横屏时不吸顶（交给原生全屏）。
- **章节 chips**：`overflow-x:auto; scroll-snap-type:x mandatory`，chip 高 36、`--r-full`，内容“0:04 浏览器发出请求”；当前 chip 主色底 + on-primary 字，并 `scrollIntoView({inline:'center'})`；两端渐隐遮罩提示可滑动。
- 平板 768：视频全宽，章节列表为下方 2 列网格；首页卡片 2 列。
- 触控目标 ≥ 44×44；正文 16px，不出现横向页面滚动（仅代码块内部滚动）。

---

## 6. 交互与状态

| 元素 | hover | focus-visible | active/选中 | 禁用 |
|---|---|---|---|---|
| 链接 | 下划线加粗、颜色提亮 | `--focus-ring` | — | — |
| 主按钮 | 亮度 +8% | focus-ring | 下压 `scale(.98)` | `surface-2` 底 + muted 字 |
| Ghost 按钮（从这里看） | 主色 12% 底 | focus-ring | 主色 20% 底 | — |
| EpisodeCard | 上移 2px + `--shadow-2` + 描边变主色 40% + 封面放大 1.03 | 整卡 focus-ring | — | — |
| 章节项 / chip | `surface-2` 底 | focus-ring | 当前：主色边/底 + `aria-current` | — |
| 标签 pill | 描边主色 | focus-ring | 主色底 `aria-pressed="true"` | — |

**键盘可达**
- 首屏第一个可聚焦元素为“跳到正文”skip link。
- Tab 顺序：导航 → 视频 → 章节列表 → 正文 → 幕后 → 翻页；章节列表为 `<ol>` 内 `<button>`，支持 ↑/↓ 在章节间移动，Enter/Space 跳转。
- 单期页快捷键（焦点不在输入框时）：`K`/空格 播放暂停，`J`/`L` 上/下一章，提示写在章节面板底部 `?` 弹层。
- 焦点环永不移除（只用 `:focus-visible` 隐藏鼠标点击时的环）。
- 汉堡抽屉：打开时焦点锁定，Esc 关闭并还原焦点。

**可访问性**：视频提供字幕轨 `<track kind="captions" srclang="zh">`（由 script.md 生成 VTT）；图标按钮带 `aria-label`；章节跳转后用 `aria-live` 播报“已跳转到 第 3 章 服务器处理请求”。

**prefers-reduced-motion: reduce**
- 关闭卡片上移/封面缩放、平滑滚动改为瞬时（`scroll-behavior:auto`）、chips 不做动画滚动、Hero 渐变不动；视频不自动播放（本站本来就不自动播放）。

**状态**：图片/视频加载前显示 `surface` 骨架块（保持 16:9）；视频加载失败显示“视频加载失败，[下载 mp4]”；无 JS 时章节列表仍为 `<a href="#request">` 正文锚点（渐进增强）。

---

## 7. 组件清单（Astro 落地）

| 组件 | 类型 | Props | 用途 |
|---|---|---|---|
| `BaseLayout` | .astro | `title, description, ogImage?` | html 骨架、tokens、meta/OG、skip link |
| `SiteHeader` | .astro + 小岛(抽屉) | `current: 'home'\|'tags'\|'about'` | 顶部导航 |
| `SiteFooter` | .astro | `version` | 页脚 |
| `Hero` | .astro | `episode: EpisodeMeta` | 首页最新一期 |
| `EpisodeCard` | .astro | `slug, ep, title, summary, duration, tags[], poster` | 期数卡片 |
| `EpisodeGrid` | .astro | `episodes: EpisodeMeta[]` | 响应式网格 |
| `TagFilter` | React 岛 `client:idle` | `tags: string[], selected?: string` | 首页标签过滤 + URL 同步 |
| `TagPill` | .astro | `tag, href?, active?` | 标签胶囊 |
| `Breadcrumb` | .astro | `items: {label, href?}[]` | 面包屑 |
| `EpisodeHeader` | .astro | `title, date, duration, tags[]` | 单期页标题区 |
| `VideoPlayer` | React 岛 `client:visible` | `src, poster, captions?, chapters: Chapter[], stickyOnMobile=true` | 视频 + 章节跳转/高亮（内含 ChapterList/ChapterChips），对外暴露 `seek(id)` 事件总线 |
| `ChapterList` | 子组件 | `chapters, currentId, onSeek` | 桌面右侧章节列表 |
| `ChapterChips` | 子组件 | `chapters, currentId, onSeek` | 手机横向 chips |
| `ChapterHeading` | .astro（MDX 映射 h2） | `id, index, title, start` | 正文章节标题 + “▶ 从这里看”（派发 `vs:seek` 自定义事件） |
| `CodeBlock` | .astro（Shiki） | `lang, title?, variant?: 'request'\|'response', lineNumbers?` | 代码/报文 |
| `Figure` | .astro | `src, alt, caption?, wide?, seekTo?: number` | 配图 |
| `Callout` | .astro | `type: 'info'\|'tip'\|'warn'\|'danger', title?` | 提示框 |
| `Steps` | .astro | `items?` / slot | 流程步骤 |
| `Summary` | .astro | slot | 小结卡 |
| `BehindTheScenes` | .astro | `script, storyboard, source` (URL) | 幕后链接 |
| `EpisodePager` | .astro | `prev?: {slug,title}, next?: {slug,title}` | 上一期/下一期 |
| `Toc` | .astro + 小岛 | `headings` | ≥1440 正文目录 |
| `EmptyState` | .astro | `message` | 空结果 |

**数据类型**
```ts
type Chapter = { id: string; title: string; start: number };   // 来自 article.mdx frontmatter
type EpisodeMeta = {
  slug: string; ep: number; title: string; summary: string;
  duration: number /* 秒，按实际渲染 33.2 */; tags: string[];
  date: string; poster: string; video: string; chapters: Chapter[];
};
```
- 页面：`src/pages/index.astro`、`src/pages/episodes/[slug].astro`、`src/pages/tags/index.astro`、`src/pages/tags/[tag].astro`、`src/pages/about.astro`。
- MDX 组件映射：`h2 → ChapterHeading`、`pre → CodeBlock`、`blockquote → Callout(info)`，这样 Sorkin 的现有 Markdown 稿无需改写即可生效。
- 视频/正文通信：`ChapterHeading` 派发 `window.dispatchEvent(new CustomEvent('vs:seek',{detail:{id}}))`，`VideoPlayer` 监听；`VideoPlayer` 派发 `vs:chapter` 让正文按钮切换“正在播放”。

---

## 8. 验收清单（给 Nolan）
- [ ] 390 / 768 / 1280 / 1440 四档无横向溢出，首页 1/2/3/3 列
- [ ] 点击章节与“▶ 从这里看”都能跳到对应秒数并播放；播放中高亮随时间变化
- [ ] 纯键盘可完成：进单期页 → 跳第 3 章 → 复制报文
- [ ] Lighthouse 可访问性 ≥ 95；正文无低于 4.5:1 的文字
- [ ] reduced-motion 下无位移动画
