# EP.21 · Outbox：制作说明

2026-10-24，首次独立单机制短片。14镜28句、3499帧（116.633秒），画布1920×1080/30fps；镜内帧从0起。storyboard全文SHA `b87d09750f92d0b0dcbfc6968b8fde7f3fd69c03c8fb26a3922e56e06a4342c4`，音轨 `136ff7fe37a5834a407e69b428ba9041cd9d0dfb895d8a9be8a76a09e726aba0`，脚本 `f765c0fd52937ecfabff0c335d55af5100b52218e57ae2dc2514a8b39d0d4af7`，covers `8a93c5c1136c90241d298d80aeec9bdd584f511cc60ec2d81b40e0e78d5e5bdb`。冻结由root通用freeze执行，当前说明不是提前认可旧媒体。

## 主线与具体对象

订单8124、事件E8124、商品7042库存4买1。生产端订单和待办共同保存，relay独立读取/发送/标记结果；发送后标记前崩溃可重发同一E8124。消费端库存扣减和唯一处理标记共同保存，重复后仍3。生产与消费边界分开，不画成跨队列的一次原子提交。业务拒绝另起缺货0分支，不靠无限重试自动成功。

## 布局与连续动作

- 顶部左[100,54]片章分类；白话章节[100,103]；右上IT小村与示例角标。
- 标题[130,190]46px；分支重置[130,276]23px；说明带y805、31px；字幕带[130,925,1660,至少100]40px；片尾原创y880。
- 生产端共同边界[235,365,1450,390]，订单与待办分别在x520/1400，中心状态条y258确保边界标题345上方留23px。
- 发送段待办x435、发送程序x960、队列x1480；消息沿y575路径进入队列，确认沿y665返回，再标本地结果。消息不因程序停止从队列消失；恢复重发抵达后第二个同ID副本出现。
- 消费端边界[975,345,780,425]，库存x1220，唯一标记x1560；状态条y241到305，与边界label325留20px。输入消息从左侧410沿路径进入；候选标记在消息抵达后才生成，库存与标记在共同提交帧同时变更。
- 所有示例分支先明确重置/回看起始条件。消息副本同ID是实际重发含义，不将它当成新订单；演员发送程序只保留一个。

## 真实事件帧

| 镜 | 绝对起点 | 帧数 | 事件（镜内帧） |
|---|---:|---:|---|
| 01 | 0 | 233 | send-path-stops=72 |
| 02 | 233 | 251 |  |
| 03 | 484 | 226 | order-candidate=24；event-candidate=69 |
| 04 | 710 | 230 | producer-joint-commit=56；application-stops-records-survive=149 |
| 05 | 940 | 226 | event-write-fails=56；producer-both-rolled-back=153 |
| 06 | 1166 | 226 | relay-reads-durable-event=169 |
| 07 | 1392 | 245 | broker-accepts-event=78；relay-records-sent=178 |
| 08 | 1637 | 280 | relay-stops-before-sent-mark=184 |
| 09 | 1917 | 258 | same-event-republished=73；duplicate-awaits-consumption=159 |
| 10 | 2175 | 285 | consumer-candidate-created=84；consumer-joint-commit=198 |
| 11 | 2460 | 226 | consumer-first-candidate-created=36；consumer-retry-candidate-created=152；consumer-both-rolled-back=67；retry-consumer-joint-commit=178 |
| 12 | 2686 | 271 | duplicate-recognized=192 |
| 13 | 2957 | 266 | reset-to-business-rejection=145；business-rejection=202 |
| 14 | 3223 | 276 | focus-relay=74；focus-consumer=151 |

以上由实际motion.ts的events函数导出，不另写一份声学算法。首次Outbox/幂等标签只读取cueFrames.labels，句首声学strict0失败0例外、完整至少63帧；字幕照真实句级from/to，不猜句内字级时刻。

## 封面与实际预检

16:9、4:3、3:4由本期Cover.tsx和covers.json产生。4:3内容x315..1125且最末文字底904<918，三构图PNG/JPEG尺寸已核对；poster与3:4 JPEG相同。无浏览器、假设备、实物比喻、DevTools或大面积白底；boxShots为空，以业务记录/消息和动作承担解释。

首轮真实音轨预演前发现10顶部状态条与边界标题净距不足，已上移；候选标记生成与消息抵达、重发抵达与队列副本出现也统一到事件点。后续以最终同bundle预演及独立审查、实际编码抽帧闭合，不用此说明替代检查。未执行逐字ASR或全片人工听辨。
