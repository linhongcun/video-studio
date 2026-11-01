# 后台改了价格，页面怎么还是旧的？：全流程导航版最终成片检查

## 当前：MySQL数据库身份修订（#230）

当前正式成片SHA-256：`5315ac57c2ae1d9041bd730b6fe0a03393afcec0008ba0691dee74ea50282f1f`，3464帧，1920×1080/30fps。库名旁增加数据库圆柱与MySQL识别图标；内部记录、原字幕、分镜、数值、相机及原混合AAC保持。原AAC完整SHA为`336a701c415e6ecd0a5e3f446795049377f742868c80400429aa773db8c166d2`，与新片提取流逐字节一致；完整解码、格式与冻结输入检查通过。

独立执行者`/root/tx_saga`从正式新MP4实际查看[729, 2243]帧，真实范围见[本轮QA](qa-mysql-identity.json)及[独立报告](../../docs/mysql-database-identity/final-review-cache-consistency.json)；预演和fresh构建另有记录，不将它们冒称全片人工听看或用户已认可。发布状态见[本期发布记录](release.md)。

## 修订前历史检查

以下段落保留修订前检查的原始范围，历史媒体与输入由[Git索引](revisions/mysql-identity-before.json)追溯；不能将旧SHA对应的检查冒记为本次重新执行。

对应[#199](https://github.com/linhongcun/video-studio/issues/199)。3464帧，画面115.467秒、容器115.477秒，24句字幕、3章。最终完整SHA-256：`c2cd0d7ed3dc9d202c2e364550f73e7c1586d2d2673256a594c9780fe8d4ff0d`，13,207,379 bytes。

本批按实际扫描筛选，增加全局地图、局部聚焦、当前位置与情景回图；图按本片真实机制组织，核心范围、原配音、脚本、字幕、cue和全部镜头起止保持。原始输入/媒体通过[追溯索引](revisions/pre-flow-map.json)与基线Git版本查回；[原最终检查](revisions/pre-flow-map-qa-final.md)保留为旧版证据，不冒充新版。

## 动态与正式媒体

- 实际关键有字幕状态、真无字幕跨镜过程及生产者实际查看范围见[qa-flow-map.json](qa-flow-map.json)和本期导航说明；独立编辑范围、发现与修后闭合见[本片审查](../../docs/flow-navigation-audit/cache-consistency-review.json)。保留修前证据与未改区间的真实来源，定向复验不伪造所有旧样本的新源SHA。
- 停写后冻结102项输入。正式编码前后逐项SHA一致；H.264、1920×1080、30fps、AAC48k，帧数与时长匹配，完整解码通过。
- 61份预演图片与61个唯一编码帧进行保真核对，最大平均RGB差2.7333/255；这验证编码保真，不是教学评分。
- root实际查看完整正式MP4中的帧：0, 1513, 2211, 2243, 2442, 3463，观察与来源见[正式媒体记录](qa-root-media.json)。
- 混音-16.0LUFS、真峰-3.8dBTP；原版与新版AAC流逐字节相同，原声保持且没有重新请求TTS或加速。

未执行逐字ASR或全片实时人工听看，不把文件/抽帧检查写成用户已经认可本批新版。GitHub站点按持续授权发布；本地成片已完成，最终版本、Release后部署、线上核验与issue收尾见发布记录。用户对v0.51.0四支事务导航片的认可单独保留，不能推广为对这六支新片的观看结论。
