# tx-tcc 片尾参考资料

以下列出本片采用的2项核心官方资料，技术正文均沿用2026-10-24（北京时间）的实际阅读记录。本轮于2026-10-26另补Seata官方仓库中的完整题名及Fence文章的明确作者；题名补证不等于重新核验技术正文。原文章、研究记录和旧脚注全部保留。

采用`title-author`简表：2项1页、5秒；视频只显示实际原题与明确作者或机构，不显示摘录、日期、位置或提示。

**[R1] Seata TCC Mode**

Apache Seata · Seata TCC 用户文档 · 原技术实读2026-10-24：[官方资料](https://seata.apache.org/docs/user/mode/tcc/)；[既有实读记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/656b525f533037f1c0dff6383c4afa69926e612c/episodes-codex/tx-tcc/research.md#L7)。 [原题补证（2026-10-26，官方仓库）](https://github.com/apache/incubator-seata-website/blob/ae31c10be89d7cca4d3a7010f3875d30992731c8/i18n/en/docusaurus-plugin-content-docs/current/user/mode/tcc.md)。

支持范围：业务实现Try检查并预留资源，再根据协调决定选择Confirm或Cancel；确认与取消是互斥结局，不是三个动作依次全部执行。；TCC要求业务提供相应动作及资源约束，不能把给远程接口加标记当成通用数据库自动回滚。

边界：Seata是本片引用的公开TCC实现，不是唯一实现；不采用文档中面向所有系统的性能或适用性口号。；保留本片订单8124、库存4及购买1件的教学身份，不当作官方案例或实测。

内部定位：Overview；Disadvantages；Overall Mechanism；Basic Usage

**[R2] Alibaba Seata Resolves Idempotence, Dangling, and Empty Rollback Issues in TCC Mode**

Zhu Jinjun（发布机构：Apache Seata） · 2022-06-25 · Seata 1.5.1 Fence公开实现，仅参考：[官方资料](https://seata.apache.org/blog/seata-tcc-fence/)；[既有实读记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/656b525f533037f1c0dff6383c4afa69926e612c/episodes-codex/tx-tcc/research.md#L9)。 [原题与署名补证（2026-10-26，官方仓库）](https://github.com/apache/incubator-seata-website/blob/ae31c10be89d7cca4d3a7010f3875d30992731c8/i18n/en/docusaurus-plugin-content-blog/seata-tcc-fence.md)。 仅参考：2022-06-25的Seata 1.5.1公开实现，不作为现行版本默认行为或所有TCC框架的保证。

支持范围：Try需要真正提交业务预留，相关控制状态和资源修改需要正确原子衔接。；具体Fence实现展示对幂等、空回滚、悬挂问题的处理；重复确认或释放不能再次改变资源数量。

边界：仅作公开实现参考，不根据标题中的Resolves推导所有框架、版本或业务代码天然正确。；确认与取消需要依据持久决定恢复，不能因一次超时擅自切换结果；其他写入路径仍需遵守预留约束。；旧文的1.5.1版本及具体Fence表不作为当前部署默认值。

内部定位：TCC；Try本地提交；幂等、空回滚、悬挂；Fence状态表与业务操作的本地事务

未选资料：开发文档原题与用户文档同名，旧阅读与本轮辅助题名证据保留；AWS旧记录缺少个人署名信息，不据此认定文章无作者，本轮不加入片尾，旧脚注保留。

内部证据：`docs/reference-endcards/batch-7/sources-tx-tcc.json`；完整旧研究SHA-256 `3e06809700ff7d02f37a2e4539380a0012f05b0dd15a291112aab324cd3f3fbb`。
