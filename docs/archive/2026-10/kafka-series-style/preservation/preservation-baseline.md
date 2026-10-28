# 消息队列封面：独立保护基线

基线提交：`d7a5d7682080232617a03cc988b7c25cb50446f4`。当前消息队列系列只有1个已发布条目：message-queue / EP.10 / MQ入门，实际制作入口为`episodes-codex/message-queue/revisions/mq-intro/message-queue/remotion`。

- 保护1027个规范化路径：1021现存、6个原本缺失的显式可选候选。可选候选不冒充冻结缺失，任何后续状态改变仍报告。
- 旧根工程116条与当前revision161条冻结声明，合计277条全部存在且完整SHA匹配，无冻结缺失或不匹配。
- 保护全部MQ当前发布非封面文件、已跟踪生产/历史文件和两份manifest每条实际输入；旧根工程7张封面也保护。
- 保护190份其他系列发布封面/sidecar、29份既有共享封面文件（包括2个已有缓存），以及新合并puzzles正文cover-continuity源与5期当前发布文件224路径。
- 只允许替换当前制作revision目录7份旧封面输出及发布目录3份旧封面；10份旧图均记录完整SHA与Git blob，可由基线提交恢复。发布poster.jpg此前不存在，可新增。当前revision和旧根的Cover.tsx/covers.json/source-sha256及全部媒体/输入不能改。
- 两份冻结清单均只引用Cover/covers生成输入，不引用上述待替换的PNG/JPG输出；没有放宽真实冻结输入。

重复执行：`python3 /workspace/work/mq-cover-qa/preservation.py --verify`。首次重验通过。基线SHA：`83bdeb1abbb9df8ba4675855179580b477f16d9155a3d6fd4aae4013e32839b7`。

此基线不含新共享模板和当前新封面输出，不表示实际新图目视已通过，也不表示外平台封面已经修改。
