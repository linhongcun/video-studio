# TCC：核心资料核验

访问2026-10-24（北京时间）。实际打开下列官方正文，先核对机制再写分镜；旧EP.21只作代码布局参考，不是技术出处。

| 资料 | 实际阅读范围 | 本期使用与边界 |
|---|---|---|
| [Apache Seata：TCC用户文档](https://seata.apache.org/docs/user/mode/tcc/) | Overview、Disadvantages、Overall Mechanism、Basic Usage | 业务代码提供检查/预留、确认、取消动作。预留后择一确认或释放；不是三个动作都顺次执行。需要侵入业务设计，不当作数据库通用自动回滚。 |
| [Apache Seata：TCC开发文档](https://seata.apache.org/docs/dev/mode/tcc-mode/) | 分支事务自定义prepare/commit/rollback行为 | 本地资源操作由业务实现，分布式协调与单个数据库悬挂事务不是同一层保证。本文不把Seata实现当唯一TCC实现。 |
| [Apache Seata：TCC Fence](https://seata.apache.org/blog/seata-tcc-fence/) | 2022-06-25正文，Try本地提交、幂等、空回滚、悬挂、状态表与业务共同本地事务 | 预留是真的持久化；二阶段通信可失败并重试，同一操作不能再产生副作用。Fence的具体表/版本只作公开实现例子，不声称所有框架自动覆盖业务幂等。 |
| [AWS：Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) | Retrying and side effects、Reducing client complexity | 没收到回复不等于未执行；重复请求需要保留同一操作标识，避免第二次业务效果。本文仅借此交叉核对重复确认/释放语义。 |

镜01直接售出而整单失败是明示错误示例，不是推荐实现。镜03–05依据Try检查并持久预留；镜06–08依据有效预留后的确认及重复保护；镜09–12独立重置，取消只释放本单预留。镜13–14说明业务接口和恢复责任。

订单8124、商品7042、可用4/预留0/已售0、购买1件全部是本片教学设定，不是官方性能或行业数字。正确分支均守恒4：成功4/0/0→3/1/0→3/0/1；取消分支重置后4/0/0→3/1/0→4/0/0。其他业务写入路径也必须遵守预留约束，不能绕过业务规则直接消耗已预留资源。

不使用无依据的“性能提升”“锁更快”“无阻塞”等比较。确认/释放仍可能遇到故障，需要按持久决定恢复；不能收到超时就擅自改走另一结局。空回滚、迟到Try、并发重复的复杂实现放文章，视频不铺术语表。


## 片尾参考资料

以下列出本片采用的2项核心官方资料，技术正文均沿用2026-10-24（北京时间）的实际阅读记录。本轮于2026-10-26另补Seata官方仓库中的完整题名及Fence文章的明确作者；题名补证不等于重新核验技术正文。原文章、研究记录和旧脚注全部保留。

旧技术实读记录固定于提交`656b525f533037f1c0dff6383c4afa69926e612c`，Git blob SHA-1 `99fbebecf13cf0d2d029a7db8e1fb60f9306bcea`，完整旧文件SHA-256 `3e06809700ff7d02f37a2e4539380a0012f05b0dd15a291112aab324cd3f3fbb`。本仓固定Git链接仅称“既有实读记录”，不冒充官方原文快照；实际题名补证的固定Apache提交、HTTP200、完整响应SHA及frontmatter位置见`docs/reference-endcards/batch-7/sources-tx-tcc.json`。旧研究没有保存的官方全文SHA和当日上游提交不补造。

- [R1] Seata TCC Mode — Apache Seata（发布机构：Apache Seata）；技术实读2026-10-24；对应原研究第7行。支持：业务实现Try检查并预留资源，再根据协调决定选择Confirm或Cancel；确认与取消是互斥结局，不是三个动作依次全部执行。；TCC要求业务提供相应动作及资源约束，不能把给远程接口加标记当成通用数据库自动回滚。 边界：Seata是本片引用的公开TCC实现，不是唯一实现；不采用文档中面向所有系统的性能或适用性口号。；保留本片订单8124、库存4及购买1件的教学身份，不当作官方案例或实测。
- [R2] Alibaba Seata Resolves Idempotence, Dangling, and Empty Rollback Issues in TCC Mode — Zhu Jinjun（发布机构：Apache Seata）；技术实读2026-10-24；对应原研究第9行。支持：Try需要真正提交业务预留，相关控制状态和资源修改需要正确原子衔接。；具体Fence实现展示对幂等、空回滚、悬挂问题的处理；重复确认或释放不能再次改变资源数量。 边界：仅作公开实现参考，不根据标题中的Resolves推导所有框架、版本或业务代码天然正确。；确认与取消需要依据持久决定恢复，不能因一次超时擅自切换结果；其他写入路径仍需遵守预留约束。；旧文的1.5.1版本及具体Fence表不作为当前部署默认值。

现行用户文档明确要求业务实现Try、Confirm与Cancel，提供本片主机制依据；Fence采用官方英文原题与明确署名Zhu Jinjun，保留2022历史材料“仅参考”边界。用户和开发文档的实际完整题名同为Seata TCC Mode；本轮开发文档已补取题名证据但不上片尾，以免重复书目，旧技术记录保留。AWS文章的既有笔记未保存个人署名，这不等于原文没有署名；本轮未核定其明确作者，因此不加入新片尾，原研究与原文章脚注保持不变。现有导航记录仅说明沿用前轮技术事实，不将视觉QA转写成新的官方正文读取。
