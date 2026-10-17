#!/usr/bin/env python3
"""EP.01 v6 分镜自检 v1.4.0：20b 整句后加载＋三红叉、12 信号停顿、13→15 原地 200、封面三尺寸；v1.3.1：16 改照 Knoll（13 行不滚动，4–24 帧推到 1.9× 保持）；v1.3.0（404 按完全可见帧计、回车须在打完后、成对钥匙同帧、图片占位不早于页面、18 无转圈描述、16a 推镜、11 杯子/偷看者常驻）；v1.2.0（实录时序：句子不截断/不重叠、起音 −6..+2 常开、页面未连接前不加载）；v1.1.0（新增：标签可见≥60帧、跨段不重入、几何重叠/越框、砍题禁词、讨论题一致、voice.wav 起音检查）；python3 -B validate_v6.py [storyboard.json]
沿用旧 validate.py 的通用检查（schema、连续帧、单镜 ≤300、转场、字幕逐字/连续/≤24 字、安全区、水印区、
入场 4 帧动画、cueText、字号与裁切估算），去掉重置版专属内容（旧章节/结尾/数字与「第一步」禁词/33–40 镜）。
新增 v6 规则：框图镜头 ≤3 且仅 7/9/20；封面大字与冲突画面第 0 帧；404 卡 20 帧；12 行滚动；无信封；
provisionalTiming。无 voice.wav 时跳过起音检查（存在时调用 ../http-request/onset.py 的方法需另行接入）。"""
import json, math, re, sys, unicodedata
from pathlib import Path
R = Path(__file__).resolve().parent
P = Path(sys.argv[1]) if len(sys.argv) > 1 else R/'storyboard.json'
d = json.loads(P.read_text()); script = (R/'script.md').read_text()
ERR = []; N = [0]
def check(c, m):
    N[0] += 1
    if not c: ERR.append(m)
PUNCT = '，。：；？！、,.:;?!…「」 '
est = lambda t: math.ceil(sum(1 for c in t if c not in PUNCT)/4.2*30)
def _interp(ks, f):
    if f <= ks[0]['frame']: return ks[0]['value']
    for a, b in zip(ks, ks[1:]):
        if f <= b['frame']: return a['value'] + (b['value']-a['value'])*(f-a['frame'])/(b['frame']-a['frame'])
    return ks[-1]['value']
def fullvis(sh, e):
    """完全可见帧数：在 [入场, 消失) 且不在出场转场内，opacity 与 scale 均为 1。"""
    L = sh['durationInFrames']; n = 0
    for f in range(L - sh['transition']['durationInFrames']):
        if f < e.get('appearFrame', 0) or (e.get('disappearFrame') is not None and f >= e['disappearFrame']): continue
        ok = True
        for pr in ('opacity', 'scale'):
            t = [a for a in sh['animations'] if a['elementId'] == e['id'] and a['property'] == pr]
            if t and abs(_interp(t[0]['keyframes'], f) - 1) > 1e-9: ok = False
        n += ok
    return n
