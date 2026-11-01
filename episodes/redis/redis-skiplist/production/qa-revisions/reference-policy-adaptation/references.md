# 原始资料与片尾清单

资料核对日期：2026-10-26（北京时间）。片尾采用`original-title-quote`，一页两项、默认5秒；原题与连续短引保持原语言，不把译文当成原题。

1. Redis，**Redis sorted sets**。固定官方文档：https://github.com/redis/docs/blob/fcc15c76a48baeb0dc08fc839242a7799c077080/content/develop/data-types/sorted-sets.md。原题证据为Markdown front matter `title`；连续原文见references.json，支持有序集合排序及普通跳表编码下的结构分工。
2. Redis，**t_zset.c**。Redis Open Source8.4.0固定源码：https://github.com/redis/redis/blob/60ba86f3c8b4e1ec96451171753a0a38e5c45a0c/src/t_zset.c。这是实际原文件名，不是自拟文章题名；GitHub Contents API原`name`/`path`元数据为题名证据。`zslRandomLevel`与`zslInsert`支持随机层高、先比较后前进、在当前位置下降、各层前驱与前向链接接入。代码不强塞进可暂停资料卡的短引。

图文另引用**Memory optimization**：https://github.com/redis/docs/blob/fcc15c76a48baeb0dc08fc839242a7799c077080/content/operate/oss_and_stack/management/optimization/memory-optimization.md，仅用于紧凑编码与配置阈值边界，不把8节点教学图说成默认Redis真实内存布局。

本轮实际通过官方GitHub Contents API取回固定原文字节并核SHA-256/Git blob；对应redis.io官网URL为读者入口，本轮不宣称官网成功访问。具体获取时间、字节和元数据见research/source-verification.json。
