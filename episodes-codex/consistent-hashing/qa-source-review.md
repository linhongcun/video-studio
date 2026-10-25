# 一致性哈希：独立动画源语义复核

检查时间：2026-10-25T21:44:59.375179+08:00。结论：**源语义通过；无必须修改的机制错误。真实时序连续媒体与成片仍待独立复核。**

Read-only semantic review of source plus11 actually viewed provisional PNGs; actual assembled storyboard source timings additionally calculated. No final encoded-video, continuous-motion, complete audio listening, ASR, or viewer-learning approval.

## 核验结果

- **data-contract**：pass。graphics.tsx directly imports ../../model.json; SampleTable reads M.keys fields, and Imbalance reads M.rings.after.intervalCounts. Supplemental literal labels/segments agree with the locked model.
- **07-same-domain**：pass。The line morphs into a ring; A20/B50/C85 and key 56 share fixed angular coordinates. Key 56 remains distinct from a cache value and node identifier. Viewed provisional early and late frames.
- **08-lookup-key-vs-owner**：pass。Ring draws the key at point(56,217), while a separate trace advances at radius250 from56 to85. Node C remains at85; the key coordinate never interpolates toward85.
- **09-wrap**：pass。Trace95→120 uses periodic point() geometry to reach A20 across0. The independently drawn key remains at95. Source and viewed late provisional frame agree.
- **10-open-closed-interval**：pass。New segment50→70 and retained segment70→85 match (50,70]→D and (70,85]→C; text says50之后，到70为止, B50/D70 remain their labeled nodes. Exact key50/70 ownership was proven by model QA; the visual does not draw separate boundary key dots.
- **11-sample-results**：pass。Same ten model rows produce modulo8/10 and ring2/10; only56/64 change C→D. Result counts increment after each transition completes and are labeled as this sample only. No animation depicts cache-value migration completed.
- **12-interval-length**：pass。A arc85→120 has length35; B20→50 length30; C70→85 length15; D50→70 length20. Bars read the model and are explicitly space length, not actual request volume or memory.
- **13-virtual-physical-identity**：pass。VNodes selects new tokens with n.physicalId===D. Ring chooses physical=n.physicalId??n.id for colors/opacity while displaying distinct token IDs. D1/D2/D3 appear in viewed corrected frames; the three new ranges match (5,10],(28,34],(82,88]. A1/A2/A3 map to the same A cache.
- **virtual-example-reset-and-hotkey**：pass。The virtual example is explicitly a separate preconfigured topology; it does not claim an in-place free conversion or perfect25% distribution. Recap shows an unspecified generic hot key with one A owner; it does not label it K06 or assert it is model.hotKey (whose owner is C).
- **source-events-fit-actual-assembled-timing**：pass-with-media-review-pending。Relevant source completion formulas fit inside all actual assembled shots, with >=76 frames of result hold for the checked major events. This is a source timing calculation, not an audio/content sync or final MP4 check.

## 真实分镜的源事件窗口

制作期间真实TTS已装配为5881帧，以下仅将源事件公式代入真实句级cue，并未听辨或查看真实时序MP4。

| 镜号 | 事件完成帧 | 镜头总帧 | 之后停留帧 |
|---|---:|---:|---:|
| 04 | 328 | 404 | 76 |
| 07 | 258 | 453 | 195 |
| 08 | 211 | 356 | 145 |
| 09 | 204 | 375 | 171 |
| 10 | 234 | 394 | 160 |
| 11 | 160 | 442 | 282 |
| 13 | 354 | 473 | 119 |
| 14 | 354 | 555 | 201 |

## 实际查看的临时PNG

共11张，全部使用450帧/镜占位时序。此前的截图保留原manifest源SHA；不把历史预演说成当前源或正式成片。

- `remotion/out/ring-label-fixed/07-local405.png`
- `remotion/out/ring-label-fixed/08-local225.png`
- `remotion/out/ring-label-fixed/09-local405.png`
- `remotion/out/ring-label-fixed/10-local405.png`
- `remotion/out/ring-label-fixed/12-local405.png`
- `remotion/out/virtual-identity-fixed/13-local113.png`
- `remotion/out/virtual-identity-fixed/13-local405.png`
- `remotion/out/provisional-preview/04-local405.png`
- `remotion/out/provisional-preview/11-local405.png`
- `remotion/out/provisional-preview/14-local225.png`
- `remotion/out/ring-label-fixed/07-local045.png`

## 当前源码指纹

- `model.json`：`b5cf59ec258441d113ae1a4f27f366fb04769c80d6e64fc0d0a54eb19d05728b`
- `script.md`：`3095da4f3233f04ba9d621732825fbced8181cf72a94f30df6299bf1a6d82486`
- `storyboard.json`：`b5b2b600fc4cec145e1d7965b3d6ea21744db535d53dbda8c25fdeb7fd49d231`
- `remotion/src/Main.tsx`：`5f0e511ae702ac37deef7c4cdd19a11737a70d0dbac0afe21bc02eb42a2ff5cc`
- `remotion/src/graphics.tsx`：`23d626e58eb6c95554ab4e988082668c7be2022a6648df32b65fae9645a6f82e`
- `remotion/src/data.ts`：`587fbe61b0729e36fcc6754b70ace442edf985fb7fd64a4b21cde8f1c2678785`

## 边界与后续

- The11 viewed PNGs use provisional450-frame shot timing; they are not final-video frames and have no audio.
- Earlier ring/table previews have recorded historical source SHA values. Current source was read separately; those screenshots are not falsely relabeled as current-source final render evidence.
- The corrected virtual-identity sample manifest records Main f2ff8180 and graphics23d626e5. Current Main has later opening/hash/cue changes; current graphics remains at the recorded corrected identity revision.
- Actual TTS/words/storyboard became available during this review. Only source event windows were evaluated against them; the audio itself was not listened to or recognized.

- [ ] Render and inspect actual-timing continuous clips for07→09 and10→13, including morph/trace start-middle-end and physical grouping; do not reuse placeholder durations as audio sync evidence.
- [ ] Check current-source completed sample counts8/10 and2/10, interval label50-exclusive70-inclusive, and D1/D2/D3 visibility in actual encoded output.
- [ ] Run the project onset/layout/copyfit checks and final-media/deployment checks independently; this review replaces none of those gates.
