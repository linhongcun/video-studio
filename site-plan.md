# 站点升级方案：Video Studio 科普站 v0.2.0

目标：从“单视频作品页”升级为“视频 + 图文”的技术科普站，可持续扩展到几十上百期。

## 信息架构
- 首页：最新一期大卡 + 期数网格（封面、标题、时长、标签）
- 单期页 /episodes/<slug>/：顶部视频（带章节跳转）→ 图文讲解（分段配插图/代码块，和视频章节一一对应）→ 小结/延伸阅读 → 幕后（脚本、分镜、源码链接）
- 标签/专题页：如「网络基础」「前端」「后端」
- 关于页：团队与制作流程

## 代码架构
- 站点：Astro + MDX（静态生成，适合内容站；交互组件用 React 岛）
- 目录：每期一个目录 episodes/<slug>/ 内含 plan.md、script.md、storyboard.json、remotion/、article.mdx、meta.json（标题、简介、时长、标签、发布日期、封面帧）
- 站点构建时从 episodes/*/meta.json 与 article.mdx 自动生成列表和单期页；视频与封面拷入站点产物
- 复用组件：VideoPlayer（章节跳转）、Figure、CodeBlock、Callout、Steps
- 部署：GitHub Actions 构建 Astro → GitHub Pages；视频渲染仍在本地/手动，产物入库（单片控制在 ~5MB 内）
- 版本号三段式，本次升级发布 v0.2.0

## 视觉
- 延续片中配色（bg #0B1020、primary #22D3EE、secondary #3B82F6、success #22C55E），中文字体 Noto Sans SC，代码等宽字体
- 阅读宽度 ~720px，支持桌面与手机

## 分工
- Hayao Miyazaki：UI 设计稿 design.md（首页、单期页、手机版的布局、组件样式、配色字号规范）
- Aaron Sorkin：第一期图文稿 episodes/http-request/article.mdx（按视频 5 段对应，配图提示、可含一个最小 HTTP 请求/响应报文示例）
- John Knoll：Astro 工程与内容目录迁移、组件实现、Actions 部署；按设计稿和图文稿落地
- Christopher Nolan：审核各环节，最终桌面+手机验收
