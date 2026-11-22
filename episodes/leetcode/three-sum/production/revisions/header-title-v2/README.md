# LC.15《三数之和》顶部栏视觉修订（`header-title-v2`）

按 [#527](https://github.com/linhongcun/video-studio/issues/527) 批量视觉修订：仅将正片帧 `0..5497` 顶部栏 `LC.15` 右侧的「算法可视化」替换为基于 `episodes/_shared/leetcode-video/FrameV2.tsx` 真实渲染的算法题名称「三数之和」。

- **基线提交**：`6b1518876a5eab2b0460319c072fa05d0884fdb8`（基线成片 SHA-256：`f8a085e7b49265e25cb39970f39e1f1fed77e071eff12493ad9dbbbad61dd5b5`）
- **新版成片 SHA-256**：`d0ace75aab62bce68bc1d775944b225d6f9985d93310c6a9ca08dd74af648203`（`9,416,313` 字节）
- **完整保真核验**：全部 150 帧参考资料解码帧逐帧一致、全部 AAC 音频包/时序与解码 PCM 逐字节一致、全片时间轴一致、补丁外未改区域最低 PSNR `59.63 dB`（代码卡 `64.4 dB`）、补丁接缝中位 RGB 差 `0`（四边均值最大 `0.5833`）。
- **历史冻结保护**：既有源码、旧冻结清单及 v1 共享文件保持原字节不变。
