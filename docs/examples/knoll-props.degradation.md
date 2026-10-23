# 范例：EP.14 degradation 制作说明

空白模板在 [../knoll-props.template.md](../knoll-props.template.md)。下面是 EP.14 的完整制作说明，用来看每一节该写成什么样。文中的哈希、镜号和坐标属于这一期，不要抄进新期。

文首点名的 `make_knoll_props.py` 不在本仓，不要去跑。

---

# EP.14 degradation-v1 搜索页和结算页，为什么两个价不一样：组件用法与 Knoll 需要新增的页型与属性

依据：storyboard.json 6265993b（冻结副本 storyboard.6265993b.json，两者逐字节相同）；covers.json 8cb7aafb。本文件由 make_knoll_props.py 从分镜生成，值与分镜逐字一致；script 94a2e143 / voice 9e70470c / words 36bccee8 / cues 751217cb / shot_frames f8f03b6c，5152 帧，20 镜，镜头绝对帧按 Knoll 所定。
所有帧号从本镜第 0 帧算；坐标一律是 1920×1080 画面坐标（封面为封面画布坐标）。渲染代码不写死任何文字、颜色、坐标或帧号。

只给人看 / 给 validate 用、渲染时忽略的字段：`cueLog` `timerLog` `cueOnset` `onsetLocal` `timingReason` `timingRole` `appearTimer` `dimFromCue` `overlayOk` `conflict` `sampleData` `questionText` `boxCard` `timerDriven` `outsidePage` `sync` `cueText` `disappearCueText` `addressFit` `coverStill`。
`strike` + `strikeColor` 是渲染属性（文字中线删除线，线宽 = fontSize × 0.08，颜色缺省取 `color`），本期用在镜 8, 9, 16。

## 本版相对 8508f1a2 的变化（Deming 预检 3 必改 + 7 可选、Knoll 预检 2 项）——要重渲：镜 1–19（「示例数据」角标 w 168→172 每镜都动；实质画面变化在 1、3、4、5、7、8、9、10、11、13、14、16、17、19），镜 20 不变；三张封面全部重渲
- **镜 7、8、9 三列**（必改 1）：`a-search`「搜索页 →」[420,300,240,72] 右对齐、新增 `svc-node`「红包服务」[700,300,240,72] 居中（第 0 帧即在，唯一节点）、`a-checkout`「← 结算页」[980,300,240,72] 左对齐；镜 7 `slow`、镜 8 `keep` x 980；镜 9 `prio` [700,440]。划线/变暖/加粗的状态帧不变。
- **镜 16** `keep`「保核心链路（示例）」移到 [1000,420]（「结算 179」正下方，必改 2），帧与挂词不变。
- **封面**（必改 3 + Nolan 定）：单个结算页窗口（双窗在 4:3 放不下：两窗 < 600 进 compact，地址栏会缩字），`backTabs: []`；页面首行离页头 ≥ 24 px（boxes 从页头 80 下算）；窗口下方一行价格「搜索 199 元 → 结算 179 元（示例）」由 5 段普通 text 拼成（`priceLine: true`，`priceRole` big/small 只给人看），199 暖色、179 绿色大号数字。原「ask/result」两行删除。
- **镜 3** 第 0 帧即唯一空白标签（`pageBlank`、url 空），「打开搜索页」处 type1 起逐字输入（不再有 newTab 状态，也不留旧结算标签）；`nocoupon` 移到 [1160,610]。
- **标签链少一个「结算」**（可选 7）：镜 4 新开后 backTabs [搜索]；镜 13 第 0 帧即搜索标签（afterTabs [结算]，无切换状态）；镜 14 切到结算后 backTabs [搜索]；镜 19 第 0 帧即成功页（backTabs [搜索]），「要是」只压暗。
- **点击波纹 20 帧**（Knoll）：镜 4 按加购后 20 帧才新开标签（输入、加载随之后移，加载在第 45 帧左右，红包行与 179 的挂词帧不变）；镜 14 按提交后 20 帧才出成功页。
- **镜 5** 竖线 h 340（延到「= 到手价」）；**镜 10、11** 说明卡 y 230 h 570（不压示例角标），首行 y 262；镜 13 `works` 移到 [1160,610]；所有 CalloutTag / CornerBadge 加宽 12 px（页外状态角标 x 同步左移 12）。

