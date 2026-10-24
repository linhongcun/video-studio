#!/usr/bin/env python3
"""Storyboard validator: generic checks here, episode-specific checks in the spec's checks(v).

  python3 -B episodes/_shared/storyboard/validate.py --spec SPEC.py --episode-dir EPDIR [--inputs MAP.json] \\
      [--storyboard storyboard.json] [--covers covers.json] [--report validate.txt]

Exit 0 = no errors, 1 = errors (each printed as "ERR ..."). Every check() call counts once in "检查 N 项".
Onsets are re-checked independently via onset_check.py -> episodes/_shared/onset_rule.py (window -6..+2).

Generic sections (driven by spec constants): input sha pinning (SHA), narration == NARRATION_FILE N, words.json scriptSha,
root schema, TITLE/EPISODE/SLUG, CANVAS, real timing + onset-rule marker, discussion question Q, NEXT (episode, teaser),
DEVTOOLS + MAX_EXC in meta, script shot coverage / per-shot narration / BROWSER_SHOTS / BOX_SHOTS, the timeline (scene and shot
continuity, MIN..MAX with MAX_EXC, TR fade, direction, words.json interval, KNOLL, voice placement, verbatim subtitles, one
subtitle layer, element types), WAVLEN / NSENT, frame kind per shot, FAKE_COMP / FAKE_TEXT, URL_DOMAIN only on browser shots,
box cards only on BOX_SHOTS (BOX_NOCARD_OK exempt), FILM_BANNED words, SAMPLE_RE numbers marked SAMPLE_MARK, no early view
switch after a canvas shot, ripple -> next state >= RIPPLE_MIN, TERMS not before their shot, WATERMARK / subtitle band /
"示例数据" badge (shots < SAMPLE_UNTIL) / outsidePage badges, DARK strips padLeft >= 32 in windows, MAP_SHOTS, sample badge vs
box cards, CalloutTag / CornerBadge slack >= 12, early anchors, state frames, script 屏幕文字 on screen, 标注表 hooks
(STRUCT_HOOK), no overlap, no shrink, covers (== meta.covers, bottom 15%, centerRegion, watermark, sample outside window,
first page row >= 24, badge slack), article quotes (ref-sources.md quotes found in src/*.txt, >= MIN_QUOTES), Q and
ARTICLE_NEEDS in the article, onset recheck."""
import argparse, json, math, re, sys, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit
import onset_check as OC


