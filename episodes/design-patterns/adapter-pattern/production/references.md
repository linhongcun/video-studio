# adapter-pattern · 片尾参考资料

清单整理及题名／署名补核日期2026-10-26；两项技术实读日期保留为2026-10-25（北京时间）。本轮两份完整固定官方raw响应SHA与旧业务边界来源记录逐字节一致，未把元数据核验改写为新的技术访问日期。

title-author清单2项、一页5秒，只显示原题和明确个人作者或机构。Spring原源码明确署名Juergen Hoeller；Azure只有维护账号，不据此填写个人author。完整原研究Git/blob/SHA、原逐论点读取及本轮原字节／全SHA见[本轮证据](../../docs/archive/2026-10/reference-endcards-batch-12/sources-adapter-pattern.json)。

## R1 · TaskExecutorAdapter

作者：Juergen Hoeller · 发布机构：Spring Framework

- 版本／实读日期：Spring Framework · 主干快照7bdf9c86f865 · 实读2026-10-25
- 官方固定来源：[TaskExecutorAdapter](https://github.com/spring-projects/spring-framework/blob/7bdf9c86f8657029567067051b7c6bd47b4ae67e/spring-core/src/main/java/org/springframework/core/task/support/TaskExecutorAdapter.java)
- 实际原文：[固定raw](https://raw.githubusercontent.com/spring-projects/spring-framework/7bdf9c86f8657029567067051b7c6bd47b4ae67e/spring-core/src/main/java/org/springframework/core/task/support/TaskExecutorAdapter.java)
- 原研究记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/adapter-pattern/research.md#L11)
- 原题定位：TaskExecutorAdapter.java · 类声明（第45行）
- 正文位置：类声明与构造 · execute / submit / doExecute

对应主张：

- 实际实现目标接口、持有既有Executor，并在转换后真实委托，支持本片对象适配器的契约、持有和调用关系。
- 这是具体实现证据；不将该框架的异步、装饰或异常策略推广为所有适配器或本片通知服务的统一语义。

## R2 · Anti-Corruption Layer pattern

发布机构：Microsoft · Azure Architecture Center

- 版本／实读日期：Azure Architecture Center · 文档日期2026-05-28 · 实读2026-10-25
- 官方固定来源：[Anti-Corruption Layer pattern](https://github.com/MicrosoftDocs/architecture-center/blob/b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a/docs/patterns/anti-corruption-layer.md)
- 实际原文：[固定raw](https://raw.githubusercontent.com/MicrosoftDocs/architecture-center/b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a/docs/patterns/anti-corruption-layer.md)
- 原研究记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/adapter-pattern/research.md#L15)
- 原题定位：anti-corruption-layer.md · H1（第11行）
- 正文位置：Solution · Problems and considerations · When to use this pattern

对应主张：

- 业务侧可以继续使用自己的数据模型与用法，将外部调用的模型和格式转换集中于接入边界。
- 保护领域模型是防腐层的目的；本例适配器有边界保护作用，但不等同完整防腐层，也不保证外部能力改变后上层永远无需调整。

本清单不引用未取得的GoF全文，不把此前Refactoring.Guru当作本轮重读；不把适配器与完整防腐层混为一谈。原文章引用与配图、旧出处及制作范围保持。