## 相对 EP.13 的变化——Knoll 必读
- **新页型 `page: 'shopPrice'`**（BrowserChrome）：一张页型三种 `view`——`search`（搜索结果页）、`checkout`（结算页，带红包抵扣行）、`success`（成功页）。取代 EP.13 的 shopCheckout（本期没有运费险行）。见 §1。
- **全片不开开发者工具**：没有 DevToolsNetwork / BlockHighlight / devtoolsRow。
- **镜 1、17 两扇窗口**：`page`（左，search）与 `page2`（右，checkout）同镜并排，各自独立的 BrowserChrome，`scale` 0.6。
- **标签切换不重开**：镜 13、14 用状态帧直接改 `view`/`url`/`title`/`backTabs`/`afterTabs`（切回已开标签，不新开、不输入）；镜 3、4 是新开标签 + 逐字输入。
- **按钮波纹可指向任意按钮框**：`ripples[].center` 取 `boxes` 里的键（镜 4 = `item0Button` 加购；镜 14 = `button` 提交订单）。
- **页外右上状态角标** `svc`（CornerBadge，`outsidePage: true`，右缘 1660，y 90）：镜 3/13/14「搜索页红包计算：已关闭（示例）」，镜 4「结算页红包计算：正常（示例）」（绿字 #86EFAC、底 #14532D）。
- **段长例外**：[{"shot": 1, "frames": 314, "max": 300, "reason": "Knoll 帧表定稿（开场冲突＋问题句），不剪配音"}]（Knoll 帧表定稿）。
- 沿用：dimFrom / backTabs / afterTabs / ripples / readAlong / dimPage / fadeOut / CornerBadge / CalloutTag / `highlighted`+`pulse` / `strike` / `padLeft` / rect 的 `w` 状态帧（镜 6 资源横条）。

## 0. 画面类型 `frame`
| 镜 | id | frame | 绝对帧 | 帧数 | 方框 |
|---|---|---|---|---|---|
| 1 | 01-hook | `"browser"` | 0–314 | 314 |  |
| 2 | 02-not-bug | `"canvas"` | 314–595 | 281 |  |
| 3 | 03-search-page | `"browser"` | 595–865 | 270 |  |
| 4 | 04-checkout-page | `"browser"` | 865–1131 | 266 |  |
| 5 | 05-price-deps | `"canvas"` | 1131–1395 | 264 |  |
| 6 | 06-search-load | `"canvas"` | 1395–1650 | 255 |  |
| 7 | 07-contend | `"canvas"` | 1650–1905 | 255 |  |
| 8 | 08-turn-off | `"canvas"` | 1905–2148 | 243 |  |
| 9 | 09-after-off | `"canvas"` | 2148–2382 | 234 |  |
| 10 | 10-term-core | `"canvas"` | 2382–2632 | 250 | 是 |
| 11 | 11-term-degrade | `"canvas"` | 2632–2858 | 226 | 是 |
| 12 | 12-bridge-ep13 | `"canvas"` | 2858–3115 | 257 |  |
| 13 | 13-search-ok | `"browser"` | 3115–3375 | 260 |  |
| 14 | 14-checkout-ok | `"browser"` | 3375–3601 | 226 |  |
| 15 | 15-coupon-safe | `"canvas"` | 3601–3827 | 226 |  |
| 16 | 16-two-prices | `"canvas"` | 3827–4103 | 276 |  |
| 17 | 17-opening-resolved | `"browser"` | 4103–4363 | 260 |  |
| 18 | 18-kept-vs-dropped | `"canvas"` | 4363–4630 | 267 | 是 |
| 19 | 19-discussion | `"browser"` | 4630–4883 | 253 |  |
| 20 | 20-next-episode | `"canvas"` | 4883–5152 | 269 | 是 |

canvas 镜全屏干净底色，不画外框、标签页、地址栏和网址。

