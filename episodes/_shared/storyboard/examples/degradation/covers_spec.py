"""EP.14 degradation (slug degradation-v1) covers spec — ported from the episode-dir make_covers.py v1.1.0.
Run:  python3 -B episodes/_shared/storyboard/make_covers.py --spec episodes/_shared/storyboard/examples/degradation/covers_spec.py --out OUT/covers.json
Main visual = one real checkout window shop.example/checkout (shopPrice checkout view: item 199, coupon −20, total 179, submit button)
plus one price line under it, "搜索 199 元 → 结算 179 元（示例）", built from five same-baseline text segments (199 warm / 179 green, >= 2x the small text).
A two-window layout does not fit 4:3 (810 px; both windows would go compact and the 26 px mono URL needs >= 435 px each), so single window.
One tab only (backTabs: []); first page row >= 24 px below the 80 px header; sample badge outside the page; 4:3 inside x 315..1125, y < 918; poster = 3:4."""
import json, math, unicodedata
TITLE = '搜索页和结算页，为什么两个价不一样？'
HEADER = 80; FIRST_ROW_GAP = 24   # BrowserChrome shopPrice 页头高 80（browserLayout.browserHeaderHeight）；首行距页头 ≥ 24（Knoll 预检）
def wid(t, fs): return sum(1 if unicodedata.east_asian_width(c) in 'WFA' else .62 for c in t)*fs
def txt(id_, text, x, y, w, h, fs, color, weight=700, **kw):
    return {'id': id_, 'type': 'text', 'text': text, 'x': x, 'y': y, 'w': w, 'h': h, 'fontSize': fs, 'color': color, 'align': 'center', 'fontWeight': weight, **kw}
def T(x, y, w, h, fs):
    return {'id': 'title', 'type': 'text', 'text': '搜索页和结算页，\n为什么两个价不一样？', 'x': x, 'y': y, 'w': w, 'h': h, 'fontSize': fs, 'color': '#FFFFFF', 'align': 'center', 'fontWeight': 900, 'secondLineColor': '#22D3EE'}
def pill(x, y):
    return {'id': 'series', 'type': 'pill', 'text': '扛住高峰', 'fontSize': 40, 'fontWeight': 'Bold (NotoSansCJK-Bold)', 'fill': '#22D3EE', 'color': '#0B1020', 'radius': 36, 'x': x, 'y': y, 'w': 200, 'h': 72}
def badge(id_, text, x, y, fs=26, **kw):
    w = math.ceil(wid(text, fs)) + 32
    return {**txt(id_, text, x, y, max(160, w), math.ceil(fs*1.2)+16, fs, '#FDE68A'), 'component': 'CornerBadge', 'background': '#7C2D12', **kw}
def boxes(px, py, s):
    r = lambda v: round(v*s); m = r(40); rh = max(24, r(56)); t = max(FIRST_ROW_GAP, r(40))
    return {'product': [px + m, py + t, r(900), rh], 'address': [px + m, py + t + r(80), r(900), rh], 'coupon': [px + m, py + t + r(160), r(900), rh],
            'total': [px + m, py + t + r(240), r(900), rh], 'button': [px + m, py + t + r(320), r(240), max(28, r(72))],
            'headline': [px + m, py + t, r(1100), max(32, r(80))], 'paid': [px + m, py + t + r(110), r(900), rh]}
