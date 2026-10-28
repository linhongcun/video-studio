# P05 两枚鸡蛋：独立源码与最终抽帧复核

日期：2026-10-28。执行者：Codex 独立子代理 `visual_approach`，未参与 P05 视觉实现、渲染或站点接入。结论：通过下述源码、静帧和媒体身份复核范围，无未解决的阻塞问题。

## 实际候选与范围

媒体与视觉源码候选提交为 `a40c87558b435eb17917e96f4f9171726754efc0`。复核结束时 HEAD 为 `3b6c4bc526c8769acb26a16a6cbd3bdac38e47eb`；已实际比较两者：后者只规范五期 `meta.json.updatedAt` 的微秒为整秒，并更新共享 README 与日期修正记录。P05 视觉源码、模型、媒体、冻结清单、资料回执及最终抽帧相对前者均无变化，本报告的媒体与视觉结论因此覆盖该 HEAD。

逐文件比较 `episodes-codex/egg-drop/remotion/src/cover-continuity/` 中 `Main.tsx`、`Building.tsx`、`primitives.tsx`、`theme.ts`、`Root.tsx` 与原 `src/` 对应文件。实际打开 `final/egg-drop/frame-01.png` 至 `frame-07.png` 七张 PNG，并打开现行封面总览 `design/puzzles-covers-20261027/puzzles-covers-preview.png` 的 P05 作风格对照。另读取共享 `Frame.tsx`、主题及封面 catalog，核对最终媒体报告、资料回执、元数据与实际 MP4 的 SHA、字节及 ffprobe 流信息。

## 源码结论

`Main.tsx` 的差异仅为复用模块的相对导入和加入静态 `PuzzleCanvas`；场景分支、状态取值、字幕查找、Sequence 起止与时长均保留。`Building.tsx` 仅调整模型导入路径及未碎鸡蛋的填充、描边、文字颜色，鸡蛋路径、坐标、缩放、破碎分支和动作表达保持原实现。`primitives.tsx` 改用共享 `PuzzleHeader`，其余正文图元和面板不变；主题改从封面 catalog 派生；新 Root 仅登记相同 VIDEO 参数的 Main，不重复登记旧封面组合。

已检查该候选相对父提交的原 `Main.tsx`、`Building.tsx`、`egg-model.ts`、`scene-state.ts`、`data.ts`、分镜、words、旧 source freeze 及发布字幕无 diff。未发现模型、推理、动作公式或旁白/字幕时序改动。

## 实际看图结论

七张最终 PNG 对应帧为 `0、2784、3300、5568、5569、5644、5718`，图像 SHA 全部与 `final/egg-drop/final-media-check.json` 一致。

- 首帧的紫黑背景、浅紫线描、珊瑚 P05 标签与重点、字体和边缘静态图形，与封面总览 P05 属同一视觉系列；楼体与两枚编号鸡蛋可辨。
- 2784 与 3300 帧中，14 楼及 27 楼的预算分支、已知安全/会碎边界、剩余待查区间与次数清楚。标题、副题、模式标记、正文注记及字幕未相互遮挡或裁切。
- 正文末帧明确区分最高安全层 31、本局实际 8 次和方案保证最多 14 次；两枚蛋破碎状态与边界可见。
- 资料首、中、末帧均完整显示原题《1884. Egg Drop With 2 Eggs and N Floors》及机构 LeetCode，紫色背景延续正文，无截断或正文字幕跨入资料区。

## 媒体与接入身份

实际发布 MP4 与制作 MP4 的完整 SHA-256 均为 `3337082e3e5100e82eeee2fdde6314579edb8e1efda666d1e08fd14f8b237045`；发布文件为 10,205,386 字节。ffprobe 实测 H.264、1920×1080、30/1 fps、5719 帧，音轨 AAC、48 kHz、双声道、起点 0、8703 包。正文 5569 帧加资料卡 150 帧，与最终媒体报告、三处资料 receipt、render-result 及发布元数据一致。单期 `checkEpisode('episodes/egg-drop')` 在当前 HEAD 通过。

最终媒体报告中的元数据 SHA 属于 `a40c875`。已核对当前 P05 元数据唯一变化为 `updatedAt` 精度，当前 SHA `4d821d503976adc8385e1c909612769f0a34c86c4662a6dea43f8bc206b96e83` 与 `metadata-date-normalization.json` 的 after 身份一致；未将旧元数据 SHA 冒充当前值。

只读核对现有 baseline-audio 与附录媒体报告：二者记录完整 8703 个 AAC 包 payload/PTS/DTS/duration 保持，PCM 指纹为 `SHA256=d22a1ee97a598c9d4b06778e9820fa26da00888d61d37a86362597d5f2bce365`；附录报告记录新正文全部解码帧/PTS 保持及最终时间线连续，且输出 SHA 绑定本次实际 MP4。本次没有重复执行全文件解码，这些全量媒体结论引用已经执行的引擎检查。

本报告不等同于全片连续审看、人工听辨、逐字 ASR、站点播放器操作或部署核验。复核者仅新增本报告，完成后停写；相关媒体或输入改变后应按变化范围重新复核。
