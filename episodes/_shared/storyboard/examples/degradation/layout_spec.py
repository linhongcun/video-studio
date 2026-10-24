"""EP.14 degradation (slug degradation-v1) layout spec — ported from the episode-dir layout.py v1.0.0 (script 629b5042, voice 9e70470c).
Run:  python3 -B episodes/_shared/storyboard/layout.py --spec episodes/_shared/storyboard/examples/degradation/layout_spec.py \
        --episode-dir episodes/degradation --inputs episodes/_shared/storyboard/examples/degradation/repo-inputs.json --out OUT/layout.json
Two picture kinds (the script marks each shot's frame):
  browser (shots 1, 3, 4, 13, 14, 17, 19): real pages shop.example/search and shop.example/checkout (BrowserChrome page type shopPrice:
    view = search | checkout | success); shots 1 and 17 two windows side by side; shots 3/4 open a new tab and type the URL; 13/14 switch tabs; no devtools.
  canvas (the other 13 shots): no chrome, no URL; borderless text flows, counters, comparisons; box cards only on shots 10, 11, 18, 20.
Frame specs and helpers: see episodes/_shared/storyboard/layout_kit.py."""
import math
from layout_kit import C, TM, W, T, S, wid
NSHOT = 20
BROWSER = (1, 3, 4, 13, 14, 17, 19)
BOXSHOTS = (10, 11, 18, 20)
OPAQUE = '#0B1020'; WARM = '#FDBA74'; GREEN = '#86EFAC'; CYAN = '#22D3EE'; MUTED = '#94A3B8'; ROWBG = '#1F2937'; YEL = '#FDE68A'; WHITE = '#FFFFFF'
LIT = {'highlighted': True, 'pulse': True}
def badge(id_, text, x, y=160, fs=32, **kw):
    a = dict(color=YEL, comp='CornerBadge', background='#7C2D12', sampleData=True, w=168, h=54); a.update(kw)
    return T(id_, text, x, y, fs, **a)
# 角标「示例数据」：canvas 镜放右上内容区（避开水印区 [1680,30,1880,100]）；browser 镜放页外深色底（页面下沿与字幕带 900 之间）
def sample(cue=None, x=1560, y=160, id_='sample'): return badge(id_, '示例数据', x, y, cue=cue)
def sample_out(cue=None): return {**badge('sample', '示例数据', 1612, 834, cue=cue), 'outsidePage': True}
# 红包计算状态角标：页外右上（网页窗口上沿 280 之上），右缘 1660（避开右上水印 x ≥ 1680）
FY = 90
OFF = '搜索页红包计算：已关闭（示例）'; ON = '结算页红包计算：正常（示例）'
def stat(id_, text, cue=None, color=YEL, background='#7C2D12', **kw):
    x = 1660 - (math.ceil(wid(text, 32)) + 32 + 12)
    return {**badge(id_, text, x, FY, fs=32, cue=cue, color=color, background=background, **kw), 'outsidePage': True}
def note(id_, text, x, y, cue, fs=32, color=YEL, **kw):
    return T(id_, text, x, y, fs, cue=cue, color=color, comp='CalloutTag', align='left', background=OPAQUE, **kw)
def plain(id_, text, x, y, cue, fs=40, color='#E5E7EB', **kw):
    return T(id_, text, x, y, fs, cue=cue, color=color, align='left', background=OPAQUE, **kw)
def line(id_, x, y, w, h, cue, **kw):
    return W(id_, None, x, y, w, h, z=2, cue=cue, background=MUTED, radius=2, timingReason='无边框连线', **kw)
# ---------- 网页（新页型 shopPrice：搜索结果页 + 结算页 + 成功页）----------
URL_S = 'shop.example/search'; URL_C = 'shop.example/checkout'; TAB_S = '搜索'; TAB_C = '结算'
QUERY = '搜索：卫衣'
ITEM0 = '卫衣　到手价 199 元（示例）'; ITEM1 = '运动裤　到手价 129 元（示例）'
def SE(hl=False): return {'query': QUERY, 'items': [{'text': ITEM0, 'button': '加购', 'highlighted': hl}, {'text': ITEM1, 'button': '加购', 'highlighted': False, 'background': True}]}
PRODUCT = '商品：卫衣 ×1　199 元（示例）'; ADDRESS = '收货地址：示例路 1 号（示例）'; COUPON = '红包抵扣：−20 元（示例）'
TOTAL199 = '应付：199 元（示例）'; TOTAL179 = '应付：179 元（示例）'
OK_HEAD = '订单已提交，付款成功（示例）'; PAID = '已付：179 元（示例）'
def CO(coupon='applied', hl=False):
    vis = coupon != 'hidden'; app = coupon == 'applied'
    return {'product': PRODUCT, 'address': ADDRESS, 'coupon': {'visible': vis, 'applied': app, 'text': COUPON if vis else '', 'highlighted': hl},
            'total': TOTAL179 if app else TOTAL199, 'button': '提交订单'}