class V:
    """Validation context: data + helpers; passed to spec.checks(v)."""
    def __init__(self):
        self.ERR = []; self.WARN = []; self.N = 0

    def check(self, c, msg):
        self.N += 1
        if not c: self.ERR.append(msg)

    def warn(self, c, msg):
        if not c: self.WARN.append(msg)

    @staticmethod
    def wid(t, fs): return sum(1 if unicodedata.east_asian_width(c) in 'WF' else .62 for c in t)*fs

    def E(self, n): return {e['id']: e for e in next(s for s in self.shots if s['scriptShot'] == n)['elements']}
    def pages(self, n): return [e for e in self.E(n).values() if e.get('component') == 'BrowserChrome']

    @staticmethod
    def final(e, key):
        v = e.get(key)
        for k in e.get('stateKeyframes') or []:
            if key in k: v = k[key]
        return v

    @staticmethod
    def at(e, key, f):
        v = e.get(key)
        for k in e.get('stateKeyframes') or []:
            if k['frame'] <= f and key in k: v = k[key]
        return v

    @staticmethod
    def texts_of(e):
        t = [e.get('text') or '']
        for k in e.get('stateKeyframes') or []: t.append(k.get('text') or '')
        return t

    def seq(self, e): return [t for t in self.texts_of(e) if t]
    @staticmethod
    def kf(e, state): return next(k for k in e.get('stateKeyframes') or [] if k.get('state') == state)
    @staticmethod
    def frames(e): return [e['appearFrame']] + [k['frame'] for k in (e.get('stateKeyframes') or [])[1:]]

    def page_texts(self, p):
        out = []
        for k in [p] + (p.get('stateKeyframes') or []):
            for key in self.PAGE_VIEWS:
                v = k.get(key)
                if isinstance(v, dict): out.append(json.dumps(v, ensure_ascii=False))
            for key in ('title', 'url'):
                if k.get(key): out.append(k[key])
        return out

    @staticmethod
    def nrm(t): return re.sub(r'\s+', ' ', t.replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"').replace('\u201d', '"').replace('\u2013', '–').replace('\xa0', ' '))

    @staticmethod
    def overlap(a, b): return a['x'] < b['x'] + b['w'] and b['x'] < a['x'] + a['w'] and a['y'] < b['y'] + b['h'] and b['y'] < a['y'] + a['h']


def G(spec, name, default): return getattr(spec, name, default)


def run(spec, inp, sb_path, covers_path, report=None):
    v = V(); check = v.check
    d = json.loads(Path(sb_path).read_text()); script = inp.text('script.md')
    W = inp.json('words.json'); VS = {x['id']: x for s_ in W['shots'] for x in s_['sentences']}
    m = d['meta']
    v.d, v.m, v.script, v.W, v.VS, v.inp = d, m, script, W, VS, inp
    v.PAGE_VIEWS = G(spec, 'PAGE_VIEWS', ('search', 'checkout', 'success'))
    SHA = G(spec, 'SHA', {}); MAX_EXC = G(spec, 'MAX_EXC', {}); NSHOT = spec.NSHOT
    BROWSER_SHOTS = list(spec.BROWSER_SHOTS); BOX_SHOTS = list(spec.BOX_SHOTS)
    # ---------- inputs / meta ----------
    for f, h in SHA.items():
        check(kit.sha256(inp(f)).startswith(h), f'{f} 非 {h}')
    nf = G(spec, 'NARRATION_FILE', None)
    if nf:
        NARR = kit.load_spec(inp(nf), 'narr')
        check(re.findall(r'^旁白：(.*)$', script, re.M) == list(NARR.N), f'script 旁白与 {nf} 不逐字一致')
    if G(spec, 'WORDS_SCRIPT_SHA', None): check(W['scriptSha256'].startswith(spec.WORDS_SCRIPT_SHA), f'words.json 配音依据仍是 {spec.WORDS_SCRIPT_SHA}')
    check(set(d) == {'meta', 'assets', 'scenes'}, 'root schema')
    check(m['title'] == spec.TITLE and m['episode'] == spec.EPISODE and m['slug'] == spec.SLUG, 'title/episode/slug')
    check((m['width'], m['height'], m['fps']) == tuple(G(spec, 'CANVAS', (1920, 1080, 30))), 'canvas')
    wav_pre = SHA.get('voice.wav', kit.sha256(inp('voice.wav'))[:8])
    check(m['provisionalTiming'] is False and wav_pre in m['timingSource'] and m['onsetRule']['module'].endswith('_shared/onset_rule.py'), '实录时序 + 开口规则标记')
    check(m['discussionQuestion'] == spec.Q, '讨论题')
    if G(spec, 'NEXT', None):
        check(m['nextEpisode']['teaser'] == spec.NEXT[1] and m['nextEpisode']['episode'] == spec.NEXT[0], '下期预告')
    dx = m.get('durationExceptions') or []
    check(m.get('devtoolsShots') == list(G(spec, 'DEVTOOLS', [])) and len(dx) == len(MAX_EXC)
          and dx == [{'shot': n, 'frames': f, 'max': spec.MAX, 'reason': dx[i]['reason']} for i, (n, f) in enumerate(MAX_EXC.items())], 'meta devtools / 段长例外')
    # ---------- script coverage ----------
    shots = [s for sc in d['scenes'] for s in sc['shots']]; v.shots = shots
    check([s['scriptShot'] for s in shots] == list(range(1, NSHOT+1)), f'覆盖脚本 {NSHOT} 镜')
    smd = re.findall(r'^### (\d+) [^\n]+\nframe：(\w+)\n画面：(.*?)\n旁白：(.*?)$', script, re.M | re.S); v.smd = smd
    check(len(smd) == NSHOT, f'script 镜数 {len(smd)}')
    check({s['scriptShot']: s['narration'] for s in shots} == {int(k): t.strip() for k, _, _, t in smd}, 'script 逐镜旁白一致')
    SCRIPT_FRAME = {int(k): f for k, f, _, _ in smd}; v.SCRIPT_FRAME = SCRIPT_FRAME
    check(sorted(n for n, f in SCRIPT_FRAME.items() if f == 'browser') == BROWSER_SHOTS, f'脚本 frame：browser {len(BROWSER_SHOTS)}')
    boxp = [s['id'] for s in shots if s['boxShot']]
    check(boxp == m['boxShots'] and [s['scriptShot'] for s in shots if s['boxShot']] == BOX_SHOTS, f'boxShot = 镜 {BOX_SHOTS}')
    # ---------- timeline ----------
    WS = {int(x['id'][:2]): x for x in W['shots']}; KNOLL = G(spec, 'KNOLL', None)
    TR = G(spec, 'TR', 10)
    g = 0; used = []
    for sc in d['scenes']:
        check(sc['from'] == g, sc['id']+' scene from')
        check(sc['durationInFrames'] == sum(s['durationInFrames'] for s in sc['shots']), sc['id']+' scene len')
        for sh in sc['shots']:
            sid, L = sh['id'], sh['durationInFrames']
            check(sh['from'] == g, sid+' from 不连续')
            lim = MAX_EXC.get(sh['scriptShot'], spec.MAX)
            check(spec.MIN <= L <= lim, sid+f' 段长 {L} 不在 {spec.MIN}..{lim}')
            check(sh['transition'] == {'type': 'fade', 'durationInFrames': TR}, sid+' 转场')
            check(bool(sh.get('direction')), sid+' 缺调度')
            ws = WS[sh['scriptShot']]; check(ws['id'] == sid and ws['startFrame'] == g and ws['endFrame'] - ws['startFrame'] == L, sid+' 镜头区间 ≠ words.json')
            if KNOLL is not None: check((g, g + L) == tuple(KNOLL[sh['scriptShot'] - 1]), sid+f' ≠ 定稿帧表 {KNOLL[sh["scriptShot"] - 1]}')
            tm = sh['timing']
            check(tm['holdFrames'] == 0 and L == tm['wavTo'] - tm['wavFrom'] and tm['wavFrom'] == g, sid+' 段长/起点')
            for y in sh['voice']:
                used.append(y['id']); s_ = VS[y['id']]
                check(math.isclose(y['wavStart'], s_['startFrame']) and math.isclose(y['wavEnd'], s_['endFrame']), sid+' 句子 wav 帧被改')
                check(abs((sh['from'] + y['localStart']) - y['wavStart']) <= 0.5, sid+f" 句子 {y['id']} 未按原位置放")
                check(y['localEnd'] <= L - 1, sid+f" 句子 {y['id']} 溢出")
            g += L
            st = sh['subtitles']
            check(st[0]['from'] == 0 and st[-1]['to'] == L-1, sid+' 字幕首尾')
            check(''.join(x['text'] for x in st) == sh['narration'], sid+' 字幕非逐字')
            check(all(re.search(r'[\u4e00-\u9fffA-Za-z0-9]', x['text']) for x in st), sid+' 字幕出现只有标点的一行')
            check(all(x['from'] <= x['to'] for x in st) and all(b['from'] == a['to'] + 1 for a, b in zip(st, st[1:])), sid+' 字幕时间不连续')
            els = sh['elements']; ids = [e['id'] for e in els]
            check(len(set(ids)) == len(ids), sid+' 重复元素')
            check(sum(e.get('role') == 'subtitle' for e in els) == 1, sid+' 单字幕层')
            for e in els:
                if e.get('role') == 'subtitle': continue
                af = e.get('appearFrame', 0)
                check(e['type'] in ('rect', 'text') and isinstance(af, int) and 0 <= af < L, sid+'/'+e['id']+f' type/appearFrame {af}')
    check(g == spec.WAVLEN, f'总长 {g} ≠ {spec.WAVLEN}')
    NSENT = G(spec, 'NSENT', len(VS))
    check(len(used) == NSENT and len(set(used)) == NSENT, f'句子数 {len(used)} ≠ {NSENT}')
    texts_of, seq, pages, E = v.texts_of, v.seq, v.pages, v.E
    ALLTXT = [(s['scriptShot'], e['id'], t) for s in shots for e in s['elements'] if e.get('role') != 'subtitle' for t in texts_of(e) + (v.page_texts(e) if e.get('component') == 'BrowserChrome' else []) if t]
    v.ALLTXT = ALLTXT; v.SL = {s_['scriptShot']: s_['durationInFrames'] for s_ in shots}
    # ---------- frame kind / fake windows / banned words ----------
    FAKE_COMP = G(spec, 'FAKE_COMP', ('NotepadWindow', 'Terminal', 'LogWindow', 'Dashboard', 'DevToolsNetwork', 'BlockHighlight'))
    DOMAIN = G(spec, 'URL_DOMAIN', 'shop.example'); NOCARD_OK = tuple(G(spec, 'BOX_NOCARD_OK', ()))
    for sh in shots:
        n = sh['scriptShot']
        check(sh['frame'] == ('browser' if n in BROWSER_SHOTS else 'canvas'), f'{sh["id"]} frame {sh["frame"]}')
        for e in sh['elements']:
            check(e.get('component') not in FAKE_COMP, f'{sh["id"]}/{e["id"]} 假窗口/开发者工具组件 {e.get("component")}')
            if sh['frame'] == 'canvas':
                check(e.get('component') != 'BrowserChrome' and DOMAIN not in json.dumps(e, ensure_ascii=False), f'{sh["id"]}/{e["id"]} canvas 出现网页/网址')
        if n not in BOX_SHOTS: check(not any(e.get('boxCard') for e in sh['elements']), f'{sh["id"]} 非方框镜出现说明卡')
        else: check(any(e.get('boxCard') for e in sh['elements']) or n in NOCARD_OK, f'{sh["id"]} 方框镜缺卡')
    for n, eid, t in ALLTXT:
        for w in G(spec, 'FAKE_TEXT', ()):
            check(w not in t, f'镜 {n}/{eid} 画面文字含禁词「{w}」')
    FILM = json.dumps([[e for e in s['elements']] for s in shots], ensure_ascii=False) + json.dumps(m['covers'], ensure_ascii=False) + m['title'] + m['discussionQuestion']
    for w in G(spec, 'FILM_BANNED', ()):
        check(w not in FILM and all(w not in s['narration'] for s in shots), f'「{w}」出现在片中文字')
    SAMPLE_RE = G(spec, 'SAMPLE_RE', None); MARK = G(spec, 'SAMPLE_MARK', '示例')
    if SAMPLE_RE:
        for n, eid, t in ALLTXT:
            for seg in re.split(G(spec, 'SAMPLE_SPLIT', r'["，、；]'), t):
                if re.search(SAMPLE_RE, seg):
                    check(MARK in seg, f'镜 {n}/{eid} 示例数字未标（{MARK}）：{seg[:30]}')
    # ---------- browser shots after a canvas shot: no view switch in the first 8 frames; ripple spacing ----------
    for n in BROWSER_SHOTS:
        if n == 1 or SCRIPT_FRAME.get(n - 1) != 'canvas': continue
        for pg in pages(n):
            early_sw = [k['state'] for k in pg.get('stateKeyframes') or [] if 0 < k['frame'] <= 8 and ('view' in k or 'pageBlank' in k)]
            check(not early_sw, f'镜 {n}/{pg["id"]} 上一镜是 canvas，前 8 帧又换页面 {early_sw}（第 0 帧闪一帧别的状态）')
    RIP = G(spec, 'RIPPLE_MIN', 12)
    for s_ in shots:
        for e in s_['elements']:
            sk = e.get('stateKeyframes') or []
            for a_, b_ in zip(sk, sk[1:]):
                if a_.get('ripples'):
                    check(b_['frame'] - a_['frame'] >= RIP, f"{s_['id']}/{e['id']} 点击（帧 {a_['frame']}）到下一状态（帧 {b_['frame']}）只隔 {b_['frame'] - a_['frame']} 帧 < {RIP}")
    # ---------- terms not on screen before the shot that says them ----------
    TERMS = G(spec, 'TERMS', ())
    for n, eid, t in ALLTXT:
        for term, n0 in TERMS:
            if n < n0: check(term not in t, f'镜 {n}/{eid}「{term}」早于口播')
    # ---------- watermark / subtitle band / sample badge / outsidePage ----------
    WM = tuple(G(spec, 'WATERMARK', (1680, 30, 1880, 100))); SUBTOP = G(spec, 'SUBTITLE_TOP', 900)
    SAMPLE_UNTIL = G(spec, 'SAMPLE_UNTIL', NSHOT); SAMPLE_TEXT = G(spec, 'SAMPLE_TEXT', '示例数据')
    for sh in shots:
        n = sh['scriptShot']
        for e in sh['elements']:
            if e.get('role') == 'subtitle': continue
            check(e['x'] + e['w'] <= WM[0] or e['y'] >= WM[3] or e['x'] >= WM[2] or e['y'] + e['h'] <= WM[1], f'{sh["id"]}/{e["id"]} 压右上水印')
            check(e['y'] + e['h'] <= SUBTOP or e.get('role') == 'subtitle', f'{sh["id"]}/{e["id"]} 进字幕带')
        if n >= SAMPLE_UNTIL: continue
        sb = [e for e in sh['elements'] if e.get('id') == 'sample']
        check(len(sb) == 1 and sb[0]['text'] == SAMPLE_TEXT, f'{sh["id"]} 缺{SAMPLE_TEXT}角标')
        for pg in pages(n):
            for e in sh['elements']:
                if e.get('outsidePage'):
                    check(e['y'] >= pg['y'] + pg['h'] or e['y'] + e['h'] <= pg['y'] or e['x'] >= pg['x'] + pg['w'] or e['x'] + e['w'] <= pg['x'], f'{sh["id"]}/{e["id"]} 页外角标压在网页上')
    DARK = G(spec, 'DARK', '#0B1020')
    for n in BROWSER_SHOTS:
        for pg in pages(n):
            for e in E(n).values():
                if e.get('role') == 'subtitle' or e.get('component') == 'BrowserChrome': continue
                if e.get('background') == DARK and pg['x'] <= e['x'] < pg['x'] + pg['w'] and pg['y'] <= e['y'] < pg['y'] + pg['h']:
                    check(e['x'] - pg['x'] >= 32 or e.get('padLeft', 0) >= 32, f'镜 {n}/{e["id"]} 窗口内深色条左内边距 < 32')
    check(m['mapShots'] == list(G(spec, 'MAP_SHOTS', [])), f'mapShots = {G(spec, "MAP_SHOTS", [])}')
    for sh in shots:
        sb_ = [e for e in sh['elements'] if e.get('id') == 'sample']
        for c_ in [e for e in sh['elements'] if e.get('boxCard')]:
            for b in sb_:
                check(b['x'] + b['w'] <= c_['x'] or b['x'] >= c_['x'] + c_['w'] or b['y'] + b['h'] <= c_['y'] or b['y'] >= c_['y'] + c_['h'], f'{sh["id"]} 示例角标压住说明卡 {c_["id"]}')
        for e in sh['elements']:
            if e.get('component') in ('CalloutTag', 'CornerBadge'):
                pad = 38 if e['component'] == 'CalloutTag' else 30
                for t in seq(e): check(e['w'] - pad - v.wid(t, e['fontSize']) >= 12, f'{sh["id"]}/{e["id"]} 横向余量 < 12')
    # ---------- early anchors / state frames ----------
    GAPS = []
    for sh in shots:
        early = any(e.get('role') != 'subtitle' and e.get('id') != 'sample' and (e.get('appearFrame', 0) <= 8 or e.get('dimFrom') is not None) for e in sh['elements'])
        check(early, f'{sh["id"]} 开场近空镜（无早期锚）')
        for e in sh['elements']:
            fr = [k['frame'] for k in e.get('stateKeyframes') or []]
            if len(fr) > 1: GAPS.append(min(b - a for a, b in zip(fr, fr[1:])))
            check(all(b > a for a, b in zip(fr, fr[1:])) and all(0 <= f < sh['durationInFrames'] for f in fr), f'{sh["id"]}/{e["id"]} 状态帧非递增或越界：{fr}')
            if 'disappearFrame' in e: check(e['disappearFrame'] >= e.get('appearFrame', 0), f'{sh["id"]}/{e["id"]} 先消失后出现')
    # ---------- script 屏幕文字 lands on screen ----------
    CUT = G(spec, 'SCREEN_CUT', None); STRIP = G(spec, 'SCREEN_STRIP', r'。$'); COVER_SHOTS = tuple(G(spec, 'SCREEN_COVER_SHOTS', ()))
    for k, _, _, _ in smd:
        n = int(k); body = script.split(f'\n### {n} ')[1].split('\n### ')[0]
        mm = re.search(r'^屏幕文字：(.*)$', body, re.M); scr = mm.group(1) if mm else ''
        if CUT: scr = re.split(CUT, scr)[0]
        have = ' '.join(t for nn, _, t in ALLTXT if nn == n) + ' ' + ' '.join(json.dumps(m['covers'], ensure_ascii=False) for _ in [0] if n in COVER_SHOTS)
        for item in [x.strip() for x in re.split(r'／|→', scr) if x.strip()]:
            item = re.sub(STRIP, '', item).strip()
            if not item: continue
            check(item in have or item.rstrip('。') in have, f'镜 {n} 脚本屏幕文字未落画面：{item}')
    # ---------- 标注表 hooks ----------
    ANN = {}
    for ln in script.splitlines():
        if re.match(r'^\|\s*\d+\s*\|', ln):
            parts = [p.strip() for p in ln.strip('|').split('|')]
            if len(parts) >= 4 and parts[0].isdigit(): ANN[int(parts[0])] = parts[3]
    STRUCT_HOOK = G(spec, 'STRUCT_HOOK', {})
    VERB_OK = 0; VERB_MISS = []
    for sh in shots:
        n = sh['scriptShot']; have = set()
        for e in sh['elements']:
            if isinstance(e.get('cueText'), str) and e['cueText']: have.add(e['cueText'])
            for sk in e.get('stateKeyframes') or []:
                if isinstance(sk.get('cueText'), str): have.add(sk['cueText'])
            if isinstance(e.get('disappearCueText'), str): have.add(e['disappearCueText'])
            for tl in e.get('timerLog') or []: have.add(tl.get('after', ''))
            if (e.get('reveal') or {}).get('mode') == 'readAlong': have.add(e.get('text') or '')
        for (n_, c_) in STRUCT_HOOK:
            if n_ == n: have.add(c_)
        for c in re.findall(r'「([^」]+)」', ANN.get(n, '')):
            if c not in sh['narration']: continue
            if any(c == h or c in h or h in c for h in have if h): VERB_OK += 1
            else: VERB_MISS.append(f'{sh["id"]}「{c}」')
    check(not VERB_MISS, '标注表挂接词未挂：' + '; '.join(VERB_MISS))
    # ---------- no overlap between visible elements ----------
    for s_ in shots:
        els_ = [e for e in s_['elements'] if e.get('role') != 'subtitle' and not e.get('overlayOk') and e.get('component') != 'BrowserChrome' and not e.get('boxCard')]
        for i, a in enumerate(els_):
            for b in els_[i+1:]:
                ov = v.overlap(a, b)
                gone = lambda e, o_: e.get('disappearFrame') is not None and e['disappearFrame'] <= o_.get('appearFrame', 0)
                check(not ov or gone(a, b) or gone(b, a), f"{s_['id']} {a['id']} 与 {b['id']} 重叠")
    # ---------- no shrink: every text (incl. state texts) fits at its font size ----------
    for s_ in shots:
        for e in s_['elements']:
            if e['type'] != 'text' or not e.get('fontSize') or e['id'] == 'subtitle': continue
            for t in seq(e):
                for ln in t.split('\n'):
                    check(v.wid(ln, e['fontSize']) <= e['w'] - 16 - e.get('padLeft', 0), f"{s_['id']}/{e['id']} 文字「{ln[:20]}」宽 {v.wid(ln, e['fontSize']):.0f} > 框 {e['w']}，会被缩字")
    # ---------- covers ----------
    cv = json.loads(Path(covers_path).read_text()); v.cv = cv
    check(m['covers'] == cv, '分镜 meta 内封面与 covers.json 一致')
    HEADER = G(spec, 'COVER_HEADER', 80); FIRST_GAP = G(spec, 'COVER_FIRST_ROW_GAP', 24)
    for name, sz in cv['sizes'].items():
        cr = sz.get('centerRegion'); wz = sz['watermarkZone']
        for e in sz['elements']:
            check(e['y'] + e['h'] <= sz['bottom15Y'], f'封面 {name}/{e["id"]} 进底部 15%')
            if cr: check(cr[0] <= e['x'] and e['x'] + e['w'] <= cr[1] and e['y'] + e['h'] < sz['bottom15Y'], f'封面 {name} {e["id"]} 越界')
            check(e['x'] >= wz[2] or e['x'] + e['w'] <= wz[0] or e['y'] >= wz[3] or e['y'] + e['h'] <= wz[1], f'封面 {name}/{e["id"]} 压水印')
        sbs = [e for e in sz['elements'] if e.get('id') == 'sample']
        for pg in [e for e in sz['elements'] if e.get('component') == 'BrowserChrome']:
            for sb in sbs:
                check(sb['y'] + sb['h'] <= pg['y'] or sb['y'] >= pg['y'] + pg['h'] or sb['x'] >= pg['x'] + pg['w'] or sb['x'] + sb['w'] <= pg['x'], f'封面 {name} 示例数据压在页面上')
            if pg.get('boxes'):
                first = min(b[1] for b in pg['boxes'].values())
                check(first - (pg['y'] + 3 + HEADER) >= FIRST_GAP, f'封面 {name} 首行离页头 {first - (pg["y"] + 3 + HEADER)} < {FIRST_GAP}')
        for e in sz['elements']:
            if e.get('component') in ('CornerBadge',): check(e['w'] - (v.wid(e['text'], e['fontSize']) + 30) >= 12, f'封面 {name}/{e["id"]} 角标余量 < 12')
    # ---------- article ----------
    art = inp.text('article.mdx'); v.art = art
    srcs = ' '.join(v.nrm(f.read_text(errors='ignore')) for f in sorted(inp('src').glob('*.txt'))) if inp.exists('src') else ''; v.srcs = srcs
    QUOTES = re.findall(r'^\s+- "(.+)"$', inp.text('ref-sources.md'), re.M) if inp.exists('ref-sources.md') else []
    MINQ = G(spec, 'MIN_QUOTES', 8)
    check(len(QUOTES) >= MINQ, f'出处原句过少 {len(QUOTES)}')
    for qt in QUOTES: check(v.nrm(qt) in srcs, f'出处原句不在 src/：{qt[:50]}…')
    check(spec.Q in art, '文章未逐字收录讨论题')
    for need in G(spec, 'ARTICLE_NEEDS', ()):
        check(need in art, f'文章缺「{need}」')
    # ---------- episode-specific ----------
    if hasattr(spec, 'checks'): spec.checks(v)
    # ---------- independent onset recheck ----------
    CHK = OC.Checker(inp('voice.wav'), inp('words.json'))
    rows = CHK.check(d); fail = [r for r in rows if not r['ok']]; okn = len(rows) - len(fail)
    for r in fail[:8]: print(' FAIL', OC.fmt(r))
    check(not fail, f'开口失败 {len(fail)} 条（窗口 −6..+2）')
    print(f'开口（_shared/onset_rule.py）复核 {len(rows)} 个事件，通过 {okn}，失败 {len(fail)}')
    print(f'检查 {v.N} 项，错误 {len(v.ERR)}，标注表挂接 {VERB_OK}，未挂 {len(VERB_MISS)}，状态帧最小间距 {min(GAPS) if GAPS else None}')
    for e in v.ERR: print('ERR', e)
    for w_ in v.WARN: print('WARN', w_)
    if report:
        Path(report).write_text(f'开口复核 {len(rows)} 事件通过 {okn} 失败 {len(fail)}\n检查 {v.N} 通过 {v.N-len(v.ERR)} 错误 {len(v.ERR)}\n标注表挂接 {VERB_OK} 未挂 {len(VERB_MISS)}\n' + ''.join('ERR '+e+'\n' for e in v.ERR) + ''.join('WARN '+w_+'\n' for w_ in v.WARN))
    v.rows, v.fail, v.VERB_OK, v.VERB_MISS = rows, fail, VERB_OK, VERB_MISS
    return v


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    kit.add_input_args(ap)
    ap.add_argument('--storyboard', help='default <episode-dir>/storyboard.json'); ap.add_argument('--covers', help='default <episode-dir>/covers.json')
    ap.add_argument('--report', help='also write a validate.txt-style summary here')
    a = ap.parse_args(argv)
    v = run(kit.load_spec(a.spec, 'validate'), kit.inputs_from(a), a.storyboard or kit.default_out(a, 'storyboard.json'), a.covers or kit.default_out(a, 'covers.json'), a.report)
    return 1 if v.ERR else 0


if __name__ == '__main__':
    sys.exit(main())
