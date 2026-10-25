# D03独立预检

状态：通过，gateReadyForFreeze=true。产品小标签修订已定向独立复核关闭，可进入冻结及正式编码。

执行者：`/root/observer_qa`。只写独立报告及解码证据，没有修改制作输入或重渲未变小样。

- 文稿概念门及正式24句身份通过，实际Java编译运行12组行为与21行同源卡通过，见`qa-editorial-independent.md/.json`。
- 本轮实际33张MP4解码帧、8张状态PNG检查通过，精确范围见`qa-motion-independent.md/.json`；动态不靠字幕解释，只有同一订单17、地址、正文与Q17的一次请求回放。
- 三种最终封面PNG/JPG均实际查看，主次文字清晰，无截字；所有文件SHA与`cover-copyfit.json`对应，COPYFIT为空。
- 4:3封面实际布局与配置一致：文字区域x315..1125、底部小于918，配置中所有textBoxes的边界逐项满足安全区；Cover.tsx也检查实际DOM相同区域，制作报告无COPYFIT。独立未重新渲染封面。
- 真实body为5121帧，加150帧静默Java得到5271帧。只读核对`qa-java-endcard.json`：前缀PCM精确、240000尾样本全零、旧句界不改、whole偏移0、唯一术语cue1194对起音1194.72差−0.72帧。这是制作方工具报告，本独立没有重复执行或声称全片听辨。
- v1 metadata漏列components已披露。独立核对真实归档字节及09唯一局部diff，支持两支未变小样复用；最终09取v2。未回填历史manifest。

已关闭：ProductPanel单处文本改为“订单状态：已发货”。实际查看当前01-391/08-340/09-0三张图，无碰撞或截字；独立确认精确差异只有这个文本节点，当前全部源及manifest/PNG SHA匹配、COPYFIT为空。此前33张真实小样帧的有限因果检查按纯文案变更继续沿用，未重跑旧clip或改贴旧源身份。完整关闭证据在qa-motion-independent.md/.json。

后续仍须freeze后正式编码、真正MP4及发布检查。本轮没有ASR、全片听辨或真实初学者实验。
