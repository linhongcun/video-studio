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
| postcard-mini.svg | 0 0 960 600 | 第1章飞行、第2章装箱（小尺寸） | 同 postcard，去掉全部文字 | 小于 960 宽显示时文字会 <28px，所以只留形状；960×600 全尺寸时用 postcard.svg（缩放 1.0，最小 28px） |
| keypair-public.svg | 0 0 512 512 | 第3章、第4章（被调包的亮色钥匙）、第5章 | primary #22D3EE，标签“公钥” | `public-key`、`tag`；沿线交换移动；调包时可换 danger 色描边 |
| keypair-private.svg | 0 0 512 512 | 第3章 | 暗色体 surface-2 #1F2937 + secondary #3B82F6 描边/盾牌，标签“私钥” | `private-key`、`shield`；始终留在本端，只做轻微呼吸 opacity |
| envelope.svg | 0 0 512 512 | 第1章（明信片/明文信）、结尾起点 | surface #111827、text-2 描边、text 信纸、muted 文字条 | `letter` 从信封抽出/插入 translateY；`flap-open` 默认 opacity 0 备用 |
| envelope-sealed.svg | 0 0 512 512 | 第2章（上锁信箱）、第6章（封条）、结尾 | surface、surface-2 封口、accent 封印、success #22C55E 封条 | `flap` 合上、`seal` scale 盖章、`tamper-strip` 宽度 0→100%；被篡改时封条改 danger #F87171 并抖动 |
| certificate.svg | 0 0 720 512 | 第4章 | surface 纸、primary 边框/域名、accent 印章与绶带、text/text-2 文字 | `domain`（占位 `example.com`，替换文字即可）、`pubkey-chip`、`seal` 盖章 scale 1.4→1 + 旋转、`ribbon` 下落 |
| ca-badge.svg | 0 0 512 512 | 第4章（证书链/根证书）、结尾“印章”图标 | accent 盾、surface 外环、bg 文字与勾 | `badge`、`check`；证书链逐层打勾：check stroke-dashoffset 描线动画 |
| eavesdropper.svg | 0 0 512 512 | 开场、第1/2/4章、第3章“算不出” | muted 剪影、surface-2 帽子、danger 眼睛 | `figure`、`eyes`；淡入、眼睛闪烁（ry 缩放）、伸手动作用整体平移；中性剪影无真人特征 |
| ecdhe-mix.svg | 0 0 1600 900 | 第3章、第5章 | primary 公开参数、danger 浏览器私有、success 服务器私有、secondary+半透明叠色表示“混合后公开值”、accent 会话密钥、text-2 箭头文字 | 顺序：`shared-param` → `left-secret`/`right-secret` → 合成 `left-public`/`right-public`（scale 弹出）→ `exchange` 虚线 dashoffset 流动 → `eve` 淡入 → `left-derive`/`right-derive` 同时出现金色圆 |
| ecdhe-combine.svg | 0 0 1600 900 | 第3章状态② | secondary+对方私有色叠色＝收到的公开值、danger/success 自己的私有、accent 会话密钥、text-2 标签 | `left-combine` / `right-combine`；两侧同时“+”合成，箭头下落后金色圆 scale 0→1 |
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

字号（实测）：节点标签 38 单位，“只交换公开值”“偷听者算不出”“算出会话密钥”40，“浏览器/服务器”与结论 48，“+”64。分镜中按 1468×780 contain 放置，缩放 = min(1468/1600, 780/900) = 0.8667，屏幕最小字号 38×0.8667 ≈ 32.9px（≥28px）。第3章 ECDHE 镜头只用 3 个关键状态：step4（交换公开值）→ ecdhe-combine（各自合成）→ step6（同一把金钥匙，含偷听者算不出；两把相同 key-symmetric 金钥匙 160×160 放在屏幕 (411,566) 与 (1347,566)，紧贴底部两个橙色圆正上方，同时弹出并慢转 8°；step6 下落箭头已缩短为 560→600 让位），切点跟随字幕分句；step1–3、5 保留备用。

## storyboard.json 用到的动画属性与元素字段（按 storyboard.json 实际 grep 整理）

关键帧 `frame` 相对镜头；`value` 按下表解释。

| 属性 | 用于 | 含义 / 实现建议 |
|---|---|---|
| opacity | 全片 | 0→1 淡入 / 1→0 淡出 |
| scale | 全片 | 缩放，以元素中心为原点；spring 用于弹出 |
| x / y | 全片 | 元素左上角绝对坐标（px，1920×1080） |
| rotate | keyL、keyR（asymmetric-2）、keyFly | 角度（°），中心旋转；ECDHE 状态③ 两把金钥匙各自 0→8° 慢转 |
| charsVisible | intro-1 login | 打字机，显示前 N 个字符 |
| drawProgress | handshake 箭头 ch / sh / data | 箭头描线 0→1（stroke-dashoffset） |
| tamperStrip | envelope-sealed（integrity-1、recap-1 box） | `#tamper-strip` 宽度 0→100%（0→1） |
| tamperAlarm | envelope-sealed（integrity-1 box） | 0→1：封条改 danger #F87171 并左右抖动 ±6px 约 10 帧 |
| drawCheck | ca-badge（certificate-3 rootOk/midOk/leafOk） | `#check` 描线 stroke-dashoffset 0→1 |
| badgeDanger | hash-check（integrity-1 hash） | 0→1：`#badge` 颜色 success → danger，勾可隐去 |
| glowPlaintext | postcard（plaintext-2） | 0→1：`#plaintext` 外发光 danger 色并轻闪，强调明文可见 |

| 元素字段 | 含义 |
|---|---|
| type | text / rect / image / icon / arrow / line |
| asset | image 的 SVG 路径（相对 episodes/https/） |
| fit | image 缩放方式；`contain` = 等比放入 w×h 并居中 |
| tint | 给 SVG 主色整体换色（certificate-1 `fake` 公钥用 danger #F87171 表示假钥匙） |
| state | ECDHE 状态说明（仅注释） |
| label / note | rect、icon、arrow 上的显示文字 / 实现备注（note 不上屏） |
| direction | arrow 方向：r 向右、l 向左、lr 双向 |
| role=subtitle | 字幕层，固定 y 900–980 |
| stroke / radius / align / font / fontSize | 描边色 / 圆角 / 对齐 / 字体 / 字号（px） |

| 已替换的占位 icon | 现用资产 | 镜头 |
|---|---|---|
| cup（原 icon） | coffee-cup.svg：琥珀色杯身、热气、托盘，无文字 | intro-1 |
| eye（原 icon） | eye.svg：danger 色眼睛轮廓 + 虹膜/瞳孔 | plaintext-2 |
| pencil（原 icon） | pencil.svg：斜放铅笔 + 涂改线，danger 色 | plaintext-2、integrity-1（向信箱移动） |
| mask（原 icon） | mask.svg：danger 色半脸面具 | plaintext-2 |

| server | plaintext-1、symmetric-2 | type=rect 卡片，与浏览器同一套样式（panel 底、secondary 描边、圆角 16），标签「服务器」36px，由 Knoll 实现 |

storyboard 中已无 type=icon 元素；所有图标均为自绘 SVG（商用安全）。

字号规则：所有画面文字（含 SVG 内文字 × 放置缩放）屏幕上 ≥28px，validate.py 自动检查（字幕除外）。公钥/私钥标签 54 单位（280 宽显示时 29.5px）；ca-badge “CA” 132 单位（110 宽显示时 28.4px）。
