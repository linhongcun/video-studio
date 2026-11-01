# 原始资料与片尾清单

资料核对日期：2026-10-26（北京时间）。片尾采用`title-author`，每页最多4项、默认5秒；只显示实际原题与作者或机构。本期两份来源无明确个人署名，均显示Redis机构，共1页。连续原文、定位、版本与核验日保留在研究、文章及资料元数据。

1. Redis，**Redis sorted sets**。固定官方文档：https://github.com/redis/docs/blob/fcc15c76a48baeb0dc08fc839242a7799c077080/content/develop/data-types/sorted-sets.md。原题证据为Markdown front matter `title`；连续原文见references.json，支持有序集合排序及普通跳表编码下的结构分工。
2. Redis，**t_zset.c**。Redis Open Source8.4.0固定源码：https://github.com/redis/redis/blob/60ba86f3c8b4e1ec96451171753a0a38e5c45a0c/src/t_zset.c。这是实际原文件名，不是自拟文章题名；GitHub Contents API原`name`/`path`元数据为题名证据。`zslRandomLevel`与`zslInsert`支持随机层高、先比较后前进、在当前位置下降、各层前驱与前向链接接入。代码与函数定位保留为文章和研究记录，不进入视频资料列表。

图文另引用**Memory optimization**：https://github.com/redis/docs/blob/fcc15c76a48baeb0dc08fc839242a7799c077080/content/operate/oss_and_stack/management/optimization/memory-optimization.md，仅用于紧凑编码与配置阈值边界，不把8节点教学图说成默认Redis真实内存布局。

本轮实际通过官方GitHub Contents API取回固定原文字节并核SHA-256/Git blob；对应redis.io官网URL为读者入口，本轮不宣称官网成功访问。具体获取时间、字节和元数据见research/source-verification.json。


## 本次层高选择说明的依据

保留的Redis8.4.0固定源码t_zset.c中，zslRandomLevel从1起，zslInsert先选择level并创建相应节点，再对i<level逐层改forward。因此，新55只有一层是合法选择，二层并非每次插入的必选条件。源码后续仍维护未接入层的span；本片只展示前向链接，不能把“上层不加入55”扩大为所有内部元数据都不变。

height-options.json由相同before独立构造两分支：height1两次forward写入后完成，上层仍head→40→70；height2在接线前已分配两槽，按原四写接入。07在分支间明确重置，不把一层完成态变成同次插入的临时升级。它们是固定合法教学选择，不是Redis随机数回放或性能实验。独立模型检查绑定实际JSON，来源原题/原文与必要片尾身份仍沿用原证据。