SUCCESS = {'headline': OK_HEAD, 'paid': PAID}
def boxes(px, py, s):
    r = lambda v: round(v*s); m = r(40); rh = max(44, r(56)); fs = max(28, r(40))
    bx = {'query': [px + m, py + r(30), r(700), rh],
          'item0': [px + m, py + r(130), r(1000), rh], 'item0Button': [px + m + r(1060), py + r(130), r(150), rh],
          'item1': [px + m, py + r(230), r(1000), rh], 'item1Button': [px + m + r(1060), py + r(230), r(150), rh],
          'product': [px + m, py + r(40), r(900), rh], 'address': [px + m, py + r(120), r(900), rh],
          'coupon': [px + m, py + r(200), r(900), rh],
          'total': [px + m, py + r(280), r(900), rh], 'button': [px + m, py + r(360), r(240), max(52, r(72))],
          'headline': [px + m, py + r(40), r(1100), max(56, r(80))], 'paid': [px + m, py + r(150), r(900), rh]}
    return bx, {'rowSize': fs, 'buttonSize': fs, 'headlineSize': max(40, r(56))}
def ripple(id_, born, center='button'): return {'id': id_, 'bornFrame': born, 'center': center, 'r0': 12, 'r1': 96, 'growFrames': 20, 'holdOpacity': 0.45, 'color': CYAN}
W1 = dict(x=120, y=280, w=1680, h=540); SC = 0.8
WL = dict(x=120, y=280, w=820, h=480, s=0.6); WR = dict(x=980, y=280, w=820, h=480, s=0.6)   # 镜 1、17 左右两扇窗口
def page(id_='page', x=120, y=280, w=1680, h=540, s=SC, view='search', co=None, se=None, cue=None, z=1, url=None, tab=None,
         ripples=(), backTabs=(), afterTabs=(), **kw):
    bx, fs = boxes(x + 3, y + 3 + 80, s)
    url = url or (URL_S if view == 'search' else URL_C); tab = tab or (TAB_S if view == 'search' else TAB_C)
    d = W(id_, 'BrowserChrome', x, y, w, h, z=z, cue=cue, page='shopPrice', title=tab, url=url, showPadlock=True, sampleData=True,
          pageBlank=False, view=view, search=se or SE(), checkout=co or CO(), success=dict(SUCCESS), buttonPressed=False, tabLoading=False,
          ripples=list(ripples), backTabs=list(backTabs), afterTabs=list(afterTabs), scale=s, **fs, boxes=bx)
    d.update(kw); return d