## 1. BrowserChrome `page: 'shopPrice'`（新）
外框、标签页、地址栏同现有 BrowserChrome（`showPadlock`、`title`、`url`、`pageBlank`、`tabLoading`、`backTabs`、`afterTabs`、`dimPage`、`ripples`、`buttonPressed`）。页面区白底，按 `view` 画；区块位置全在 `boxes`，字号 `rowSize` `buttonSize` `headlineSize`；`scale` 只给人看（boxes 已按它算好）。
| 字段 | 类型 | 含义 |
|---|---|---|
| `view` | 'search' \| 'checkout' \| 'success' | 见下 |
| `search` | {query, items:[{text, button, highlighted, background?}]} | search 视图：`boxes.query` 搜索框文字；`items[i]` 画在 `boxes.item{i}`，按钮文字画在 `boxes.item{i}Button`；`highlighted` = 行底浅黄 + 轻微脉动；`background: true` 的行只作背景（正常画，不另强调） |
| `checkout` | {product, address, coupon:{visible, applied, text, highlighted}, total, button} | checkout 视图：`boxes.product` `address` `coupon` `total` `button`；见 §1.1 |
| `success` | {headline, paid} | success 视图：`boxes.headline` `boxes.paid`（不画按钮、不画红包行） |

### 1.1 红包抵扣行 `checkout.coupon`
| visible | applied | 画法 |
|---|---|---|
| false | false | 行位置保留、不画任何东西（镜 4 加载后、「多出一行红包抵扣」前） |
| true | false | 画 `text`（绿色字 #15803D），应付仍为 199（镜 4「多出一行红包抵扣」到「红包这时才真正算上」之间） |
| true | true | 画 `text`，应付 = 179（已计入） |
`highlighted: true` = 该行底浅黄 + 轻微脉动（镜 1、4、17）。应付文字直接取 `checkout.total`，渲染不自己算。

### 1.2 各镜窗口与状态帧（本镜帧）
- 镜 1 `page` [120,280,820,480] scale=0.6：初始 view=search url='shop.example/search' title='搜索' coupon={"visible": true, "applied": true, "text": "红包抵扣：−20 元（示例）", "highlighted": false} total='应付：179 元（示例）' backTabs=[] afterTabs=[]
- 镜 1 `page2` [980,280,820,480] scale=0.6：初始 view=checkout url='shop.example/checkout' title='结算' coupon={"visible": true, "applied": true, "text": "红包抵扣：−20 元（示例）", "highlighted": false} total='应付：179 元（示例）' backTabs=[] afterTabs=[]
  - 帧 211（couponLit，对「红包这时才算上」）{"coupon": {"visible": true, "applied": true, "text": "红包抵扣：−20 元（示例）", "highlighted": true}, "total": "应付：179 元（示例）"}
- 镜 3 `page` [120,280,1680,540] scale=0.8：初始 view=search url='' title='新标签页' coupon={"visible": true, "applied": true, "text": "红包抵扣：−20 元（示例）", "highlighted": false} total='应付：179 元（示例）' backTabs=[] afterTabs=[]
  - 帧 22（loaded，对「计时」）{"pageBlank": false, "title": "搜索", "url": "shop.example/search", "view": "search", "item0.highlighted": false}
  - 帧 42（itemLit，对「列表上每件商品都标着一个到手价」）{"item0.highlighted": true}
  - 逐字输入 type1..type19：帧 1–19（每帧一字），`url` 依次为 `shop.example/search` 前 1..19 个字符
