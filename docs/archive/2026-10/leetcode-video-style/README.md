# LeetCode十一期正文与封面统一

日期2026-10-28，状态：制作和逐镜预检中，尚未发布。本轮在干净最新main d04a30c12b1ce0fb5743f20ce61f9db8908311ad / v0.84.1上开始，保留已合并的Kafka与MySQL变更，初始计划版本v0.84.2；编码后发现主干新增Redis独立方向（821a299/v0.85.0），保留该变更后实际版本顺延v0.85.1，新旧566输入零交集无需重新编码。

范围为LC.1、3、11、42、46、70、200、206、547、704、739，依次对应两数之和、最长子串、盛最多水、接雨水、全排列、爬楼梯、岛屿数量、反转链表、省份数量、二分查找、每日温度。正文、完整Python代码页和参考资料页沿现有深蓝/暖金/青色封面；原封面、问题、推导、模型、动画状态、字幕、章节与配音时序保持。原技术来源日期保留，不新增官网GET声明。

新视觉入口为各期`remotion/src/leetcode-style/index.ts`，本轮独立冻结与输出在`revisions/leetcode-style/`，共享工具及不可变style-v1/identities-v1位于`episodes-codex/_shared/leetcode-video/`。不会把会随新增题增长的封面catalog作为编码运行输入；常规标题栏使用“算法可视化”，具体方法仍由原镜头引出，代码页才显示方法信息。旧源码/原冻结不改写，170份原输入保护身份见[preservation-baseline.json](preservation-baseline.json)。

每片正文包含原150帧完整Python卡，之后再加150帧原题/机构资料页；不能用后者替换前者。11份基线MP4按Git原始发布字节恢复并与receipt完整SHA一致，在替换前保存旧metadata/receipt与当前发布文章快照。新成片将完整流拷贝基线AAC并核对载荷、时间戳和PCM，不重新录制或运行时序装配。

当前证据：[开工记录](startup.json)、[独立范围盘点](independent-scope-audit.md)、[独立视觉源复核](independent-visual-source-review.md)。正式预检、媒体终审与网站检查完成后补齐；实际GitHub发布以v0.85.1 Release回执为准，不预记上线或用户观看认可。

能力边界如实记录：源码一致性不代替全片动态/听辨；本轮未新ASR或真机验证。当前网络策略未开放canonical站点或原生Release上传域名，发布后按普通请求核对并记录实际结果，不绕过访问策略，不将本地HTTP/GitHub源SHA称为canonical线上完整SHA。只发布GitHub本站，不重发视频平台。
