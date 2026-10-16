# EP.22 封面 v0.29.1：Codex(gpt-6-astra) 版式 codex-cover-raw.md 实现。
# 叙事：数据库=绿块新价 --(断开虚线+红叉)--> 缓存=黄块旧价 --(黄箭头)--> 手机屏=黄块旧价。
# 无价签形状、无门店/总部比喻、无数字。phone-page.svg 含价签形，改为自绘手机。
import io, os
from PIL import Image, ImageDraw, ImageFont, ImageChops
import cairosvg
A = '/workspace/miyazaki-backup/cache-consistency/assets/'
B = '/workspace/miyazaki-backup/cache-consistency/'
OUT = B + 'cover/'; JPG = B + 'covers/'; REP = B + 'replacements/'
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
FT = lambda s: ImageFont.truetype(FONT, int(s), index=2)
BG = '#0B1020'
TITLE = ["后台改了价格", "页面怎么还是旧的？"]; BADGE = "缓存一致性"

def svg(n, w, h):
    im = Image.open(io.BytesIO(cairosvg.svg2png(url=A + n + '.svg', output_width=1600))).convert('RGBA')
    im = im.crop(im.getbbox()); k = min(w / im.width, h / im.height)
    return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)

def box(F, n, x, y, w, h):
    im = svg(n, w, h); px, py = int(x + (w - im.width) / 2), int(y + (h - im.height) / 2)
    F.alpha_composite(im, (px, py)); return (px, py, px + im.width, py + im.height)

def phone(d, x, y, w, h):
    d.rounded_rectangle([x, y, x + w, y + h], 36, fill='#111827', outline='#E5E7EB', width=6)
    d.rounded_rectangle([x + 16, y + 44, x + w - 16, y + h - 22], 22, fill=BG)
    d.rounded_rectangle([x + w / 2 - 28, y + 18, x + w / 2 + 28, y + 24], 3, fill='#6B7280')
    return (x, y, x + w, y + h)

def dash(d, p, q):
    (x0, y0), (x1, y1) = p, q; L = max(abs(x1 - x0), abs(y1 - y0)); t = 0
    while t < L:
        e = min(t + 12, L)
        d.line([(x0 + (x1 - x0) * t / L, y0 + (y1 - y0) * t / L), (x0 + (x1 - x0) * e / L, y0 + (y1 - y0) * e / L)], fill='#6B7280', width=5)
        t += 22

def cross(d, cx, cy):
    for s in (1, -1): d.line([(cx - 12, cy - 12 * s), (cx + 12, cy + 12 * s)], fill='#F87171', width=6)

def arrow(d, pts):
    d.line(pts, fill='#F59E0B', width=8, joint='curve')
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    if y0 == y1: d.polygon([(x1, y1), (x1 - 18, y1 - 10), (x1 - 18, y1 + 10)], fill='#F59E0B')
    else: d.polygon([(x1, y1), (x1 - 10, y1 - 18), (x1 + 10, y1 - 18)], fill='#F59E0B')

def head(d, lines, badge, wx, wy):
    R = []
    for (x, y, fs, anc), t, c in zip(lines, TITLE, ('#FFFFFF', '#F59E0B')):
        d.text((x, y), t, font=FT(fs), fill=c, anchor=anc, stroke_width=4, stroke_fill=BG)
        R.append(d.textbbox((x, y), t, font=FT(fs), anchor=anc))
    bx, by, cx = badge; bw = int(d.textlength(BADGE, font=FT(44))) + 80
    if cx: bx = int(bx - bw / 2)
    d.rounded_rectangle([bx, by, bx + bw, by + 80], 40, fill='#22D3EE')
    d.text((bx + bw / 2, by + 40), BADGE, font=FT(44), fill=BG, anchor='mm'); R.append((bx, by, bx + bw, by + 80))
    d.text((wx, wy), "IT小村", font=FT(40), fill='#E5E7EB', anchor='ra'); R.append(d.textbbox((wx, wy), "IT小村", font=FT(40), anchor='ra'))
    return R

def scene(F, d, db, g, ca, y_, ph, yb, dashes, xc, arr):
    for p, q in dashes: dash(d, p, q)
    cross(d, *xc); arrow(d, arr)
    G = [box(F, 'db', *db), box(F, 'cache', *ca), phone(d, *ph)]
    for n, b, t in (('data-new', g, '新价'), ('data-old', y_, '旧价'), ('data-old', yb, '旧价')): tag(F, d, n, b, t)
    return G

def tag(F, d, n, b, t):
    # v0.29.1-r2：块内标注（Nolan 要求每个数据块都带「新价/旧价」），用块底色盖掉示意横线后写深色字
    x0, y0, x1, y1 = box(F, n, *b); w, h = x1 - x0, y1 - y0; i = max(7, h * .09)
    fill, ink = ('#22C55E', '#052E16') if n == 'data-new' else ('#F59E0B', '#1C1306')
    d.rounded_rectangle([x0 + i, y0 + i, x1 - i, y1 - i], int(h * .16), fill=fill)
    fs = int(min(h * .58, (w - 2 * i) * .80 / 2)); f = FT(fs); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d.text((cx, cy), t, font=f, fill=ink, anchor='mm'); tb = d.textbbox((cx, cy), t, font=f, anchor='mm')
    ok = tb[0] > x0 + i and tb[2] < x1 - i and tb[1] > y0 + i and tb[3] < y1 - i
    print('  label', t, 'fs', fs, 'block', (w, h), 'inside' if ok else 'OUTSIDE')

