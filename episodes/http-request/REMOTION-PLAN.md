# v2 Remotion 工程计划（尚未渲染）

v2 = 完整版（科普向），约 2 分 13 秒（+44% 配音），10 段：开场 + 8 章 + 回顾。分镜（storyboard.json）还在画，本目录先不放 remotion/ 和 video.mp4，meta.json 标记 `draft: true`，站点构建时隐藏，旧链接 `/episodes/http-request/` 临时跳转到速览版。

## 与速览版共享
速览版工程在 `episodes/http-request-quick/remotion/`，渲染器是“读 storyboard.json 驱动”的通用实现（rect/text/icon/packet/arrow/code 元素 + keyframes 动画 + 字幕层 + 每镜头一条配音）。v2 计划：

1. 抽出共享包 `packages/remotion-kit/`（npm workspaces）：`Element`、`animValue`、`Shot`、`subtitleTimes`、图标（server-rack / gear / folder-html）、音效常量、调色板。
2. 两期的 `remotion/src/Main.tsx` 只保留各自的 storyboard/timing 导入和 SFX 表；速览版改用共享包后需逐帧比对，确保 video.mp4 不变（不变则不重新渲染）。
3. v2 新增元素类型按分镜需要补到共享包：时序图（三次握手/TLS）、DNS 层级树、缓存决策流程、渲染流水线。
4. 配音流程复用：edge-tts（zh-CN-YunxiNeural，+15%）每段一条 → 去尾静音 → ffprobe 实测 → 写 `remotion/src/timing.json`；站点章节起点由 timing.json 自动计算（与速览版相同）。
5. 渲染后补 poster.jpg / frames/，把 meta.json 的 `draft` 去掉即上线。

## 站点侧待办
- v2 article.mdx 的 8 个章节标题是 `###`（h3），目前“▶ 从这里看”只映射 h2；上线前需让 ChapterHeading 支持 h3（或改为按 frontmatter chapters 的 id 匹配任意级标题）。
- v2 有 10 段视频但 frontmatter 只有 8 章：需约定开场/回顾是否算章节，`computeChapters` 目前按 scene 顺序对齐，需改为按 scene id 显式映射。