- 镜 4 `page` [120,280,1680,540] scale=0.8：初始 view=search url='shop.example/search' title='搜索' coupon={"visible": true, "applied": true, "text": "红包抵扣：−20 元（示例）", "highlighted": false} total='应付：179 元（示例）' backTabs=[] afterTabs=[]
  - 帧 1（press，对「加购进结算页」）{"ripples": [{"id": "r1", "bornFrame": 1, "center": "item0Button", "r0": 12, "r1": 96, "growFrames": 20, "holdOpacity": 0.45, "color": "#22D3EE"}]}
  - 帧 21（newTab，对「计时」）{"pageBlank": true, "url": "", "title": "新标签页", "tabLoading": false, "backTabs": ["搜索"], "ripples": []}
  - 帧 46（loaded，对「计时」）{"pageBlank": false, "title": "结算", "url": "shop.example/checkout", "view": "checkout", "coupon": {"visible": false, "applied": false, "text": "", "highlighted": false}, "total": "应付：199 元（示例）"}
  - 帧 133（couponRow，对「多出一行红包抵扣」）{"coupon": {"visible": true, "applied": false, "text": "红包抵扣：−20 元（示例）", "highlighted": true}, "total": "应付：199 元（示例）"}
  - 帧 187（applied，对「红包这时才真正算上」）{"coupon": {"visible": true, "applied": true, "text": "红包抵扣：−20 元（示例）", "highlighted": false}, "total": "应付：179 元（示例）"}
  - 逐字输入 type1..type21：帧 23–43（每帧一字），`url` 依次为 `shop.example/checkout` 前 1..21 个字符
- 镜 13 `page` [120,280,1680,540] scale=0.8：初始 view=search url='shop.example/search' title='搜索' coupon={"visible": true, "applied": true, "text": "红包抵扣：−20 元（示例）", "highlighted": false} total='应付：179 元（示例）' backTabs=[] afterTabs=['结算']
- 镜 14 `page` [120,280,1680,540] scale=0.8：初始 view=search url='shop.example/search' title='搜索' coupon={"visible": true, "applied": true, "text": "红包抵扣：−20 元（示例）", "highlighted": false} total='应付：179 元（示例）' backTabs=[] afterTabs=['结算']
  - 帧 1（tabCheckout，对「结算页照常」）{"view": "checkout", "title": "结算", "url": "shop.example/checkout", "backTabs": ["搜索"], "afterTabs": [], "coupon": {"visible": true, "applied": true, "text": "红包抵扣：−20 元（示例）", "highlighted": false}, "total": "应付：179 元（示例）"}
  - 帧 77（press，对「也能继续下单付款」）{"buttonPressed": true, "ripples": [{"id": "r1", "bornFrame": 77, "center": "button", "r0": 12, "r1": 96, "growFrames": 20, "holdOpacity": 0.45, "color": "#22D3EE"}]}
  - 帧 97（success，对「计时」）{"view": "success", "buttonPressed": false}
- 镜 17 `page` [120,280,820,480] scale=0.6：初始 view=search url='shop.example/search' title='搜索' coupon={"visible": true, "applied": true, "text": "红包抵扣：−20 元（示例）", "highlighted": false} total='应付：179 元（示例）' backTabs=[] afterTabs=[]
  - 帧 55（itemLit，对「搜索页没算红包」）{"item0.highlighted": true}
- 镜 17 `page2` [980,280,820,480] scale=0.6：初始 view=checkout url='shop.example/checkout' title='结算' coupon={"visible": true, "applied": true, "text": "红包抵扣：−20 元（示例）", "highlighted": false} total='应付：179 元（示例）' backTabs=[] afterTabs=[]
  - 帧 105（couponLit，对「结算页才把红包算上」）{"coupon": {"visible": true, "applied": true, "text": "红包抵扣：−20 元（示例）", "highlighted": true}, "total": "应付：179 元（示例）"}
- 镜 19 `page` [120,280,1680,540] scale=0.8：初始 view=success url='shop.example/checkout' title='结算' coupon={"visible": true, "applied": true, "text": "红包抵扣：−20 元（示例）", "highlighted": false} total='应付：179 元（示例）' backTabs=['搜索'] afterTabs=[]
  - 帧 1（successDim，对「要是」）{"dimPage": 0.7}

### 1.3 标签延续
- 镜 3：第 0 帧即唯一空白标签；「打开搜索页」起逐字输入 → 加载搜索页。
- 镜 4：接搜索标签；按「加购」（波纹 20 帧）→ 20 帧后新开结算标签（搜索在左）→ 输入 → 加载（无红包行，应付 199）→ 红包行出现 → 应付 179（只变一次）。不提交。
- 镜 13：第 0 帧即搜索标签（`afterTabs` [结算]），无切换。镜 14：「结算页照常」切到结算标签（`backTabs` [搜索]）→ 按提交（波纹 20 帧）→ 20 帧后成功页。
- 镜 19：第 0 帧即镜 14 成功页（`backTabs` [搜索]）；「要是」处 `dimPage` 0.7；讨论题 `padLeft` 32。
- 镜 17 回放镜 1 两窗（不新开、不输入、不提交）；左窗首行、右窗红包行各随一句轻亮。

