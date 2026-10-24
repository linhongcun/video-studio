# 策略模式新手版：真实时序与无字幕过程

2026-10-25（北京时间）。只对应13镜26句的新手重排版；旧16镜与三镜桥接报告保存在历史目录，不作本轮结论。

## 最终来源与执行

最终all预检为remotion/out/beginner-final-preflight-all/frames.json，生成130图；关键过程为beginner-final-preflight-motion/frames.json，生成53图和06–10五段连续MP4。两命令exit0，provisional:false，COPYFIT零，composition最终props为hideSubtitles:true/showSubtitles:false，QA媒体无音频。完整样本与源SHA见qa-motion-samples.json。

Root实际查看03-316、05-178、06-289、07-264、09-217、10-361共六张最终源图，并保存原图及索引qa-root-beginner-preflight.json。独立质检另实际查看全13镜25图，从五段实际连续MP4自行抽取16中间态并查看；具体范围和各源SHA见qa-teaching-beginner.md，不将参数或文件数当作已观看。

## 动作判断

- 03明确会员函数作用示例；05开始新结算，清掉之前示例结果。
- 06传入函数本身，金额结果尚未产生；函数名称与金额保持不同身份。
- 07先对应金额参数，再对应当前函数；箭头从实际10000/member文字区域分别指向amount/pricing，没有复制第二套算法。
- 08先调用，再计算9000分、返回90元；09先清旧结果，再换活动函数，原输入始终10000分。
- 10重新执行活动得到8000分/80元，会员不执行、折扣不叠加。
- 11回收选择/调用/计算，12–13只讲维护与阅读成本，不重新加改价/新增支线。

Main与QA事件共用motion.ts的beat窗口和实际状态阈值，保证采样覆盖开始、进行中与落定，而不是只列理论时间。视觉自检曾发现pre-line吞掉Python前导缩进，已将mono文本设为pre并实际复验；root补data.ts传递当前章名，并在最终预检前停掉旧批次、重跑当前最终源，旧批次不计本报告证据。

## 结论与限制

本轮真实时序与独立连续预编码检查通过，可对137项已冻结输入正式编码。正式媒体另从实际成片复核，见qa-final.md与qa-teaching-beginner.md的最终段。此报告不称全片人工听辨或新手理解实验，也不预记用户认可。
