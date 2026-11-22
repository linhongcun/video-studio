# LC.3《无重复字符的最长子串》顶部栏视觉修订（`header-title-v2`）

按 [#527](https://github.com/linhongcun/video-studio/issues/527) 批量视觉修订：仅将正片帧 `0..5829` 顶部栏 `LC.3` 右侧的「算法可视化」替换为基于 `episodes/_shared/leetcode-video/FrameV2.tsx` 真实渲染的算法题名称「无重复字符的最长子串」。

- **基线提交**：`6b1518876a5eab2b0460319c072fa05d0884fdb8`（基线成片 SHA-256：`07cb15f1aef63a6e8ed3beb298298cd503df3d46f811c83b354b15984fd03077`）
- **新版成片 SHA-256**：`decddd32a5ff24a947870e0b976ea7ace5af4a9fc6c370789f23c3db64b1fafd`（`13,303,253` 字节）
- **完整保真核验**：全部 150 帧参考资料解码帧逐帧一致、全部 AAC 音频包/时序与解码 PCM 逐字节一致、全片时间轴一致、补丁外未改区域最低 PSNR `55.98 dB`（代码卡 `62.08 dB`）、补丁接缝中位 RGB 差 `0`（四边均值最大 `0.2143`）。
- **历史冻结保护**：既有源码、旧冻结清单及 v1 共享文件保持原字节不变。
