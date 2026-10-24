# EP.05 CDN 地图与术语返工

2026-10-24（北京时间），根据用户实际观看v0.48.0的反馈返工。用户要求地图展示临近节点取数据，并在合适时机点出CDN等核心技术名词；旧片文件校验通过不代表这两项教学目标已完成。

范围仅EP.05：地图上的用户、边缘节点与源站保持对应，同一公开图片在未命中时回源、可复用命中时直接返回；用“CDN · 内容分发网络”衔接名称与机制，结合动作解释边缘节点与回源。节点选择按网络时延等条件，地图距离不作为唯一调度依据。不重发平台，保留原发布日期和历史平台投稿。

旧站点成片SHA-256：`11c4163980a1f71f19ca0960c5d6033d51b640dfc9f1c7baac2c9499f34a5539`，3901帧。该版独立检查和发布证明作为历史记录保留。

对应重制issue [#57](https://github.com/linhongcun/video-studio/issues/57)已为本次返工重新打开，并于线上核验通过后以completed关闭。

当前状态：v0.50.3已合并、发布并部署；2026-10-24 22:24:22（北京时间）线上视频/海报完整SHA、字幕逐字节、章节/源码与首页/更新日志均核验通过。

教训见L019；S002补充了正式名称必须落地的适用边界。新的有效做法须有实际独立检查证据后再写入成功经验。

[独立预审](cdn-map-terms/independent-preflight.md)已实际核读AWS交付流程、RFC 9111及Cloudflare缓存正文，并检查改稿范围；此阶段只表示事实/样稿检查，不替代新版动态或成片检查。

已保存[地图资产核验](cdn-map-terms/map-asset-review.md)、[首批小样实际查看记录](cdn-map-terms/root-preview-v1.json)及[修复路线压图后的实际静帧记录](cdn-map-terms/root-preview-v2.json)。旧问题和本次修复分别留证；无字幕小样的实际MP4阶段图与传参/输入身份见本期QA。

## 新版实际产物与本地检查

- 视频SHA-256：`3715e0514c8ec1cef02a8b32027910de16fd18b04ef5b1b0191f9596f277d9e6`，7005064字节，3989帧/132.966667秒；1920×1080、30fps、H.264/AAC48k，−16.0LUFS/−3.9dBTP。
- 12镜24句，4句新候选、20句保留原选定takes；102项真实输入冻结、编码前后逐文件全文SHA一致，全片解码和正式0COPYFIT通过。具体执行者与能力限制见[最终QA](../episodes-codex/cdn/qa-final.md)。
- [站点构建/冻结校验](cdn-map-terms/local-validation.json)、[真实浏览器加载/章节seek/桌面及手机布局](cdn-map-terms/browser-smoke.json)均通过；VTT逐字节使用冻结字幕，章节直接使用frame/fps。
- [保留范围](cdn-map-terms/preservation.json)：仅CDN视频替换；其他28条既有视频完整SHA不变，全部29条元数据的历史字段保留，含原发布日期、首发版本与平台投稿。
- [root实际成片图审](cdn-map-terms/root-final-review.json)：8张新MP4解码图，含地图/CDN、回源/回填/命中、09抵达相邻帧及收束。此范围不扩称整片实时观看或听辨。

本轮未执行逐字ASR或完整独立人工听辨；句级声学起音、静帧与文件检查不冒充这些能力。新版尚未获用户观看认可。

[最终独立结论](cdn-map-terms/independent-final.md)及[新片独立解码35帧索引](cdn-map-terms/independent-final-frames.json)绑定新MP4完整SHA；图审范围不扩称全片实时播放/词级ASR/独立听辨。

候选提交检查：密钥扫描通过；[5处结构性空白记录](cdn-map-terms/whitespace.json)均在当前冻结输入或原样历史快照内，保留其完整SHA，非冻结文件无空白告警。已合入最新主干的LC.11线上证明，站点程序与其他视频媒体未改变。

发布前已合入LC.11完整代码片尾及线上证明，当前本批版本顺延为v0.50.3。成功经验中的地图案例编号为S014，保留主干已发表的S013代码卡案例；两项指导同时保留。

## 发布与线上证明

[媒体PR](https://github.com/linhongcun/video-studio/pull/162) · [v0.50.3](https://github.com/linhongcun/video-studio/releases/tag/v0.50.3) · [Release后部署](https://github.com/linhongcun/video-studio/actions/runs/40102166946) · [完整线上JSON](cdn-map-terms/online.json)。