## 2. 页外角标与叠字
- 镜 1 `why` CalloutTag [820,778,376,67] fs=36 color=#FDE68A bg=#0B1020 appear=264 text='怎么回事？（示例）'
- 镜 3 `nocoupon` CalloutTag [1160,610,556,67] fs=36 color=#FDE68A bg=#0B1020 appear=202 text='本页到手价：未算红包（示例）'
- 镜 3 `svc` CornerBadge [1136,90,524,55] fs=32 color=#FDE68A bg=#7C2D12 appear=202 text='搜索页红包计算：已关闭（示例）'
- 镜 4 `svc` CornerBadge [1168,90,492,55] fs=32 color=#86EFAC bg=#14532D appear=187 text='结算页红包计算：正常（示例）'
- 镜 7 `a-search` None [420,300,240,72] fs=48 color=#FFFFFF bg=#0B1020 appear=0 states=[[98, "warm"]] text='搜索页 →'
- 镜 7 `svc-node` None [700,300,240,72] fs=48 color=#FFFFFF bg=#0B1020 appear=0 text='红包服务'
- 镜 7 `a-checkout` None [980,300,240,72] fs=48 color=#FFFFFF bg=#0B1020 appear=1 states=[[98, "warm"]] text='← 结算页'
- 镜 7 `slow` CalloutTag [980,420,520,67] fs=36 color=#FDBA74 bg=#0B1020 appear=180 text='结算变慢／可能卡住（示例）'
- 镜 8 `a-search` None [420,300,240,72] fs=48 color=#FDBA74 bg=#0B1020 appear=0 states=[[1, "struck"]] text='搜索页 →'
- 镜 8 `svc-node` None [700,300,240,72] fs=48 color=#FFFFFF bg=#0B1020 appear=0 text='红包服务'
- 镜 8 `a-checkout` None [980,300,240,72] fs=48 color=#FDBA74 bg=#0B1020 appear=0 states=[[189, "bold"]] text='← 结算页'
- 镜 8 `keep` CalloutTag [980,420,448,67] fs=36 color=#86EFAC bg=#0B1020 appear=189 text='资源留给结算页（示例）'
- 镜 9 `a-search` None [420,300,240,72] fs=48 color=#94A3B8 bg=#0B1020 appear=0 text='搜索页 →'
- 镜 9 `svc-node` None [700,300,240,72] fs=48 color=#FFFFFF bg=#0B1020 appear=0 text='红包服务'
- 镜 9 `a-checkout` None [980,300,240,72] fs=48 color=#86EFAC bg=#0B1020 appear=0 text='← 结算页'
- 镜 9 `prio` None [700,440,680,62] fs=40 color=#86EFAC bg=#0B1020 appear=53 text='红包服务：优先服务结算页（示例）'
- 镜 13 `works` CalloutTag [1160,610,412,67] fs=36 color=#86EFAC bg=#0B1020 appear=1 text='能搜、能加购（示例）'
- 镜 13 `svc` CornerBadge [1136,90,524,55] fs=32 color=#FDE68A bg=#7C2D12 appear=0 states=[[207, "lit"]] text='搜索页红包计算：已关闭（示例）'
- 镜 14 `works` CalloutTag [1160,610,412,67] fs=36 color=#86EFAC bg=#0B1020 appear=0 disappear=1 fadeOut=6 text='能搜、能加购（示例）'
- 镜 14 `svc` CornerBadge [1136,90,524,55] fs=32 color=#FDE68A bg=#7C2D12 appear=0 disappear=1 fadeOut=6 text='搜索页红包计算：已关闭（示例）'
- 镜 14 `core` CalloutTag [1100,600,448,67] fs=36 color=#86EFAC bg=#0B1020 appear=171 text='核心链路：正常（示例）'
- 镜 16 `keep` None [1000,420,472,72] fs=48 color=#22D3EE bg=#0B1020 appear=128 text='保核心链路（示例）'
- 镜 17 `deg` CalloutTag [160,778,532,62] fs=32 color=#FDE68A bg=#0B1020 appear=168 text='降级：关搜索页红包计算（示例）'
- 镜 17 `core` CalloutTag [1000,778,532,62] fs=32 color=#86EFAC bg=#0B1020 appear=168 text='核心链路：结算下单照常（示例）'

