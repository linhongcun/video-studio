# EP.13 权威资料核验

实际访问日期：2026-10-24（北京时间）。使用可调用网页读取工具实读正文；只使用官方文档，旧脚本不是出处。

## R1 [Microsoft Azure Architecture Center — Circuit Breaker pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)

实际读取 Context and problem、Solution、Problems and considerations：等待占用共享资源可能导致级联故障；按近期失败条件暂停调用；暂停时快速返回；少量探测；达恢复条件再恢复，失败则继续暂停。

## R2 [AWS Well-Architected — graceful degradation](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_mitigate_interaction_failure_graceful_degradation.html)

实际读取主功能与软依赖、业务一致性边界；熔断可以配合降级，但不保证修复远端，不应把关键事务跳过后当成功。此文有一处将阻止调用状态称closed，与Azure常见命名相反，视频因此只用正常/暂停/探测，术语定义以R1为准。

## 画面主张核验

|镜头|主张与教学边界|依据|
|---|---|---|
|01|一个服务故障，为什么还能下单？。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|02|下单请求 · 一直等待。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|03|局部等待 · 占满共享资源。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|04|观察失败 · 达到条件。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|05|暂停这条故障调用。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|06|运费险暂不可用 · 仍可提交订单。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|07|等待恢复 · 核心校验继续。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|08|少量探测 · 失败继续暂停。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|09|满足条件 · 恢复调用。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|10|控制故障影响 · 给恢复留时间。数据均为示例，不能推断实际系统统一策略。|R1、R2|

## 导航重制实际复读（flow-map-20261024 / #199）

2026-10-24 UTC，实际重新下载并阅读MicrosoftDocs官方仓库的[architecture-center/docs/patterns/circuit-breaker.md](https://github.com/MicrosoftDocs/architecture-center/blob/main/docs/patterns/circuit-breaker.md)，不是用旧稿代替资料。正文`ms.date`为2025-02-05，本次读取Context and problem、Solution与相关considerations；实际获取的正文SHA-256：`29baeab9e19c54c9fdae01dfa4c431bae0c6811e0c5267a1d6c8c78267b8146e`。会话正文副本位于工作盘`/workspace/.video-studio-flow-audit/circuit-breaker-official.md`。

- Closed仍转发调用，并观察近期失败；满足设定窗口/阈值后进入Open。因此无保护基线不能直接称为Closed，另作不连接状态箭头的图外教学对照。
- Open立即返回不可用，不把调用送往该下游；它不表示下游已经修复。
- 等待条件满足后进入Half-Open，仅允许少量请求；探测失败回Open并重新等待，满足恢复条件才回Closed。08失败与09等待后的新一轮探测分开，不把一次失败直接剪成成功。
- 异常如何处置由调用方业务决定，可选运费险不可用不等于跳过必要库存或支付校验；下游本身的恢复仍取决于外部修复。

本次只为原机制增加空间关系与明确状态名，保留原旁白、20句字幕、10镜与2926帧，不新增实现分类或通用阈值承诺。示例3次失败仍明确为教学阈值，真实恢复条件按服务设计。


## 本轮片尾原题与连续原文核验（2026-10-26）

本轮仅补既有视频的资料附录。原script/research的历史R1/R2语义不改，新增清单R1为Circuit Breaker Pattern、R2为Retry pattern，原R2 AWS阅读仍按原日期保留。正式来源与题名记录见[完整证据](../../docs/reference-endcards/batch-4/sources-circuit-breaker.json)。

固定提交：`b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a`，MicrosoftDocs/architecture-center官方仓库。三份实际完整GET200分别为：

- https://raw.githubusercontent.com/MicrosoftDocs/architecture-center/b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a/docs/patterns/circuit-breaker.md：25769字节，SHA-256 `29baeab9e19c54c9fdae01dfa4c431bae0c6811e0c5267a1d6c8c78267b8146e`。
- https://raw.githubusercontent.com/MicrosoftDocs/architecture-center/b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a/docs/patterns/retry-content.md：12141字节，SHA-256 `619b34a5b1eaf6508715080192feb9fcd85447d402f29816e9f3ffaf294f91a8`。
- https://raw.githubusercontent.com/MicrosoftDocs/architecture-center/b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a/docs/patterns/retry.yml：726字节，SHA-256 `245b362e50caeafa0da00807bc5edcf3dbdbf5279ed8ead60ff1fe784b67666a`。

两canonical本轮实际GET均因Tunnel 403未取得正文；成功实读仅指上述固定官方原文，不把原canonical历史访问伪装本轮新读。Circuit Breaker原题来自frontmatter第2行`Circuit Breaker Pattern`；H1第11行为`Circuit Breaker pattern`，本清单明确采用实际metadata大小写。Retry原题来自同提交retry.yml metadata.title第3行，content第18行绑定retry-content.md正文。以上核验差异留内部，不写入面向读者的资料流程。

### 新R1 · Circuit Breaker Pattern

> A limited number of requests from the application are allowed to pass through and invoke the operation.

位置：Solution / Half-Open · line 45。连续完整原句，未改词、标点、未添加省略或译文。

- 编者说明：等待下游响应的请求可占住共享资源并造成级联影响；熔断观察近期失败，达到配置条件后暂停可能失败的调用。
- 编者说明：Closed放行并统计近期失败；Open快速返回；Half-Open仅允许少量试探，失败继续暂停、达到成功条件后恢复。
- 编者说明：熔断参数要匹配服务恢复能力，业务自行处理不可用；系统恢复仍依赖外部修复，不保证网站永不故障。

### 新R2 · Retry pattern

> For some noncritical operations, it's better to fail fast rather than retry several times and affect the throughput of the application.

位置：Issues and considerations / Impact on performance · line 44。连续完整原句，未改词、标点、未添加省略或译文。

- 编者说明：非关键操作可选择快速失败并给出合适反馈，避免反复重试牺牲应用吞吐或加重繁忙下游。
- 编者说明：持续失败时可停止继续访问，等待后少量试探；故障性质、业务要求和实际测试决定策略。
- 编者说明：重试事务操作要考虑一致性和副作用；运费险教学示例不表示可以跳过库存、支付等必要业务校验。

**状态边界：**Closed放行并观察，Open拒绝后续受保护调用，Half-Open只放少量试探；失败回Open，满足恢复条件回Closed。读到正文第38／43／45／56–65行，以及Exception handling和Recoverability。Retry第44–48行支持非关键快速失败、避免加重负载与等待后试探；第52／62行支持副作用与事务边界。片中没有增加重试算法课程。

**教学边界：**处理位、三次失败与示意探测量均不当作统一默认值；运费险为可选教学支路，不跳过支付、库存等必要检查。系统修复依赖外部操作，不把冷却时间结束画作服务已修好。实际媒体追加、独立审片和发布由根任务另做，不在本记录预记通过。
