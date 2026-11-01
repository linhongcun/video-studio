# EP05 CDN 独立真实过程片阶段复核

更新时间：2026-10-24T21:51:29.357733+08:00（北京时间）

实际从三段已编码MP4独立解码抽取58帧，并逐张查看7张联系表；未把81张源渲染PNG当编码证据。未声称整段实时播放或听辨。

- `map-03-07-silent.mp4`：1602帧；SHA `a4b4b40060ce8589ac382a099f2e1e2c023d23ac2c72267f344073dbb4fdedf4`。
- `refresh-09-silent.mp4`：336帧；SHA `76f863d40aaa6caa75e1d1317af75e1073db7181aff01f45234fb2537f6971fc`。
- `recap-12-silent.mp4`：396帧；SHA `7088aeccc8649c51631375588e9e3867dad84fba2db1b5d16df57c8d4805ebca`。

预演的26项输入当前逐文件哈希一致：True。解析props关闭字幕；实际三片均仅视频轨，所看58帧无底部旁白字幕。

- 03/04/05: map geography and roles recognizable, stable coordinates across03→04; CDN introduced and held; local request arrives63 then cache check/miss, empty selected cache then long origin request.
- 06: return reaches selected edge69/70, forward reaches user119/120, only that edge later retains reusable copy; no automatic fill of other map nodes. Routes remain beneath image shapes in inspected stages.
- 07: same-region visitor request reaches edge62/63; hit precedes short local return151/152. Origin stays muted and no active long branch; known first-still path-through-picture issue absent in these actual encoded stages.
- 09: prior image explicitly marked last request; new pending request clears client display; cache stale then source check, edge state changes208/209 after reply. Image travels edge→user; local258 waits until259 switches to current received. Old source risk not present in these new actual process stages.
- 12: same map short-return recap; map and old paths fade out by346 before brand appears358 onward.
- All58 inspected frames have no bottom narration subtitles; resolved props hideSubtitles=true/showSubtitles=false and all3 media are video-only.

结论：本次所见实际过程阶段无未解决阻断，可进入既定冻结/正式编码步骤；最终全片实际解码图仍待复核。

事实预审另见 `/tmp/codex-ep05-cdn-independent-preflight.md/json`；地图资产/投影窄子审另见 `/tmp/codex-ep05-map-asset-review.md/json`。旧v0.48的09源码风险不是旧视频实际帧结论，新过程片修复证据仅绑定本报告三段SHA。
