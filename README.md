# video-studio

用 Remotion 代码生成的视频项目。每个视频一个子目录：plan.md、script.md、storyboard.json、remotion/ 工程。成片放在 Releases。

- http-request/：一次 HTTP 请求是如何完成的？

## 平台封面（专用封面，非截帧）

模板在 `episodes/_shared/cover/`（Remotion Still：Cover169 1920×1080、Cover43 1440×1080 = 16:9 居中裁切、Cover34 1080×1440）。版式和文字来自 `episodes/<slug>/storyboard.json` 的 `cover` 节点（没有则用 `covers/cover-spec.json[slug]`）。

```sh
cd episodes/_shared/cover && npm ci   # 首次
npm run covers -- <slug>              # 输出 episodes/<slug>/cover-16x9.jpg、cover-4x3.jpg、cover-3x4.jpg（JPG ≤2MB）
npm run covers -- <slug> --out <dir> --only Cover34   # 可选：换输出目录 / 只出某个尺寸
```

安全区：16:9 内容在 x280–1640（B站 4:3 预览裁两边），y>900 不放字；3:4 顶部 y<144、底部 y>1224 不放字。
