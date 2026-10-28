# LeetCode十一期正文与封面统一

日期2026-10-28。11期成片及独立正式复核完成，最终网站验收通过。版本v0.85.1；初始计划v0.84.2，后保留最新Redis独立方向821a299/v0.85.0并顺延修订号。冻结输入零交集，视频未因整合重新编码，见[同步记录](upstream-integration.json)。

范围为LC.1、3、11、42、46、70、200、206、547、704、739。正文、完整Python代码页和参考资料页沿现有封面的深蓝/暖金/青色，原题、推导、模型、演示状态、字幕、章节和配音时序保持；原33张封面未重新生成。常规标题栏采用“算法可视化”，具体方法仍由原镜头引出，代码页才显示方法信息。

## 当前制作身份

新源位于各期`remotion/src/leetcode-style/`，独立冻结与输出在`revisions/leetcode-style/`，共享入口为`episodes-codex/_shared/leetcode-video/`。style-v1与身份快照不可变，未来题库扩展不改已经编码的输入。170份旧源保持原字节，401份唯一仓内文件对应逐期566项输入，加6唯一字体/88角色绑定；旧manifest保留历史身份，不把其缺缓存条目写成已重新验证。

每片先完整保留150帧Python页，再追加150帧参考资料。原完整AAC载荷、PTS/DTS/duration与PCM逐一相同；追加前后新正文（含代码页）全帧/PTS相同，不能将此理解为旧画面未改。原文章文字、引用与回看时间逐字节保持，11幅图取自新版对应帧；小数111.666667秒按30fps精确落在帧3350，短片实测见工具记录。

| 题号 | 总帧数 | Python页 | 资料页 | 最终SHA前12位 |
| --- | ---: | --- | --- | --- |
| LC.1 | 5246 | 4946–5095 | 5096–5245 | `2fc16b8a54ec` |
| LC.3 | 6130 | 5830–5979 | 5980–6129 | `07cb15f1aef6` |
| LC.11 | 6967 | 6667–6816 | 6817–6966 | `12da2aa4f827` |
| LC.42 | 6076 | 5776–5925 | 5926–6075 | `0f8bc6053a08` |
| LC.46 | 5763 | 5463–5612 | 5613–5762 | `af8ec425c6e9` |
| LC.70 | 4929 | 4629–4778 | 4779–4928 | `380f1ed1aa76` |
| LC.200 | 5995 | 5695–5844 | 5845–5994 | `9f7189bd8ae1` |
| LC.206 | 5550 | 5250–5399 | 5400–5549 | `acea509d3bb3` |
| LC.547 | 5309 | 5009–5158 | 5159–5308 | `bf12aed27c5f` |
| LC.704 | 5359 | 5059–5208 | 5209–5358 | `89da3531d0a7` |
| LC.739 | 5308 | 5008–5157 | 5158–5307 | `0b787d7cbb72` |

完整SHA、原音轨、旧metadata保护、Figure帧与110张正式采样身份见[媒体汇总](final-media-summary.json)。恢复旧声音必须按baseline-publication中的原Git提交/完整SHA，不用当前新版片代替。

## 实际检查

- [独立范围盘点](independent-scope-audit.md)、[68份视觉源审查](independent-visual-source-review.md)及[6坐标修订](independent-bounded-footer-review.json)通过；动作/状态/程序和时序保持，11份Python共182行含原缩进和空行一致。
- [545唯一逐镜/代码采样](preflight-summary.json)最终通过，共正式渲染1090次；[44张实际图审](independent-preflight-visual-review.md)通过。首轮页脚间距、代码卡两种标记识别、早期背景遮挡问题与原图/旧源保留，未降低边界或缩字号来通过。
- [工具独立审核](independent-tool-review.md)、合成附录、字体缺项只读拒绝及13例精确选帧通过；[实际TwoSum安装后verify](production-verify.json)通过，24生产文件SHA/bytes/mtime不变。其它10片未重复完整解码。
- [正式77图与文件独立终审](independent-final-review.md)全部通过，11/11成片、566输入、字体、三份媒体、全文冻结与完整报告链均过；[33实际交付JPG](restored-original-covers.json)与Git/旧cover-style完整SHA相同。稀疏检出中的已看PNG按当前Git blob完整SHA复核，源图未丢失；6旧PNG缓存读取问题与正常API补核范围如实保留。
- 最终产品候选`43d662ef6f987581999c20db117653b7b3c7eb25`已整合Redis；首次完整网站构建，49日期/49附录、48文章/74精确引文/55配图、Pagefind48页通过。完整双视口交互通过；随后全屏实看发现默认原生字幕与烧录字幕重复，仅加11份burnedInCaptions标记并按该事实关闭原生轨道默认值，VTT仍可显式启用。最终候选e783e5356c4f0a8ebec870b0ad8ef5b44852fc06补一次必要构建及22页新鲜默认/开启/关闭/代码/资料切换检查通过；其余已过交互和33媒体SHA有界复用。完整数字及30张网页选图见[网站验收](site-final/)，之后只补文档证据，产品与最终候选保持一致。

交付分A/B两ZIP，实际题号、大小、全部条目与完整SHA见[交付清单](delivery-package-manifest.json)。只发布GitHub本站，不重发外部视频平台。正式Release入口为[v0.85.1](https://github.com/linhongcun/video-studio/releases/tag/v0.85.1)，实际tag/main/Pages/下载身份与canonical请求结果以该Release链接的publication.json为准，回执完成前不表示已发布。

本轮没有新ASR、全片人工听辨、真机或用户新版观看认可声明。原资料实读日期保留，不声称新增官网GET。当前环境未开放canonical域名或原生Release上传域名，使用普通请求记录实际能力边界与Git交付，不将本地HTTP/GitHub源SHA称为canonical线上完整SHA。已冻结源及原样历史快照中的纯空白行格式按原字节保留，检查范围见[发布前记录](prepublication-checks.json)。
