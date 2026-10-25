# P05 · 两枚鸡蛋与100层楼

内部EP33，趣味推理P05，对应#209。制作在此目录，发布数据在episodes/egg-drop/，站点读取后者。开工基线和主干隐藏草稿预留见startup.json及PR #270；真实交付状态另记qa-final.md/release.md，不把制作检查写成用户观看认可。

本片兑现“怎样保证14次以内找到最高安全楼层”：先建立两枚相同阈值鸡蛋、未碎可复用/碎后消耗，再解释最后一枚为何要逐层查。固定10层晚碎的19次引出剩余预算；从14次倒推14、27、39的递减间隔，100层封顶。完整F31实例走8次，最后两枚都碎且答案唯一仍成功。严格最优性、完整边界和容量递推只在文章，视频无附录口头入口、代码卡或额外证明尾段。

原题楼层、鸡蛋及已知安全/会碎边界共同承担推理。条件预算分支与完整实例清楚分开，计数和边界只在落地结果确认后提交；最后一枚逐层试，未测楼层不提前显示成已知安全。实际帧、正常配音、候选和能力范围由本期QA记录，不把临时原型当作真实时序通过。

## 实际入口

下列共享实现保持原样，本期只用薄包装和参数，不复制起音、TTS、装配或混音算法。TTS先经过本期独立五稿审，正常语速；voice/input-provenance.json保留实际生成来源。

```sh
python3 episodes-codex/egg-drop/verify_math.py --output episodes-codex/egg-drop/qa-math.json
python3 episodes/_shared/voice/build.py --dir episodes-codex/egg-drop
python3 episodes-codex/egg-drop/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes-codex/egg-drop --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/egg-drop
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/egg-drop
```

原始候选的prep/gen与选take由voice记录；直接build使用已经存在的同文take，不重新随机生成候选。当前plan没有额外命名术语cue，严格标签检查如实为0项，不套用旧期数量；动作仍须按真实句时检查。

Remotion以本期锁文件进行实体npm ci，入口在remotion/package.json。先做真实配音下的关键连续片、实际DOM/文字运动包络及三尺寸封面检查，修正后停写所有生产输入。

冻结和独立verify必须分开成功，再启动正式编码：

```sh
python3 episodes-codex/egg-drop/freeze.py
python3 episodes-codex/egg-drop/freeze.py --verify
```

从remotion/运行本期npm run render，完整编码使用/tmp/video-studio-render.lock及有空间的短TMPDIR。正式媒体另核完整解码、连续PTS、同尺寸关键帧保真、独立实际画面及全轨/逐句选定音源覆盖，不把数值一致性冒充ASR或人工听辨。

正式媒体通过后才接入站点、升实际可用版本并检查双视口、24句字幕、四章、普通文章锚点和独立五课目录。按持续授权合并、附注tag/Release、Release后Pages和线上完整摘要核验；全部完成后以completed关闭#209，将#204更新为完成5题。外部平台投稿不在此授权内。
