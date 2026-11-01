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
