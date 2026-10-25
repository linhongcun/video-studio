# 什么是分布式事务？：全流程导航版最终成片检查

## 当前：MySQL数据库身份修订（#230）

当前正式成片SHA-256：`ae3f2740f8319d435ee8bcb36351493a16956a1800a758cba2106413f63ab62a`，5155帧，1920×1080/30fps。库名旁增加数据库圆柱与MySQL识别图标；内部记录、原字幕、分镜、数值、相机及原混合AAC保持。原AAC完整SHA为`d88bc29e32c09acc9eb928696d3a6e567ca0f69dd96a5eec2cfe17ba32066e75`，与新片提取流逐字节一致；完整解码、格式与冻结输入检查通过。

独立执行者`/root/tx_outbox`从正式新MP4实际查看[1725, 2818]帧，真实范围见[本轮QA](qa-mysql-identity.json)及[独立报告](../../docs/mysql-database-identity/final-review-distributed-tx-intro.json)；预演和fresh构建另有记录，不将它们冒称全片人工听看或用户已认可。发布状态见[本期发布记录](release.md)。

## 修订前历史检查

以下段落保留修订前检查的原始范围，历史媒体与输入由[Git索引](revisions/mysql-identity-before.json)追溯；不能将旧SHA对应的检查冒记为本次重新执行。

对应[#199](https://github.com/linhongcun/video-studio/issues/199)。5155帧，画面171.833秒、容器171.84秒，40句字幕、5章。最终完整SHA-256：`23c1e396def6d06b26b98ce0d7a71534a144b7fb9dfbb3814875f9a0ad66845d`，12,975,810 bytes。

本批按实际扫描筛选，增加全局地图、局部聚焦、当前位置与情景回图；图按本片真实机制组织，核心范围、原配音、脚本、字幕、cue和全部镜头起止保持。原始输入/媒体通过[追溯索引](revisions/pre-flow-map.json)与基线Git版本查回；[原最终检查](revisions/pre-flow-map-qa-final.md)保留为旧版证据，不冒充新版。

## 动态与正式媒体

- 实际关键有字幕状态、真无字幕跨镜过程及生产者实际查看范围见[qa-navigation-samples.json](qa-navigation-samples.json)和本期导航说明；独立编辑范围、发现与修后闭合见[本片审查](../../docs/flow-navigation-audit/intro-review.json)。保留修前证据与未改区间的真实来源，定向复验不伪造所有旧样本的新源SHA。
- 停写后冻结173项输入。正式编码前后逐项SHA一致；H.264、1920×1080、30fps、AAC48k，帧数与时长匹配，完整解码通过。
- 86份预演图片与86个唯一编码帧进行保真核对，最大平均RGB差2.7157/255；这验证编码保真，不是教学评分。
- root实际查看完整正式MP4中的帧：482, 1848, 2818, 3289, 4403, 5154，观察与来源见[正式媒体记录](qa-root-media.json)。
- 混音-16.0LUFS、真峰-3.6dBTP；原版与新版AAC流逐字节相同，原声保持且没有重新请求TTS或加速。

未执行逐字ASR或全片实时人工听看，不把文件/抽帧检查写成用户已经认可本批新版。GitHub站点按持续授权发布；本地成片已完成，最终版本、Release后部署、线上核验与issue收尾见发布记录。用户对v0.51.0四支事务导航片的认可单独保留，不能推广为对这六支新片的观看结论。