def wid(t, fs): return sum(1 if unicodedata.east_asian_width(c) in 'WF' else .62 for c in t)*fs
import voicemap as VM
VW = VM.load_words(); VS = {x['id']: x for s_ in VW['shots'] for x in s_['sentences']}
m = d['meta']; Q_ = '你遇到过同一个网页有时很快、有时加载很久的情况吗？'
check(set(d) == {'meta', 'assets', 'scenes'}, 'root schema')
check(m['title'] == '浏览器输入网址后发生了什么？', 'title')
check((m['width'], m['height'], m['fps']) == (1920, 1080, 30), 'canvas')
check(re.fullmatch(r'v\d+\.\d+\.\d+', m['release']) is not None, '三段版本号')
check(m['provisionalTiming'] is False and 'bc4b16bc' in m['timingSource'], '实录时序标记')
shots = [s for sc in d['scenes'] for s in sc['shots']]
check(len({s['id'] for s in shots}) == len(shots), '重复镜号')
check(sorted({s['scriptShot'] for s in shots}) == list(range(1, 21)), '覆盖脚本 20 镜')
narr = [n.strip() for n in re.findall(r'^旁白：(.*)$', script, re.M)]
joined = {}
for s in shots: joined[s['scriptShot']] = joined.get(s['scriptShot'], '') + s['narration']
check([joined[i] for i in range(1, 21)] == narr, 'script 逐镜旁白一致')
box = sorted({s['scriptShot'] for s in shots if s['boxShot']})
check(box == [7, 9, 20], f'框图镜头须为 7/9/20，实为 {box}')
check(len(box)*3 <= 20, '框图 ≤1/3')
g = 0
for sc in d['scenes']:
    check(sc['from'] == g, sc['id']+' scene from')
    check(sc['durationInFrames'] == sum(s['durationInFrames'] for s in sc['shots']), sc['id']+' scene len')
    for sh in sc['shots']:
        sid, L = sh['id'], sh['durationInFrames']
        check(sh['from'] == g, sid+' from 不连续'); g += L
        check(0 < L <= 300, sid+' 单镜超 300')
        check(sh['transition'] == {'type': 'fade', 'durationInFrames': 10}, sid+' 转场')
        check(bool(sh.get('direction')), sid+' 缺调度')
        v = sh['voice']
        check(''.join(VS[y['id']]['text'] for y in v).rstrip('，') == sh['narration'].rstrip('，'), sid+' 旁白与 words.json 句子不符')
        for y in v:
            check(math.isclose(y['wavStart'], VS[y['id']]['startFrame']) and math.isclose(y['wavEnd'], VS[y['id']]['endFrame']), sid+' 句子 wav 帧被改')
            check(y['localEnd'] - y['localStart'] >= y['wavEnd'] - y['wavStart'] - 0.5, sid+' 句长被压缩')
            check(y['localEnd'] <= L - 1, sid+f" 句子 {y['id']} 溢出本段（{y['localEnd']} > {L-1}）")
        check(all(a['localEnd'] < b['localStart'] for a, b in zip(v, v[1:])) and v[0]['localStart'] >= 0, sid+' 段内句子重叠')
        st = sh['subtitles']
        check(st[0]['from'] == 0 and st[-1]['to'] == L-1, sid+' 字幕首尾')
        check(all(a['to']+1 == b['from'] for a, b in zip(st, st[1:])), sid+' 字幕不连续')
        check(all(x['from'] <= x['to'] and len(x['text']) <= 24 for x in st), sid+' 字幕长')
        check(''.join(x['text'] for x in st) == sh['narration'], sid+' 字幕非逐字')
        blob = json.dumps(sh, ensure_ascii=False)
        check('信封' not in blob and 'envelope' not in blob.lower(), sid+' 出现信封')
        els = sh['elements']; ids = [e['id'] for e in els]
        check(len(set(ids)) == len(ids), sid+' 重复元素')
        check(sum(e.get('role') == 'subtitle' for e in els) == 1, sid+' 单字幕层')
        for e in els:
            eid = sid+'/'+e['id']
            check(e['type'] in ('rect', 'text', 'line', 'arrow'), eid+' type')
            if e.get('role') == 'subtitle': continue
            x, y, w, h = e['x'], e['y'], e['w'], e['h']
            check(x >= 80 and y >= 80 and x+w <= 1840 and y+h <= 880, eid+' 越安全区')
            check(not (x < 1840 and 1700 < x+w and y < 130 and 80 < y+h), eid+' 水印区')
            if e.get('timingRole') == 'structural':
                check(e['appearFrame'] == 0 and bool(e.get('timingReason')), eid+' 结构元素说明')
            else:
                check(e['cueText'] in sh['narration'] and e['cueText'], eid+' cueText 不在旁白')
                check(0 < e['appearFrame'] < L-10, eid+' 入场帧')
                for pr in ('opacity', 'scale'):
                    t = [a for a in sh['animations'] if a['elementId'] == e['id'] and a['property'] == pr]
                    check(len(t) == 1 and t[0]['keyframes'][0]['frame'] == e['appearFrame'] and t[0]['keyframes'][-1]['frame'] == e['appearFrame']+4, eid+' 入场动画 '+pr)
            if e['type'] == 'text':
                ls_ = e['text'].split('\n'); check(e['fontSize'] >= 28 and max(wid(x, e['fontSize']) for x in ls_) <= e['w']-8 and len(ls_)*e['fontSize']*1.25 <= e['h'], eid+' 文字裁切')
        for a in sh['animations']:
            check(a['elementId'] in ids and all(0 <= k['frame'] < L for k in a['keyframes']), sid+' 动画越界')
