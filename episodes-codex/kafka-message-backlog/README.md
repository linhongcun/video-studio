# MQ07 / EP47 · 消息积压

题名：《消息积压：加了十台消费者，为什么还越排越长？》；slug `kafka-message-backlog`，#315。本批MQ05–07基线`f01411f7e2a2d1cef480cd0f6b73d4c29d7169f3`，branch `codex/mq05-07-implementation-20261030`，仅此新目录可写；旧生产、共享、声音、QA和冻结回执未复制或修改。

来源/精确脚本/模型/文章已通过独立编辑与根审定；根已生成并接受新声轨，body 6058帧，voice SHA `f4f478dcedbd17e10df0f50ed6ae5f724726f5f5ef580f99db4d4fcca49c2803`，storyboard SHA `a26c7ac995ac0770eb17272ee7d9a2689b221fcae34622b1ad6c941197c8bb4e`。21条原a保持，3条仅同文补b，声学筛查与PCM/文本/onset检查由根及独立QA完成，不推定整片语义听辨。owner没有执行prepare/TTS/build/assemble，未冻结、未正式编码、未接站点。12镜24句，精确旁白身份见 [editorial-version.json](editorial-version.json)，script与voice params保持批准字节。

主机制为按member.id排序形成Range分区列表，再将本地列表变成Fetch候选；poll交还记录后，应用另行等待通知成功才计完成。两分区/十二动态成员最多两份非空列表，不泛化为所有应用只能两业务线程；本例明确每分区串行通知且无额外工作池。

先只比分工、通知未启动，之后稳定共同起点才跟同批E01，避免抹除旧在途业务。4进/2完、降流入1/s均标教学假设非benchmark；前五步每区2进1完，各积5，之后逐秒交替投向两区，按各区min(可用,1)完成，十步排空。清空后只来1条便只完成1条。模型输出27快照/246有限断言，不冒充真实运行。

[research.md](research.md)记录本轮真实GET、执行链与未覆盖边界；[references.json](references.json)保留四项官方源码原题/Apache Kafka机构与连续精确原文，[article-sources.json](article-sources.json)另有明确标为Javadoc应用示例的A1。共享来源preflight已通过四项；此检查不代替独立实现与可懂性审读。本轮runtime07的20项断言PASS已实际复读并绑定runtime-cross-evidence.json：分配扩容与独立单成员poll门控组分开，非十二成员吞吐或通知业务测试。

[article-figure-plan.json](article-figure-plan.json)已按上述真实声轨定四图：整数帧2250、3260、4320、5418，seconds=frame/30，MDX同步seekTo。owner实际逐张查看对应1080p Remotion PNG，归属完成、已poll未完成、五步各积5、十步排空均与图注一致；正式MP4 JPEG仍待根编码后提取与复核。

Remotion从现行已保留工程取同一依赖锁图并fresh npm ci（257包），只复制package/config/data薄层，不复制旧Main/声音/QA/输出。新的Main逐状态读取本期model；共享style-v1和Kafka identity只读引用。`src/placeholders/storyboard.json`仅保留无声450帧/镜布局身份，正式入口读取实际storyboard及voice localStart/localEnd。默认字幕true，支持hideSubtitles。

实测时序自审见 [qa-self-finaltiming/report.json](qa-self-finaltiming/report.json)：98张实际PNG（含27个关键阈值前后、逐镜与四图位），5段连续无字幕短窗共1610帧；两处composition/inputProps均明确关字幕。全部短窗视频与AAC解码通过，owner实际查看162个顺序解码时点、12张联系图及四张1080p图位，未见阻塞。检查保留边界：这是作者自审，不是独立动态放行、正式成片审或全片听辨；独立跨审与根生产闸门仍待完成。

排序布局自审发现输入与输出原本相同，已保留旧27态/244断言与PNG，仅修正twelve-empty输入名单，加入2条断言。排序后及其余26态全同，独立有界复核见qa-editorial/model-sort-correction-independent.json。新模型27态/246断言，排序别名和真实运行memberId仍分开。

字体账本后续冻结使用`docs/archive/2026-10/mq05-07-implementation/font-environment.json`；不可变Kafka style-v1、实际附录adapter和根生产helpers要随实际输入冻结。新封面由独立`kafka-covers-mq05-07`入口处理，不扩写旧已冻结catalog。

只读/本目录开发命令：

```bash
node site/scripts/check-references.mjs --sources episodes-codex/kafka-message-backlog
npm --prefix episodes-codex/kafka-message-backlog/remotion run check:types
```

`model.py`会重写本目录模型输出，编辑停写后不要自行重跑。以上来源检查需从仓根执行；不运行TTS、freeze或正式render入口来试探闸门。
