# EP.55 hat-parity · 一句话怎样传出奇偶并推出本人帽色

本期新制作，无上一冻结版；所有正文、声音、封面均为P08输入。沿用系列紫色Frame/theme，替换为右向队列与本题奇偶推理，不使用上一期分金币图。

## 输入身份

- storyboard.json: 2a8697ee1b92bd5890c8a7300b2f3f7f4791a3ccdc6a059cf1085b700170c7b0
- covers.json: 2b1b4bc12a6bb983c5fcc68ba48bacbdd34fb9ac3f9b42b9bddf8d66230cc88f
- script.md: 2927fd3b944c881eb34c5fe19df55e0a002999986ce8b4808323af85abfa3a1a
- voice.wav: de9a74c834a58e10c4297226624da4e81519f77e85eef3cc09cab35a89f415a6
- words.json: 3491fe98fffdceb8198c4d4062c3d33494ef28f2aa1c8a66c4ffa8cba6ea0cfb
- model-data.json: 1c339ca718f8a423bf87cb276e9e1e30f9cc24e65a6da62b294904973a96b617
- remotion/src/Main.tsx: 6f35d9a3b75d044d27854a0024c9c261f88fdb705e015b12769c4510222e6ac4
- remotion/src/model.ts: 3e164bd009e0381c72a7e256e621106211eadec09e5052702823fb95377bcdb7

实测正文4876帧，14镜，1920×1080，30fps；下表为绝对区间，右端不含。声音数据仅具句级声学边界，不宣称逐字ASR或全片语义听辨。

## 画面类型与实际区间

| 镜 | id | frame | from | until | 帧数 |
|---|---|---|---:|---:|---:|
| 1 | 01 | canvas | 0 | 349 | 349 |
| 2 | 02 | canvas | 349 | 754 | 405 |
| 3 | 03 | canvas | 754 | 1049 | 295 |
| 4 | 04 | canvas | 1049 | 1452 | 403 |
| 5 | 05 | canvas | 1452 | 1814 | 362 |
| 6 | 06 | canvas | 1814 | 2145 | 331 |
| 7 | 07 | canvas | 2145 | 2448 | 303 |
| 8 | 08 | canvas | 2448 | 2719 | 271 |
| 9 | 09 | canvas | 2719 | 3075 | 356 |
| 10 | 10 | canvas | 3075 | 3411 | 336 |
| 11 | 11 | canvas | 3411 | 3704 | 293 |
| 12 | 12 | canvas | 3704 | 4076 | 372 |
| 13 | 13 | canvas | 4076 | 4438 | 362 |
| 14 | 14 | canvas | 4438 | 4876 | 438 |

全片canvas，不画浏览器、地址栏或DevTools。人物身份与帽色来自model-data；1号在队尾左侧先答，所有人朝右看。问号为当前人不知道，不是第三种帽色。

## 状态与同步

实际动作公式见remotion/src/model.ts的timings/answerCues和Main.tsx；每镜句首、句尾均读取storyboard.voice的实测localStart/localEnd。句内比例是视觉分段，不冒称逐词ASR对齐。

03—04在2号本人帽位比较假设白／黑，先展示2与3的配对区别，再由1号视野引出总奇偶。05后段首词进入独立消息区。06—10先比较目标与所见奇偶，再推定自身，最后给出色词；扣黑翻转、扣白不变。11才揭示本例1号白帽。12把同一递推范围推进到后续位置；13只翻首人帽色，前方保持相同。

1号原始消息始终为奇，不改写成剩余奇偶，也不进入已知本人帽色行；已知答案从2号开始，来自协议推理，没有裁判报正误。扣除只改变统计范围，不移除人物或真实帽子。

字幕由shots.subtitles读取，位于y931起的字幕带；题内说明/比较区在此之上。页面渲染读取shot.id/from/durationInFrames/voice/subtitles和model-data，cueOnset及审计记录供QA读取。strike/strikeColor本期不用，无额外讨论或下期预告卡。

## 三比例封面

制作与实际布局见covers.json、cover-style.json、cover-render-report.json；共享入口只扩展P08题图，旧七期保护结果见qa/covers-preservation.json。

## 资料附录

按现行title-author规则列2项实际原题与作者/机构，每页最多4项，默认150帧/5秒，无旁白。旧模板original-title-quote条款已被现行AGENTS与RULES取代，不在视频显示短引、日期、URL或暂停提示。
资料区间计划从正文4876帧到5026帧；实际编码区间和SHA以reference-appendix.json和render-result.json为准。

默认入口render-final.sh→render.py先检查来源/冻结，渲染正文并实际full601→limited709转换，共享混音后追加参考列表。文章两图稳定态与回看时间编码前确定并冻结，成片后按相同整数帧导出。

本说明记录输入与画法；实际预检、动态复核、编码/声音/网页和上线结果另见qa，不预先写通过。
