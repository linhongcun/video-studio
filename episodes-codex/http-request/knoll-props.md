# EP.01 HTTP请求：技术细节版制作说明

本轮由用户观看反馈触发（#283），17镜34句，5406帧/180.2秒，1920×1080、30fps。沿同一shop.example/products/42商品页，四段总览中建连接展开TCP与TLS。

真实配音SHA-256：`60d4b10d0e57abea68918ed576086721c50ddcb50cdef422956707b229e0f53a`；脚本SHA-256：`fae264f755fd010023d2a9d76ff271d2ea8e3a30638b860d5e6ed78df30f8ff1`。声音不变速；只记录句级真实边界与声学起音，不声称逐字ASR或人工听辨。

## 当前实现

Main.tsx读取冻结分镜并以整轨从0帧播放。Scenes.tsx按production.json的slug定位画面；句首cue启动术语标题，第二句边界驱动后续动作。导航由五个具体阶段组成，TCP/TLS用括组归入四段总览的建连接。HTTP/1.1请求与响应是两处报文节选，明确为TLS解密后的教学明文。

三次握手沿固定两端逐镜保留：SYN seq1000；SYN+ACK seq5000 ack1001；ACK seq1001 ack5001。客户端收到第二次有效报文时进入已建立，服务端收到第三次才进入。09明确为同一第三次报文的解释回看。资源请求复用原连接，样式先返回、图片延续到布局绘制时才补齐。DOM/CSSOM节点对应原商品页标题/价格/按钮。

## 时序

|镜|slug|起帧|帧数|画面类型|
|---|---|---:|---:|---|
|01|hook|0|233|browser|
|02|overview|233|386|canvas|
|03|url|619|285|canvas|
|04|dns|904|272|canvas|
|05|tcp|1176|245|canvas|
|06|syn|1421|292|canvas|
|07|synack|1713|389|canvas|
|08|ack|2102|297|canvas|
|09|why-third|2399|248|canvas|
|10|tls|2647|312|canvas|
|11|request|2959|345|canvas|
|12|response|3304|264|canvas|
|13|resources|3568|360|canvas|
|14|parse|3928|336|canvas|
|15|paint|4264|337|browser|
|16|variants|4601|371|canvas|
|17|recap|4972|434|canvas|

## 冻结与出片

所有写入方停写、真实动态复核闭合后执行freeze.py；该入口写入storyboard快照、public分镜占位和source-sha256.json。再运行preflight.py、共享whole铺轨检查和label_onset_strict.py。正式产物由remotion/package.json的render脚本先编码H.264、再经共享mix_bgm.py混到−16LUFS；audit_encoded.py逐文件复核冻结清单、帧数、全解码、音量并抽编码帧，实际视觉仍需独立查看。

封面三尺寸由covers脚本读取production和covers.json产生。4:3内容在x315..1125、y<918；本轮只上站点，历史平台链接保持。修前输入/技术检查以revisions/technical-depth-v2/与Git基线追溯，新版检查不能改写用户否定旧版深度的反馈。