def check(tag, W, H, T, G, top=0):
    U = lambda b: (min(x[0] for x in b), min(x[1] for x in b), max(x[2] for x in b), max(x[3] for x in b))
    err = [('bottom15%', t) for t in T if t[3] > H * 0.85] + [('top', t) for t in T if t[1] < top]
    err += [('edge', b) for b in T + G if b[0] < 0 or b[1] < 0 or b[2] > W or b[3] > H]
    err += [('overlap', a, b) for i, a in enumerate(T) for b in T[i + 1:] + G if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]]
    print(tag, 'ERR' if err else 'OK', err, 'subject', U(G))

L = {}
def mk(tag, W, H, lines, badge, wx, wy, sc, top=0):
    F = Image.new('RGBA', (W, H), BG); d = ImageDraw.Draw(F)
    T = head(d, lines, badge, wx, wy); G = scene(F, d, **sc)
    check(tag, W, H, T, G, top); im = F.convert('RGB'); im.save(OUT + f'ep22-{tag}.png'); L[tag] = im

mk('16x9', 1920, 1080, [(280, 72, 96, 'la'), (280, 200, 96, 'la')], (280, 342, 0), 1660, 72, dict(
    db=(280, 550, 320, 300), g=(358, 664, 164, 96), ca=(790, 550, 350, 300), y_=(879, 660, 172, 100),
    ph=(1380, 476, 280, 440), yb=(1430, 646, 180, 108), dashes=[((600, 700), (666, 700)), ((724, 700), (790, 700))],
    xc=(695, 700), arr=[(1140, 700), (1378, 700)]))
mk('4x3', 1440, 1080, [(100, 72, 96, 'la'), (100, 200, 96, 'la')], (100, 342, 0), 1340, 72, dict(
    db=(100, 570, 280, 270), g=(168, 672, 144, 88), ca=(560, 560, 300, 280), y_=(632, 662, 156, 96),
    ph=(1090, 506, 240, 400), yb=(1130, 660, 160, 96), dashes=[((380, 700), (440, 700)), ((500, 700), (560, 700))],
    xc=(470, 700), arr=[(860, 700), (1088, 700)]))
mk('3x4', 1080, 1440, [(540, 254, 110, 'ma'), (540, 398, 96, 'ma')], (540, 552, 1), 1020, 168, dict(
    db=(60, 820, 240, 250), g=(116, 914, 128, 80), ca=(400, 820, 270, 250), y_=(463, 910, 144, 88),
    ph=(780, 740, 240, 440), yb=(820, 906, 160, 96), dashes=[((300, 954), (324, 954)), ((376, 954), (400, 954))],
    xc=(350, 954), arr=[(670, 954), (778, 954)]), top=144)
mk('9x16', 1080, 1920, [(540, 288, 110, 'ma'), (540, 432, 96, 'ma')], (540, 588, 1), 1020, 168, dict(
    db=(60, 760, 260, 260), g=(118, 858, 144, 88), ca=(400, 1000, 280, 260), y_=(464, 1094, 152, 92),
    ph=(760, 1180, 260, 440), yb=(805, 1346, 170, 102), dashes=[((320, 890), (388, 890)), ((448, 890), (540, 890)), ((540, 890), (540, 1000))],
    xc=(418, 890), arr=[(680, 1130), (890, 1130), (890, 1178)]), top=144)

os.makedirs(JPG, exist_ok=True)
R = 'episodes/cache-consistency/'
rep = {R + 'cover-16x9.jpg': '16x9', R + 'cover-4x3.jpg': '4x3', R + 'cover-3x4.jpg': '3x4',
       'site/public/' + R + 'cover-16x9.jpg': '16x9',
       R + 'cover/ep22-16x9.png': '16x9', R + 'cover/ep22-4x3.png': '4x3', R + 'cover/ep22-3x4.png': '3x4'}
for t, im in L.items(): im.save(JPG + f'ep22-{t}.jpg', 'JPEG', quality=92, optimize=True)
for p, t in rep.items():
    os.makedirs(os.path.dirname(REP + p), exist_ok=True)
    L[t].save(REP + p, 'JPEG', quality=92, optimize=True) if p.endswith('.jpg') else L[t].save(REP + p)
S = Image.new('RGB', (3000, 1000), '#1F2937'); x = 20
for t in ('16x9', '4x3', '3x4', '9x16'):
    im = L[t].copy(); im.thumbnail((900, 640) if t in ('16x9', '4x3') else (520, 960)); S.paste(im, (x, 20)); x += im.width + 20
S.crop((0, 0, x, 1000)).save(OUT + 'ep22-covers-sheet.png'); print('sheet', x)
