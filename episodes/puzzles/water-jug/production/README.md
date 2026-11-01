# P03 · 3升与5升量出4升

本期使用两个初始空、无刻度的3升/5升容器，目标是5升容器内恰有4升。视频讲清操作条件与选择思路，连续演示六次合法操作，用小壶存2升形成1升空位，最后从满5升中倒出1升留下4升。独立系列为趣味推理，内部EP30；完整BFS与目标变体说明保留文章。

开工基线、版本计划和真实依赖入口见startup.json。制作在本目录，站点读取episodes/water-jug/，不依赖已删除工程的ignored缓存。Remotion按当前锁npm ci实体安装；配音、句级装配、起音、主题及混音使用共享实现。

## 制作与核验入口

脚本经根与独立编辑审查后，再使用共享voice prep/gen/build生成冰糖正常语速配音。选定takes、参数与实际能力记录在voice目录；不为估计时长加速。

```sh
python3 episodes-codex/water-jug/verify_math.py --output episodes-codex/water-jug/qa-math.json
python3 episodes/_shared/voice/build.py --dir episodes-codex/water-jug
python3 episodes-codex/water-jug/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes-codex/water-jug --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/water-jug
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/water-jug
```

assemble.py只调用当前共享装配。public/audio/voice.wav必须是实体副本，从第0帧开始；words的scriptSha256采用完整script.md。句级时间包络不代表逐字ASR或内部词对齐。

先实际查看关键真无字幕过程，检查两壶水量同步、来源与出口、合法停点和跨镜状态，再停写冻结。冻结和正式编码分开执行，前一步成功后再继续：

```sh
python3 episodes-codex/water-jug/freeze.py
python3 episodes-codex/water-jug/freeze.py --verify
```

正式渲染使用本期remotion/package.json真实入口，共享/tmp/video-studio-render.lock，TMPDIR采用有空间的短路径。编码前后核对同一清单，实际MP4另检查完整解码、PTS、声音与关键过程，不用预演代替成片。

## 目标与表达边界

状态按(3升壶,5升壶)书写，终态(3,4)满足本期目标，总水为7升；力扣365的两壶总量4升是不同目标，不能混用。图中的数字由合法操作推算，是讲解标注，不是给原壶增加刻度；两条抽象容量条按同一像素/升比例绘制，不模拟拟真器具。

实际制作、成片、本地与线上交付结果分别记录在qa-final.md及release.md。完成GitHub持续授权范围内的检查、合并、Release和Pages，并核对完整线上文件后关闭#207、更新#204；外部平台发布需另行授权。尚未执行的检查与用户观看结论不得预写通过。

## 已交付版本

v0.61.0已通过PR #256合并上线，4977帧约2分46秒。Pages40153856609成功后，完整线上视频/海报、24条字幕、四章及新增日志核验通过，#207已completed关闭。GitHub CLI/API后段401由现有connector能力完成替代核验，媒体未变；9站点canonical GET和1份独立Release记录分别计数。实际SHA、范围、能力限制与出处见qa-final.md、release.md、online-verification.json。

## 第11批参考资料名单与当前入口

本批只在完整原片后追加`title-author`参考资料名单，每页最多4项、默认5秒；本片无Python或Java代码卡，原有收尾、旁白、字幕、场景和配图保持。基线`a1a9821845c83a61a57fbb3f0e10461ef4c55238`的Git发布原片已核对原render-result与总帧数，逐字节保存为`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`。本批直接使用该完整原片追加，不寻找缓存、不重制正文。

原130项历史输入全部现存并按原路径或before快照逐一验证，保留全部原key。当前清单只声明真实现存依赖及本轮资料/入口，不能用作原MP4已重渲的证明。旧freezer、清单和修前文稿/入口完整归档；数学检查、旧渲染编排和媒体QA保留历史身份，本批不重跑。当前freeze.py保留原实质输入约束，并只读核对分镜快照和placeholder；不调用共享写入型freezer、装配、TTS或数学程序。完整源码静态import、别名和公开音轨的实际结果见[入口报告](../../docs/reference-endcards/batch-11/production-entry-check.json)。

资料负责人停写且来源预检通过后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/water-jug
python3 episodes-codex/water-jug/freeze.py
python3 episodes-codex/water-jug/freeze.py --verify
```

默认`npm run render`经共享bibliography wrapper核对来源和冻结后，执行`render:body`并追加参考资料。`render:body`保留原voice→mix命令、H.264/CRF20、concurrency=2及Chromium参数，仅把默认mix输出改至`out/body.mp4`；旧特别修订命令保留历史用途，交付需通过当前参考资料检查。`npm run render:references`从完整body单独追加名单；`npm run verify:references`用于后续完整交付复核。本批只执行来源和只读冻结/入口检查，不运行正文、混音、数学重验或重复全片解码。最终总帧数以新receipt、render-result及发布metadata为准；[本批记录](../../docs/reference-endcards/batch-11/README.md)不预记媒体和线上通过。
