# 导航片实际冻结器快照

`navigation-freezer-20261024.py.txt`保存四片编码前实际使用的冻结器原字节，不作为执行入口。原位置是`../_shared/freeze_sentence_episode.py`；协作主干的LC.11也固定引用规范冻结器，因此将导航版本原字节迁到本目录，规范路径恢复主干原字节。

四片各自的`revisions/navigation-freeze-original.json`和`freezer-path-relocation.json`记录原清单、原完整SHA及路径映射。所有原冻结内容及摘要完全不变，仅一个控制脚本快照的位置变化；没有用新摘要认可旧视频。实际渲染代码、音轨、分镜与已检查媒体未变化。

今后导航片用`freeze_navigation_episode.py`薄包装调用规范冻结器，再加入本片实际共享导航依赖；不要修改已经被其他已发布片固定引用的规范实现。
