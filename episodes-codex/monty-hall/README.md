# P04 · 三门问题

本期为趣味推理P04／内部EP32，制作目录为此处，站点读取episodes/monty-hall/。用户在认可P03后授权自主选择下一题，当前开工基线与版本计划见startup.json；实际交付状态另记qa-final.md和release.md，不将制作检查当作用户观看认可。

视频围绕一个问题：主持人按规则开出空门后，为什么始终换门更容易中奖？固定编号与初选，先完整走一局，再从第一次选对/选错入手，展开三个各1/3的初始奖位。主持人知情、必开未选空门、必给换门机会；可开两空门时公平随机选一。初选正确的两条开门分支属于同一个1/3初始情景，不能拆成四条等权情景；三行是穷尽推理，不是三次抽样实验。

保持门位、初选与奖品在同一局的身份；玩家选择框连续移动，主持人开门和玩家换门分别表达。使用抽象门位图，不做拟真实物模拟。短结尾收回始终换2/3、始终留1/3；额外后验和盲开恰空变体只留文章，不加口头入口或代码卡。

## 实际制作入口

配音与句级时间按当前共享实现，不复制TTS、拼接或起音算法；正式稿独立审查通过后再生成，正常语速，不用加速适配估计时长。实际可用听辨/ASR能力如实记录。

```sh
python3 episodes-codex/monty-hall/verify_math.py --output episodes-codex/monty-hall/qa-math.json
python3 episodes/_shared/voice/build.py --dir episodes-codex/monty-hall
python3 episodes-codex/monty-hall/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes-codex/monty-hall --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/monty-hall
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/monty-hall
```

Remotion使用本期当前锁文件npm ci实体安装，只引用保留的共享主题和混音能力。先做真实时序的无字幕关键过程，实际检查合法开门、换门移动、奖品不移动、初始权重与结果提交，停写后再冻结。

冻结与正式编码必须分开执行，冻结成功并独立verify后才启动正式render：

```sh
python3 episodes-codex/monty-hall/freeze.py
python3 episodes-codex/monty-hall/freeze.py --verify
```

实际渲染以remotion/package.json入口为准，使用/tmp/video-studio-render.lock和有空间的短TMPDIR。全片完成后核对同一清单、完整解码、连续PTS、实际中间帧及全轨/句级音源覆盖。站点只同步通过的同一份媒体和所需数据，逐一核对本期实际字幕、章节、目录、两视口播放与正文阅读。

通过GitHub持续授权范围内的检查后，合并PR、附注tag/Release、Release后Pages及线上完整媒体SHA核验，再以completed关闭#208、将#204更新为完成4题。平台新发须另行明确授权。

## 第11批参考资料名单与当前入口

本批只在完整原片后追加`title-author`参考资料名单，每页最多4项、默认5秒；本片无Python或Java代码卡，原有收尾、旁白、字幕、场景和配图保持。基线`a1a9821845c83a61a57fbb3f0e10461ef4c55238`的Git发布原片已核对原render-result与总帧数，逐字节保存为`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`。本批直接使用该完整原片追加，不寻找缓存、不重制正文。

原165项历史输入全部现存并按原路径或before快照逐一验证，保留全部原key。当前清单只声明真实现存依赖及本轮资料/入口，不能用作原MP4已重渲的证明。旧freezer、清单和修前文稿/入口完整归档；数学检查、旧渲染编排和媒体QA保留历史身份，本批不重跑。当前freeze.py保留原实质输入约束，并只读核对分镜快照和placeholder；不调用共享写入型freezer、装配、TTS或数学程序。完整源码静态import、别名和公开音轨的实际结果见[入口报告](../../docs/reference-endcards/batch-11/production-entry-check.json)。

资料负责人停写且来源预检通过后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/monty-hall
python3 episodes-codex/monty-hall/freeze.py
python3 episodes-codex/monty-hall/freeze.py --verify
```

默认`npm run render`经共享bibliography wrapper核对来源和冻结后，执行`render:body`并追加参考资料。`render:body`保留原voice→mix命令、H.264/CRF20、concurrency=2及Chromium参数，仅把默认mix输出改至`out/body.mp4`；旧特别修订命令保留历史用途，交付需通过当前参考资料检查。`npm run render:references`从完整body单独追加名单；`npm run verify:references`用于后续完整交付复核。本批只执行来源和只读冻结/入口检查，不运行正文、混音、数学重验或重复全片解码。最终总帧数以新receipt、render-result及发布metadata为准；[本批记录](../../docs/reference-endcards/batch-11/README.md)不预记媒体和线上通过。
