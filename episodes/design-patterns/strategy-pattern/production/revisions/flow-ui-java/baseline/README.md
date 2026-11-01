# EP.23 · 设计模式D01：策略模式设计思想修订

本轮依据用户2026-10-25反馈：上一版过度讲函数和参数，偏语法；设计模式应讲与语言无关的思想，并要求更新经验教训。制作issue为#163，系列总览#161，原观看URL和firstRelease保持。

## 当前主线

《策略模式：结算怎样换一种算价办法？》为11镜22句，只讲结算流程、定价策略、选择三类职责。两种策略完成相同任务，按共同业务约定接收原金额、交回应付金额；结算把具体定价委托给已选策略。会员100元得90元，再重置原价只换活动得80元。重点是变化隔离、共同流程为何保留、独立维护边界和协作成本，不以算术或某语言机制代替模式定义。

视频无代码或语言语法；具体Python实现、函数绑定与校验仅在配套文章可选附录。现有demo记录证明教学金额与该实现，不定义模式。新稿、真实时序和媒体SHA以本轮script/QA/release为准；不能把旧版已通过的程序和音画检查当作新方向已通过。

## 历史与经验

v0.52.0首发、v0.54.1章节衔接版、v0.54.4语言实现讲解版的报告分别在对应revisions目录；原媒体、音轨和源码可从各自不可变Git tag恢复。所有旧takes原位保留，新稿使用idea后缀，必要idea2。本轮完整重做，不使用历史局部拼接入口。

用户反馈已写入RULES设计模式教学节、pipeline思想审查、L030及项目记忆，并纠正L027/S016把函数传参当核心目标的适用范围。经验记录须区分用户指导、独立检查和真实观看效果。

## 配音、装配和冻结

沿用episodes/_shared/voice的prep/gen/build，以及共享assemble_sentence_episode、place_v2、label_onset_strict、check_sentence_episode，不复制TTS、起音、铺轨或混音算法。重建已有选定takes无需再次请求TTS：

```sh
python3 episodes/_shared/voice/build.py --dir episodes-codex/strategy-pattern
python3 episodes-codex/_shared/assemble_sentence_episode.py episodes-codex/strategy-pattern
python3 episodes/_shared/place_v2.py --dir episodes-codex/strategy-pattern --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/strategy-pattern
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/strategy-pattern
```

词兼容字段是句包络，不是逐字识别。04第一句策略模式按共享声学起音出现至少63帧；无可用ASR/听辨时如实写边界，不称读音或全片听辨通过。

真实时序预检前运行npx tsc --noEmit；既有qa.mjs生成全11镜无字幕图及03/06/07关键连续片及05/08状态图，检查最终props、非占位、COPYFIT和实际中间态。思想审查须仅凭本片解释谁选择、谁委托、谁计算、何种约定使替换成立。生产源停写且独立预检通过后：

```sh
python3 episodes-codex/strategy-pattern/freeze.py
python3 episodes-codex/strategy-pattern/freeze.py --verify
```

## 编码与上线

本期remotion下用原npm run render完整编码，短TMPDIR=/workspace/strategy-tmp与/tmp/video-studio-render.lock串行锁；共享Wallpaper混音目标-16LUFS。封面原件内容仍符合规则独立和流程稳定，核对完整SHA后复用。冻结后源变更须停止编码并重新检查/冻结。

正式片执行共享check_encoded、完整解码/PTS、实际成片字幕与职责过程复核，再复制同一媒体接入网站。合并、Release后Pages部署、8个canonical普通GET流式完整核对视频/海报/VTT及四章/目录/源码/系列/RSS/更新日志，通过后completed关闭#163。平台未新发；实际结果见release.md和本轮报告。
