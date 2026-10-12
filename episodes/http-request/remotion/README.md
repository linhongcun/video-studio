# v2 面试满分版 · Remotion

- 渲染：`npm ci && npx remotion render src/index.ts Main ../video.mp4 --codec=h264 --crf=26`
- 数据：`../storyboard.json`（分镜，原样未改）驱动通用渲染器 `src/Main.tsx`；复用速览版的浏览器/服务器机柜/信封/响应包/文件夹/齿轮组件。
- 配音：edge-tts `zh-CN-YunxiNeural --rate=-5%`，每镜头一条 → 去尾部静音 → `public/audio/<shotId>.wav`；`python3 make_timing.py` 用 ffprobe 实测生成 `src/timing.json`（镜头时长 = 配音帧 + 每段 2 秒停顿均摊，动画/字幕相对帧按 `scale` 等比缩放）。
- 制作侧覆盖（Main.tsx 内 OVERRIDES / ANIM_OVERRIDES / PINNED）：
  - connect-2 `quic` 与 `tls13note` 同在右下角重叠 → `quic` x 1300→120；`tls13note` 固定在镜头第 200 帧淡入（不缩放）。
  - dns-2 `ip`/`ipNote` 原定 190/200 帧出现、仅停留约 10 帧就淡出 → 提前到 150/158 帧。
  - server-2 信封到达源站后淡出，避免盖住机柜。
- 关键帧检查图：`../frames/`（每章 1 张）。
