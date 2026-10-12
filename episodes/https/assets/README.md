# 第二期《HTTPS 为什么安全？》视觉资产

- 生成脚本：`../gen_assets.py`（改色/改形状请改脚本后重新生成）
- 配色：只用 design.md §1.1 深色令牌（视频画面固定深色，§10 规定浅色主题下视频画面不变），底色按 `#0B1020` 设计，SVG 本身透明背景
- 每个 SVG 都有 viewBox，无外部字体（文字用系统字体栈 system-ui / PingFang SC / Noto Sans CJK SC），矢量缩放，1920×1080 下任意尺寸都清晰
- 关键子元素都有 `id`，Remotion 中可内联为 JSX 后对各 `<g id>` 做 transform/opacity 插值
- 预览：`preview.png`（4×5 联系表，深色底，含 6 个 ECDHE 分步帧）
- 画面文字均为中文；保留的英文仅为术语/内容本身：CA、TLS、HTTP、example.com、明信片上的明文 `user=alice&password=123456`

| 资产 | viewBox | 章节 | 颜色（令牌） | 可动画元素 id / 建议状态 |
|---|---|---|---|---|
| padlock-open.svg | 0 0 512 512 | 开场、第2章、结尾 | muted #6B7280 锁体、text-2 #9CA3AF 锁梁 | `shackle` 上抬 40px；与 closed 交叉淡化或 shackle 下落 translateY(-40→0) 表示“上锁” |
| padlock-closed.svg | 0 0 512 512 | 第2章、第5章（加密通信）、结尾、地址栏锁 | primary #22D3EE 锁体、text #E5E7EB 锁梁 | `shackle`、`body`；上锁瞬间 scale 1→1.08→1 弹一下 |
| key-symmetric.svg | 0 0 512 512 | 第2章（同一把钥匙）、第3/5章（金色会话密钥） | accent #F59E0B | `key`；两端各一把（复制）；飞行路径 + 旋转；被抓时晃动；第3章“合成”后 scale 0→1 出现 |
| postcard.svg | 0 0 960 600 | 第1章（HTTP 像明信片）、结尾（明信片→信箱→盖章→封条的起点） | surface 卡面、text-2 描边、surface-2 明文框、text 明文、danger 高亮 `password=123456`、accent 邮票、primary 收件地址 | `card` 飞行（浏览器→中转站→服务器）、`plaintext` 被眼睛图标扫过时闪烁、`stamp` 盖下、`address`；结尾整体缩小并装入 envelope-sealed |
| keypair-public.svg | 0 0 512 512 | 第3章、第4章（被调包的亮色钥匙）、第5章 | primary #22D3EE，标签“公钥” | `public-key`、`tag`；沿线交换移动；调包时可换 danger 色描边 |
| keypair-private.svg | 0 0 512 512 | 第3章 | 暗色体 surface-2 #1F2937 + secondary #3B82F6 描边/盾牌，标签“私钥” | `private-key`、`shield`；始终留在本端，只做轻微呼吸 opacity |
| envelope.svg | 0 0 512 512 | 第1章（明信片/明文信）、结尾起点 | surface #111827、text-2 描边、text 信纸、muted 文字条 | `letter` 从信封抽出/插入 translateY；`flap-open` 默认 opacity 0 备用 |
| envelope-sealed.svg | 0 0 512 512 | 第2章（上锁信箱）、第6章（封条）、结尾 | surface、surface-2 封口、accent 封印、success #22C55E 封条 | `flap` 合上、`seal` scale 盖章、`tamper-strip` 宽度 0→100%；被篡改时封条改 danger #F87171 并抖动 |
| certificate.svg | 0 0 720 512 | 第4章 | surface 纸、primary 边框/域名、accent 印章与绶带、text/text-2 文字 | `domain`（占位 `example.com`，替换文字即可）、`pubkey-chip`、`seal` 盖章 scale 1.4→1 + 旋转、`ribbon` 下落 |
| ca-badge.svg | 0 0 512 512 | 第4章（证书链/根证书）、结尾“印章”图标 | accent 盾、surface 外环、bg 文字与勾 | `badge`、`check`；证书链逐层打勾：check stroke-dashoffset 描线动画 |
| eavesdropper.svg | 0 0 512 512 | 开场、第1/2/4章、第3章“算不出” | muted 剪影、surface-2 帽子、danger 眼睛 | `figure`、`eyes`；淡入、眼睛闪烁（ry 缩放）、伸手动作用整体平移；中性剪影无真人特征 |
| ecdhe-mix.svg | 0 0 1600 900 | 第3章、第5章 | primary 公开参数、danger 浏览器私有、success 服务器私有、secondary+半透明叠色表示“混合后公开值”、accent 会话密钥、text-2 箭头文字 | 顺序：`shared-param` → `left-secret`/`right-secret` → 合成 `left-public`/`right-public`（scale 弹出）→ `exchange` 虚线 dashoffset 流动 → `eve` 淡入 → `left-derive`/`right-derive` 同时出现金色圆 |
| hash-check.svg | 0 0 512 512 | 第6章（AEAD 校验）、结尾“封条”图标 | primary 指纹线、success 勾章 | `fingerprint` 描线（dashoffset）、`badge` scale 弹出、`check` 描线；校验失败时 badge 换 danger |

注意：ecdhe-mix 中“公开值”的紫/青色是 secondary 与私有色半透明叠加得到的，属混色效果而非新令牌。

## ECDHE 分步帧（第3章 24 秒全屏，第5章复用最后一帧）

`ecdhe-step1..6.svg` 都是 1600×900 的整帧（自带 bg #0B1020 底），每一步在上一步基础上多出一层，元素 id 与 ecdhe-mix.svg 相同（ecdhe-mix = 第 6 步，透明底）：

1. `shared-param` 公开参数
2. `left-secret` / `right-secret` 双方私有色
3. `mix` 虚线 + `left-public` / `right-public` 混合出公开值
4. `exchange` 只交换公开值
5. `eve` 偷听者算不出
6. `left-derive` / `right-derive` + “= 同一把会话密钥 =”

字号：节点标签 30 单位，“只交换公开值”“偷听者算不出”32，标题与结论 44；按 1920 宽渲染（×1.2）最小为 36px，满足 ≥28px。建议每步约 4 秒，可直接切帧，也可用 mix 内联后对新增层做淡入。
