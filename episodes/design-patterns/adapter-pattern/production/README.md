# 设计模式D03：适配器模式（v0.64.1修订已上线）

用户已观看v0.63.0并指出讲解复杂、偏向不得已兼容。本轮保留订单17发货提醒，改从日常主动统一业务用法、隔离服务升级两个收益展开。新稿10镜20句，结构与同一次请求往返之后，用后来升级的开发对照展示变化集中在适配器和接线；异常细节主要留图文。正文讲思想，片尾5秒Java节选可暂停。

修订前已从干净main同步5a5594fb、按本工程锁fresh npm ci。旧29份source/report、120份voice和旧整轨先归档；原v0.63.0的完整工程/视频保持Git可追溯，不将旧检查改名为新版证据。[本轮范围与状态](revisions/business-boundary-v2/README.md) · [修前基线](revisions/business-boundary-v2/baseline/baseline-manifest.json)

## 真实入口与派生顺序

```sh
python3 episodes-codex/adapter-pattern/demo-java/verify.py
# 只有新正文真实生成/装配并通过检查后，才追加5秒Java静默尾：
python3 episodes-codex/_shared/append_java_endcard.py append episodes-codex/adapter-pattern --frames 150 --body-dir revisions/business-boundary-v2/voiced-body
python3 episodes-codex/_shared/append_java_endcard.py verify episodes-codex/adapter-pattern --body-dir revisions/business-boundary-v2/voiced-body
python3 episodes-codex/adapter-pattern/freeze.py
python3 episodes-codex/adapter-pattern/freeze.py --verify
```

使用共享voice/build、句级装配、起音及Java尾工具，不复制算法。新body显式存business-boundary-v2/voiced-body，不覆盖旧revisions/flow-ui-java/voiced-body。Java尾追加后不要再次运行正文装配覆盖尾卡。新冻结器仍调用原canonical freezer，补充本期实际阅读来源、Java与显式新body，旧共享freezer不改。

原Java V1源码和12组行为保留，新V2示例另验证8组；关键卡为15行真实源节选，完整构造/转换/错误处理在源码，不能单独复制节选运行。程序运行检查与配音、动态、成片和用户观看结论分开。

新版媒体和站点验收已完成，已由PR #272合并并按v0.64.1发布，Release后Pages成功，11个普通GET的完整媒体/海报/字幕/章节/导航与真实更新日志核验通过，#165已completed关闭。首发v0.63.0与publishedAt保持，外部平台未新发。真实结果见[本轮交付记录](revisions/business-boundary-v2/release.md)、qa-final.md和qa-site-online.json；旧首发报告在baseline/released Git历史保留。

## 第12批参考资料与当前入口

本批从基线`f3610e244f9e23e7a9075e406bbc990ba53b7699`的完整Git发布原片追加`title-author`参考资料，每页最多4项、默认5秒。原MP4已核对完整SHA和总帧数，保存为`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`；本批直接使用这些原片，不重渲正文、混音或TTS。保留3861帧正文后的原150帧Java关键节选卡，完整body共4011帧；参考资料从Java卡结束之后开始。Java源、显示JSON、正文快照、逐句时序及静音派生通过原共享工具的纯函数只读核对，不调用会写报告或改输入的Java append/verify入口，不编译或运行演示。

原184项声明全部现存，按原路径或article/research/freezer/package四份before快照逐项核对；旧源与旧引擎原路径及字节保持。新freeze.py只写当前清单，分镜快照/placeholder只读核对，不调用旧写入型冻结器。当前新增清单说明真实入口与附录输入，不声称已据此重现原MP4；旧QA与历史制作事实保留原意。

来源全部停写后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/adapter-pattern
python3 episodes-codex/adapter-pattern/freeze.py
python3 episodes-codex/adapter-pattern/freeze.py --verify
```

默认`npm run render`经共享bibliography wrapper检查来源和冻结，再生成完整body并追加资料。当前render:body保留原voice→mix闭环。默认mix只改输出到`out/body.mp4`，其余混音参数及concurrency=2保留。`npm run render:references`从完整body单独追加；`npm run verify:references`用于后续完整交付核验。最终总帧数由新receipt/render-result与发布meta声明，正文SB/words范围不改。生产整合结果见[入口报告](../../docs/archive/2026-10/reference-endcards-batch-12/production-entry-check.json)，[本批记录](../../docs/archive/2026-10/reference-endcards-batch-12/README.md)只按真实完成状态更新。
