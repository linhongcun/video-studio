# 片尾参考资料 · 第四批

本批选择消息队列、限流、熔断，三片共6项引用、3页各5秒。片尾保留原始题名、机构/版本、连续原文短引和出处位置；文章提供正式与实读固定版本链接，内部证据记录原题与逐论点原文。原讲解、声音、字幕、分镜及视觉保持，不重新配音或整条渲染。

|视频|引用原题|最终时长|
|---|---|---|
|[订单已提交，为什么还没处理完？](https://linhongcun.github.io/video-studio/episodes/message-queue/)|Consumer Acknowledgements and Publisher Confirms；Reliability Guide|108.333秒|
|[抢票时，为什么总提示系统繁忙？](https://linhongcun.github.io/video-studio/episodes/rate-limit/)|Local rate limit；429 Too Many Requests|114.033秒|
|[一个服务出故障，为什么整个网站没跟着崩？](https://linhongcun.github.io/video-studio/episodes/circuit-breaker/)|Circuit Breaker Pattern；Retry pattern|102.533秒|

RabbitMQ原文区分publisher confirm和consumer ack，手动确认/断连重入队及可靠保存都有前提，未作恰好一次或永久不丢保证。Envoy/MDN原文支持令牌桶容量与补充、429及可选等待提示；教学容量2/每秒补1不作为统一默认，速率与突发限制不等于当前并发或库存判断。Microsoft原文明确半开仅做有限试探，失败回Open，恢复依赖外部修复；Retry参考仅支持失败收尾/重试边界，不扩写为另一课。

开工clean同步3156d845/v0.70.4，保存各Git发布原片完整SHA及不可变body，只编码新卡。三份实际producer媒体报告逐项核对全部原正文帧/时间戳、AAC包/时间戳与PCM完全相同，完整新片解码及连续时间线通过。源/发布文章分别保留各自完整主体、frontmatter、锚点、章节/源码入口、首发时间及平台信息，仅追加资料段并更新真实修改时间与最终媒体范围。

三期默认入口接入新模式，原voice→mix正文流程与CB并发设置保持。旧291项冻结历史无缺失，四个允许变更的文稿/入口均有before快照，MQ中间件与导航依赖不回退；新312项输入通过source preflight、freeze只读复核及wrapper.verify_freeze。CB旧freeze.py静态忽略--verify参数会进入写入流程，本轮仅为本期入口补只读检查与参数拒绝；正确/错误SHA临时fixture与生产复核均证明不改写输入/清单字节和mtime，旧写入器未执行，独立校验器保留。见production-entry-check.json与L005补充。

新旧追加器、全局发布门禁与锁文件保持。小批次公开拷贝和QA入口复用既有实现，历史脚本字节不改。全站构建通过：16片附录验证，其余30片只在固定媒体SHA未变时暂缓，未扩大豁免；本批帧数和日期/RSS检查通过。未重复整片声音解码、没有ASR或全片人工听辨，生产full媒体保真与独立视觉、浏览器检查分别记录。仅GitHub站点，不重发平台，不预记用户观看认可或传播效果。

证据：startup.json、sources-*.json、production-entry-check.json、delivery.json、validation.json与单期revisions/reference-endcards基线/receipt/media-check。独立来源和实际帧、播放器、本地上线及线上报告按各自真实执行另记。

## 本地验收

独立完整GET核验6条引用及9份官方固定文件，原题、原句和定位行号均通过；12张实际MP4的正文末帧/卡首中末帧逐张实看通过。浏览器6场景153项断言、24精确暂停点、3次桌面1倍速尾段到结束、3页手机原生全屏、3次完整MP4 GET/SHA与12次出处点击通过，9张截图实际view_image。详见qa-independent.json和qa-browser.json。模拟手机/静音播放与原生小窗限制如实记录，不声称真机、ASR或全片听辨；本地上线预检已通过。