## 3. 计数与同步（画面节奏，同帧）
- 镜 6 `reqs`（与资源同帧同步）帧 [87, 153, 161, 169] → ["请求：10（示例）", "请求：20（示例）", "请求：30（示例）", "请求：40（示例）"]
- 镜 6 `res`（与请求数同帧同步）帧 [145, 153, 161, 169] → ["红包服务可用资源：100%（示例）", "红包服务可用资源：80%（示例）", "红包服务可用资源：60%（示例）", "红包服务可用资源：40%（示例）"]
- 镜 6 `res-free`（与资源数字同帧同步）帧 [145, 153, 161, 169] → [800, 640, 480, 320]
- 镜 6 `res-track`（暖色底槽，被占用部分）与 `res-free`（绿色，可用部分，`w` 状态帧 800→640→480→320）叠放，同帧出现。

## 4. 封面 covers.json
covers.json 8cb7aafb：三尺寸 16x9 / 4x3 / 3x4 + poster（= 3x4）。单窗 `page: 'shopPrice'`、`view: 'checkout'`、红包行已计入且轻亮、应付 179（`coverStill: true` = 静帧），`backTabs: []`；窗口下方一行价格「搜索 199 元 → 结算 179 元（示例）」（5 段 text，同一 y，199/179 大号异色）；「示例数据」CornerBadge 在页面外。选单窗原因：双窗在 4:3 的 810 px 内放不下（两窗 < 600 进 compact，地址栏 26px 等宽 333 px 需窗宽 ≥ 435，合计 > 810 只能缩字），按 Nolan 退路用单窗＋一行大号价格。4:3 内容全在 x 315..1125、y < 918。
- 16x9 1920×1080 bottom15Y=918 窗口 [330,370,900,400] backTabs=[] 首行离页头 28 px；价格行 y 784 h 104：'搜索'[363,99] fs40 #E5E7EB、'199'[468,160] fs80 #FDBA74、'元 → 结算'[634,229] fs40 #E5E7EB、'179'[869,160] fs80 #86EFAC、'元（示例）'[1035,222] fs40 #E5E7EB
- 4x3 1440×1080 bottom15Y=918 窗口 [340,330,780,400] backTabs=[] 首行离页头 24 px；价格行 y 750 h 95：'搜索'[337,82] fs32 #E5E7EB、'199'[425,146] fs72 #FDBA74、'元 → 结算'[577,187] fs32 #E5E7EB、'179'[770,146] fs72 #86EFAC、'元（示例）'[922,181] fs32 #E5E7EB
- 3x4 1080×1440 bottom15Y=1224 窗口 [140,380,800,480] backTabs=[] 首行离页头 28 px；价格行 y 900 h 123：'搜索'[64,99] fs40 #E5E7EB、'199'[169,189] fs96 #FDBA74、'元 → 结算'[364,229] fs40 #E5E7EB、'179'[599,189] fs96 #86EFAC、'元（示例）'[794,222] fs40 #E5E7EB

## 5. 方框加文字镜 / 讨论题 / 下期
boxShots = ['10-term-core', '11-term-degrade', '18-kept-vs-dropped', '20-next-episode']（脚本 629b5042：方框加文字仅镜 10、11、18、20，4/20 = 20%）
discussionQuestion = '要是搜索页和结算页都把红包计算一起关掉，下单还能不能顺利完成？评论区说说。'
nextEpisode = {"episode": 15, "title": "加个索引，为啥就快了？", "teaser": "下期，加个索引，为啥就快了？"}
