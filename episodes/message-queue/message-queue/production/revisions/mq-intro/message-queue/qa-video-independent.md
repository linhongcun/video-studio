# MQ入门改造：最终编码视频独立抽检

2026-10-27，执行者为Codex独立制作审查代理`mq_production_audit`。本报告检查交付的实际`video.mp4`，采用逐镜代表帧与关键落点抽检；不把Remotion预览截图当成正式编码结果。

## 结论与媒体身份

实际查看35张从最终MP4解码的1920×1080图片，覆盖12镜各两处代表点、06/09/10动作落点、正文末帧和资料卡首中尾。在该有限范围内，字幕、任务身份、业务状态、计数和资料原题及机构署名清楚，无新增阻断问题。没有修改冻结输入或重新渲染。

- 最终文件SHA256：`639d373be2afe007440e31a6877609c2b883bcc7a0af213a535b8caf4783b52e`。
- 文件大小：6,430,510字节；H.264，1920×1080，30fps，共3700帧，123.333秒；AAC为48kHz立体声。
- 正文3550帧，资料卡150帧；资料从全局帧3550开始，持续5秒。帧号从0开始，时间为帧号÷30。
- [抽检清单](qa/encoded/manifest.json)记录35个实际查看帧、各PNG的SHA、字幕预期及ffprobe元数据；[回执交叉核验](qa/encoded/receipt-check.json)保存最终文件身份与所读技术回执的文件SHA。

抽帧使用ffmpeg对实际编码文件按帧索引一次解码选取，随后用`view_image`实际打开每一张；未再调用Remotion生成本报告图片。保存于`qa/encoded/`的35张PNG均已实际查看，并重新核对各文件SHA与最终视频SHA。

## 实际查看范围

下表每镜两张代表图取自两句旁白对应的中部。实际看到的中文字幕完整落在画面内，未发现截字、挤压、错字或遮挡核心对象；订单数字7042/7043/7044与字幕中口述数字对应。

| 镜头 | 实际编码代表帧 | 检查结果 |
|---|---|---|
| 01 submit | [119](qa/encoded/frame-00119.png)、[290](qa/encoded/frame-00290.png) | 同一7042已受理，后台尚未完成；引入问题明确 |
| 02 burst | [413](qa/encoded/frame-00413.png)、[552](qa/encoded/frame-00552.png) | 三笔教学订单与后台单笔处理能力可辨认 |
| 03 roles | [705](qa/encoded/frame-00705.png)、[851](qa/encoded/frame-00851.png) | 队列、网站服务、后台的对象身份清楚；字幕完整介绍生产者和消费者 |
| 04 accepted | [1079](qa/encoded/frame-01079.png)、[1235](qa/encoded/frame-01235.png) | 保存回执与页面受理能区分；未把受理写成业务完成 |
| 05 pause | [1381](qa/encoded/frame-01381.png)、[1512](qa/encoded/frame-01512.png) | 7042仍留在等待队列；消费者暂停前尚未接收该任务 |
| 06 resume | [1651](qa/encoded/frame-01651.png)、[1769](qa/encoded/frame-01769.png) | 同一7042从队列到后台，7043/7044等待；移动期间没有旧状态文字遮挡 |
| 07 work | [1901](qa/encoded/frame-01901.png)、[2021](qa/encoded/frame-02021.png) | 处理过程与业务成功有区分；送出任务未被直接视为完成 |
| 08 ack | [2143](qa/encoded/frame-02143.png)、[2254](qa/encoded/frame-02254.png) | 处理确认返回队列，页面仍为已受理，未画成ACK直接通知页面 |
| 09 result | [2386](qa/encoded/frame-02386.png)、[2521](qa/encoded/frame-02521.png) | 网站服务发起结果查询，返回途中页面仍为已受理 |
| 10 drain | [2661](qa/encoded/frame-02661.png)、[2803](qa/encoded/frame-02803.png) | 输入已停止；剩余7043/7044继续处理，7044运输卡无遮挡空态文字 |
| 11 growth | [2978](qa/encoded/frame-02978.png)、[3136](qa/encoded/frame-03136.png) | 另起教学情景并重新计数；第0/4秒完整窗口分别为进入0/8、完成0/4、未完成0/4；“含排队与处理中”“容量有限”可读 |
| 12 recap | [3294](qa/encoded/frame-03294.png)、[3440](qa/encoded/frame-03440.png) | 受理与完成两种状态及后台能力边界清楚 |