check(g == m['durationInFrames'], '总帧数')
s1 = shots[0]; e1 = {e['id']: e for e in s1['elements']}
check(e1['cover-title']['appearFrame'] == 0 and e1['laptop-right']['appearFrame'] == 0 and e1['spinner-right']['appearFrame'] == 0, '开场 0–2 秒封面+冲突')
check(e1['laptop-left']['w'] <= 860 and e1['laptop-right']['w'] <= 860, '镜1 每台 ≤860px')
c404 = [e for s in shots for e in s['elements'] if e['id'] == 'card404'][0]

rows = [e for s in shots for e in s['elements'] if e['id'] == 'rows']
check(rows and all(e['rows'] == 13 for e in rows), '镜16 13 行（首行 example.com + 原 12 行）')
s11 = json.dumps([s for s in shots if s['scriptShot'] == 11], ensure_ascii=False)
check(all(k in s11 for k in ('CoffeeCup', 'PeekerFigure', 'GET example.com', 'ScrambleText')), '镜11 元素')

# ---- v1.1.0 ----
CUT = ['八步', '第 N 步', '信封', '抽屉', '道路', '价签', '下期', '下集', '预告', 'HSTS', '挥手', 'FIN', 'RST', '连接关闭',
       'HTTP/3', 'QUIC', 'HPACK', 'QPACK', 'CDN', '回源', 'async', 'defer', '光栅化', '304', 'ETag', 'TTL', 'envelope']