def win(id_, x, y, w, h, s):
    return {'id': id_, 'type': 'rect', 'component': 'BrowserChrome', 'frame': 'browser', 'x': x, 'y': y, 'w': w, 'h': h, 'z': 1,
            'page': 'shopPrice', 'title': '结算', 'url': 'shop.example/checkout', 'showPadlock': True, 'sampleData': True,
            'pageBlank': False, 'view': 'checkout',
            'checkout': {'product': '商品：卫衣 ×1　199 元（示例）', 'address': '收货地址：示例路 1 号（示例）',
                         'coupon': {'visible': True, 'applied': True, 'text': '红包抵扣：−20 元（示例）', 'highlighted': True},
                         'total': '应付：179 元（示例）', 'button': '提交订单'},
            'success': {'headline': '订单已提交，付款成功（示例）', 'paid': '已付：179 元（示例）'},
            'buttonPressed': False, 'tabLoading': False, 'backTabs': [], 'afterTabs': [], 'ripples': [],
            'coverStill': True, 'scale': s, 'rowSize': max(16, round(40*s)), 'buttonSize': max(16, round(40*s)), 'headlineSize': max(20, round(56*s)),
            'boxes': boxes(x+3, y+3+HEADER, s)}
def rtw(t, fs):   # 渲染器 ui.textWidth：非 Latin-1 = fs，其余 0.58 fs
    return sum(fs if ord(c) > 255 else fs*.58 for c in t)
SEGS = [('搜索', 'small', '#E5E7EB'), ('199', 'big', '#FDBA74'), ('元 → 结算', 'small', '#E5E7EB'), ('179', 'big', '#86EFAC'), ('元（示例）', 'small', '#E5E7EB')]
def prices(x0, x1, y, small, big, gap=6):
    h = math.ceil(big*1.15) + 12
    ws = [math.ceil(rtw(t, small if k == 'small' else big) * 1.03) + 16 for t, k, _ in SEGS]
    x = x0 + (x1 - x0 - sum(ws) - gap*(len(ws)-1)) // 2; out = []
    assert x >= x0, ('价格行超出可用宽', x0, x1, sum(ws))
    for (t, k, col), w in zip(SEGS, ws):
        out.append({**txt(f'price-{len(out)}', t, x, y, w, h, small if k == 'small' else big, col, 900 if k == 'big' else 800), 'priceLine': True, 'priceRole': k})
        x += w + gap
    return out
BANNED = ('熔断',)


def build():
    C = {'rule': '大字标题（两行）＋系列胶囊「扛住高峰」；主视觉 = 一个真实结算页 shop.example/checkout（红包抵扣 −20 元、应付 179 元，提交订单照常，只一个标签）＋窗口下方一行「搜索 199 元 → 结算 179 元（示例）」（199、179 大号异色）；「示例数据」在页外深色底；4:3 全部在 x 315..1125、y < 918；poster = 3:4；不用旧封面实物',
         'title': TITLE, 'seriesTag': '扛住高峰', 'conclusion': '降级：关掉搜索页红包计算，保住结算下单（核心链路）', 'priceLine': '搜索 199 元 → 结算 179 元（示例）', 'layout': 'single-window',
         'layoutReason': '双窗在 4:3 的 810 px 内放不下（两窗 < 600 进 compact，地址栏 26px 等宽 333 px 需窗宽 ≥ 435，合计 > 810 只能缩字），按 Nolan 退路用单窗＋一行大号价格',
         'watermark': {'text': 'IT小村', 'anchor': 'top-right', 'offset': [60, 40], 'fontSize': 40, 'color': '#E5E7EB', 'clearZone': '按尺寸见 sizes[].watermarkZone'},
         'poster': {'source': '3x4', 'file': 'poster.jpg', 'width': 1080, 'height': 1440, 'note': 'poster = 3x4 封面同一竖版构图；不取正片帧'},
         'sizes': {
            '16x9': {'width': 1920, 'height': 1080, 'bottom15Y': 918, 'watermarkZone': [1680, 30, 1880, 100],
                     'elements': [T(96, 60, 1560, 200, 80), pill(96, 280), win('page', 330, 370, 900, 400, 0.7), *prices(160, 1460, 784, 40, 80), badge('sample', '示例数据', 1260, 380, sampleData=True)]},
            '4x3': {'width': 1440, 'height': 1080, 'bottom15Y': 918, 'centerRegion': [315, 1125], 'watermarkZone': [1200, 30, 1400, 100],
                    'elements': [T(315, 60, 810, 160, 56), pill(620, 240), win('page', 340, 330, 780, 400, 0.6), *prices(315, 1125, 750, 32, 72), badge('sample', '示例数据', 370, 270, sampleData=True)]},
            '3x4': {'width': 1080, 'height': 1440, 'bottom15Y': 1224, 'watermarkZone': [840, 30, 1040, 100],
                    'elements': [T(54, 104, 972, 170, 60), pill(440, 280), win('page', 140, 380, 800, 480, 0.7), *prices(54, 1026, 900, 40, 96), badge('sample', '示例数据', 140, 300, sampleData=True)]}}}
    return C

