# MQ15：一条记录如何跨过复制完成边界

当前生产输入使用root最终接受的D/storyboard.json：5460帧/182秒，voiceSHA256=388aa7072e3329d76360aca4063c20b901d642bdad256307869a40200286b9d9。字面@storyboard优先实际board；历史storyboard.prevoice.json及40张布局自采分别保留原身份，不作为最终时序证据。实际动作从两句localStart/localEnd计算，只称实测句包络，不冒称句内字词强制对齐。第9镜第一句内完成Fetch0→复制→追加→下一Fetch1报告，第二句保持完成判断与回应展示。

1920×1080 /30fps。只导入episodes/_shared/kafka-covers/style-v1.json字体及配色，不改共享style。页身#211D1B，面板#302823，正文#FFF1E8，次字#C3ADA0；主写入与记录副本橙#FFAE73，请求/进度报告蓝#93CCE5，确认完成绿#90D3AB，拒绝/缺失红#F78E82。记录ID始终用前景字色，不随边线降到低对比。

全局四段导航：主副本确认／复制进度／同步数量／确认边界。顶栏与末镜IT小村 · 原创留独立宽度。13镜保持同一P0的B1/B2/B3三个日志空间，网站发送结果置顶。第1镜任务区建立待解释的问题，不提前制造成功；第2镜从空日志正式展开对象与下一位置。第5、11、12镜明确同事件从空日志重新比较，不把前一分支的接收和故障结果补齐或复活。

每份日志位置固定在[x=100/710/1320,y=430,w=500,h=350]。真实原日志卡位于各panel内y=534，offset0追加后一直保留。下一位置是物理末尾；下方蓝字另列Leader已知的位置，二者从同一模型快照读取。第二份写好后下一位置1、Leader已知0的中间状态不能省。拉取响应仅移动小圆点代表字节副本，不把主日志卡拿走。复制请求和响应沿panel上方y=414保留通道；响应返网站沿左侧x=72通道，移动点不带文字，静态标签留在通道上方。

第6镜数量判断先通过，再追加并建立requiredOffset=1。第7镜Fetch0→复制响应→本地append；第8镜下一Fetch1抵达才改Leader已知，min(1,1,0)=0继续等待。第9镜第三份重复同一动作，报告后min(1,1,1)=1，先满足完成判断，再发回复、网站收到后才显示成功。第10镜是已收敛的故障点，对照clean新主保留E01，不演KRaft投票。第11镜同空起点稳定ISR2，复制与报告仍完整；第12镜稳定ISR1本次追加前拒绝，不能拿它代表所有失败。第13镜只画抽象职责与边界，不合并分支日志。

所有时点由sceneTiming(s)读取本镜voice两句localStart/localEnd生成，stateAt导出同源状态。只有未生成真实board时，才有明确PREVOICE估计fallback。Header、Caller、Foot完成词随状态守卫；请求在途、响应在途、Future成功是不同展示点。默认烧录字幕，Main同时支持showSubtitles:false/hideSubtitles:true；正式有音轨才加载Audio，prevoice缺audio有显式编译守卫。

独立QA可读data-model-state、data-branch、data-reset-before、data-leader、data-isr、data-hw、data-leader-known-next、data-required-offset、data-producer-future/response、data-admission-passed、data-business-complete；每份日志另有data-replica/role/available/records/physical-next/leader-known/local-hw，原记录有event-id/offset/value。移动体data-moving-body、data-from/to；仅record-copy带data-moving-record=E01。文字data-text/data-copyfit保留。无浏览器外壳、无真实URL假界面、无全类名巡览。

本期默认render由薄包装进入共享pipeline：正文H264后实际pc601→limitedBT709转换及混音，再追加同色title-author资料；预演PNG不代替实际编码颜色、字幕和成片复核。5份原题/机构资料默认两页，每页5秒，实际帧数与媒体由root正式编码后核实。4Figure已按最终声轨固定整数帧1621/3281/3732/4964，seconds=frame/30及article seekTo一致；尚待编码后实际抽图与逐张验收。
