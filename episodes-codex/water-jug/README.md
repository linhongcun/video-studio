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
