# P03量水题：v0.61.0已交付

已完成制作、合并、Release、Pages与线上完整核验。本期仅发布GitHub站点。

[观看视频与文章](https://linhongcun.github.io/video-studio/episodes/water-jug/)。内部EP30／趣味推理P03，12镜24句、四章，4977帧／30fps，约2分46秒；1920×1080／H264／AAC48kHz，−16.0LUFS／−3.7dBTP。

## 发布身份

- [制作PR #256](https://github.com/linhongcun/video-studio/pull/256)合并提交`1b2ab500b8f304a7a97ae698caf2fd39f5ab7c4b`。
- [v0.61.0附注tag及Release](https://github.com/linhongcun/video-studio/releases/tag/v0.61.0)准确指向该提交；tag对象`0b8d55444dc2a44be2fa96f469cf1b2213310b30`，Release id423100441，UTC02:16:39发布。已有标签未移动。
- [Release后Pages40153856609](https://github.com/linhongcun/video-studio/actions/runs/40153856609)成功，head同上。build UTC02:16:58—02:19:58，deploy02:20:02—02:20:18。生产合并使用[skip ci]省略Release前重复部署，手动工作流完整执行安装、构建、上传与发布。
- 发布前整合v0.60.4，保持退役Agent两期删除及其他课程变更；冻结源交集为空。发布后保留同事新增的设计模式观看反馈提交ff730833…adc73，不覆盖其文档更新。

## 线上结果

北京时间`2026-10-25T10:22:14.226868+08:00`，首轮9个普通站点canonical GET全部成功：完整视频/海报SHA及字节、24句VTT逐字节、四章起点0/907/2042/3587精确frame/fps、普通文章证明与LC365锚点、源码、三课独立目录、首页/系列/学习/RSS及真实v0.61.0新增日志一致。

- 视频7,345,199字节，SHA256：`f5462dc2f399f9aaaee666e8f14c2df2a737f1a58a51d347a8067fedc235ef63`。
- 海报104,418字节，SHA256：`b739867e4162493be807a561b7f4319cf346969cb85ae6c45cddd64a2c58bfcb`。
- VTT2,422字节，SHA256：`ff98f106236cb06d056d35bb157234649951e6ed2a219906a086b21597758951`。
- [制作issue #207](https://github.com/linhongcun/video-studio/issues/207)核验后已completed关闭；[总览#204](https://github.com/linhongcun/video-studio/issues/204)同步已完成3题，剩余7题待安排。

部署观察期间，本地GitHub CLI/API返回401；现有GitHub connector仍可用，已通过它确认完整部署结果并独立读取真实Release。报告将9次站点HTTP GET与1份connector Release证据分别计数，不声称10次本地HTTP请求，也未修改身份、代理或CA。没有cache-bust、Range、强制缓存或站点重试，未保存远端媒体。详见online-verification.json、release-connector.json、deployment.json与issue-completion.json。

本地数学、实际动态、正式媒体、130冻结源、配音与两视口范围见qa-final.md。制作检查未执行ASR、全片人工听辨、完整实时观看或初学者实验；用户后续观看反馈见下节。

## 用户观看反馈

2026-10-25，用户实际观看本期v0.61.0，评价大小壶互倒动画“挺流畅”“挺准确”，并表示“整个视频就很清楚地说明了这个比较绕的逻辑”。记录为对本片动态表达与讲解清晰度的定性认可，与原有数学、媒体检查分开；不扩大为普遍学习效果、其他题目的效果保证，也不替代制作人员未执行的检查。可复用做法补入项目经验S004。
