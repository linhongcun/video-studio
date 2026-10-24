# EP.14 v0.45.0 固定回归输入

这里是历史制作样例，不是现行视频工程。输入逐字节提取自提交
`c1da2a1eef696d8bd08c9b078d7b833d75308498` 的 `episodes/degradation/`。
当站点的 EP.14 被新一轮 Codex 成片替换后，共享工具仍应能够复现这份
20镜、5152帧的既有回归结果。

- `manifest.json` 记录 Git blob ID 和完整 SHA-256。测试先核验这些实体文件，缺失或修改均失败。
- 音轨是实体 `remotion/public/audio/voice.wav`，SHA-256 为
  `9e70470c096c4198f679eceb5323b0cd9f90323784e7dad284dc43c47265468b`。
- `storyboard.json` 与 `storyboard.6265993b.json` 为同一旧分镜的字节副本。
- 只保存测试实际需要的六种旧输入及分镜快照；已有配音构建记录、ASR结果和
  起音预期仍复用 `../../golden/`，不更新或放宽既有 golden。
- `docs/examples/knoll_props_spec.degradation.py` 在本目录作为 `--dir` 时仍生成
  原历史制作说明；该 spec 的实际代码和说明正文保持不变。
- `episodes/_shared/storyboard/examples/degradation/rerun.sh` 用本固定输入和原始
  spec 重建分镜、封面，仍要求 `6623` 项检查、`91/91` 起音以及逐字节一致。

这是版本命名的不可变 fixture。今后新案例应建立新目录，不用当前站点文件
覆盖这里，也不改写旧 golden。历史 words 的脚本SHA与后来仅修改画面说明的
script.md 不同；配音回归保留原来只比较该元字段之外内容的既有断言。
