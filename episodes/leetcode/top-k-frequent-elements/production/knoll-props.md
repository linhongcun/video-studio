# EP58 · LC347 制作说明

本期回答：只要频次最高的k个数字，为什么把候选里次数最少的放在堆顶。

1920×1080、30fps，沿共享 LeetCode 不可变 style-v1；Header 通过独立identity传入LC347，不修改历史身份。按 script.md 与 plan.json 的16镜制作，真实时序以共享冰糖句级TTS装配结果为准。输入为同一16项数组，k=3，计数1:3/2:2/3:1/4:4/5:5/6:1；节点始终“数字×次数”，数组索引与次数分开。

research/build_trace.py记录经典逻辑交换，与heapq完成态交叉核验；不声称画面是CPython临时空位赋值的逐行重现。新节点按层从左到右放入，只沿父链比较。超过k先显示4节点，再删除根；末位补根保持紧凑树形，与较少孩子比较/交换。移动节点沿分离弧线，文本跟随身份，不用数字大小代表频次。

正文两处关键代码按句切换；最后150帧是完整solution.py静态卡，字幕与voice PCM在此前结束。默认npm run render通过本期render.py与references_bt709.py，正文直接真实limited BT.709编码，参考资料同参数生成；执行资料预检、冻结核验、正文/混音/正文媒体检查、追加150帧title-author列表；交付只能用最终video.mp4。研究证据、原题与署名随references.json纳入冻结。

封面沿共享leetcode-covers模板，production/cover-inputs保存本期真实输入；只安装本期三比例。文章Figure图位在真实配音后、冻结前确定，最终编码后提取核验图。字体系统文件与仓内快照通过render-inputs/font-bindings.json逐项对应。

质量结论按qa目录实际记录；句级包络不是逐字ASR，信号/文本身份不能代替语义听辨。仅GitHub站点按持续授权交付，外平台未含在本次授权。