另实际查看以下关键状态：

- 06投递落点[1698](qa/encoded/frame-01698.png)与镜末[1843](qa/encoded/frame-01843.png)：7042到达后台，其他订单留在队列，已开始处理；与前期预检的修复结论一致。
- 09查询返回完成[2562](qa/encoded/frame-02562.png)：页面此时才显示“处理完成”，任务仍为7042，业务结果来源明确。
- 10相邻完成边界[2797](qa/encoded/frame-02797.png)→[2798](qa/encoded/frame-02798.png)：7043从处理中到已完成，未完成2＋已完成1转为1＋2；7044同时开始投递，计数没有提前减少。
- 10最后完成边界[2865](qa/encoded/frame-02865.png)→[2866](qa/encoded/frame-02866.png)：7044完成后才变为未完成0＋已完成3，待处理与投递未确认均为0，原三笔订单全部有身份记录。

这些静图检查可确认指定落点和相邻状态；不据此声称检查了其间所有动画帧。完整动作轨迹的有限预检范围、两处原遮挡与修复证据另见[动态预检](qa-motion-independent.md)。03角色标签在第二句结束后完整显示71帧的结论来自该预检；本报告的03两张中部抽帧未单独重新测量标签出现时刻。

## 资料附录与正文边界

实际查看[3549正文末帧](qa/encoded/frame-03549.png)、[3550资料首帧](qa/encoded/frame-03550.png)、[3625资料中帧](qa/encoded/frame-03625.png)、[3699最终帧](qa/encoded/frame-03699.png)。正文在3549仍为总结，3550起切到“参考资料”，正文字幕不残留。首、中、末三个资料画面中，以下原题及RabbitMQ机构署名均完整、可辨读；最长第三题未被截断：

1. `RabbitMQ tutorial - Work Queues` — RabbitMQ。
2. `Queues` — RabbitMQ。
3. `Consumer Acknowledgements and Publisher Confirms` — RabbitMQ。

与[资料源清单](references.json)及[附录回执](reference-appendix.json)一致。资料页采用原题＋机构，没有显示正文摘录或不存在的个人作者。原题在附录中的5秒停留允许暂停查阅；本报告没有做观众阅读速度测试。

## 技术回执的实际核对及能力边界

实际读取并核对[渲染结果](render-result.json)、[编码媒体检查](qa-encoded-media.json)、[附录保留检查](reference-appendix-media-check.json)和附录回执。最终文件实算SHA、大小及ffprobe与回执一致；3550＋150＝3700，视频流时间线连续。已完成回执记录整片全解码通过、响度−16.0 LUFS、真峰值−3.8 dBTP；附录保留检查记录正文逐帧和时间戳相同，5548个AAC包及时间相同，解码PCM SHA为`2adddb98ab8992cba19691c485631352d8a52647829a9e7bcbdfd47e1fdb4f38`。音轨保持原118.336秒结束点，资料附录未增加音包。

这些全解码、响度与流保留结论复用已经完成的实际回执，没有重复宣称独立重测。本报告新增的是最终文件身份交叉核验与35张实际编码图片的视觉抽查。没有进行全片按真实时间连续观看、人工逐句听辨、逐字ASR、真实Broker实验或观众理解度验收。站点播放器和浏览器交互由主代理另行核验，不在本报告的通过范围内。
