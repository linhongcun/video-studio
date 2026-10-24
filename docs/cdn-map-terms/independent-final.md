# EP05 CDN 地图返工：独立最终编码图审

更新时间：2026-10-24T22:08:47.795308+08:00（北京时间）

**结论：按本次事实、地图资产、实际过程阶段和最终编码抽帧的记录范围，无未解决阻断，可按既定授权交付。**

正式视频完整SHA-256：`3715e0514c8ec1cef02a8b32027910de16fd18b04ef5b1b0191f9596f277d9e6`。由本复核者独立计算，与制作记录一致。独立ffprobe显示1920×1080、30fps、3989帧、AAC48kHz，7005064字节。制作方完整解码/102冻结输入/−16.0LUFS/−3.9dBTP见render-result，未冒称这四项均由本复核者重跑。

从此正式MP4自行解码35张并实际查看全部6份联系表；逐图帧号、SHA及路径见 `/tmp/codex-ep05-independent-final/frames.json`。这些是最终全片的实际编码图，与源PNG、无字幕过程片分别记录。

- 03: actual629 has no CDN label,630 introduces CDN·内容分发网络;664 clearly holds it. Map Asia/Pacific/North America and user/selected edge/far origin are recognizable.
- 03 final1033→04 first1034 retains map and role coordinates; source remains contextual while request/cache check becomes focus.
- 05 request/miss and long origin path shown at1351/1498; no usable copy falsely appears at selected edge before content returns.
- 06 actual1677/1678 and1727/1728 preserve origin→edge→user return sequence.1818 still receives/forwards,1819 selected edge has reusable copy.1930 retains it; other map nodes remain unfilled/unexamined.
- 07 actual1931 explicitly another same-region visitor;1993→1994 lookup/hit,2082→2083 short return. Origin stays inactive, no new long return branch; route does not cross image contents in inspected encoded stages.
- 08 actual2231/2453/2612 explicitly distinguishes historical origin path from this request and limits performance to network/hit conditions. No fabricated timing or speed factor.
- 09 actual2613 begins prior received copy,2671/2677 show stale pending check;2821 still pending then2822 usable only after return;2871 user still waiting then2872 says current received. Old source-level waiting/image risk is absent in new actual encoded state transitions.
- 10 actual3189 shows private response bypassing shared cache under configured rules; public image stays shared.11 actual3455 says nodes do not automatically solve source program/database slowness.
- 12 actual3938/3939 old map and paths already exited,3951 brand starts,3988 brand fully visible. No overlap with departing map objects.

此前完成的层次：官方CDN事实预审 `/tmp/codex-ep05-cdn-independent-preflight.md/json`；地图资产/许可/投影窄子审 `/tmp/codex-ep05-map-asset-review.md/json`（执行者cdn_map_asset_check）；三段实际无字幕过程片58帧独立抽看 `/tmp/codex-ep05-independent-motion.md` 与其frames.json。该58帧不等于81源PNG，也不等于整段实时播放。

旧v0.48.0的09只记录源码风险，未宣称看见旧片缺陷；新版2821/2822、2871/2872确认修复。初稿07穿图问题在新过程片和正式1993/1994、2082/2083未重现。旧证据保留，各自绑定原版本/媒介，不归到新视频哈希。

能力边界：未声称整部实时完整播放、词级ASR或独立听辨；最终目视仅覆盖列出的35帧。地图节点/路线是位置示例，离岸点位建议属非阻断观感项，依root收敛意见未继续扩源。未改仓库或Git。
