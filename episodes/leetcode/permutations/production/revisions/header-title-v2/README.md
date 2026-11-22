# LC.46《全排列》顶部栏视觉修订（`header-title-v2`）

按 [#527](https://github.com/linhongcun/video-studio/issues/527) 批量视觉修订：仅将正片帧 `0..5462` 顶部栏 `LC.46` 右侧的「算法可视化」替换为基于 `episodes/_shared/leetcode-video/FrameV2.tsx` 真实渲染的算法题名称「全排列」。

- **基线提交**：`6b1518876a5eab2b0460319c072fa05d0884fdb8`（基线成片 SHA-256：`af8ec425c6e92c9aa2da041be26b4050e0e6da41b7191b4d94efd70d32dfcb91`）
- **新版成片 SHA-256**：`0613ba8ce033dcfe7218b930295b711980260285704bdd89b75bd6d8a9d9d2ca`（`11,303,362` 字节）
- **完整保真核验**：全部 150 帧参考资料解码帧逐帧一致、全部 AAC 音频包/时序与解码 PCM 逐字节一致、全片时间轴一致、补丁外未改区域最低 PSNR `57.63 dB`（代码卡 `61.29 dB`）、补丁接缝中位 RGB 差 `0`（四边均值最大 `0.2381`）。
- **历史冻结保护**：既有源码、旧冻结清单及 v1 共享文件保持原字节不变。
