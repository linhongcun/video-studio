# EP.01–14 Codex 重制记录

2026-10-24（北京时间），按用户明确要求，将EP.01–14上一轮Cursor重制版全部按今天Codex规格与经验重新制作。

本次版本 **v0.48.0**。14期本地制作、独立实际关键帧复核、统一构建和浏览器验证已完成，等待按持续授权合并、发布Release、部署并核验线上文件；此阶段不记作线上核验完成或用户已经观看认可。

| EP | 主题 / 工程 | 实际帧数 | 成片SHA前缀 | 状态 |
|---|---|---|---|---|
| 01 | [输入网址](../episodes-codex/http-request/README.md) | 3417 | `b4ee185f` | 本地 / 构建 / 浏览器通过，待线上核验 |
| 02 | [HTTPS](../episodes-codex/https/README.md) | 3589 | `f3c9db28` | 本地 / 构建 / 浏览器通过，待线上核验 |
| 03 | [DNS](../episodes-codex/dns/README.md) | 3200 | `2e75955d` | 本地 / 构建 / 浏览器通过，待线上核验 |
| 04 | [登录状态](../episodes-codex/cookie-session/README.md) | 3344 | `26244de0` | 本地 / 构建 / 浏览器通过，待线上核验 |
| 05 | [CDN](../episodes-codex/cdn/README.md) | 3901 | `11c41639` | 本地 / 构建 / 浏览器通过，待线上核验 |
| 06 | [负载均衡](../episodes-codex/load-balancing/README.md) | 3186 | `c2f92744` | 本地 / 构建 / 浏览器通过，待线上核验 |
| 07 | [浏览器缓存](../episodes-codex/browser-cache/README.md) | 2646 | `30ca1fd4` | 本地 / 构建 / 浏览器通过，待线上核验 |
| 08 | [服务端缓存](../episodes-codex/server-cache/README.md) | 3491 | `185ef935` | 本地 / 构建 / 浏览器通过，待线上核验 |
| 09 | [缓存一致性](../episodes-codex/cache-consistency/README.md) | 3464 | `3199246b` | 本地 / 构建 / 浏览器通过，待线上核验 |
| 10 | [消息队列](../episodes-codex/message-queue/README.md) | 3100 | `cd6d0e8b` | 本地 / 构建 / 浏览器通过，待线上核验 |
| 11 | [限流](../episodes-codex/rate-limit/README.md) | 3271 | `3ccfda88` | 本地 / 构建 / 浏览器通过，待线上核验 |
| 12 | [幂等](../episodes-codex/idempotency/README.md) | 2998 | `93167c78` | 本地 / 构建 / 浏览器通过，待线上核验 |
| 13 | [熔断](../episodes-codex/circuit-breaker/README.md) | 2926 | `8cb05987` | 本地 / 构建 / 浏览器通过，待线上核验 |
| 14 | [降级](../episodes-codex/degradation/README.md) | 3134 | `4b589fd0` | 本地 / 构建 / 浏览器通过，待线上核验 |

共160镜、320句新配音、45667帧，合计约25分22秒。每期84–95项实际输入冻结，全文SHA、媒体指标及逐期核验见[本地验证JSON](codex-remake-ep01-14/local-validation.json)。

- 实际读取官方/标准正文并记录主张、日期与边界；同一示例、渐进揭示和因果动作，镜数/时长按内容决定。
- 配音整轨、声学句首、字幕原文和冻结时间、实际MP4完整解码/帧数/响度检查完成；[独立EP01–03图审](codex-remake-ep01-14/independent-ep01-03.md)、[独立EP04–11图审](codex-remake-ep01-14/independent-ep04-11.md)与各期QA保留具体帧数/检查者/修前证据。EP12–14的跨组检查见本期qa-independent及qa-final。
- [14期实际浏览器记录](codex-remake-ep01-14/browser-smoke.json)：视频元数据、按冻结frame/fps章节定位、实际按钮seek、正文锚点、源码入口、桌面/手机宽度。
- [代表工程干净复现](codex-remake-ep01-14/clean-reproduction.json)：EP01从Git暂存树独立安装，94项输入核对、类型检查及第0帧PNG完整SHA与工作区一致。不扩称14期逐一冷安装。
- 旧EP14回归输入已[独立固定](../episodes/_shared/tests/fixtures/degradation-v0.45.0/README.md)，原golden/生产算法不变；铺轨、制作说明、起音、配音与历史生成链通过，旧分镜和封面逐字节相同。
- [保留范围](codex-remake-ep01-14/preservation.json)：本轮14期媒体均已替换，其他13条既有视频媒体及全部27条站点元数据的历史字段保留（含最新主干新增短片与归档状态）。

站点使用检查通过的冻结媒体；`sourcePath`指向当前Codex工程。文章接入层仅添加导航锚点，EP06/07另加分节标题，不改原文事实或冻结音视频输入；生产稿与导航稿分别记录哈希。没有正文的章节在无脚本时回到播放器。

本轮未执行逐字ASR或独立完整人工听辨。实际完成的声学时序、阶段图、编码静帧和机器指标不冒充这些能力，具体范围在各期QA中明确记录。

旧Cursor轮次issue已关闭，不据此判本轮完成。GitHub发布按持续授权推进，历史平台投稿保留，本轮不新发平台。线上核验将使用`episodes-codex/verify-online.py`对canonical地址真实GET、完整视频/海报SHA、VTT逐字节、HTML章节/源码及Release更新日志检查。
