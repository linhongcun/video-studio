# 片尾参考资料 · 首批

用户要求后续技术视频片尾固定附权威参考资料，存量分批补齐。本批选择同属网络基础的HTTPS、DNS与浏览器缓存，已追加实际可见的5秒暂停资料卡，正文动画、配音、字幕源及既有章节保持。

| 视频 | 主要来源 | 新片时长 | 状态 |
|---|---|---|---|
| [HTTPS](https://linhongcun.github.io/video-studio/episodes/https/) | RFC 9846、RFC 9110、MDN TLS | 124.633秒 | 本地完成，待站点核验 |
| [DNS](https://linhongcun.github.io/video-studio/episodes/dns/) | RFC 9499、MDN DNS | 111.667秒 | 本地完成，待站点核验 |
| [浏览器缓存](https://linhongcun.github.io/video-studio/episodes/browser-cache/) | RFC 9111、MDN HTTP caching | 93.2秒 | 本地完成，待站点核验 |

7项来源逐条对应片中论点，完整标题、正式链接和实际读取的官方固定版本列在配套文章。网络访问范围在source-verification.json如实记录，canonical站点未访问成功不记为成功。旧基础标准保留历史访问和“仅参考”标签，不把文章拓展当作正文依据。

制作沿当前共享append_references.py追加新画面，不重新合成或混音正文。297项当前生产输入核对通过；三片原正文所有解码帧及PTS、原AAC包及时间戳、全部解码音频PCM严格保持，150帧资料卡新增后时间线连续。基线、旧冻结清单和原媒体Git来源分别保存在各期revisions/reference-endcards，追加输入/输出与工具链有独立receipt。

文章制作稿和站点稿原先已有差异，本批只替换/追加引用节，保留站点frontmatter、章节锚点、首发时间与平台链接。最终时长以发布meta.finalVideoFrames为准，原分镜/words仍声明正文范围；字幕结束在参考卡首帧之前，沿用最新主干更严格的原生字幕结束策略。

检查证据：startup.json、upstream-check.json、source-verification.json、delivery.json、qa-independent.json、qa-static.json、qa-browser.json（完成后）、各期reference-appendix-media-check.json。独立重新GET七份正文并核对完整SHA和引文，实际查看三片12张正式编码边界/片尾帧。未重新执行正文人工听辨、逐字ASR或用户观看验收；不宣称片尾资料能保证涨粉。

本批只更新GitHub站点，平台历史链接保留。发布版本、PR、部署与线上完整SHA结果在完成后追加。存量总表见[处理清单](../inventory.json)，其余pending-review条目留待后续分批审查，不预记完成或自动安排定时任务。
