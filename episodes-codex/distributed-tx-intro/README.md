# EP.21 · 入门：什么是分布式事务？

产品场景示范修订 #242：从订单页面的“待确认”反馈进入订单8124与库存4的对应关系，再进入原有概念大纲；结尾回到同一订单页。原5155帧、配音字幕及后续机制保留。实现与真实检查范围见[本次记录](../../docs/product-scene-intro/README.md)。

本轮`flow-map-20261024/#199`导航修订：以同一张概念图区分管理范围对照、问题示例与恢复要求，细讲留位置、换情景回图，保持原5155帧及配音字幕。见[navigation.md](navigation.md)；新版正式成片检查见[qa-final.md](qa-final.md)，上线结果见[release.md](release.md)；修订前媒体与源码由[原版索引](revisions/pre-flow-map.json)追溯。

按用户指导新增概念前置，现有[EP.21方案详解](../distributed-tx/README.md)保留五类机制与适用边界。新片20镜40句、5章，5155帧（约171.8秒）；同一订单8124购买商品7042一件，从库存4到3的教学规则贯穿全片。完整媒体指标须以`render-result.json`及实际成片检查为准。

先认识同一业务目标，再看同一本地事务的共同提交/撤销、拆分后的独立边界、部分成功、超时结果未知，以及持久进度、安全重试和失败收尾。不在入门片堆五类方案缩写，不将所有工程路线说成全局ACID。

- [script.md](script.md)、[research.md](research.md)、[article.mdx](article.mdx)：40句口播、实际阅读的8份当前官方资料及早期仅参考资料、五章文章。
- [intro-plan.json](intro-plan.json)、[visual-direction.md](visual-direction.md)、[knoll-props.md](knoll-props.md)：逐镜动作、互斥分支重置与事务边界。
- [voice/substitutions.md](voice/substitutions.md)：38b+2c候选选择、来源与检查能力；真实音轨SHA256为`86b9bd79c1d623918ce96d49867e789e005aa481a50fed42e2afcbc190a96b22`。
- [qa-timing.json](qa-timing.json)、[qa-independent.md](qa-independent.md)、[qa-motion.md](qa-motion.md)、[qa-final.md](qa-final.md)：实际句级时序、独立教学与动画、最终编码检查。未执行的检查不记为通过。

三个首次术语都位于真实句首：本地事务、分布式事务、最终一致。句内字符只保存句包络，不是逐字ASR。当前没有可用官方medium ASR权重，不声称逐字识别或全片人工听辨。

配音、裁尾、铺轨、起音与混音均复用`episodes/_shared/`；保留所选takes与元数据，重建音轨无需重新请求TTS。Python需numpy/scipy/soundfile，使用已配置的虚拟环境。

```sh
python3 episodes/_shared/voice/build.py --dir episodes-codex/distributed-tx-intro
python3 episodes-codex/distributed-tx-intro/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes-codex/distributed-tx-intro --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/distributed-tx-intro
python3 episodes-codex/distributed-tx-intro/check-timing.py
```

动画与封面入口：

```sh
cd episodes-codex/distributed-tx-intro/remotion
npm ci
npx tsc --noEmit
TMPDIR=/workspace/.video-studio-tmp node scripts/branch-qa.mjs /workspace/.video-studio-flow-audit/intro-remake
npm run covers
```

实际动态复核收敛、所有写入负责人停写后，从仓根运行`python3 episodes-codex/distributed-tx-intro/freeze.py`，再从`remotion/`执行`npm run render`。多人共用渲染器时用`/tmp/video-studio-render.lock`串行编码；冻结后改源须先停止本期排队/执行任务，重新冻结和完整渲染，不能更新清单去认可旧视频。混音报告复制至本期`mix-report.json`后执行`check-final.py`。

站点从`episodes/distributed-tx-intro/`读取发布副本，源码链接指向本目录。两片共用整数期号21，以“入门”“方案详解”区分；学习顺序EP.20 → 入门 → 方案详解，分别保留独立URL/媒体/章节。原方案详解冻结输入与成片不因站点引导改动而变。

三构图封面由本期Cover.tsx/covers.json生成；4:3核心x315..1125、y<918，poster与3:4 JPEG相同。成片不追加全局片尾。配乐Kevin MacLeod《Wallpaper》，CC BY 4.0。
