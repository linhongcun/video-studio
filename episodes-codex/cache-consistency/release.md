# 数据库身份修订（#230）

后台改了价格，页面怎么还是旧的？：保留原配音、字幕与3464帧时长，给真实库角色增加MySQL识别标记，内部记录与提交范围保持。

当前视频完整SHA-256：`5315ac57c2ae1d9041bd730b6fe0a03393afcec0008ba0691dee74ea50282f1f`；原混合AAC逐字节保持。正式媒体/预演/fresh复现的实际范围见[本轮QA](qa-mysql-identity.json)。图标来源为Devicon，原始SVG、MIT notice和品牌说明见[共享素材](../_shared/database-identity/source.json)，不称官方授权素材。

[PR #235](https://github.com/linhongcun/video-studio/pull/235)已合并，随[v0.58.1](https://github.com/linhongcun/video-studio/releases/tag/v0.58.1)发布；[Release后Pages部署](https://github.com/linhongcun/video-studio/actions/runs/40147968820)成功。线上10支完整视频SHA、字幕、章节、封面、源链接与实际更新日志核验通过，#230已以completed关闭。仅更新GitHub站点，用户对新版的观看反馈后续另记。

[实际线上证据](../../docs/mysql-database-identity/online-verification.json)。

## 历史发布记录

# 后台改了价格，页面怎么还是旧的？：全流程与局部定位重制

对应[#199](https://github.com/linhongcun/video-studio/issues/199)，本批设计ID与实际站点发布号分别追溯。保留原配音、字幕与3464帧时长，增加适合本片机制的稀疏全局图、局部聚焦、情景重置与结尾回收。

完整视频SHA-256：`c2cd0d7ed3dc9d202c2e364550f73e7c1586d2d2673256a594c9780fe8d4ff0d`。具体动态、独立编辑与正式媒体证据见[最终检查](qa-final.md)。历史媒体与源见[原版索引](revisions/pre-flow-map.json)。

已由[PR #224](https://github.com/linhongcun/video-studio/pull/224)合并，随[v0.56.2](https://github.com/linhongcun/video-studio/releases/tag/v0.56.2)上线，并经[Release后Pages部署](https://github.com/linhongcun/video-studio/actions/runs/40118710238)成功。线上视频完整SHA与上述本地成片一致，字幕、章节、海报和更新日志已核验；#199已以completed关闭，见[线上证据](../../docs/flow-navigation-audit/online-verification.json)。本轮仅更新GitHub站点，用户对新版的观看反馈后续另记。

## v0.70.4 · 第三批片尾参考资料

本片补充一页5秒可暂停资料卡，保留实际原题、连续原文摘录和位置；原正文/音轨/分镜与视觉保持，最终3614帧，完整SHA-256：`77c9567e43c9de5f12056c8616339107a9b75635b6c39e32e708cd10d5924d80`。[PR #339](https://github.com/linhongcun/video-studio/pull/339)、[Release](https://github.com/linhongcun/video-studio/releases/tag/v0.70.4)和[Release后Pages](https://github.com/linhongcun/video-studio/actions/runs/40242724829)完成。13次canonical完整GET覆盖本片视频/海报SHA、字幕、章节、出处和更新日志通过，见[本批记录](../../docs/reference-endcards/batch-3/README.md)。仅GitHub站点，无平台重发或本版用户观看结论。