def typing_after(cue, url, d0, step10, first_cue=False):
    out = [(TM(cue, d0 + i*step10//10, '地址栏逐字输入（画面节奏）'), f'type{i+1}', {'url': url[:i+1]}) for i in range(len(url))]
    if first_cue: out[0] = (C(cue, d0), 'type1', {'url': url[:1]})   # 首字挂口播词（开口规则），之后每帧一字
    return out
NEWTAB = {'pageBlank': True, 'url': '', 'title': '新标签页', 'tabLoading': False}
TITLE = '搜索页和结算页，为什么两个价不一样？'
SERIES = '扛住高峰'
Q1 = '要是搜索页和结算页都把红包计算一起关掉，下单还能不能顺利完成？'
Q2 = '评论区说说。'
NEXT = '下期，加个索引，为啥就快了？'
FOLLOW = '关注我，觉得有用就点赞、收藏一下吧。'
WRAP = '降级就讲到这里。'


def build(ctx):
    part = ctx.part; reveal = ctx.reveal
    # ================= 开场 =================
    part(1, '第 0 帧（挂「大促时」起点）同时可见：封面大字、系列角标「扛住高峰」、左右两扇真实浏览器窗口——左 `shop.example/search` 搜索结果（首行「卫衣　到手价 199 元（示例）」、次行背景商品），右 `shop.example/checkout` 结算页（商品 199 元、「红包抵扣：−20 元（示例）」、「应付：179 元（示例）」、「提交订单」）；页外「示例数据」；0–2 秒保持「搜索 199／结算 179」冲突。「红包这时才算上」处右窗红包抵扣行轻亮；「这是怎么回事」处两窗下方中部叠字「怎么回事？（示例）」。开场为结果预置，不点提交。', [
        {**page(**WL, view='search'), 'conflict': True, 'timingReason': '开场冲突：左窗搜索页，第 0 帧即在'},
        {**page('page2', **WR, view='checkout', co=CO('applied'),
                stateCues=S(('红包这时才算上', 'couponLit', {'checkout': CO('applied', hl=True)}))),
         'conflict': True, 'timingReason': '开场冲突：右窗结算页，第 0 帧即在'},
        T('cover-title', TITLE, 160, 150, 72, z=5, color=WHITE, fontWeight=900, background=OPAQUE, conflict=True, w=1600, h=112, timingReason='封面大字，第 0 帧即在，保持到镜尾'),
        T('series-tag', SERIES, 160, 90, 34, z=5, color='#0B1020', background=CYAN, radius=26, fontWeight=700, w=200, h=52, conflict=True, timingReason='封面系列角标，第 0 帧即在'),
        {**sample_out(), 'conflict': True, 'timingReason': '常驻示例角标，第 0 帧即在'},
        note('why', '怎么回事？（示例）', 820, 778, '这是怎么回事', fs=36, color=YEL),
    ])
    part(2, '干净全屏无边框文字对照（canvas）：「这不一定是算错了」处镜 1 网页与封面题目离场，出「示例数据」，左侧「搜索页：到手价　不含红包（示例）」压暗占位；「搜索页的到手价先不算红包」处左侧亮起；「到了结算页」处右侧「结算页」；「红包抵扣这一项才算上」处右侧补「红包抵扣：算上（示例）」。不画方框、不画实物。', [
        sample(cue='这不一定是算错了'),
        plain('left', '搜索页：到手价　不含红包（示例）', 160, 320, '搜索页的到手价先不算红包', fs=44, color=WHITE, fontWeight=800, dimFrom=0, dimOpacity=0.3),
        plain('right', '结算页', 1060, 320, '到了结算页', fs=44, color=WHITE, fontWeight=800),
        plain('right2', '红包抵扣：算上（示例）', 1060, 420, '红包抵扣这一项才算上', fs=44, color=GREEN, fontWeight=800),
    ])
    # ================= 一、两个价分别怎么算 =================
    LOAD3 = TM('打开搜索页', 0 + 18 + 3, '输完地址 3 帧后回车加载（画面节奏）')
    part(3, '镜首即是浏览器里新开的空白标签页（只此一个标签；上一镜是 canvas，第 0 帧不闪别的页面），页外「示例数据」；「打开搜索页」处地址栏开始逐字（每帧一字）输入 `shop.example/search`，回车后搜索结果页加载：「搜索：卫衣」、两行商品卡片（首行「卫衣　到手价 199 元（示例）」，次行「运动裤　到手价 129 元（示例）」仅作背景不读）；「列表上每件商品都标着一个到手价」处首行轻亮；「没有把红包算进去」处页内叠字「本页到手价：未算红包（示例）」，同帧页外右上静止角标「搜索页红包计算：已关闭（示例）」。不开开发者工具。该标签（搜索）留到镜 13 切回。', [
        {**page(**W1, view='search', **NEWTAB,
                stateCues=S(*typing_after('打开搜索页', URL_S, 0, 10, first_cue=True),
                            (LOAD3, 'loaded', {'pageBlank': False, 'title': TAB_S, 'url': URL_S, 'view': 'search', 'search': SE()}),
                            ('列表上每件商品都标着一个到手价', 'itemLit', {'search': SE(hl=True)}))),
         'url': '', 'timingReason': '镜首即新开的空白标签页（唯一标签），第 0 帧即在；「打开搜索页」处开始输入'},
        sample_out('打开搜索页'),
        note('nocoupon', '本页到手价：未算红包（示例）', 1160, 610, '没有把红包算进去', fs=36, color=YEL),
        stat('svc', OFF, cue='没有把红包算进去'),
    ])
    LOAD4 = TM('加购进结算页', 22 + 20 + 3, '输完地址 3 帧后回车加载（画面节奏）')
    part(4, '接镜 3 搜索标签：「加购进结算页」处首行「加购」按下（一圈波纹，20 帧长满），20 帧后新开空白标签页（左侧保留搜索标签），页外「示例数据」；地址栏逐字（每帧一字）输入 `shop.example/checkout`，回车后结算页加载：「商品：卫衣 ×1　199 元（示例）」「收货地址：示例路 1 号（示例）」、红包抵扣行空着、「应付：199 元（示例）」、「提交订单」；「多出一行红包抵扣」处出现「红包抵扣：−20 元（示例）」（尚未计入）；「红包这时才真正算上」处应付变「应付：179 元（示例）」（只变这一次），同帧页外右上角标「结算页红包计算：正常（示例）」。不开工具；不点提交。', [
        {**page(**W1, view='search',
                stateCues=S(('加购进结算页', 'press', {'ripples': [ripple('r1', '@', 'item0Button')]}),
                            (TM('加购进结算页', 20, '按下加购后 20 帧新开标签（点击波纹 20 帧长满；Knoll 预检）'), 'newTab', dict(NEWTAB, backTabs=[TAB_S], ripples=[])),
                            *typing_after('加购进结算页', URL_C, 22, 10),
                            (LOAD4, 'loaded', {'pageBlank': False, 'title': TAB_C, 'url': URL_C, 'view': 'checkout', 'checkout': CO('hidden')}),
                            ('多出一行红包抵扣', 'couponRow', {'checkout': CO('shown', hl=True)}),
                            ('红包这时才真正算上', 'applied', {'checkout': CO('applied')}))),
         'timingReason': '接镜 3 搜索标签，第 0 帧即在'},
        sample_out('加购进结算页'),
        stat('svc', ON, cue='红包这时才真正算上', color=GREEN, background='#14532D'),
    ])
    GX = 160; SX = GX + 80   # 三行服务挂在「到手价计算」下方（子流程缩进在父节点 x 之后）
    part(5, '全屏无边框流程（canvas）：「算一个到手价」处镜 4 网页离场，出「示例数据」与「到手价计算（示例）」；「商品价格」「优惠券」「红包」处在其下方依次出「→ 商品价格服务」「→ 优惠券服务」「→ 红包服务」（同出一条无边框竖线）；「全回来」处三行同时轻亮（回话都到）；「拼出这个数字」处下方合流出「= 到手价（示例）」。不画方框。', [
        sample(cue='算一个到手价'),
        plain('calc', '到手价计算（示例）', GX, 200, '算一个到手价', fs=52, color=WHITE, fontWeight=900),
        line('spine', SX - 40, 320, 4, 340, '商品价格'),   # Deming 可选 6：竖线延到 y660，接上「= 到手价」
        *[plain(f'svc{i+1}', t, SX, 310 + 100*i, c, fs=44, color=CYAN, fontWeight=800, highlighted=False, stateCues=S(('全回来', 'back', LIT)))
          for i, (t, c) in enumerate([('→ 商品价格服务', '商品价格'), ('→ 优惠券服务', '优惠券'), ('→ 红包服务', '红包')])],
        plain('sum', '= 到手价（示例）', SX, 640, '拼出这个数字', fs=48, color=YEL, fontWeight=900),
    ])
    # ================= 二、为什么关掉搜索页的红包计算 =================
    STEP6 = [TM('占掉红包服务不少计算和连接资源', 8*i, f'第 {i+1} 档（请求数与资源同帧同步）') if i else '占掉红包服务不少计算和连接资源' for i in range(4)]
    part(6, '全屏无边框计数（canvas）：「大促时人一多」处「搜索页请求：在算红包（示例）」与「示例数据」；「一遍遍去算红包」处请求计数「请求：10（示例）」；「占掉红包服务不少计算和连接资源」处右侧「红包服务可用资源：100%（示例）」与横条出现（对应请求 10），之后每 8 帧一档：请求 20／30／40 与资源 80%／60%／40%、横条同帧同步，每档对应、不跳号。横条只是示例对应关系。', [
        sample(cue='大促时人一多'),
        plain('head', '搜索页请求：在算红包（示例）', 160, 200, '大促时人一多', fs=48, color=WHITE, fontWeight=800),
        plain('reqs', '请求：10（示例）', 160, 330, '一遍遍去算红包', fs=48, color=WARM, fontWeight=800, sync='与资源同帧同步',
              stateCues=S(*[(STEP6[i], f'q{i+1}', {'text': f'请求：{10*(i+1)}（示例）'}) for i in range(1, 4)])),
        plain('res', '红包服务可用资源：100%（示例）', 900, 330, '占掉红包服务不少计算和连接资源', fs=48, color=GREEN, fontWeight=800, sync='与请求数同帧同步',
              stateCues=S(*[(STEP6[i], f'r{i+1}', {'text': f'红包服务可用资源：{100-20*i}%（示例）'}) for i in range(1, 4)])),
        W('res-track', None, 900, 440, 800, 28, z=2, cue='占掉红包服务不少计算和连接资源', background=WARM, radius=8, timingReason='资源横条底槽（被占用部分显示为暖色）'),
        W('res-free', None, 900, 440, 800, 28, z=3, cue='占掉红包服务不少计算和连接资源', background=GREEN, radius=8, overlayOk='可用部分压在底槽上', sync='与资源数字同帧同步',
          stateCues=S(*[(STEP6[i], f'w{i+1}', {'w': 800 - 160*i}) for i in range(1, 4)])),
    ])
    LX, RX = 160, 1000
    AX, NX, BX = 420, 700, 980   # Deming 必改 1：三列——「搜索页 →」/ 唯一一个「红包服务」/「← 结算页」
    def node(): return {**T('svc-node', '红包服务', NX, 300, 48, cue=None, color=WHITE, fontWeight=800, background=OPAQUE, w=240, h=72, align='center'), 'sharedNode': True, 'timingReason': '旁白「同一个红包服务」：全片 7–9 镜只画这一个节点，第 0 帧即在'}
    def arrows(cue_c=None, keep=False):
        a = T('a-search', '搜索页 →', AX, 300, 48, cue=None, color=WHITE, fontWeight=800, background=OPAQUE, w=240, h=72, align='right', pointsTo='svc-node')
        b = T('a-checkout', '← 结算页', BX, 300, 48, cue=cue_c, color=WHITE, fontWeight=800, background=OPAQUE, w=240, h=72, align='left', pointsTo='svc-node')
        a['timingReason'] = '左侧沿用镜 6 的搜索页在算红包，第 0 帧即在' if not keep else '沿用上一镜，第 0 帧即在'
        if keep: b['timingReason'] = '沿用上一镜，第 0 帧即在'
        return a, b
    a7, b7 = arrows('结算页下单也要问')
    a7['stateCues'] = S(('两边一起抢资源', 'warm', {'color': WARM, 'pulse': True})); b7['stateCues'] = S(('两边一起抢资源', 'warm', {'color': WARM, 'pulse': True}))
    part(7, '全屏无边框三列（canvas）：中间唯一一个「红包服务」与左侧「搜索页 →」第 0 帧即在；「结算页下单也要问」处右侧出「← 结算页」与「示例数据」（两条箭头指向同一个红包服务）；「两边一起抢资源」处两条箭头同时变暖色；「容易变慢甚至卡住」处右列下方叠字「结算变慢／可能卡住（示例）」。不画方框。', [
        sample(cue='结算页下单也要问'),
        a7, node(), b7,
        note('slow', '结算变慢／可能卡住（示例）', BX, 420, '容易变慢甚至卡住', fs=36, color=WARM),
    ])
    a8, b8 = arrows(keep=True)
    a8['color'] = b8['color'] = WARM
    a8['stateCues'] = S(('所以网站会提前关掉', 'struck', {'strike': True, 'strikeColor': WARM, 'color': MUTED}))
    b8['stateCues'] = S(('留给结算页', 'bold', {'color': GREEN, 'fontWeight': 900, 'pulse': True}))
    part(8, '全屏无边框三列（canvas）：沿用镜 7（两条暖色箭头指向中间同一个「红包服务」）与「示例数据」；「所以网站会提前关掉」处「搜索页 →」划掉、变灰，同帧左上出「关闭：搜索页红包计算（示例）」；「留给结算页」处「← 结算页」加粗变绿，右列下方旁注「资源留给结算页（示例）」。', [
        {**sample(), 'timingReason': '常驻示例角标，第 0 帧即在'},
        a8, node(), b8,
        plain('off', '关闭：搜索页红包计算（示例）', LX, 190, '所以网站会提前关掉', fs=44, color=YEL, fontWeight=800),
        note('keep', '资源留给结算页（示例）', BX, 420, '留给结算页', fs=36, color=GREEN),
    ])
    a9, b9 = arrows(keep=True)
    a9.update(strike=True, strikeColor=WARM, color=MUTED); b9.update(color=GREEN, fontWeight=900)
    part(9, '全屏无边框结果（canvas）：「关掉之后」处沿用镜 8 三列关闭态（「搜索页 →」划掉、「← 结算页」加粗、中间同一个「红包服务」）与「示例数据」；「主要只给结算页用」处在「红包服务」正下方出「红包服务：优先服务结算页（示例）」；「搜索页不再去问」处左侧「搜索页：不再问红包金额（示例）」。', [
        sample(cue='关掉之后'),
        a9, node(), b9,
        plain('prio', '红包服务：优先服务结算页（示例）', NX, 440, '主要只给结算页用', fs=40, color=GREEN, fontWeight=800),
        plain('noask', '搜索页：不再问红包金额（示例）', LX, 560, '搜索页不再去问', fs=40, color=YEL, fontWeight=800),
    ])
    # ================= 三、核心链路与降级 =================
    def card(): return {**W('card', None, 240, 230, 1440, 570, z=2, cue=None, background=ROWBG, radius=16, boxCard=True), 'timingReason': '说明卡底，第 0 帧即在'}
    part(10, '本镜计入方框加文字（canvas）：说明卡底第 0 帧即在；「从加购」处「示例数据」；「加购到提交订单再付款」处卡上「加购 → 结算 → 提交订单 → 付款」；「最要紧的下单路」处补「网站最要紧的下单路」；到旁白说「核心链路」才补术语「核心链路」，白话保留。', [
        sample(cue='从加购'),
        card(),
        T('path', '加购 → 结算 → 提交订单 → 付款', 280, 262, 52, z=4, cue='加购到提交订单再付款', color=WHITE, fontWeight=800, w=1360, h=76, overlayOk='卡内文字'),
        T('plain', '网站最要紧的下单路', 280, 380, 48, z=4, cue='最要紧的下单路', color=YEL, fontWeight=800, w=1360, h=72, overlayOk='卡内文字'),
        T('term', '核心链路', 280, 560, 72, z=4, cue='核心链路', color=CYAN, fontWeight=900, w=1360, h=104, overlayOk='卡内术语'),
    ], box=True)
    part(11, '本镜计入方框加文字（canvas）：说明卡底第 0 帧即在；「这种」处「示例数据」；「主动关掉不太要紧的功能」处卡上第一行「关掉不太要紧的功能」；「把有限资源留给最要紧那一段」处第二行「→ 资源留给最要紧那一段」；到旁白「降级」才补术语「降级」，白话保留。不用比喻。', [
        sample(cue='这种'),
        card(),
        T('l1', '关掉不太要紧的功能', 280, 262, 48, z=4, cue='主动关掉不太要紧的功能', color=WARM, fontWeight=800, w=1360, h=72, overlayOk='卡内文字'),
        T('l2', '→ 资源留给最要紧那一段', 280, 370, 48, z=4, cue='把有限资源留给最要紧那一段', color=WHITE, fontWeight=800, w=1360, h=72, overlayOk='卡内文字'),
        T('term', '降级', 280, 560, 72, z=4, cue='降级', color=CYAN, fontWeight=900, w=1360, h=104, overlayOk='卡内术语'),
    ], box=True)
    part(12, '全屏无边框承接（canvas）：「上期讲过」处「示例数据」与一行「上期：运费险故障 → 跳过运费险 → 照样下单（示例）」（镜首压暗占位）；「也算一种降级」处该行下方补「也算一种降级」。不展开上期机制、不出现上期术语。', [
        sample(cue='上期讲过'),
        plain('prev', '上期：运费险故障 → 跳过运费险 → 照样下单（示例）', 160, 300, '上期讲过', fs=44, color=WHITE, fontWeight=800, dimFrom=0, dimOpacity=0.3),
        plain('also', '也算一种降级', 160, 430, '也算一种降级', fs=56, color=CYAN, fontWeight=900),
    ])
    # ================= 四、降级之后 =================
    part(13, '镜首即切回镜 3 开的搜索标签（`shop.example/search`，不另打开、不重输网址；结算标签留在右侧；上一镜是 canvas，第 0 帧不闪结算页），列表「卫衣　到手价 199 元（示例）」照常；「降级之后」处页内叠字「能搜、能加购（示例）」，页外「示例数据」；页外右上「搜索页红包计算：已关闭（示例）」第 0 帧即在（静止），「先不算红包」处该角标轻亮一次。不开工具。', [
        {**page(**W1, view='search', co=CO('applied'), afterTabs=[TAB_C]),
         'timingReason': '镜首即切回镜 3 开的搜索标签（上一镜是 canvas，第 0 帧不闪结算页；结算标签在右），第 0 帧即在'},
        sample_out('降级之后'),
        note('works', '能搜、能加购（示例）', 1160, 610, '降级之后', fs=36, color=GREEN),
        {**stat('svc', OFF, highlighted=False, stateCues=S(('先不算红包', 'lit', LIT))), 'timingReason': '镜 3 同一静止角标（关闭仍在），第 0 帧即在'},
    ])
    part(14, '接镜 13 搜索标签；「结算页照常」处切到镜 4 结算标签（`shop.example/checkout`，不另打开）：商品 199 元、「红包抵扣：−20 元（示例）」、「应付：179 元（示例）」、「提交订单」照常；镜 13 叠字与角标同词淡出；「也能继续下单付款」处按下「提交订单」（一圈波纹，20 帧长满），20 帧后变「订单已提交，付款成功（示例）」「已付：179 元（示例）」；「没有被拖慢」处叠字「核心链路：正常（示例）」。页外「示例数据」。不开工具。', [
        {**page(**W1, view='search', afterTabs=[TAB_C],
                stateCues=S(('结算页照常', 'tabCheckout', {'view': 'checkout', 'title': TAB_C, 'url': URL_C, 'backTabs': [TAB_S], 'afterTabs': [], 'checkout': CO('applied')}),
                            ('也能继续下单付款', 'press', {'buttonPressed': True, 'ripples': [ripple('r1', '@')]}),
                            (TM('也能继续下单付款', 20, '按下后 20 帧出成功页（点击波纹 20 帧长满；Knoll 预检）'), 'success', {'view': 'success', 'buttonPressed': False}))),
         'timingReason': '接镜 13 搜索标签，第 0 帧即在；「结算页照常」处切到结算标签'},
        {**sample_out(), 'timingReason': '常驻示例角标，第 0 帧即在'},
        {**note('works', '能搜、能加购（示例）', 1160, 610, None, fs=36, color=GREEN), 'timingReason': '镜 13 叠字，随切标签淡出', 'disappearCue': '结算页照常', 'fadeOut': 6},
        {**stat('svc', OFF), 'timingReason': '镜 13 角标，随切标签淡出', 'disappearCue': '结算页照常', 'fadeOut': 6},
        note('core', '核心链路：正常（示例）', 1100, 600, '没有被拖慢', fs=36, color=GREEN),
    ])
    part(15, '全屏无边框（canvas）：「红包本身还在」处镜 14 网页离场，出「我的红包：仍在账户（示例）」与「示例数据」；「搜索页这一步先不去算它」处下方旁注「搜索页：先不算（示例）」；「也不会因为这次搜索把它用掉」处再旁注「未被搜索用掉（示例）」。', [
        sample(cue='红包本身还在'),
        plain('mine', '我的红包：仍在账户（示例）', 160, 260, '红包本身还在', fs=52, color=GREEN, fontWeight=900),
        plain('notcalc', '搜索页：先不算（示例）', 240, 400, '搜索页这一步先不去算它', fs=44, color=YEL, fontWeight=800),
        plain('notused', '未被搜索用掉（示例）', 240, 510, '也不会因为这次搜索把它用掉', fs=44, color=CYAN, fontWeight=800),
    ])
    part(16, '全屏无边框左右对照（canvas）：「所以你看到两个价不一样」处左「搜索 199 元（示例）」右「结算 179 元（示例）」与「示例数据」；「关掉了搜索页的红包计算」处右列「结算 179 元」正下方出「保核心链路（示例）」（右 = 结算 = 核心链路）；「并不是单纯把价格算错了」处叠字「算错了？」，到「算错了」三字时划掉。', [
        sample(cue='所以你看到两个价不一样'),
        plain('p-search', '搜索 199 元（示例）', 160, 260, '所以你看到两个价不一样', fs=64, color=WHITE, fontWeight=900),
        plain('p-check', '结算 179 元（示例）', 1000, 260, '所以你看到两个价不一样', fs=64, color=GREEN, fontWeight=900),
        plain('keep', '保核心链路（示例）', 1000, 420, '关掉了搜索页的红包计算', fs=48, color=CYAN, fontWeight=800),
        plain('wrong', '算错了？', 160, 560, '并不是单纯把价格算错了', fs=56, color=WARM, fontWeight=900,
              stateCues=S(('算错了', 'struck', {'strike': True, 'strikeColor': WARM, 'color': MUTED}))),
    ])
    # ================= 结尾 =================
    part(17, '回到开场：回放镜 1 左右两扇窗口（左 `shop.example/search`「卫衣　到手价 199 元（示例）」，右 `shop.example/checkout`「红包抵扣：−20 元（示例）」「应付：179 元（示例）」），页外「示例数据」挂「回到开场」，不重复封面题目；「搜索页没算红包」处左窗首行轻亮；「结算页才把红包算上」处右窗红包抵扣行轻亮；「正是这一次降级在起作用」处两窗下方叠字「降级：关搜索页红包计算（示例）」与「核心链路：结算下单照常（示例）」。不点提交、不产生新订单。', [
        {**page(**WL, view='search', stateCues=S(('搜索页没算红包', 'itemLit', {'search': SE(hl=True)}))), 'timingReason': '回放开场左窗搜索页，第 0 帧即在'},
        {**page('page2', **WR, view='checkout', co=CO('applied'), stateCues=S(('结算页才把红包算上', 'couponLit', {'checkout': CO('applied', hl=True)}))),
         'timingReason': '回放开场右窗结算页，第 0 帧即在'},
        sample_out('回到开场'),
        note('deg', '降级：关搜索页红包计算（示例）', 160, 778, '正是这一次降级在起作用', fs=32, color=YEL),
        note('core', '核心链路：结算下单照常（示例）', 1000, 778, '正是这一次降级在起作用', fs=32, color=GREEN),
    ])
    part(18, '本镜计入方框加文字（canvas）：首词「降级舍掉的是」处镜 17 网页离场，出「示例数据」与左卡「舍掉：搜索页红包计算」；「保住的是」处右卡「保住：结算和下单」；「核心链路」处右卡补术语「核心链路」（镜 10 已出现，此处复现）。', [
        sample(cue='降级舍掉的是'),
        W('lcard', None, 160, 240, 760, 400, z=2, cue='降级舍掉的是', background=ROWBG, radius=16, boxCard=True, timingReason='左卡底'),
        T('l', '舍掉：搜索页红包计算', 180, 300, 52, z=4, cue='降级舍掉的是', color=WARM, fontWeight=800, w=720, h=80, overlayOk='卡内文字'),
        W('rcard', None, 1000, 240, 760, 400, z=2, cue='保住的是', background=ROWBG, radius=16, boxCard=True, timingReason='右卡底'),
        T('r', '保住：结算和下单', 1020, 300, 52, z=4, cue='保住的是', color=GREEN, fontWeight=800, w=720, h=80, overlayOk='卡内文字'),
        T('term', '核心链路', 1020, 500, 64, z=4, cue='核心链路', color=CYAN, fontWeight=900, w=720, h=96, overlayOk='卡内术语'),
    ], box=True)
    QX = W1['x'] + 40; QW = W1['w'] - 80   # 浏览器窗口内的深色条左内边距 ≥ 32 px
    part(19, '镜首即镜 14 已付款成功的结算标签（第 0 帧即成功页，不闪未付款页）；「要是」处压暗（`shop.example/checkout`，「订单已提交，付款成功（示例）」「已付：179 元（示例）」），网页压暗作背景；页外「示例数据」常驻。中部讨论题两行（左内边距 40 px）：第一行从「要是」逐字跟读到问号；第二行随「评论区说说」跟读，两行留到镜尾，不给答案。', [
        {**page(**W1, view='success', co=CO('applied'), backTabs=[TAB_S],
                stateCues=S(('要是', 'successDim', {'dimPage': 0.7}))),
         'timingReason': '镜首即镜 14 已付款成功页（不闪未付款结算页），第 0 帧即在；「要是」处压暗'},
        {**sample_out(), 'timingReason': '常驻示例角标，第 0 帧即在'},
        T('question', Q1, QX, 600, 40, z=5, cue='要是', color=WHITE, fontWeight=800, background=OPAQUE, w=QW, h=64, padLeft=32, questionText=Q1 + Q2, reveal=reveal(19, Q1), align='left'),
        T('question2', Q2, QX, 690, 40, z=5, cue='评论区说说', color=WHITE, fontWeight=800, background=OPAQUE, w=QW, h=64, padLeft=32, reveal=reveal(19, Q2), align='left'),
    ])
    part(20, '干净全屏片尾（canvas，计入方框加文字）：「降级就讲到这里」处镜 19 离场，系列角标「扛住高峰」与「降级就讲到这里。」；「下期」处预告「下期，加个索引，为啥就快了？」逐字跟读至问号完整；「关注我」处关注句逐字跟读至镜尾。不展开 EP.15 原理。', [
        T('series-tag', SERIES, 160, 236, 34, z=3, cue='降级就讲到这里', color='#0B1020', background=CYAN, radius=26, fontWeight=700, w=200, h=52),
        plain('wrap', WRAP, 160, 320, '降级就讲到这里', fs=44, color=YEL),
        T('next-episode-title', NEXT, 160, 400, 56, z=3, cue='下期', color=WHITE, fontWeight=800, w=1600, background=OPAQUE, reveal=reveal(20, NEXT), align='left'),
        T('follow', FOLLOW, 160, 540, 48, z=3, cue='关注我', color=CYAN, w=1600, background=OPAQUE, fontWeight=800, reveal=reveal(20, FOLLOW), align='left'),
    ], box=True)
