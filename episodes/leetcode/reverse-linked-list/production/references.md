# reverse-linked-list · 片尾参考资料

采用 `presentation: title-author`：只显示实际原题与机构，每页最多4项、默认5秒；追加于原完整Python代码卡之后。代码卡150帧、讲解、程序和声音由root保存原字节，本资料任务没有重建或检查新媒体。

技术实读日期均为 **2026-10-25（北京时间）**。原题与实际被读章节题名已在旧记录，未新GET，不声称26日当前H1或技术正文复核；没有明确个人署名，省略author字段。

证据见[sources-reverse-linked-list.json](../../docs/reference-endcards/batch-9/sources-reverse-linked-list.json)；[固定既有实读记录](https://github.com/linhongcun/video-studio/blob/036ce88d416e08127f8135afb55d1d62044f30f6/episodes-codex/reverse-linked-list/research.md)与[逐字旧研究归档](../../docs/reference-endcards/batch-9/reverse-linked-list-evidence/prior-research-036ce88d.md)为本仓历史记录，非官方固定正文。

- 基线：`036ce88d416e08127f8135afb55d1d62044f30f6`
- 原research Git blob：`a2b8518e6fc70d8a54563dac326bcac0c9823d51`
- 原research完整SHA-256：`5777c0ad31a49674655d49260daf5f3e947ab1aa7e05441834cf8f3e098998b9`（5208字节）
- 原article完整SHA-256：`3ac678192ceab522985a885dbf55dc7092c17f978237638132a9a0edced71c54`（7215字节）

## R1 · Reverse Linked List

- 发布方：LeetCode
- 版本：LeetCode 206 · 官方题面（未标发布日期或更新时间）
- 正式链接：[Reverse Linked List（官方资料）](https://leetcode.com/problems/reverse-linked-list/description/)
- [既有实读记录（2026-10-25，R1）](https://github.com/linhongcun/video-studio/blob/036ce88d416e08127f8135afb55d1d62044f30f6/episodes-codex/reverse-linked-list/research.md#L5-L12)
- 对照题面：[反转链表（力扣官方中文题面）](https://leetcode.cn/problems/reverse-linked-list/description/)

- 原题位置：2026-10-25既有实读记录research.md第7行：LeetCode 206.后的英文原题；article.mdx第98行同名题面交叉
- 实际阅读范围：中英文Description、三组输入输出、Constraints与迭代/递归进阶；不含官方editorial正文
- 对应镜头：01, 02

旧主张记录：给定单链表的头节点，反转链表并返回反转后的链表；官方允许0..5000个节点，节点值范围-5000..5000。空链表是题面明确展示的合法输入。进阶提到迭代与递归两种实现，本期只讲迭代。

## R2 · Assignment statements

- 发布方：Python Software Foundation
- 版本：Python 3 Language Reference（旧记录未注明小版本）
- 正式链接：[Assignment statements（官方资料）](https://docs.python.org/3/reference/simple_stmts.html#assignment-statements)
- [既有实读记录（2026-10-25，R2）](https://github.com/linhongcun/video-studio/blob/036ce88d416e08127f8135afb55d1d62044f30f6/episodes-codex/reverse-linked-list/research.md#L14-L20)

- 原题位置：2026-10-25既有实读记录research.md第16行：Python Language Reference —后的实际被读章节原题
- 实际阅读范围：Assignment statements：名称绑定、属性赋值、右侧求值与多目标赋值部分
- 对应镜头：03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15

旧主张记录：名称赋值重新绑定已有对象；属性目标赋值要求对象修改该属性，不会因为`cur.next = prev`而自动新建一个节点。右侧先求值，随后才进行相应赋值。

## 保留的独立身份

官方editorial只返回登录、导航和编辑器空壳，没有题解正文，因此不引用官方迭代题解。三引用方案、不变式、O(n)/O(1)、节点身份与值保持的实现证明及有限执行，继续属于原独立推导/执行记录；本轮未重跑程序或改写这些结论的验证身份。

原article/research全文、frontmatter、全部锚点、资料与核验段和唯一Python程序块完整保留。未改solution/SB/words/媒体/冻结/共享代码；不预记渲染、声音/成片检查、上线或用户认可。
