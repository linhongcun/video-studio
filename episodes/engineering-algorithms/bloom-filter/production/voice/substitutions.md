# 配音选段与替换记录

本期真实合成31个候选，最终26句选择22a、3b、1c。首次26个a候选的来源请求和raw→48k PCM转换均匹配，4句因裁尾后至少0.50秒低电平区间追加b；02-bits-1再追加c。原始失败/警告记录保留在qa-voice-takes-a.json与qa-voice-takes-b.json，最终qa-voice-takes.json为0失败、0警告。

没有修改脚本、字幕或送模文本；b/c只调整合成风格以比较信号连贯性，最终选段见picks.json。未加速语音，停顿由本期params.json和共享build生成。

共享build、assemble、whole铺轨、严格起音和句级检查均已实际运行。未执行逐字ASR、语义听辨或全片人工听辨；信号检查不能证明具体读音，完整成片混音与编码仍需另验。
