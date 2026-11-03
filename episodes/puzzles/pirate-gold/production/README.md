# P09 · 五个海盗分金币（制作草稿）

本轮从最新主干 `2159b75f8eb2fc246b7ff0174c31ac8542f97de6` 开工，选择 [#213](https://github.com/linhongcun/video-studio/issues/213)，计划EP54／趣味推理P09／pirate-gold。当前仅为新期草稿，不是成片；不沿用P07的配音、时序、冻结、媒体或QA身份。

已完成两项公开来源实读、14镜28句脚本及独立静态审读。人数、金币与投票规则的精确核验已在OpenAI functions V8执行：110个小规模案例；100枚金币下1至5人、半数与严格多数两种规则逐一穷举分法。五人局每种规则各检查4,598,126个分配，主模型最高98，严格多数变体最高97，后者仅进文章。实际能力范围见model-verification.json。

## 当前阻断

本轮完成开工fetch和本地建分支后，所选云环境变为unavailable。exec_command明确返回“No usable execution environment”。控制面running/connected不代表当前命令工具可用。root已请求恢复环境；其间用GitHub连接保存可复核的文本草稿。

配音、音频/实际分镜装配、真实无字幕小样、COPYFIT、封面、冻结、正式编码、站点与线上检查尚未运行。不能把静态审稿或V8数学核验写成上述步骤已通过；两张Figure的0秒图位仍是草稿占位，冻结前须换成真实音轨中的稳定时点。

## 恢复后继续

1. 检查本地未提交工作，fetch并快进到此制作分支；重新核对origin/main与EP/版本占用，不覆盖其他工作。
2. 按当前保留工程的锁文件安装新期依赖，复用共享TTS、整轨、起音、冻结及附录工具；按本期人数、提案、否决后所得和选票重新设计动画。
3. 可在Node复验数学并另存新回执（不要把V8记录改称Node已跑）：`node verify_model.mjs --out model-node-replay.json`。
4. 完成来源预检、冰糖配音、实计时分镜与独立动态；所有金币投票前为拟分配，通过后才确认为实得。1—5号身份固定，每一假设局明确倒推，不画先真实出局再复活。
5. 定好文章实际图位与共享紫色三比例封面，停写并冻结后渲染正文＋5秒原题/机构参考列表；实际确认烧录字幕后设置发布metadata的burnedInCaptions。
6. 完成成片、站点、Release后部署与普通canonical完整SHA核验，再按持续授权以completed关闭#213并同步#204。当前不关闭、不发Release、不合并main。

正式依赖与命令以恢复后的当前源码为准，不伪造本期尚不存在的渲染器入口。首次公开再填写publishedAt和firstRelease，站点版本不在草稿阶段预占。当前publication/meta.json仅draft:true，省略未产出的video/poster；sourcePath暂指真实production文稿目录，建立动画后改为实际入口。
