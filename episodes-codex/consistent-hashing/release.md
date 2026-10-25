# EA01 一致性哈希发布记录

已于2026-10-25完成制作、检查、合并及GitHub站点上线，首发v0.70.0，制作PR#304，内部EP38。保留并整合LeetCode三片v0.69.0、三片参考资料v0.69.1、默认资料流程b83a0b04、观察者模式v0.69.2及第二批参考资料v0.69.3。

- 目标页面：https://linhongcun.github.io/video-studio/episodes/consistent-hashing/
- 最终视频：6031帧、201.033333秒、10,338,139字节。
- 最终SHA-256：`12aae6e323046bc6bd22aa593de69916f4c17314b2d08199108857df0f545d89`。
- 正文：5881帧，来源Git c80faaefa7750dd8facebc0dc65658ca56400a4d；追加150帧资料卡，正文像素/PTS、9191个AAC包/PTS及PCM保持。
- 原146项正文输入保留，新默认编排157项验证；独立成片/片尾及网站完整检查见qa-final.md和对应JSON。
- 实际合并：`751def7a1baeeaa271be0b786b64684ee70e17bc`，tag v0.70.0指向此提交。
- 正式[Release v0.70.0](https://github.com/linhongcun/video-studio/releases/tag/v0.70.0)发布于2026-10-25T15:15:24Z，随后手动[Pages部署](https://github.com/linhongcun/video-studio/actions/runs/40206090199)成功。
- 2026-10-25T23:21:04.266650+08:00，10项普通canonical GET核验通过：线上完整MP4、16:9海报与字幕字节一致，页面四章、系列/学习/内容库/首页入口和实际Release更新日志齐全。见online-verification.json及publication-evidence.json。
- 最终上游整合后：123页/45课程索引，8项参考资料通过、38项历史暂缓；本期157项冻结输入未变。见qa-final-upstream-integration.json。
- 本次只上GitHub站点，无外部平台投稿，尚无用户观看结论。

Pages只发布video.mp4与meta.poster（16:9）；4:3/3:4封面留Git。verify_published.py记录源验证器SHA并修正线上GET白名单，末次真实canonical GET报告另存online-verification.json。

正式线上浏览器轻检：Chromium154在1440与390宽度均实际短播放、点击四章seek并暂停首个参考卡，原生28cue载入且首卡activeCues为空，无JS错误。不是实体手机、全片播放或声音听辨；实际范围、截图见qa-online-browser.json与qa-online-browser-evidence。root实际查看两张正式网页资料卡截图，来源与正文说明匹配。

制作issue [#295](https://github.com/linhongcun/video-studio/issues/295)已于2026-10-25T15:24:26Z以completed关闭；总览[#294](https://github.com/linhongcun/video-studio/issues/294)同步为1项完成、其余8项待安排。
