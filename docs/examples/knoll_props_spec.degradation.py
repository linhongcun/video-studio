"""EP.14 degradation-v1。build(ctx) -> str。

散文、shopPrice 字段表和本镜状态补丁留在这里。表、叠字、同步、封面尺寸、§5 用共享 helper。
输出与 docs/examples/knoll-props.degradation.md 第 9 行起逐字节相同。
"""
FORBID = ('熔断',)

_OVERLAY_IDS = ('svc', 'why', 'nocoupon', 'works', 'core', 'deg', 'svc-node', 'a-search', 'a-checkout', 'slow', 'keep', 'prio')


def _ep14_extra(k):
    extra = {kk: k[kk] for kk in k if kk not in ('frame', 'state', 'cueText', 'onsetLocal', 'timerDriven', 'checkout', 'search')}
    if 'checkout' in k:
        extra['coupon'] = k['checkout']['coupon']
        extra['total'] = k['checkout']['total']
    if 'search' in k:
        extra['item0.highlighted'] = k['search']['items'][0]['highlighted']
    return extra


def build(ctx):
    d = ctx.d
    cv = ctx.cv
    sbb = ctx.sbb
    cvb = ctx.cvb
    sha = ctx.sha
    J = ctx.J
    els = ctx.els
    total = ctx.total
    h_script = ctx.file_sha8(('script.md', 'script'), '94a2e143')
    h_voice = ctx.file_sha8(('voice.wav', 'remotion/public/audio/voice.wav'), '9e70470c')
    h_words = ctx.file_sha8(('words.json',), '36bccee8')
    h_cues = ctx.file_sha8(('voice/cues.json', 'cues.json'), '751217cb')
    h_frames = ctx.file_sha8(('voice/shot_frames.json', 'shot_frames.json'), 'f8f03b6c')
    o = []
    o.append('# EP.14 degradation-v1 搜索页和结算页，为什么两个价不一样：组件用法与 Knoll 需要新增的页型与属性\n')
    o.append(f'依据：storyboard.json {sha(sbb)}（冻结副本 storyboard.{sha(sbb)}.json，两者逐字节相同）；covers.json {sha(cvb)}。本文件由 make_knoll_props.py 从分镜生成，值与分镜逐字一致；script {h_script} / voice {h_voice} / words {h_words} / cues {h_cues} / shot_frames {h_frames}，{total} 帧，20 镜，镜头绝对帧按 Knoll 所定。')
    o.append('所有帧号从本镜第 0 帧算；坐标一律是 1920×1080 画面坐标（封面为封面画布坐标）。渲染代码不写死任何文字、颜色、坐标或帧号。\n')
    o.append(ctx.ignore_line())
    o.append(ctx.strike_line() + '\n')
    o.append('## 本版相对 8508f1a2 的变化（Deming 预检 3 必改 + 7 可选、Knoll 预检 2 项）——要重渲：镜 1–19（「示例数据」角标 w 168→172 每镜都动；实质画面变化在 1、3、4、5、7、8、9、10、11、13、14、16、17、19），镜 20 不变；三张封面全部重渲')
    o.append('- **镜 7、8、9 三列**（必改 1）：`a-search`「搜索页 →」[420,300,240,72] 右对齐、新增 `svc-node`「红包服务」[700,300,240,72] 居中（第 0 帧即在，唯一节点）、`a-checkout`「← 结算页」[980,300,240,72] 左对齐；镜 7 `slow`、镜 8 `keep` x 980；镜 9 `prio` [700,440]。划线/变暖/加粗的状态帧不变。')
    o.append('- **镜 16** `keep`「保核心链路（示例）」移到 [1000,420]（「结算 179」正下方，必改 2），帧与挂词不变。')
    o.append('- **封面**（必改 3 + Nolan 定）：单个结算页窗口（双窗在 4:3 放不下：两窗 < 600 进 compact，地址栏会缩字），`backTabs: []`；页面首行离页头 ≥ 24 px（boxes 从页头 80 下算）；窗口下方一行价格「搜索 199 元 → 结算 179 元（示例）」由 5 段普通 text 拼成（`priceLine: true`，`priceRole` big/small 只给人看），199 暖色、179 绿色大号数字。原「ask/result」两行删除。')
    o.append('- **镜 3** 第 0 帧即唯一空白标签（`pageBlank`、url 空），「打开搜索页」处 type1 起逐字输入（不再有 newTab 状态，也不留旧结算标签）；`nocoupon` 移到 [1160,610]。')
    o.append('- **标签链少一个「结算」**（可选 7）：镜 4 新开后 backTabs [搜索]；镜 13 第 0 帧即搜索标签（afterTabs [结算]，无切换状态）；镜 14 切到结算后 backTabs [搜索]；镜 19 第 0 帧即成功页（backTabs [搜索]），「要是」只压暗。')
    o.append('- **点击波纹 20 帧**（Knoll）：镜 4 按加购后 20 帧才新开标签（输入、加载随之后移，加载在第 45 帧左右，红包行与 179 的挂词帧不变）；镜 14 按提交后 20 帧才出成功页。')
    o.append('- **镜 5** 竖线 h 340（延到「= 到手价」）；**镜 10、11** 说明卡 y 230 h 570（不压示例角标），首行 y 262；镜 13 `works` 移到 [1160,610]；所有 CalloutTag / CornerBadge 加宽 12 px（页外状态角标 x 同步左移 12）。\n')
    o.append('## 相对 EP.13 的变化——Knoll 必读')
    o.append('- **新页型 `page: \'shopPrice\'`**（BrowserChrome）：一张页型三种 `view`——`search`（搜索结果页）、`checkout`（结算页，带红包抵扣行）、`success`（成功页）。取代 EP.13 的 shopCheckout（本期没有运费险行）。见 §1。')
    o.append('- **全片不开开发者工具**：没有 DevToolsNetwork / BlockHighlight / devtoolsRow。')
    o.append('- **镜 1、17 两扇窗口**：`page`（左，search）与 `page2`（右，checkout）同镜并排，各自独立的 BrowserChrome，`scale` 0.6。')
    o.append('- **标签切换不重开**：镜 13、14 用状态帧直接改 `view`/`url`/`title`/`backTabs`/`afterTabs`（切回已开标签，不新开、不输入）；镜 3、4 是新开标签 + 逐字输入。')
    o.append('- **按钮波纹可指向任意按钮框**：`ripples[].center` 取 `boxes` 里的键（镜 4 = `item0Button` 加购；镜 14 = `button` 提交订单）。')
    o.append('- **页外右上状态角标** `svc`（CornerBadge，`outsidePage: true`，右缘 1660，y 90）：镜 3/13/14「搜索页红包计算：已关闭（示例）」，镜 4「结算页红包计算：正常（示例）」（绿字 #86EFAC、底 #14532D）。')
    o.append(f"- **段长例外**：{J(d['meta']['durationExceptions'])}（Knoll 帧表定稿）。")
    o.append('- 沿用：dimFrom / backTabs / afterTabs / ripples / readAlong / dimPage / fadeOut / CornerBadge / CalloutTag / `highlighted`+`pulse` / `strike` / `padLeft` / rect 的 `w` 状态帧（镜 6 资源横条）。\n')
    o.append('## 0. 画面类型 `frame`')
    o.extend(ctx.frame_table())
    o.append(ctx.canvas_line())
    o.append("## 1. BrowserChrome `page: 'shopPrice'`（新）")
    o.append('外框、标签页、地址栏同现有 BrowserChrome（`showPadlock`、`title`、`url`、`pageBlank`、`tabLoading`、`backTabs`、`afterTabs`、`dimPage`、`ripples`、`buttonPressed`）。页面区白底，按 `view` 画；区块位置全在 `boxes`，字号 `rowSize` `buttonSize` `headlineSize`；`scale` 只给人看（boxes 已按它算好）。')
    o.append('| 字段 | 类型 | 含义 |\n|---|---|---|')
    o.append("| `view` | 'search' \\| 'checkout' \\| 'success' | 见下 |")
    o.append("| `search` | {query, items:[{text, button, highlighted, background?}]} | search 视图：`boxes.query` 搜索框文字；`items[i]` 画在 `boxes.item{i}`，按钮文字画在 `boxes.item{i}Button`；`highlighted` = 行底浅黄 + 轻微脉动；`background: true` 的行只作背景（正常画，不另强调） |")
    o.append("| `checkout` | {product, address, coupon:{visible, applied, text, highlighted}, total, button} | checkout 视图：`boxes.product` `address` `coupon` `total` `button`；见 §1.1 |")
    o.append("| `success` | {headline, paid} | success 视图：`boxes.headline` `boxes.paid`（不画按钮、不画红包行） |")
    o.append('\n### 1.1 红包抵扣行 `checkout.coupon`')
    o.append('| visible | applied | 画法 |\n|---|---|---|')
    o.append('| false | false | 行位置保留、不画任何东西（镜 4 加载后、「多出一行红包抵扣」前） |')
    o.append('| true | false | 画 `text`（绿色字 #15803D），应付仍为 199（镜 4「多出一行红包抵扣」到「红包这时才真正算上」之间） |')
    o.append('| true | true | 画 `text`，应付 = 179（已计入） |')
    o.append('`highlighted: true` = 该行底浅黄 + 轻微脉动（镜 1、4、17）。应付文字直接取 `checkout.total`，渲染不自己算。')
    o.append('\n### 1.2 各镜窗口与状态帧（本镜帧）')
    for s, e in els('BrowserChrome'):
        co = e.get('checkout') or {}
        o.append(f"- 镜 {s['scriptShot']} `{e['id']}` [{e['x']},{e['y']},{e['w']},{e['h']}] scale={e.get('scale')}：初始 view={e.get('view')} url={e.get('url')!r} title={e.get('title')!r} coupon={J(co.get('coupon'))} total={co.get('total')!r} backTabs={e.get('backTabs')} afterTabs={e.get('afterTabs')}")
        o.extend(ctx.keyframe_lines(e, _ep14_extra))
    o.append('\n### 1.3 标签延续')
    o.append('- 镜 3：第 0 帧即唯一空白标签；「打开搜索页」起逐字输入 → 加载搜索页。')
    o.append('- 镜 4：接搜索标签；按「加购」（波纹 20 帧）→ 20 帧后新开结算标签（搜索在左）→ 输入 → 加载（无红包行，应付 199）→ 红包行出现 → 应付 179（只变一次）。不提交。')
    o.append('- 镜 13：第 0 帧即搜索标签（`afterTabs` [结算]），无切换。镜 14：「结算页照常」切到结算标签（`backTabs` [搜索]）→ 按提交（波纹 20 帧）→ 20 帧后成功页。')
    o.append('- 镜 19：第 0 帧即镜 14 成功页（`backTabs` [搜索]）；「要是」处 `dimPage` 0.7；讨论题 `padLeft` 32。')
    o.append('- 镜 17 回放镜 1 两窗（不新开、不输入、不提交）；左窗首行、右窗红包行各随一句轻亮。')
    o.append('\n## 2. 页外角标与叠字')
    o.extend(ctx.overlay_lines(_OVERLAY_IDS))
    o.append('\n## 3. 计数与同步（画面节奏，同帧）')
    o.extend(ctx.sync_lines())
    o.append('- 镜 6 `res-track`（暖色底槽，被占用部分）与 `res-free`（绿色，可用部分，`w` 状态帧 800→640→480→320）叠放，同帧出现。')
    o.append('\n## 4. 封面 covers.json')
    o.append(f"covers.json {sha(cvb)}：三尺寸 16x9 / 4x3 / 3x4 + poster（= 3x4）。单窗 `page: 'shopPrice'`、`view: 'checkout'`、红包行已计入且轻亮、应付 179（`coverStill: true` = 静帧），`backTabs: []`；窗口下方一行价格「{cv['priceLine']}」（5 段 text，同一 y，199/179 大号异色）；「示例数据」CornerBadge 在页面外。选单窗原因：{cv['layoutReason']}。4:3 内容全在 x 315..1125、y < 918。")
    o.extend(ctx.cover_size_lines())
    o.append('\n## 5. 方框加文字镜 / 讨论题 / 下期')
    o.extend(ctx.section5_lines())
    txt = '\n'.join(o) + '\n'
    assert '熔断' not in txt
    return txt
