# 片尾参考资料 · 首批

用户要求后续技术视频片尾固定附权威参考资料，存量分批补齐。本批选择同属网络基础的HTTPS、DNS与浏览器缓存，已追加实际可见的5秒暂停资料卡，正文动画、配音、字幕源及既有章节保持。

| 视频 | 主要来源 | 新片时长 | 状态 |
|---|---|---|---|
| [HTTPS](https://linhongcun.github.io/video-studio/episodes/https/) | RFC 9846、RFC 9110、MDN TLS | 124.633秒 | 已上线并核验 |
| [DNS](https://linhongcun.github.io/video-studio/episodes/dns/) | RFC 9499、MDN DNS | 111.667秒 | 已上线并核验 |
| [浏览器缓存](https://linhongcun.github.io/video-studio/episodes/browser-cache/) | RFC 9111、MDN HTTP caching | 93.2秒 | 已上线并核验 |

7项来源逐条对应片中论点，完整标题、正式链接和实际读取的官方固定版本列在配套文章。网络访问范围在source-verification.json如实记录，canonical站点未访问成功不记为成功。旧基础标准保留历史访问和“仅参考”标签，不把文章拓展当作正文依据。

制作沿当前共享append_references.py追加新画面，不重新合成或混音正文。297项当前生产输入核对通过；三片原正文所有解码帧及PTS、原AAC包及时间戳、全部解码音频PCM严格保持，150帧资料卡新增后时间线连续。基线、旧冻结清单和原媒体Git来源分别保存在各期revisions/reference-endcards，追加输入/输出与工具链有独立receipt。

文章制作稿和站点稿原先已有差异，本批只替换/追加引用节，保留站点frontmatter、章节锚点、首发时间与平台链接。最终时长以发布meta.finalVideoFrames为准，原分镜/words仍声明正文范围；字幕结束在参考卡首帧之前，沿用最新主干更严格的原生字幕结束策略。

检查证据：startup.json、upstream-check.json、source-verification.json、delivery.json、qa-independent.json、qa-static.json、qa-browser.json（完成后）、各期reference-appendix-media-check.json。独立重新GET七份正文并核对完整SHA和引文，实际查看三片12张正式编码边界/片尾帧。未重新执行正文人工听辨、逐字ASR或用户观看验收；不宣称片尾资料能保证涨粉。

本批只更新GitHub站点，平台历史链接保留。本批已完成发布与线上完整SHA核验，详见下方记录。存量总表见[处理清单](../inventory.json)，其余pending-review条目留待后续分批审查，不预记完成或自动安排定时任务。

## 发布与核验

已由[PR #330](https://github.com/linhongcun/video-studio/pull/330)合并为`3b7b166a48dc5816892062aa48a6258973358fb4`，附注标签与[Release v0.69.1](https://github.com/linhongcun/video-studio/releases/tag/v0.69.1)指向该实际验收树。Release之后的[Pages部署40200401923](https://github.com/linhongcun/video-studio/actions/runs/40200401923)成功；早先自动触发的重复push部署已取消，避免排队重复部署。

2026-10-25T22:09:13.187258+08:00完成普通canonical HTTPS GET核验：三支完整视频与海报SHA、68条VTT字幕逐字节、原19章标题与起点、全部引用编号/正式及固定来源链接、原首发时间和源码入口、真实更新日志均通过。实际请求与GitHub tag/Release/部署身份见[线上证据](online-verification.json)，未以缓存参数或部分下载替代完整核验。

最终版本的桌面与手机六组播放、24个精确暂停点、28次资料链接点击及三次手机原生全屏实际核验已完成。390px内嵌播放器较小且控件仍会影响HTTPS第三项下缘，全屏与配套图文可读取完整资料；不将此局限隐藏为内嵌全部可读。详见[浏览器证据](qa-browser.json)。未声称新增用户观看认可或受众效果。
