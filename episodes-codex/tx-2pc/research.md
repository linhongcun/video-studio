# 两阶段提交：权威资料与主张边界

访问日期：2026-10-24（北京时间）。本次实际打开并阅读下列公开官方正文，不以旧视频或搜索摘要作引用。每一集只讲一个机制；“常见”指成熟文档体系中的基础协议，不提供市场占有率结论。

| 资料 | 实际阅读段落 | 本期用途与边界 |
|---|---|---|
| [MySQL 8.4 XA](https://dev.mysql.com/doc/refman/8.4/en/xa.html) | Resource Manager/Transaction Manager，以及两阶段流程段落 | 先准备并收集结果，再共同决定；参与资源必须支持相关协议，XA接口不与2PC并列当另一算法。 |
| [MySQL 8.4 XA状态](https://dev.mysql.com/doc/refman/8.4/en/xa-states.html) | PREPARED、COMMIT/ROLLBACK、RECOVER与detached段落 | 准备状态可恢复，最终按决定终结；不把连接断开画成自动撤销。 |
| [PostgreSQL PREPARE TRANSACTION](https://www.postgresql.org/docs/current/sql-prepare-transaction.html) | Description与Caution | prepare的状态可靠保存，尚未提交，锁继续持有；长期prepared会妨碍运行。只转述机制，不给出自行手工操作生产待决事务的建议。 |
| [PostgreSQL Two-Phase Transactions](https://www.postgresql.org/docs/current/two-phase.html) | 两阶段事务和外部事务管理器段落 | PREPARE/COMMIT PREPARED/ROLLBACK PREPARED及恢复状态。支持范围与使用责任重要，不是普通远程调用自动获得全局事务。 |
| [Narayana项目文档](https://www.narayana.io/docs/project/index.html) | Two-phase commit overview、Failure Recovery中的稳定决定与恢复段落 | 协调者提交决定先稳定记录，恢复后按既有决定完成，不可随参与方各自超时改成相反结果。正文为当前项目文档，不据页脚猜首次发表年份。 |
| [Oracle当前Distributed Transactions Concepts](https://docs.oracle.com/en/database/oracle/oracle-database/26/admin/distributed-transactions-concepts.html) | Prepare Phase/Commit Point Site/Commit Phase | 交叉核对准备节点承诺等待共同结果，以及各节点提交存在先后。Oracle有commit-point优化，本片不照搬成泛用2PC步骤。 |

## 逐镜映射

- 01–02：两独立本地结果可能分离；基础2PC以协调协议共同收尾。MySQL XA正文；示例订单8124、商品7042、库存4买1为教学设定。
- 03–04：待确认修改及可靠准备状态先于就绪回复，不把拟改3画成已保存3。PostgreSQL PREPARE与MySQL两阶段描述。
- 05–08：可靠共同决定在前，参与方分别落实在后；完成结果不等同同一毫秒可见，也不自动提供跨库全局快照。Narayana、MySQL、Oracle交叉核对。
- 09–10：决定保存以前有参与方拒绝则整体放弃，撤销尚未提交状态。MySQL XA。
- 11–12：已准备而共同决定未知不能自行猜回滚；故障恢复按可靠原决定处理。本例动画揭示故障前已记录保存决定，不表示重启后临时作出相反选择。Narayana、Oracle与PostgreSQL。
- 13–14：准备期间占用锁与资源，需受支持资源、及时恢复及运维。PostgreSQL Caution。

未采用任何无来源性能、普及率或厂商对比数字。未引入3PC、共识提交或产品模式列表。本资料核验不代替真实配音、动画及最终编码检查。
