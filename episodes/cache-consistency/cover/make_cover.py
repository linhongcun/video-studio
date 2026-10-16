# EP.22 封面（Miyazaki 素材）：照 EP.21 distributed-tx/cover/make_cover.py（版式 / 配色 / 字体，源自 EP.14 起的做法；16:9 1920×1080，4:3 = 16:9 裁 x240–1680 后整组缩 90% 居中，3:4 单独排 1080×1440）
# 大字「改了价」白 /「页面怎么还是旧的？」橙；青底角标「缓存一致性」；右上「IT小村」。底部 15% 无字；3:4 顶部 144px 无字。
# 主图：仓库（新绿价签）+ 备菜台（旧黄菜 + 旧黄价签）+ 手机仍显示旧价 + 厨师，对比「改了价 / 页面还是旧的」。自绘 SVG，无数字 / 英文。不取视频帧。
import io
from PIL import Image, ImageDraw, ImageFont, ImageChops
import cairosvg

A = '/workspace/miyazaki-backup/cache-consistency/assets/'
OUT = '/workspace/miyazaki-backup/cache-consistency/cover/'
SHARE = '/workspace/share/covers/'
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
FT = lambda s: ImageFont.truetype(FONT, int(s), index=2)
P = dict(
    bg="#0B1020", panel="#111827", primary="#22D3EE", secondary="#3B82F6",
    accent="#F59E0B", success="#22C55E", danger="#F87171",
    text="#FFFFFF", text2="#9CA3AF", muted="#6B7280",
)
TITLE = ["改了价", "页面怎么还是旧的？"]
BADGE = "缓存一致性"


def svg(n, w, h):
    im = Image.open(io.BytesIO(cairosvg.svg2png(url=A + n + '.svg', output_width=1600))).convert('RGBA')
    im = im.crop(im.getbbox())
    k = min(w / im.width, h / im.height)
    return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)


def place(F, im, cx, cy):
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    F.alpha_composite(im, (x, y))
    return (x, y, x + im.width, y + im.height)


def txt(d, xy, t, fs, col, anchor='mm'):
    d.text(xy, t, font=FT(fs), fill=col, anchor=anchor)
    return d.textbbox(xy, t, font=FT(fs), anchor=anchor)


def main(F, d, x, y, w, h, vertical=False):
    """主图：左仓库+新绿价签，中备菜台+旧黄菜/旧黄价签，右手机旧价页，厨师站台边。无数字/英文。"""
    if not vertical:
        wh = place(F, svg('warehouse', h * 0.72, h * 0.72), x + w * 0.18, y + h * 0.38)
        pn = place(F, svg('price-new', h * 0.28, h * 0.28), x + w * 0.30, y + h * 0.18)
        tb = place(F, svg('prep-table', w * 0.42, h * 0.42), x + w * 0.52, y + h * 0.72)
        da = place(F, svg('dish-amber', h * 0.22, h * 0.22), x + w * 0.48, y + h * 0.52)
        po = place(F, svg('price-old', h * 0.26, h * 0.26), x + w * 0.58, y + h * 0.38)
        ch = place(F, svg('chef', h * 0.55, h * 0.55), x + w * 0.40, y + h * 0.28)
        ph = place(F, svg('phone-page', h * 0.70, h * 0.70), x + w * 0.84, y + h * 0.42)
    else:
        wh = place(F, svg('warehouse', w * 0.38, w * 0.38), x + w * 0.22, y + h * 0.18)
        pn = place(F, svg('price-new', w * 0.18, w * 0.18), x + w * 0.38, y + h * 0.06)
        ch = place(F, svg('chef', w * 0.32, w * 0.32), x + w * 0.55, y + h * 0.22)
        tb = place(F, svg('prep-table', w * 0.70, w * 0.28), x + w * 0.50, y + h * 0.55)
        da = place(F, svg('dish-amber', w * 0.16, w * 0.16), x + w * 0.42, y + h * 0.42)
        po = place(F, svg('price-old', w * 0.18, w * 0.18), x + w * 0.60, y + h * 0.38)
        ph = place(F, svg('phone-page', w * 0.36, w * 0.36), x + w * 0.78, y + h * 0.78)
    G = [wh, pn, tb, da, po, ch, ph]
    return [(min(b[0] for b in G), min(b[1] for b in G), max(b[2] for b in G), max(b[3] for b in G))], []


