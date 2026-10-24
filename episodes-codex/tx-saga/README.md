# EP.21 · Saga：扣款成功，缺货了怎么办？

本期独立短片只讲Saga：各步本地提交，明确后续失败后用新业务动作补偿。14镜28句、3478帧，约115.9秒；成功/缺货/退款失败分支都有明确起点，原扣款流水不被抹掉。实际媒体指标由root编码后记录。

制作入口为本目录remotion。脚本、plan、episode-config、research/article/pronunciation与视觉说明对应；配音复用episodes/_shared/voice，句级边界与句首声学实测不冒充逐字ASR。所选28句b、原始raw、送模记录与picks保留。

从仓根运行共享assemble/check：

```sh
python3 episodes/_shared/voice/build.py --dir episodes-codex/tx-saga
python3 episodes-codex/_shared/assemble_sentence_episode.py episodes-codex/tx-saga
python3 episodes/_shared/place_v2.py --dir episodes-codex/tx-saga --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/tx-saga
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/tx-saga
```

新环境在remotion/运行npm ci，再npx tsc --noEmit、node scripts/qa.mjs /tmp/tx-saga-preview、npm run covers。依赖目录/软链接不跟踪。完整编码由root在输入停写且独立预检收敛后，先运行共享freeze_sentence_episode.py，再通过/tmp/video-studio-render.lock执行npm run render；禁止更新清单去认可旧媒体。

三构图4:3核心x315..1125、底部<918，poster与3:4 JPEG一致。没有额外全局片尾。配乐Kevin MacLeod《Wallpaper》，CC BY4.0。当前环境未执行逐字ASR或全片人工听辨；检查范围和用户观看反馈分开记录。


## 成片与发布记录

已完成正式编码与独立媒体复核，指标和完整SHA见[render-result.json](render-result.json)，执行者与限制见[qa-final.md](qa-final.md)。本批v0.47.0，按既有GitHub持续授权在站点核验后关闭对应制作issue；用户观看结论另记。
