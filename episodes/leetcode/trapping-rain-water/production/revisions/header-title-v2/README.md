# LC.42《接雨水》顶部栏视觉修订（`header-title-v2`）

按 [#527](https://github.com/linhongcun/video-studio/issues/527) 批量视觉修订：仅将正片帧 `0..5775` 顶部栏 `LC.42` 右侧的「算法可视化」替换为基于 `episodes/_shared/leetcode-video/FrameV2.tsx` 真实渲染的算法题名称「接雨水」。

- **基线提交**：`6b1518876a5eab2b0460319c072fa05d0884fdb8`（基线成片 SHA-256：`0f8bc6053a088e717b849a5c9754cbebcab192f7f4f2041e7eb879bdf1bb0388`）
- **新版成片 SHA-256**：`ce906f8e1da93ddb7d8c425c5f08ee186f3d39358333f87afd6eafde995b9004`（`10,847,587` 字节）
- **完整保真核验**：全部 150 帧参考资料解码帧逐帧一致、全部 AAC 音频包/时序与解码 PCM 逐字节一致、全片时间轴一致、补丁外未改区域最低 PSNR `58.4 dB`（代码卡 `61.4 dB`）、补丁接缝中位 RGB 差 `0`（四边均值最大 `0.2143`）。
- **历史冻结保护**：既有源码、旧冻结清单及 v1 共享文件保持原字节不变。
