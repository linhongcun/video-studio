# Kafka规划issue已应用回执

9个现有开放issue（#308、#310–316、#323）按root审查后的草稿更新title/body，逐条PATCH后重新GET，标题及正文完整SHA与草稿完全相符；issue状态全部保持open。无并行冲突，未发评论、创建或关闭issue，未触及closed #309或14个取消issue。

全部草稿先验证draft-manifest预期文件/正文SHA；9条首次GET均与旧title/bodySHA一致；每次PATCH前再GET并重复旧值匹配。请求文件issue-N-patch.json均仅title/body两键，完整preflight、before、patch-response和readback响应保留，汇总见application-report.json。

#308状态仍按已审草稿记录Kafka版MQ01制作中、其他8期未开工；正式上线之后由root按真实交付更新，不提前记为完成。
