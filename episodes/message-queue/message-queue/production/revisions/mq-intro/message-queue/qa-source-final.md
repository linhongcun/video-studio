# MQ 入门最终来源与原理审查

- 执行者：Codex mq_primary_sources
- 日期：2026-10-27（北京时间）
- 结果：本次审查范围内未发现需要阻止编码的数据保证或来源事实问题。没有修改任何冻结输入。
- 范围：逐段读取当前article、script、research、references及references.md；读取Main.tsx的正常投递、确认、页面查询与积压计数分支；对三份保存官方源重新核对题名、原句、SHA-256和Git blob身份。

## 实际完成的检查

`node site/scripts/check-references.mjs --sources episodes-codex/message-queue/revisions/mq-intro/message-queue`

结果：Reference source preflight passed: message-queue, 3 source(s)。该自动检查只验证记录、证据及文章链接；本次另做下列上下文与机制审查。

| 核对项 | 当前文稿与Main表达 | 结论 |
|---|---|---|
| 受理与完成 | Main场景04先让保存回执抵达网站服务，再回复页面已受理；article明确为本例配置和受理条件 | 没有把任意confirm当作业务完成，也没有向任意故障推广 |
| 暂停前提 | 场景05明确尚未建立消费连接、7042从未被取走；ready任务继续等待 | 没有将处理线程暂停与尚未投递混为一谈；没有重投分支 |
| 保留条件 | article/research固定durable、non-exclusive、non-auto-delete quorum queue、persistent消息及手动ACK | 没有借exclusive临时队列说明离线持久保留；明确未演示Broker故障 |
| Consumer ACK | 场景07先产生业务成功结果，08确认只从消费者到队列；队列在信号抵达后结束未确认投递 | 没有画成ACK直接通知页面；已保存业务结果未随消息移除而删除 |
| 页面完成 | 场景09显示网站服务查询业务结果、返回后页面才完成；article说明这是教学应用设计 | 没有冒称RabbitMQ自带页面通知或自动证明外部业务成功 |
| 任务数量 | 场景10同时显示剩余未完成、已完成与原三条任务的关系；场景11使用独立流量示例，未完成量明确包含处理中 | 没有以消息被拉取作为业务完成；2n减n得到n是教学计数而非基准 |
| 数据保证范围 | article/research说明正常闭环、配置与资源前提，不承诺无限保留、无限积压、任意故障不丢或业务恰好一次 | 保留了入门所需边界，未将未做的失败实验写作已经验证 |
| 来源身份 | R1/R2/R3分别为Work Queues、Queues、Confirms；三条原题/机构/连续原句与固定源相符 | 三个保存源Git blob身份和引用SHA均通过，Queues/Confirms与同commit的4.4版本目录同blob |

Main读取行段：场景04为98–100行，暂停/恢复102–106行，业务及ACK108–114行，结果查询116–118行，排空120–130行，持续计数132–138行。定位仅对应下列受审字节，不代表其他版本代码已核验。

## 实际限制

这是一轮来源与代码/文稿机制审查，未运行真实RabbitMQ、未进行性能测量或Broker故障实验；未做ASR或全片人工听辨，也未在本任务中审看片尾实际视频、全片逐帧或线上媒体。自动来源预检通过不能替代这些检查。旧父工程冻结检查结果由根代理负责，本记录不冒称本代理重新执行过。

## 受审输入身份

- `article.mdx` · SHA-256 `ae6faaa620afae330fe67bd91f3ef034f7e8d668676340d0f38152ffb1e6820c`
- `script.md` · SHA-256 `d94fc80abe0e94eef45b90dffed122a41adab128893a5d9b36491d726013e9a4`
- `research.md` · SHA-256 `a88b94f244db08c3e84385370c655cdd7082c2008043ba17981b787c549838d5`
- `references.json` · SHA-256 `f858b2fb9ad1c03618dc9af05e7642b66fe979c179e4e8cb2e20558f51827946`
- `references.md` · SHA-256 `7f534438589592483b197f706386065ad7fec437f4ebb7afdc27fa15ed9c7b82`
- `sources/evidence.json` · SHA-256 `dbc6c28ccee6c52a0aeed74d55d8ac77fec486e18178c29656bc7eef1abd7258`
- `remotion/src/Main.tsx` · SHA-256 `7104090e41f8810064a00cf7877b8cc242b66102127dc4703ebfe89edcb161a2`
