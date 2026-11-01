# EP.21 分布式事务：方案与边界（分章修订版）

用户观看v0.45.4后要求主流方案分章梳理、每种边界清楚。本工程现行入口为本目录的`remotion/`，38镜、76句、11675帧、约389.2秒。五条常见工程路线：2PC/XA、Seata AT、TCC、Saga、可靠消息；消息章区分Outbox和RocketMQ事务消息。这里是机制地图，不作市场占有率或性能排名。

- [script.md](script.md)、[article.mdx](article.mdx)、[research.md](research.md)：旁白、七章文章及实际阅读的公开权威资料。
- [overview-plan.json](overview-plan.json)、[visual-direction.md](visual-direction.md)、[knoll-props.md](knoll-props.md)：镜头/章节映射与逐步动作、成功/失败重置、事务边界。
- [voice/substitutions.md](voice/substitutions.md)、[voice/qa-v2.json](voice/qa-v2.json)：69b+6c+1d所选候选与准确检查范围。音轨SHA256为`06ac9f6c31476e24b4930042c402af1b4e82a5f73a276c705270366409f9b459`。
- [words.json](words.json)、[storyboard.json](storyboard.json)、[qa-timing.json](qa-timing.json)：真实句级边界、9个首次名称声学起音与全部76句连续字幕；不是句内逐字识别。
- `freeze.py`冻结实际输入；最终编码指标与多阶段检查另见`render-result.json`、`qa-motion.md`和`qa-final.md`，只有实际检查后才更新。

配音、裁尾、铺轨、起音和混音使用`episodes/_shared/`。重建所选音轨使用共享build，不重新请求TTS替换通过检查的文件；需要重新配音时生成独立候选并重新检查。Python依赖需numpy/scipy/soundfile，使用当前已配置的环境。

```sh
python3 episodes/_shared/voice/build.py --dir episodes-codex/distributed-tx
python3 episodes-codex/distributed-tx/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes-codex/distributed-tx --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/distributed-tx
```

渲染入口：

```sh
cd episodes-codex/distributed-tx/remotion
npm ci
npx tsc --noEmit
node scripts/v2-qa.mjs /tmp/ep21-overview-qa
npm run covers
```

所有负责人停写、实际动态检查收敛后，从仓库根目录运行`python3 episodes-codex/distributed-tx/freeze.py`；再在`remotion/`执行`npm run render`并复制`out/mix-report.json`至本目录，运行`check-final.py`。多人共用机器时完整渲染使用`/tmp/video-studio-render.lock`，冻结后修源须先停止本期排队/运行任务，再重新冻结及完整编码。

站点使用`episodes/distributed-tx/`中的发布副本；那里原有`remotion/`、旧配音/校验脚本与assets是历史工程，不用于重建本片。当前页面源码链接由meta.sourcePath明确指向这里。旧可靠消息单线版可在[v0.45.4标签](https://github.com/linhongcun/video-studio/tree/v0.45.4/episodes-codex/distributed-tx)追溯，不要用其3791帧或旧清单校验本版。

三尺寸封面使用本期Cover.tsx/covers.json；4:3核心x315..1125且y<918，poster与3:4 JPEG一致。无额外全局片尾。配乐Kevin MacLeod《Wallpaper》，CC BY 4.0。

当前环境没有可用官方ASR权重，未绕过网络限制；不声称完成逐字ASR或全片人工听辨。自动信号、全部句级时序、关键动态状态和实际编码抽帧的检查范围分别记录。

## 第12批参考资料与当前入口

本批从基线`f3610e244f9e23e7a9075e406bbc990ba53b7699`的完整Git发布原片追加`title-author`参考资料，每页最多4项、默认5秒。原MP4已核对完整SHA和总帧数，保存为`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`；本批直接使用这些原片，不重渲正文、混音或TTS。原完整body共11675帧，无代码卡，原收尾和字幕范围保持。本片仍是archived=true的历史方案合集，replacedBy与“方案合集（历史版）”身份保留，不重新放回推荐学习路径。

原194项声明全部现存，按原路径或article/research/freezer/package四份before快照逐项核对；旧源与旧引擎原路径及字节保持。新freeze.py只写当前清单，分镜快照/placeholder只读核对，不调用旧写入型冻结器。当前新增清单说明真实入口与附录输入，不声称已据此重现原MP4；旧QA与历史制作事实保留原意。

来源全部停写后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/distributed-tx
python3 episodes-codex/distributed-tx/freeze.py
python3 episodes-codex/distributed-tx/freeze.py --verify
```

默认`npm run render`经共享bibliography wrapper检查来源和冻结，再生成完整body并追加资料。当前render:body保留原voice→mix闭环。默认mix只改输出到`out/body.mp4`，其余混音参数及concurrency=2保留。`npm run render:references`从完整body单独追加；`npm run verify:references`用于后续完整交付核验。最终总帧数由新receipt/render-result与发布meta声明，正文SB/words范围不改。生产整合结果见[入口报告](../../docs/archive/2026-10/reference-endcards-batch-12/production-entry-check.json)，[本批记录](../../docs/archive/2026-10/reference-endcards-batch-12/README.md)只按真实完成状态更新。
