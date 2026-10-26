# EP.23 · 设计模式D01：保留原例的流程修订

**当前已上线v0.60.4。** 本轮媒体与网站/线上检查通过，#163已completed关闭；原例、首发与URL保留。见[发布记录](release.md)。

本轮依据用户最新要求保留原例，只调整呈现流程。仍是一笔100元订单在会员九折90元、活动八折80元之间单选，不改成支付方式，也不引入新故事。原观看URL与首次发布日期保留。

## 当前主线

《策略模式：结算怎样换一种算价办法？》保留11镜22句。开头先给结算功能教学示意，看到商品、原价、单选优惠和应付，再解释程序内部。两种策略准备好后，对照结构图说明选择方、结算上下文、定价共同约定及两个具体策略，然后沿原例演一次选择与委托、重置原价替换策略，以及维护收益和成本。

只替换01两句、05两句、06第一句，共5句；其余17句逐字保留并复用原takes。视频正文仍讲与语言无关的思想，不口播函数、参数或接口语法。片尾增加150帧静默Java关键代码节选，明确提示暂停；完整可编译程序和真实运行结果在demo-java及文章。结构图中的结算上下文是业务职责，最小Java示例的Checkout.total只展示核心定价委托，main承担输入/输出演示，并未实现整套结算页面。

## 归档与真实时序

修改前源、时序、语音及原媒体身份归档在revisions/flow-ui-java/baseline。旧takes原位保留并逐文件比对SHA。当前真实装配为正文4628帧、Java卡150帧，共4778帧，30fps。voice与时序由共享流程生成；Java尾段只由新增共享append_java_endcard.py维护，禁止用旧装配命令覆盖静默尾卡。

只读复核入口：

```sh
python3 episodes-codex/strategy-pattern/demo-java/verify.py
python3 episodes-codex/_shared/append_java_endcard.py verify episodes-codex/strategy-pattern
```

旧Python程序和完整证据继续保留作另一语言实现参考，不能把旧Python运行或旧观看反馈充当本轮Java及媒体验证。Java卡是关键节选，省略外层类、import和校验/舍入帮助方法；完整文件才是编译入口。

## 预检、冻结与编码

本期remotion已按当前lock重新npm ci；短TMPDIR为/workspace/pattern-tmp。真实时序预演记录在remotion/out/flow-preflight-v1：129张状态、01/05–06/11三个无字幕无声连续片，实际props关闭字幕，COPYFIT为空。该预演不代替正式成片或真实观看检查。

生产输入停写并经独立QA后，由主任务执行本期freeze.py及--verify，再启动package入口。正式方案记录在revisions/flow-ui-java/render-plan.json：新渲染01–07共2936帧，复用已证明等价的旧08–11正文1692帧，新渲染Java卡150帧。36张相同local状态的fresh PNG与旧accepted缓存逐字节相同，字幕与cue局部时序亦相同；证明和适用边界见tail-reuse-proof.json。

```sh
cd episodes-codex/strategy-pattern/remotion
TMPDIR=/workspace/pattern-tmp npm run render:voice -- --plan-only
TMPDIR=/workspace/pattern-tmp npm run render
```

render:voice校验生产输入SHA，旧视频只取视频流，整轨使用新WAV，重新混共享Wallpaper。保留render:voice:full作为直接全片渲染入口；不以近似时序复用任何一帧。正式编码后的长度、完整解码、PTS、两个拼接边界、字幕和音画，以及同媒体的站点接入与部署，由主任务记录最终证据。

## 历史

v0.52.0首发、v0.54.1章节衔接、v0.54.4语法讲解及v0.56.1思想修订为历史产物。对应revisions与不可变tag保留各自来源，不能改写为本轮结果。本轮是对既有思想版的有限流程修订；所学经验由主任务更新共享文档。

本轮实际冻结入口：从仓库根执行`python3 episodes-codex/strategy-pattern/freeze.py`，编码前后只读复核加`--verify`。它委托新增pattern-flow共享包装，保留旧共享检查器，显式验证真实有声正文与Java静默尾卡派生，并纳入源码、Java、正文快照、旧媒体参照和复用依据。

## 第12批参考资料与当前入口

本批从基线`f3610e244f9e23e7a9075e406bbc990ba53b7699`的完整Git发布原片追加`title-author`参考资料，每页最多4项、默认5秒。原MP4已核对完整SHA和总帧数，保存为`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`；本批直接使用这些原片，不重渲正文、混音或TTS。保留4628帧正文后的原150帧Java关键节选卡，完整body共4778帧；参考资料从Java卡结束之后开始。Java源、显示JSON、正文快照、逐句时序及静音派生通过原共享工具的纯函数只读核对，不调用会写报告或改输入的Java append/verify入口，不编译或运行演示。

原323项声明全部现存，按原路径或article/research/freezer/package四份before快照逐项核对；旧源与旧引擎原路径及字节保持。新freeze.py只写当前清单，分镜快照/placeholder只读核对，不调用旧写入型冻结器。当前新增清单说明真实入口与附录输入，不声称已据此重现原MP4；旧QA与历史制作事实保留原意。

来源全部停写后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/strategy-pattern
python3 episodes-codex/strategy-pattern/freeze.py
python3 episodes-codex/strategy-pattern/freeze.py --verify
```

默认`npm run render`经共享bibliography wrapper检查来源和冻结，再生成完整body并追加资料。原render:voice及render-flow/旧计划完整保留作历史；该计划锁定旧package.json。为不改旧计划或绕过哈希，当前render:body使用现存render:voice:full再mix，参数和完整Main/Java卡不变。默认mix只改输出到`out/body.mp4`，其余混音参数及concurrency=2保留。`npm run render:references`从完整body单独追加；`npm run verify:references`用于后续完整交付核验。最终总帧数由新receipt/render-result与发布meta声明，正文SB/words范围不改。生产整合结果见[入口报告](../../docs/archive/2026-10/reference-endcards-batch-12/production-entry-check.json)，[本批记录](../../docs/archive/2026-10/reference-endcards-batch-12/README.md)只按真实完成状态更新。