def head(d, tx, ty, tfs, tlh, align, bx, by, bh, bfs, wx, wy, tfs2=None):
    R = []
    for i, l in enumerate(TITLE):
        a = 'la' if align == 'left' else 'ma'
        fs = tfs if i == 0 else (tfs2 or tfs)
        d.text(
            (tx, ty + i * tlh), l, font=FT(fs),
            fill=P['text'] if i == 0 else P['accent'],
            anchor=a, stroke_width=4, stroke_fill=P['bg'],
        )
        R.append(d.textbbox((tx, ty + i * tlh), l, font=FT(fs), anchor=a))
    bw = int(d.textlength(BADGE, font=FT(bfs))) + bh
    if bx == 'c':
        bx = int(tx - bw / 2)
    d.rounded_rectangle([bx, by, bx + bw, by + bh], bh // 2, fill=P['primary'])
    d.text((bx + bw / 2, by + bh / 2), BADGE, font=FT(bfs), fill=P['bg'], anchor='mm')
    R.append((bx, by, bx + bw, by + bh))
    R.append(txt(d, (wx, wy), "IT小村", 40, "#E5E7EB", 'ra'))
    return R


def overl(R):
    return [
        (a, b) for i, a in enumerate(R) for b in R[i + 1:]
        if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
    ]


def check(tag, W, H, Hd, G, TX, top=0, crop=None):
    T = Hd + TX
    bot = int(H * 0.85)
    err = (
        overl(Hd + G + TX)
        + [('bottom15%', t) for t in T if t[3] > bot]
        + [('top', t) for t in T if t[1] < top]
        + [('edge', b) for b in Hd + G + TX if b[0] < 0 or b[1] < 0 or b[2] > W or b[3] > H]
    )
    if crop:
        err += [('4:3 crop', b) for b in Hd + G + TX if b[0] < crop[0] or b[2] > crop[1]]
    print(
        tag, 'ERR' if err else 'OK', err,
        'subject', min(b[0] for b in G), min(b[1] for b in G),
        max(b[2] for b in G), max(b[3] for b in G),
    )


def margins(p):
    im = Image.open(p).convert('RGB')
    bg = Image.new('RGB', im.size, P['bg'])
    df = ImageChops.difference(im, bg).convert('L').point(lambda v: 255 if v > 24 else 0)
    x0, y0, x1, y1 = df.getbbox()
    return dict(left=x0, top=y0, right=im.width - x1, bottom=im.height - y1)


# ---- 16:9 ----
F = Image.new('RGBA', (1920, 1080), P['bg'])
d = ImageDraw.Draw(F)
Hd = head(d, 280, 70, 96, 120, 'left', 280, 340, 80, 44, 1640, 70)
G, TX = main(F, d, 200, 430, 1520, 520)
check('16x9', 1920, 1080, Hd, G, TX, crop=(240, 1680))
F.convert('RGB').save(OUT + 'ep22-16x9.png')

# ---- 4:3 from 16:9 crop ----
C = F.crop((240, 0, 1680, 1080))
k = 0.9
C = C.resize((round(1440 * k), round(1080 * k)), Image.LANCZOS)
G4 = Image.new('RGBA', (1440, 1080), P['bg'])
G4.alpha_composite(C, ((1440 - C.width) // 2, (1080 - C.height) // 2))
G4.convert('RGB').save(OUT + 'ep22-4x3.png')

# ---- 3:4 ----
F = Image.new('RGBA', (1080, 1440), P['bg'])
d = ImageDraw.Draw(F)
Hd = head(d, 540, 180, 110, 130, 'center', 'c', 450, 80, 44, 1000, 140, tfs2=78)
G, TX = main(F, d, 60, 620, 960, 680, vertical=True)
check('3x4', 1080, 1440, Hd, G, TX, top=144)
F.convert('RGB').save(OUT + 'ep22-3x4.png')

for n, req in (('16x9', 0), ('4x3', 60), ('3x4', 0)):
    m = margins(OUT + f'ep22-{n}.png')
    print(n, 'margins', m, ('OK' if min(m.values()) >= req else 'FAIL(<%d)' % req) if req else '')

# also write JPG into share/covers (same naming as ep21)
import os
os.makedirs(SHARE, exist_ok=True)
for n in ('16x9', '4x3', '3x4'):
    im = Image.open(OUT + f'ep22-{n}.png').convert('RGB')
    path = SHARE + f'ep22-{n}.jpg'
    im.save(path, 'JPEG', quality=92, optimize=True)
    print('share', path, os.path.getsize(path), im.size)
