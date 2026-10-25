# Agent A01 / A02 撤下记录

2026-10-25（北京时间）。用户明确表示此前两期Agent视频效果不足，要求删除。本次移除A01 / EP.22《AI智能体，下一步怎么选？》与A02 / EP.28《AI说要调用工具，到底是谁在执行？》。该指令取代上一轮策划复盘中“保留旧媒体”的当前安排。

## 范围与基线

- 从干净主干`321e8e8c1b4ad34a6ea09eed2bb5cf369d9ab6dd`建立`codex/remove-agent-pilot`。
- 删除发布目录`episodes/agent-intro/`、`episodes/agent-tool-execution/`，共28个跟踪文件；页面、文章、字幕、媒体和元数据一并退出当前发布树。
- 删除`episodes-codex/agent-intro-v2/`、`agent-intro-v3/`、`agent-tool-execution/`三套制作工程，共560个跟踪文件；一并清除本机已忽略的旧版残留。
- 合计删除588个跟踪文件、164346559字节。旧版本通过删除前[固定提交](https://github.com/linhongcun/video-studio/tree/321e8e8c1b4ad34a6ea09eed2bb5cf369d9ab6dd)追溯，Git提交与既有Release历史不重写。
- 两期`platforms`均为空，未登记B站或抖音作品链接。此次处理本站与当前仓库内容。

## 配套处理

- 清除当前制作入口与依赖保护说明，历史反馈和制作事实继续保存；历史工程引用改为固定提交链接。
- 空Agent系列与学习方向由现有动态过滤隐藏，未来Skills、MCP、Subagent、Goal等11项研究候选继续保留，尚未制作。
- 保留发布记录按显式slug区分共用EP号的回归，改用独立fixture；检查已撤下课程不会在目录、学习路径或旧Release关联中误指其他课程。
- 构建会先清空并重新生成`public/episodes`；核对最终产物没有两期页面、字幕、视频、海报或搜索/订阅/站点地图入口。
- 上线后检查两个旧页面及视频/海报/字幕URL返回404，并检查保留课程及新更新日志。

## 验证与发布状态

当前已完成范围清理与依赖审计，其他保留工程不存在指向三套删除工程的符号链接或共享输入依赖。删除前记录其余72个发布媒体文件的完整SHA-256，用于核对本轮未修改保留媒体。

已完成锁定依赖安装、Astro/Pagefind构建（35个搜索页面）、学习路径/章节/帧数回归、秘密扫描及独立删除范围审读。1440/390两视口的首页、学习方向、目录共6个浏览器用例通过，8个旧页面/视频/海报/字幕URL在本地均返回404；其余72个媒体SHA-256保持一致。

[PR #252](https://github.com/linhongcun/video-studio/pull/252)已合并为`f7f2df5785ce057692b6ef96b4efc7456028a818`，附注tag与[Release v0.60.3](https://github.com/linhongcun/video-studio/releases/tag/v0.60.3)发布后，[部署40152148732](https://github.com/linhongcun/video-studio/actions/runs/40152148732)成功。

北京时间2026-10-25T09:53:54.026147+08:00，18个普通canonical HTTPS GET核验全部通过：两期页面、视频、海报与字幕共8个旧地址均404；首页、学习方向、目录、RSS、站点地图和含v0.60.3的更新日志均200且无两期活动链接；事务入门与观察者模式的代表视频/海报完整SHA与本轮发布输入一致。详见[验证记录](agent-video-retirement.json)。线上证据针对本次部署，不将此前技术检查写成用户认可。

#130/#131/#132已补充实际撤下状态；#131保持历史completed，#132保持not_planned。未来Agent课程可重新形成非空方向，回归按实际发布状态检查，不把本次空系列隐藏写成永久禁止新Agent内容。无新TTS、渲染或平台操作。
