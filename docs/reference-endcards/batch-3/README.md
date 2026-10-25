# 片尾参考资料 · 第三批

用户要求继续分批补齐存量。本批选择负载均衡、服务端缓存、缓存一致性，三片共6项引用、3页资料卡，各5秒并提示暂停阅读。资料卡直接保留原始题名、作者/机构、版本及连续原文短引和位置，完整正式与固定版本链接写入配套文章；不把自拟中文概括或翻译冒充原题/原文。

|视频|引用原题|最终时长|
|---|---|---|
|[一台服务器忙不过来，怎么办？](https://linhongcun.github.io/video-studio/episodes/load-balancing/)|Using nginx as HTTP load balancer；HTTP Health Checks|111.200秒|
|[数据库明明有数据，为什么还要再存一份？](https://linhongcun.github.io/video-studio/episodes/server-cache/)|Cache-Aside Pattern；EXPIRE|121.367秒|
|[后台改了价格，页面怎么还是旧的？](https://linhongcun.github.io/video-studio/episodes/cache-consistency/)|Cache-Aside Pattern；EXPIRE|120.467秒|

开工在clean工作区fetch最新4cadb5e9/v0.70.3后建立独立分支。三份Git发布原片按完整SHA逐字复制为不可变body，仅编码新资料卡；全量正文解码帧/时间戳、AAC包/时间戳与PCM保持，完整新输出解码及时间线连续检查通过。原旁白、分镜、字幕、相机、MySQL/Redis标识及导航保持，不重新配音或整条渲染。

NGINX资料保留Using nginx as HTTP load balancer与HTTP Health Checks，区分被动检查/Plus主动检查，片中两次失败或恢复是教学配置。Microsoft资料保留官方题名入口metadata.title中的Cache-Aside Pattern，正文由同一固定提交的include载入；Redis使用未归档官方docs中的EXPIRE。原文分别支持hit/miss回填、先写库后失效与TTL边界，不将操作顺序/过期时间说成强一致保证。三份sources-*.json存实际完整GET、完整SHA、原题和逐论点/短引行号；正式页面本轮不可访问如实留在内部证据，未伪称读取。

三期默认render接入现行参考资料入口；原voice→mix正文流程保持，body输出单列，后接新原题名渲染器。旧325项冻结输入完整保留（其中article/research/freeze/package四项每片有明确快照和允许变更），MySQL/middleware旧后补依赖一并列入；新346项通过source preflight、freeze只读验证及wrapper.verify_freeze。未运行完整正文render或重复全媒体wrapper --verify；当前实际媒体保真来自本轮追加器完整解码。旧追加器和全局门禁未修改。

站点只追加公开资料段，原文章全文、frontmatter、锚点、章节/源码入口与首发身份保持，仅更新实质修改时间和最终媒体范围。全站构建通过，现有13片附录完整验证，其余33片只有固定基线SHA未变时暂缓，未扩大豁免。来源/实际编码独立复核、播放器和线上核验按各自真实报告记录，未执行的完整听辨/逐字ASR不冒称通过；仅GitHub站点，不重发平台，不表示用户已观看认可或关注量已提升。

证据：startup.json、sources-*.json、production-entry-check.json、delivery.json、单期revisions/reference-endcards的baseline及完整media-check；独立审查、浏览器与上线记录完成后另记。

## 本地验收

6项引用独立核对共8次成功完整GET、6个固定URL；12张实际MP4的正文末帧和卡首/中/末帧均逐张查看通过。6个浏览器场景、153项断言、24个精确暂停点、三次桌面1倍速尾段到ended、三页手机原生全屏、三次完整本地MP4 GET/SHA与12次出处点击通过，9张浏览器截图实际查看；见qa-independent.json、qa-browser.json。手机小窗的原生控件覆盖限制与模拟视口/静音播放范围如实保留，未声称真机、逐字ASR或全片听辨。local-verification.json上线前预检已通过，早期位置写法不一致的失败记录保留，修正后真实DOM核验通过。
