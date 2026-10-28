# Redis 正文视觉入口

现有《Redis 跳表》EP.40的正文及资料页延续Redis系列封面的冷银灰、Redis红、石墨文字、字体与原始标记。`style-v1.json`是不可变视觉快照；后续新增课程向Header传真实EP和题名，不改写已经编码的样式输入，不新增R01或恢复工程算法EA03。

新源码入口在当前层高修订制作目录的`remotion/src/redis-style/index.ts`；继续引用该目录原始模型、层高选项与分镜。新媒体、清单和发布文章快照独立放在`episodes-codex/redis-skiplist/revisions/redis-style/`。站点`sourcePath`保留为这个实际Remotion目录，由该目录新增README说明本次独立入口；新媒体、回执和制作清单不覆盖原层高修订输出。原制作目录、资料核验日期、冻结清单、声音与旧入口保留历史字节。正文4557帧、资料150帧，共4707帧；不运行prepare、配音或混音脚本。

从仓根执行：

```bash
node episodes-codex/_shared/redis-video/qa.mjs redis-skiplist --out-dir work/redis-video-style/preflight
python3 episodes-codex/_shared/redis-video/render.py redis-skiplist --font-inputs
python3 episodes-codex/_shared/redis-video/render.py redis-skiplist --freeze
python3 episodes-codex/_shared/redis-video/render.py redis-skiplist --render
python3 episodes-codex/_shared/redis-video/render.py redis-skiplist --verify
```

默认只打印计划。实际画面先完成逐镜0/.5/.98采样、真实DOM和独立图义审查，再冻结并正式编码。QA默认带原字幕，检查文字安全区、字幕碰撞、字体和实际PNG；`--frames 0,100`供定向补验，静帧和DOM检查不代替动态复核或听辨。

基线完整MP4按`baseline-publication.json`记录的Git提交与完整SHA恢复至`work/redis-video-style/baseline/redis-skiplist.mp4`。新画面静音渲染后完整流拷贝该AAC，逐包载荷、PTS/DTS/duration及完整解码PCM必须相同。新资料页沿原题名与作者/机构简表排版，每页最多4项、5秒；append引擎核对全部正文解码帧及PTS和声音保真。

新清单首次写入时绑定当前实际import闭包、旧冻结、发布/制作文章、文章来源及完整保存证据、Logo原图/来源/许可和fc-match解析的CJK、等宽、品牌字体。已存在清单只读核验，缺输入或字体不重写追认。依赖按当前层高修订的锁文件安装或使用与其依赖树完全一致的保留目录。

工具仅在私有函数命名空间复用已验证媒体核心，原`puzzles-video`、旧资料引擎和历史冻结没有修改。层高1合法完成、共同before重置、预选2层后再接入的条件与动作必须保持，不能把视觉统一变成算法改写。实际制作、验收和发布结果另记在`docs/archive/2026-10/redis-video-style/`；不预记ASR、全片人工听辨、真机或用户观看结论。
