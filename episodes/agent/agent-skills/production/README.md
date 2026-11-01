# Agent Skills：一个Markdown文件，为什么能成为技能？

新方向首片，内部EP.31、slug `agent-skills`，对应[#139](https://github.com/linhongcun/video-studio/issues/139)。约3分8秒，以一次团队API兼容审查解释可发现的方法包、渐进加载、资料读取/脚本执行分流和使用代价。已按v0.62.0合并、发布并部署，[观看视频与图文](https://linhongcun.github.io/video-studio/episodes/agent-skills/)。本地制作、独立成片、站点及线上核验已完成；用户尚未观看新片，不预写其认可。

## 发行与线上证据

[PR #263](https://github.com/linhongcun/video-studio/pull/263)合并为`ea4538be0dba8d562f17db183908e03830e10db8`，附注tag与[Release v0.62.0](https://github.com/linhongcun/video-studio/releases/tag/v0.62.0)发布后，[部署40157863039](https://github.com/linhongcun/video-studio/actions/runs/40157863039)成功。

北京时间2026-10-25T11:25:29.722283+08:00，20个普通canonical HTTPS GET全部通过：新视频/海报完整SHA、24句精确VTT、页面四章与源码入口、首页/学习/目录/Agent系列/订阅/站点地图及含v0.62.0的更新日志正常；两期已删课的页面和视频共4地址仍404，保留课程代表媒体完整SHA一致。详情见[线上报告](online-verification.json)与[发行身份](release.json)。普通GET不冒充浏览器播放；真实双视口播放与跳转另见本地站点报告。

## 成片与关键身份

| 项目 | 实际结果 |
|---|---|
| 画面/时序 | 1920×1080、30fps、12镜24句4章、5648帧、188.266667秒 |
| MP4 | 10161092字节；SHA `b6db5109f529062465b0b1199042ea72f598fff59a2841acb4099174c9da355d` |
| 音轨 | SHA `83657f49cd5be00777d28aeb5442145825092582c19690e415e3a5eb2b369727`；正常语速，19a+4b+1c选段 |
| 真实成片声音 | −16.0 LUFS / −3.6 dBTP；AAC/48000Hz |
| 冻结 | 142项；清单SHA `09ba18bd51a44c60c1de1b389867b3da30969d5a3a02ff47573299d176b1c908` |
| 章节首帧 | 0 / 819 / 2244 / 4102 |

## 资料与示例

[脚本](script.md)、[文章](article.mdx)、[第一方调研](research.md)、[本地技能包](demo/README.md)。演示仅检查简化请求的必填字段规则，不是完整OpenAPI或真实服务实验。run_demo的无LLM宿主载荷示意，与真实Codex子代理按技能读取/执行的记录分别保留，不虚构自动触发或准确率提升。

[开工记录](startup.json)保存原基线；主干并行发布量水题使用原定EP30/v0.61.0后，本片先停止早期编码，再仅顺延EP31与相应身份。声音、全部24句、时序、SRT和代表画面均未变，见[身份对比](revisions/episode-renumber/voice-metadata-sync.json)与[画面对比](revisions/episode-renumber/visual-identity.json)。新身份重新冻结并完整编码，没有用旧清单追认新源。

## 复现入口

- 本地示例：仓根运行`python3 episodes-codex/agent-skills/demo/run_demo.py`。
- 句级装配：沿用共享voice build及本期薄`assemble.py`；现成冻结音轨已提供，复核不重新请求非确定性TTS。
- 冻结只读核验：`python3 episodes-codex/agent-skills/freeze.py --verify`。
- 视频：本期remotion按锁`npm ci`，使用package的render脚本和`/tmp/video-studio-render.lock`；从第0帧播放实体音轨，混音复用共享实现。
- 站点：根锁定版本后运行`sync_site.py --publish --release v0.62.0 --date 2026-10-25`；本地构建后用`verify_site.py`，部署后用`verify_online.py`显式指定base/release/out。

## 实际检查与限制

[本地汇总](qa-final.md)、[独立内容/预检](qa-value-independent.md)、[正式MP4独立复核](qa-encoded-independent.md)、[根实际查看](qa-root-editorial.md)、[站点检查](qa-site.md)、[配音记录](voice/substitutions.md)。原失败帧与正式解码、浏览器截图分别保存，静态样本不冒充多个有效动态阶段。

本轮没有逐字ASR或全片人工听辨，字符兼容字段只是句子包络。来源/信号检查、实际抽样审读与用户观看结论分别记录；原A01/A02继续保持撤下，未来10项仍为研究候选，平台未新发。

## 第12批参考资料与当前入口

本批从基线`f3610e244f9e23e7a9075e406bbc990ba53b7699`的完整Git发布原片追加`title-author`参考资料，每页最多4项、默认5秒。原MP4已核对完整SHA和总帧数，保存为`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`；本批直接使用这些原片，不重渲正文、混音或TTS。原完整body共5648帧，无代码卡，原收尾和字幕范围保持。

原142项声明全部现存，按原路径或article/research/freezer/package四份before快照逐项核对；旧源与旧引擎原路径及字节保持。新freeze.py只写当前清单，分镜快照/placeholder只读核对，不调用旧写入型冻结器。当前新增清单说明真实入口与附录输入，不声称已据此重现原MP4；旧QA与历史制作事实保留原意。

来源全部停写后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/agent-skills
python3 episodes-codex/agent-skills/freeze.py
python3 episodes-codex/agent-skills/freeze.py --verify
```

默认`npm run render`经共享bibliography wrapper检查来源和冻结，再生成完整body并追加资料。当前render:body保留原voice→mix闭环。默认mix只改输出到`out/body.mp4`，其余混音参数及concurrency=2保留。`npm run render:references`从完整body单独追加；`npm run verify:references`用于后续完整交付核验。最终总帧数由新receipt/render-result与发布meta声明，正文SB/words范围不改。生产整合结果见[入口报告](../../docs/archive/2026-10/reference-endcards-batch-12/production-entry-check.json)，[本批记录](../../docs/archive/2026-10/reference-endcards-batch-12/README.md)只按真实完成状态更新。
