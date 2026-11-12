# EP.56 twelve-balls · 趣味解题短片重构

追踪issue #484；保留题面、编号及轻重目标，以当前script/plan确定实际讲解顺序。旧版本媒体、资料核验日期和冻结证据保持历史身份。

## 实际输入身份

- storyboard.json: 96acc052254e06bb7ea60f2f2f4dba9e7c4ccee8388a798a35d91b421e5c76d5
- covers.json: 5fe6595d1f45f1dd2abcacdf34f4533949945d681df354bf20dffa3936b223af
- script.md: edf0e98b541ccef791d91e1ef37055dcc477dbbefc8b9838e10c4a72cbba8947
- voice.wav: 3df4ca0af1686801efc797aa98fc655f93cdff2d2a47db1be80940591018a51d
- words.json: be59568785896b2939b46e2d101ce6a1330d5d072b9a2e3a78a9b3b581f72a2c
- references.json: b5e1d4c798e70565d02a304626110d6569b1677bdfa3a0993dcf6ac83f4242aa
- input-provenance.json: 400fb88eb97a8fd534af942f7ce6c0e4cb1607c1538a44308822d6fe3db9fb17
- remotion/src/Main.tsx: a7e43c8f6cdc9b907dbf4cec9fe707949ce25d0c50b6c0e050a67c248ffe0a55
- remotion/src/Root.tsx: df0076e8c16b6b24e327812ab0d1252d0e839102f2ca38713bc3591f7e21b120
- remotion/src/data.ts: 086ff6127c5f84b9680abbc0d532e63321b30f5e2e8fb846e532f94452b6fd1e
- remotion/src/index.ts: f9bc4e836a064aca9c58a681e1dc779b62a4d82894450e8e15d5cdd05840e36e
- remotion/src/motion.ts: 4ef78be4c1f4030db411f805406760a3e967f897f50df5543f34dc5c95127b64
- remotion/src/theme.ts: 2ca0f4fe73e5e68581cdaffd4870efc38c786881abd6832b7e4ea08e276b02c5

实测正文4669帧，12镜，1920×1080、30fps。此为句级声学边界，无逐字ASR或全片语义听辨声明。

## 实际镜头区间

| 镜 | 画面类型 | from | until | 帧数 |
|---|---|---:|---:|---:|
| 01 | problem | 0 | 297 | 297 |
| 02 | first-weighing | 297 | 570 | 273 |
| 03 | first-left | 570 | 1026 | 456 |
| 04 | second-weighing | 1026 | 1438 | 412 |
| 05 | second-left | 1438 | 1826 | 388 |
| 06 | identify-six | 1826 | 2167 | 341 |
| 07 | second-right | 2167 | 2575 | 408 |
| 08 | second-balanced | 2575 | 2982 | 407 |
| 09 | mirrored-start | 2982 | 3382 | 400 |
| 10 | first-balanced | 3382 | 3755 | 373 |
| 11 | balanced-finish | 3755 | 4351 | 596 |
| 12 | conclusion | 4351 | 4669 | 318 |

## 画面约束

原题12球参与实际比较；未知轻重时不能把较重一侧全部认作异常候选。正常参照只能从已经观察的结果推得，未揭晓前不使用隐藏答案改变球外观。
每镜只突出当前比较及剩余嫌疑；分支切换回到对应前提，已结束实例不延续为第四称。具体动作以本轮Main.tsx、script.md和真实声音窗口为准。
抽象候选容量、完整决策表与称法构造留配套文章，视频不逐条搬演。

## 封面与资料附录

沿用上一修订的三比例封面JPG和poster，完整SHA及原始生成身份见input-provenance.coverReuse与cover-style.json，不重放已变化的共享封面目录。
正文后默认追加150帧原题/作者静态资料列表，计划总帧4819；实际区间、编码与媒体身份以新附录回执和render-result.json为准。
正式编码前先完成来源、类型、实际画面和时序检查，全部写入负责人停写后冻结。实际检查结果另留QA，不由本文件预记通过。
