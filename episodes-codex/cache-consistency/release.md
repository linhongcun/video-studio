# 数据库身份修订（#230）

后台改了价格，页面怎么还是旧的？：保留原配音、字幕与3464帧时长，给真实库角色增加MySQL识别标记，内部记录与提交范围保持。

当前视频完整SHA-256：`5315ac57c2ae1d9041bd730b6fe0a03393afcec0008ba0691dee74ea50282f1f`；原混合AAC逐字节保持。正式媒体/预演/fresh复现的实际范围见[本轮QA](qa-mysql-identity.json)。图标来源为Devicon，原始SVG、MIT notice和品牌说明见[共享素材](../_shared/database-identity/source.json)，不称官方授权素材。

拟随v0.56.5合并主干、Release后部署；线上完整文件、字幕、章节、封面与日志通过后关闭#230。只上GitHub站点，不预写用户观看认可。

## 历史发布记录

# 后台改了价格，页面怎么还是旧的？：全流程与局部定位重制

对应[#199](https://github.com/linhongcun/video-studio/issues/199)，本批设计ID与实际站点发布号分别追溯。保留原配音、字幕与3464帧时长，增加适合本片机制的稀疏全局图、局部聚焦、情景重置与结尾回收。

完整视频SHA-256：`c2cd0d7ed3dc9d202c2e364550f73e7c1586d2d2673256a594c9780fe8d4ff0d`。具体动态、独立编辑与正式媒体证据见[最终检查](qa-final.md)。历史媒体与源见[原版索引](revisions/pre-flow-map.json)。

已由[PR #224](https://github.com/linhongcun/video-studio/pull/224)合并，随[v0.56.2](https://github.com/linhongcun/video-studio/releases/tag/v0.56.2)上线，并经[Release后Pages部署](https://github.com/linhongcun/video-studio/actions/runs/40118710238)成功。线上视频完整SHA与上述本地成片一致，字幕、章节、海报和更新日志已核验；#199已以completed关闭，见[线上证据](../../docs/flow-navigation-audit/online-verification.json)。本轮仅更新GitHub站点，用户对新版的观看反馈后续另记。