# 注：旧表中「第一步…第八步」不收：v6 定稿旁白镜 3 有「第一步」，且旁白不许改（已报 Nolan）。
TXT = ('narration', 'text', 'label', 'lines', 'cells', 'names', 'items', 'labels', 'direction', 'from_', 'to', 'line', 'title', 'name')
def texts(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in TXT: yield json.dumps(v, ensure_ascii=False)
            elif isinstance(v, (dict, list)): yield from texts(v)
    elif isinstance(o, list):
        for v in o: yield from texts(v)
for sh in shots:
    t = '\n'.join(texts(sh))
    for w in CUT: check(w not in t, sh['id']+' 砍题禁词 '+w)
    L = sh['durationInFrames']
    for e in sh['elements']:
        if e.get('role') == 'subtitle' or not any(k in e for k in ('text', 'label', 'lines', 'cells', 'items', 'labels')): continue
        if e.get('holdFrames'):  # 设计上的一闪（404 卡 20 帧）
            fv = fullvis(sh, e); check(fv >= e['holdFrames'], f"{sh['id']}/{e['id']} 完全可见仅 {fv} 帧 < {e['holdFrames']}"); continue
        start = e['appearFrame'] + (0 if e.get('timingRole') == 'structural' else 4)
        end = min(e.get('disappearFrame') or L, L-10)
        # 跨段延续：结构元素若在后续段继续存在，累计可见
        check(end-start >= 60 or e.get('timingRole') == 'structural', f"{sh['id']}/{e['id']} 标签完全可见仅 {end-start} 帧")
by = {}
for sh in shots: by.setdefault(sh['scriptShot'], []).append(sh)
for n, parts in by.items():
    for a, b in zip(parts, parts[1:]):
        ida = {e['id'] for e in a['elements']}
        for e in b['elements']:
            if e['id'] in ida and e.get('role') != 'subtitle':
                check(e.get('timingRole') == 'structural' and e['appearFrame'] == 0, f"{b['id']}/{e['id']} 跨段重入")
def ov(a, b): return a['x'] < b['x']+b['w'] and b['x'] < a['x']+a['w'] and a['y'] < b['y']+b['h'] and b['y'] < a['y']+a['h']
def inside(a, b): return a['x'] >= b['x'] and a['y'] >= b['y'] and a['x']+a['w'] <= b['x']+b['w'] and a['y']+a['h'] <= b['y']+b['h']
for sh in shots:
    es = [e for e in sh['elements'] if e.get('role') != 'subtitle']
    for i, a in enumerate(es):
        for b in es[i+1:]:
            if not ov(a, b): continue
            if a['z'] == b['z']:
                check(False, f"{sh['id']} 同层重叠 {a['id']}×{b['id']}")
            else:
                lo, hi = (a, b) if a['z'] < b['z'] else (b, a)
                check(inside(hi, lo) or hi.get('overlayOk') or lo.get('overlayOk'), f"{sh['id']} {hi['id']} 越出所在框 {lo['id']}")
qs = [s for s in shots if Q_ in s['narration']]
card = [e for s in shots for e in s['elements'] if e['id'] == 'question']
check(len(qs) == 1 and len(card) == 1 and card[0]['text'].replace('\n', '') == Q_ and m.get('discussionQuestion') == Q_ and Q_ in m.get('description', '') and Q_ in script, '讨论题旁白/字卡/简介逐字一致')
for s in qs:
    e = {x['id']: x for x in s['elements']}
    qv = [y for y in s['voice'] if Q_ in VS[y['id']]['text']][0]
    check(e['follow']['appearFrame'] > qv['localEnd'], f"20c 关注句须在问题念完后出现（{e['follow']['appearFrame']} ≤ {qv['localEnd']}）")
WAV = R/'voice.wav' if (R/'voice.wav').exists() else None
OUT = []
if WAV:
    import hashlib
    check(hashlib.sha256(WAV.read_bytes()).hexdigest().startswith('bc4b16bc'), 'voice.wav 非 bc4b16bc')
    check(hashlib.sha256((R/'words.json').read_bytes()).hexdigest().startswith('c76f1d95'), 'words.json 非 c76f1d95')
    check(len(VS) == 39 and sorted(VS) == sorted(y['id'] for s_ in shots for y in s_['voice']), '39 句各用一次')
    for sh in shots:
        sents = [VS[y['id']] for y in sh['voice']]; loc = {y['id']: y for y in sh['voice']}
        for e in sh['elements']:
            if e.get('timingRole') in ('structural', 'afterVoice') or e.get('role') == 'subtitle': continue
            si, af = VM.locate(sents, sh['narration'], e['cueText'])   # 独立重算：ASR 只定位词
            o = VM.onset(af); y = loc[sents[si]['id']]
            ol = o - y['wavStart'] + y['localStart']; diff = e['appearFrame'] - ol
            OUT.append((abs(diff), f"{sh['id']}/{e['id']} {diff:+.0f}"))
            check(-6 <= diff <= 2, f"{sh['id']}/{e['id']} 起音窗口外（起音 {ol:.0f} / 入场 {e['appearFrame']}，差 {diff:+.0f}）")
# 事实：建连接（镜 12 承接）前页面不得加载；仅开场左机、镜 4/5 缓存命中的 logo 例外
for sh in shots:
    if 2 <= sh['scriptShot'] <= 12:
        for e in sh['elements']:
            check(e.get('state') != 'loaded' and 'StyledPage' not in e.get('component', ''), f"{sh['id']}/{e['id']} 连接前出现已加载页面")
# ---- v1.3.0 ----
el = lambda sid, eid: next(e for s_ in shots if s_['id'] == sid for e in s_['elements'] if e['id'] == eid)
c4 = el('15-response', 'card404'); check(fullvis(next(s_ for s_ in shots if s_['id'] == '15-response'), c4) >= 20, '404 卡完全可见 ≥20 帧')
ty, kc = el('02-typing', 'typing'), el('02-typing', 'keycap')
tend = ty.get('typeStartFrame', ty['appearFrame']) + math.ceil(len(ty['text'])/ty['charsPerFrame'])
check(tend < kc['pressFrame'] and kc['pressFrame'] >= kc['appearFrame'], f"02 回车须在 example.com 打完后按下（打完 {tend}，按下 {kc.get('pressFrame')}）")
for sh in shots:
    pairs = {}
    for e in sh['elements']:
        if e.get('pairId'): pairs.setdefault(e['pairId'], set()).add(e['appearFrame'])
    for k_, v_ in pairs.items(): check(len(v_) == 1, f"{sh['id']} 成对元素 {k_} 未同帧亮起 {sorted(v_)}")
    ex = {e['id']: e for e in sh['elements']}
    if 'img-fill' in ex and 'page' in ex:
        check(ex['img-fill']['appearFrame'] >= ex['page']['appearFrame'], f"{sh['id']} 图片占位早于页面")
        sk = ex['img-fill'].get('stateKeyframes', [])
        check(sk and sk[0]['state'] == 'grey' and all(a['frame'] < b['frame'] for a, b in zip(sk, sk[1:])) and all(k_['frame'] < sh['durationInFrames'] for k_ in sk), f"{sh['id']} 图片须先灰后清晰")
    if sh['scriptShot'] == 18:
        t = sh['direction'] + json.dumps(sh['elements'], ensure_ascii=False)
        check(not any(w in t for w in ('小圈', '转圈', 'Spinner', 'spinner', '加载圈')), f"{sh['id']} 仍提到等待转圈")
    if sh['scriptShot'] == 11:
        for eid in ('cup', 'peeker'):
            e = ex.get(eid)
            check(e is not None and e['appearFrame'] == 0 and e.get('timingRole') == 'structural' and not e.get('cueText') and e.get('disappearFrame') is None
                  and not [a for a in sh['animations'] if a['elementId'] == eid], f"{sh['id']}/{eid} 须第 0 帧常驻到镜尾、无淡入/缩放")
for sid_ in ('16a-waterfall', '16b-waterfall'):
    s_ = next(x for x in shots if x['id'] == sid_); cam = s_.get('camera') or {}; r_ = el(sid_, 'rows')
    check(s_['direction'] == '13 行，推近第一行', sid_+' 描述须为「13 行，推近第一行」')
    check(r_['rows'] == 13 == len(r_['names']) and r_['names'][0] == 'example.com' and r_['firstRow'] == {'name': 'example.com', 'method': 'GET', 'status': 200}, sid_+' 13 行且首行 example.com · GET · 200')
    check(r_['scroll'] == 'none' and r_['scrollOffset'] == 0 and r_['rowFontSize'] == 44, sid_+' 不滚动、字号不变（44）')
    check(cam.get('target') == 'rows[0]' and cam.get('hold') == 'to-end-of-16b', sid_+' 推镜对准首行并保持')
    want = [{'frame': 4, 'scale': 1.0}, {'frame': 24, 'scale': 1.9}] if sid_ == '16a-waterfall' else [{'frame': 0, 'scale': 1.9}]
    check(cam.get('keyframes') == want, sid_+f" 推镜关键帧须为 {want}")
check(m['durationInFrames'] == 5720 and next(x for x in shots if x['id'] == '15-response')['durationInFrames'] == 235, '总长 5720、15 段 235 帧（Nolan：不加帧）')
f_ = el('20c-recap', 'follow'); check(f_['text'] == '关注 · 点赞 · 收藏', '20c 关注按钮短文案（仅按钮放宽，不要求与旁白逐字）')
# 16 推镜 1.9× 后首行（名称/方法/状态三列）须落在安全区与面板内：按 Knoll 列宽与 firstRowCenter 公式计算
for sid_ in ('16a-waterfall', '16b-waterfall'):
    s_ = next(x for x in shots if x['id'] == sid_); cam = s_['camera']; dv = el(sid_, 'devtools')
    check((dv['x'], dv['w']) == (120, 1680), sid_+' Network 面板须 x120 w1680（同 15）')
    z = max(k_['scale'] for k_ in cam['keyframes']); pad = cam['panelPaddingX']; inner = dv['w'] - 2*pad
    fixed = 140+150+190+170; flex = inner - fixed; c1 = max(360, flex*1.1/2.1)
    right3 = pad + c1 + 140 + 150                       # 状态列右缘（面板内坐标）
    oy = 3 + (dv['h'] - 6 - cam['visibleRows']*cam['rowHeight']) + cam['rowHeight']/2
    zx = dv['x'] + 28 + (right3-28)*z; top = dv['y'] + oy - cam['rowHeight']*z/2; bot = dv['y'] + oy + cam['rowHeight']*z/2
    check(zx <= min(1840, dv['x']+dv['w']) and top >= max(80, dv['y']) and bot <= min(880, dv['y']+dv['h']), f"{sid_} 推镜后首行越界（右 {zx:.0f}，上 {top:.0f}，下 {bot:.0f}）")
    FIT = (round(zx), round(top), round(bot))
f2 = el('20c-recap', 'follow'); check((f2['y'], f2['h']) == (768, 112) and f2['y']+f2['h'] <= 880, '20c 关注按钮 y768 h112，底边 ≤880')
# ---- v1.4.0 ----
s20 = next(x for x in shots if x['id'] == '20b-recap'); ex20 = {e['id']: e for e in s20['elements']}
rl, sp, mr = ex20['right-loaded'], ex20['spin-right'], ex20['marks-right']
endv = max(y['localEnd'] for y in s20['voice'])
check(rl['appearFrame'] > endv and sp['disappearFrame'] == rl['appearFrame'], f"20b 右页面须在整句念完（{endv}）后才加载、转圈保持到那一刻（加载 {rl['appearFrame']}）")
check(mr['items'] == ['缓存没有', 'Wi-Fi 弱', '服务器忙'] and len(mr['itemAppearFrames']) == 3, '20b 须三个红叉：缓存没有、Wi-Fi 弱、服务器忙')
if WAV:
    sents = [VS[y['id']] for y in s20['voice']]
    for w_, f_ in zip(mr['itemCues'], mr['itemAppearFrames']):
        si, af = VM.locate(sents, s20['narration'], w_); y = s20['voice'][si]
        d_ = f_ - (VM.onset(af) - y['wavStart'] + y['localStart']); check(-6 <= d_ <= 2, f"20b 红叉「{w_}」起音窗口外 {d_:+.0f}")
check(all(a < b for a, b in zip(mr['itemAppearFrames'], mr['itemAppearFrames'][1:])), '20b 红叉逐个出现')
# 12：信号在电脑外连线上，并在弱 Wi-Fi 点停顿 15–20 帧
s12 = next(x for x in shots if x['id'] == '12-slow'); e12 = {e['id']: e for e in s12['elements']}
lap, sig, wf, ln_ = e12['laptop-right'], e12['signal'], e12['wifi-weak'], e12['link-line']
mo = sig['motion']; wx = wf['x'] + wf['w']/2 - sig['w']/2 + 0.5
check(all(k_['x'] >= lap['x']+lap['w'] and k_['x']+sig['w'] <= ln_['x']+ln_['w'] for k_ in mo), '12 信号须在电脑外的连线上')
stalls = [b['frame']-a['frame'] for a, b in zip(mo, mo[1:]) if a['x'] == b['x'] and wf['x'] <= a['x']+sig['w']/2 <= wf['x']+wf['w']]
check(stalls and all(15 <= x_ <= 20 for x_ in stalls), f'12 信号须在弱 Wi-Fi 点停顿 15–20 帧（{stalls}）')
check(mo[-1]['frame'] < s12['durationInFrames'] - 10 and mo[0]['frame'] == sig['appearFrame'], '12 信号动画在镜内')
# 13→15：同一请求行原地变 200 + 「首页收到了」
r13, r15 = el('13a-devtools-request', 'row1'), el('15-response', 'row1')
check(all(r13[k_] == r15[k_] for k_ in ('x', 'y', 'w', 'h', 'fontSize', 'persistId')) and el('13a-devtools-request', 'devtools')['layout'] == el('15-response', 'devtools')['layout'], '13→15 须同一行同一版式')
st2, gl = el('15-response', 'status200'), el('15-response', 'got-label')
check(st2['x'] >= r15['x'] and st2['x']+st2['w'] <= r15['x']+r15['w'] and st2['y'] >= r15['y'] and st2['y']+st2['h'] <= r15['y']+r15['h'], '15 200 须在请求行内原地出现')
check(gl['text'] == '首页收到了' and gl['appearFrame'] >= st2['appearFrame'], '15 「首页收到了」须在 200 之后')
# 封面
cv = m.get('covers', {}); JARGON = ['DNS', 'TCP', 'HTTP', 'HTTPS', 'IP', 'CSS', 'HTML', 'TLS', '缓存', '握手', '协议', '服务器', '连接', '响应', '请求']
check(cv.get('title') == m['title'] and set(cv.get('sizes', {})) == {'16x9', '4x3', '3x4'}, '封面三尺寸与标题')
for k_, sz in cv.get('sizes', {}).items():
    W_, H_ = sz['width'], sz['height']; es_ = {e['id']: e for e in sz['elements']}
    check(es_['title']['text'].replace('\n', '') == m['title'] and es_['title']['fontSize'] >= 100, f'封面 {k_} 标题大字')
    check(es_['laptop-left']['state'] == 'loaded' and es_['laptop-right']['state'] == 'spinning', f'封面 {k_} 左秒开右转圈')
    for e in sz['elements']:
        check(e['x'] >= 0.05*W_-1 and e['y'] >= 0.05*H_-1 and e['x']+e['w'] <= W_*0.95+1 and e['y']+e['h'] <= H_*0.95+1, f'封面 {k_}/{e["id"]} 越界')
        if e['type'] == 'text':
            ls_ = e['text'].split('\n')
            check(max(wid(x, e['fontSize']) for x in ls_) <= e['w']-8 and len(ls_)*e['fontSize']*1.25 <= e['h']+1, f'封面 {k_}/{e["id"]} 文字裁切')
            check(not any(j in e['text'] for j in JARGON), f'封面 {k_}/{e["id"]} 含术语')
    ids_ = list(es_); 
    for i, a in enumerate(ids_):
        for b in ids_[i+1:]:
            check(not ov(es_[a], es_[b]), f'封面 {k_} 重叠 {a}×{b}')
ONSET = '已运行' if WAV else '跳过（无 voice.wav）'
print("16 推镜首行范围（右/上/下）：", FIT)
print('起音最大偏差：', sorted(OUT, reverse=True)[:3] if OUT else '无')
print(f'{N[0]} checks, {len(ERR)} errors'); [print(' -', x) for x in ERR]
print(f'ALL OK（起音检查：{ONSET}）' if not ERR else 'FAIL'); sys.exit(1 if ERR else 0)
