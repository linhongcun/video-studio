# LC.206 制作说明

制作目录`episodes-codex/reverse-linked-list/`。14镜28句，四章为problem01–02、save03–06、reverse07–12、code13–14。先建立节点、next、head和原地反转任务，再用同一组原节点完整走完三轮。真实配音、分镜、冻结和渲染由root统一处理。

## 实际工程

入口`remotion/src/index.ts`，组合Main为1920×1080、30fps；总长由真实storyboard逐镜相加。`data.ts`读取分镜；`Main.tsx`绘制固定节点、next与三角色引用；`CodeCard.tsx`读取`solution.json`；`Cover.tsx`生成三尺寸封面。主题复用共享`episodes/_shared/theme/pageTheme.ts`。

依赖使用root重新npm ci得到的当前`two-sum/remotion/node_modules`，不依赖清理前的站点工程。`remotion.config.ts`优先读取`../storyboard.json`，仅在缺少真实分镜时才读`src/placeholders/storyboard.json`。占位文件明确为未配音开发时间，不能进入生产或伪称ASR。

配音使用共享prep/gen/build、句级装配、whole铺轨和严格起音；实体音轨副本为`remotion/public/audio/voice.wav`。不在本期复制TTS、拼接或起音算法。首次术语标签来自句首实际cue；动画相对句首的百分比窗口不冒充词级声学边界。

## 动作和暂停卡

原节点固定x620/1000/1380、y465..617。左None为x250、右None为x1740，两者同为空引用且没有节点框。head保留在原节点1；prev下层、cur上层、nxt下方第二层，箭头错开身份文字。具体起落和每镜状态见`visual-direction.md`。

每轮只先保存、再反转、依次移动；保存入口和改next之间有停留，prev和cur按两句话分别移动。首次反转后保留nxt→2证明后半段入口仍在，不画节点销毁。输出预览与正式执行有明确恢复标记。

末镜`codeCardFrom`后150帧硬切完整Python卡，字号39、行高45，程序与文章/solution.py逐字同源，静态且不显示正文字幕。root共享装配给尾部静音，Main不另造音轨。平台预定义节点类型，本程序不创建节点、不依赖类型导入。

## 命令与实际边界

在`remotion/`执行`./node_modules/.bin/tsc --noEmit`检查类型。root统一排队执行`npm run stills -- OUTPUT`、`npm run covers`和`npm run render`；QA脚本支持QA_SHOTS、QA_FRAMES、QA_FRACTIONS、QA_CLIPS和QA_STORYBOARD限定实际样本。两CPU条件下不并行渲染多期，不启动大矩阵或额外全片。

源码作者已执行轻量TypeScript检查；独立程序检查由research代理输出。实际无字幕动态、封面安全区、全片编码、媒体声学/响度、冻结与线上SHA核验以root和独立QA报告为准。未做的逐字ASR、完整听辨或真实新手实验不得写成已通过。

## 预检重点

- 01–02足以复述节点存值与next、head是入口、只反向改原节点连接、不交换值不新建、返回原节点3。
- 06先改1.next为空，nxt仍访问2；不把后半节点描述为立即销毁。
- 三轮保存/反转/移动顺序及数值正确；每个动作在真实句级时间内起、中、落定清楚。
- 原节点身份/位置/值、head→1跨镜保持；左右None不被当成节点。
- prev/cur/nxt重合时标签分层、箭头不压节点身份或数值；13返回prev3。
- 完整代码卡静态150帧、无字幕，return完整可读；4:3完整portrait缩放安全。

这些是需要实际验证的检查项，本文本身不声明预演或成片已经通过。
