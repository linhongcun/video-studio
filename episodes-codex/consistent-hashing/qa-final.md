# EA01 一致性哈希：最终交付与正文检查

最终视频已按最新[RULES出处要求](../../docs/RULES.md)追加150帧、5秒资料卡：**6031帧，201.033333秒，10,338,139字节，SHA-256 `12aae6e323046bc6bd22aa593de69916f4c17314b2d08199108857df0f545d89`**。R1 NGINX与R2 Cassandra是已实际核验的核心资料，完整出处/论点对应见references.json与原文章。

共享追加工具的完整解码对比证明原5881帧画面/PTS逐帧相同，原AAC所有包/PTS及完整PCM相同；不重配音；原146个正文输入按旧清单和package快照验证，未重新编码正文。默认渲染编排现纳入157项当前清单，见freeze_with_references.py与qa-reference-render-entry.json。正文媒体可从Git `c80faaefa7750dd8facebc0dc65658ca56400a4d:episodes/consistent-hashing/video.mp4`恢复。新增生成输入/输出见reference-inputs-sha256.json与revisions/reference-endcards，最终尾边界/网页资料卡复核见qa-reference-independent与最新qa-site-appendix报告。

下方保留原正文的真实检查范围，避免把旧报告中的5a54624a…媒体身份误当成追加后的整体视频。

原已验收正文媒体为1920×1080/30fps、5881帧，画面196.033秒、容器196.053秒；10,263,723字节，SHA-256 `5a54624a31f293fb2b68161ed9875a184a992fc322996a5a010d3fca61d3242e`。146项编码输入在编码前、编码后和站点接入后均核对通过。

- 公开资料：实际读取NGINX、Cassandra5.0、Redis第一方正文，主张/短引/访问日与版本边界见research.md。
- 内容：14镜28句4章，题意与方法选择动机分别审读；同一十键取余8/10、环2/10均明确为示例，53,662项独立模型断言通过。
- 动态：正式句时98张实际PNG、3段无字幕编码小样；独立查看28图，其中15图直接解码连续片。07同域、08查找、09回绕、10局部接管和13虚拟物理身份通过，原06歧义已闭环。
- 声音：39份候选最终28句，文本请求、PCM转换、声学裁尾、铺轨、两项严格起音、全轨与逐句AAC/已知BGM来源重建通过，−16.0LUFS/−3.8dBTP。没有执行逐字ASR、语义听辨或全片人工听辨，不把数值检查冒充这些能力。
- 正式成片：所有5881帧PTS连续及完整解码通过；14张同帧源图SSIM最低0.983655；独立实际查看25张编码图覆盖全14镜、中间状态与末帧，根另看4个关键最终状态。未声称实时完整观看或初学者实验。
- 封面：三尺寸6张实际PNG/JPG查看，安全区/字形边界均通过；旧封面、标签及物理身份预检失败保留在qa-revisions。
- 网站：122页/45课程，1440与390两视口实际播放；28条原生cue及毫秒时间、4章精确seek、2图、Python、TOC、六方向及新系列/首页/资料库/RSS通过。SVG属性在站点AST层规范，手机figure默认边距移除；冻结文章与视频不变，旧策略/适配器图双视口回归通过。

本地验收及GitHub站点交付已完成：PR#304合并至751def7a，发布v0.70.0，Release后Pages成功；10项普通canonical GET核验通过，线上完整MP4、海报与VTT字节一致，四章、入口及实际Release更新日志齐全。合并、Release、部署与线上证据见release.md、publication-evidence.json和online-verification.json。技术检查不表示用户已经观看认可，未执行外部平台投稿。


最新默认流程已整合b83a0b04：新source evidence改为真实仓内路径、原说明保留details；卡片显示字段与PNG逐字节不变，正文/AAC指纹和卡片解码指纹与独立审过的版本匹配。当前最终媒体中点另经实际查看，157项默认入口及全站check:references构建检查通过，最终157项AAC来源复核通过。历史8554…报告保留其真实范围，转接证明见reference-inputs-sha256.json。

正式部署后双视口轻量浏览器实测通过：实际短播放、四章点击seek、首卡原生字幕为空；见qa-online-browser.json。该检查不扩展为实体手机或全片听辨结论。