MONO32 = 403.27   # Noto Sans Mono 32px 实测 'shop.example/checkout'（EP.13 PIL getlength）
def addr_avail(w):   # BrowserChrome 非 compact 地址栏可用宽（EP.13 Knoll 公式）
    return w - 182 - min(160, w * .2)
ADDR_MARGIN = 24


def finalize(C):
    for name, sz in C['sizes'].items():
        pg_ = next(e for e in sz['elements'] if e['id'] == 'page')
        assert pg_['w'] >= 600, (name, '窗口变 compact')
        assert addr_avail(pg_['w']) >= MONO32 + ADDR_MARGIN, (name, '地址栏放不下 shop.example/checkout（32px 不缩字）', addr_avail(pg_['w']))
        pg_['addressFit'] = {'fontSize': 32, 'textWidth': MONO32, 'available': addr_avail(pg_['w']), 'font': 'Noto Sans Mono'}


def check(C):
    """EP.14-specific cover asserts (the generic ones run in make_covers.py)."""
    for name, sz in C['sizes'].items():
        pg = next(e for e in sz['elements'] if e['id'] == 'page'); sb = next(e for e in sz['elements'] if e['id'] == 'sample')
        outside = sb['y'] + sb['h'] <= pg['y'] or sb['y'] >= pg['y'] + pg['h'] or sb['x'] >= pg['x'] + pg['w'] or sb['x'] + sb['w'] <= pg['x']
        assert outside, (name, '示例数据角标压在页面上')
        ids = {e['id']: e for e in sz['elements']}
        pl = [e for e in sz['elements'] if e.get('priceLine')]
        assert len({e['y'] for e in pl}) == 1 and all(b['x'] >= a['x'] + a['w'] for a, b in zip(pl, pl[1:])), (name, '价格行不在同一行或互相压')
        for e in pl:
            assert rtw(e['text'], e['fontSize']) * 1.03 <= e['w'] - 12, (name, e['text'], '价格行放不下')
            assert not (e['x'] < pg['x'] + pg['w'] and pg['x'] < e['x'] + e['w'] and e['y'] < pg['y'] + pg['h'] and pg['y'] < e['y'] + e['h']), (name, e['id'], '价格行压在窗口上')
        big = [e for e in pl if e['priceRole'] == 'big']; sm = [e for e in pl if e['priceRole'] == 'small']
        assert [e['text'] for e in big] == ['199', '179'] and big[0]['color'] != big[1]['color'] and min(e['fontSize'] for e in big) >= 2 * max(e['fontSize'] for e in sm), (name, '199/179 不够大或同色')
        first = min(v[1] for v in pg['boxes'].values()); assert first - (pg['y'] + 3 + HEADER) >= FIRST_ROW_GAP, (name, '首行离页头 < 24')
        assert max(v[1] + v[3] for k, v in pg['boxes'].items() if k not in ('headline', 'paid')) <= pg['y'] + pg['h'] - 6, (name, '结算页内容出窗')
        for a_, b_ in (('series', 'title'), ('sample', 'series'), ('sample', 'title'), ('sample', 'page'), ('series', 'page')):
            A, B = ids[a_], ids[b_]
            assert A['x'] + A['w'] <= B['x'] or B['x'] + B['w'] <= A['x'] or A['y'] + A['h'] <= B['y'] or B['y'] + B['h'] <= A['y'], (name, a_, b_, '重叠')
