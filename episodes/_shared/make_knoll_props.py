"""从 storyboard.json + covers.json 生成 knoll-props.md。

无 --spec 时按 docs/knoll-props.template.md 的标题写骨架，散文处是（待填：…）。
有 --spec 时调用该模块的 build(ctx)。通用表、叠字、同步、封面尺寸和 §5 走这里的 helper。
"""
import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

DEFAULT_IGN = ['cueLog', 'timerLog', 'cueOnset', 'onsetLocal', 'timingReason', 'timingRole', 'appearTimer', 'dimFromCue', 'overlayOk', 'conflict', 'sampleData',
       'questionText', 'boxCard', 'timerDriven', 'outsidePage', 'sync', 'cueText', 'disappearCueText', 'addressFit', 'coverStill']

OVERLAY_COMPONENTS = ('CornerBadge', 'CalloutTag')


def load_episode(epdir, require_frozen=False, ign=None):
    R = Path(epdir)
    sbb = (R / 'storyboard.json').read_bytes()
    d = json.loads(sbb)
    cvb = (R / 'covers.json').read_bytes()
    cv = json.loads(cvb)

    def sha(b):
        return hashlib.sha256(b).hexdigest()[:8]

    sha8 = sha(sbb)
    frozen = R / f'storyboard.{sha8}.json'
    if frozen.exists():
        if frozen.read_bytes() != sbb:
            raise SystemExit('冻结副本与 storyboard.json 不一致')
    elif require_frozen:
        raise SystemExit(f'缺少冻结副本 storyboard.{sha8}.json')
    shots = [s for sc in d['scenes'] for s in sc['shots']]

    def J(x):
        return json.dumps(x, ensure_ascii=False)

    def els(component=None, pred=None):
        for s in shots:
            for e in s['elements']:
                if (component is None or e.get('component') == component) and (pred is None or pred(e)):
                    yield s, e

    IGN = list(DEFAULT_IGN if ign is None else ign)
    strike = sorted({s['scriptShot'] for s, e in els(pred=lambda e: e.get('strike') or any(k.get('strike') for k in e.get('stateKeyframes') or []))})
    total = d['meta']['durationInFrames']

    def file_sha8(names, fallback):
        for name in names:
            p = R / name
            if p.is_file():
                return sha(p.read_bytes())
        return fallback

    def ignore_line():
        return '只给人看 / 给 validate 用、渲染时忽略的字段：' + ' '.join(f'`{k}`' for k in IGN) + '。'

    def strike_line():
        body = f'`strike` + `strikeColor` 是渲染属性（文字中线删除线，线宽 = fontSize × 0.08，颜色缺省取 `color`），本期用在镜 {", ".join(map(str, strike))}。'
        if not strike:
            body = '`strike` + `strikeColor` 是渲染属性（文字中线删除线，线宽 = fontSize × 0.08，颜色缺省取 `color`），本期不用。'
        return body

    def frame_table():
        rows = []
        o = rows
        o.append('| 镜 | id | frame | 绝对帧 | 帧数 | 方框 |\n|---|---|---|---|---|---|')
        for s in shots:
            o.append(f"| {s['scriptShot']} | {s['id']} | `\"{s['frame']}\"` | {s['from']}–{s['from'] + s['durationInFrames']} | {s['durationInFrames']} | {'是' if s['boxShot'] else ''} |")
        return rows

    def canvas_line():
        o = []
        o.append('\ncanvas 镜全屏干净底色，不画外框、标签页、地址栏和网址。\n')
        return o[0]

    def typing_summary(e):
        ty = [k for k in e.get('stateKeyframes') or [] if str(k.get('state', '')).startswith('type')]
        if not ty:
            return None
        o = []
        if ty: o.append(f"  - 逐字输入 type1..type{len(ty)}：帧 {ty[0]['frame']}–{ty[-1]['frame']}（每帧一字），`url` 依次为 `{ty[-1]['url']}` 前 1..{len(ty)} 个字符")
        return o[0]

    def keyframe_lines(e, extra_fn=None):
        lines = []
        o = lines
        for k in (e.get('stateKeyframes') or [])[1:]:
            if str(k.get('state', '')).startswith('type'):
                continue
            if extra_fn is None:
                extra = {kk: k[kk] for kk in k if kk not in ('frame', 'state', 'cueText', 'onsetLocal', 'timerDriven')}
            else:
                extra = extra_fn(k)
            o.append(f"  - 帧 {k['frame']}（{k.get('state')}，对「{k.get('cueText') or '计时'}」）{J(extra) if extra else ''}")
        ty = typing_summary(e)
        if ty:
            lines.append(ty)
        return lines

    def overlay_lines(ids=None):
        if ids is None:
            pred = lambda e: bool(e.get('outsidePage')) or e.get('component') in OVERLAY_COMPONENTS
        else:
            idset = set(ids)
            pred = lambda e: e.get('id') in idset
        rows = []
        o = rows
        for s, e in els(pred=pred):
            st = [(k['frame'], k.get('state')) for k in (e.get('stateKeyframes') or [])[1:]]
            o.append(f"- 镜 {s['scriptShot']} `{e['id']}` {e.get('component')} [{e['x']},{e['y']},{e['w']},{e['h']}] fs={e.get('fontSize')} color={e.get('color')} bg={e.get('background')} appear={e.get('appearFrame')}" + (f" disappear={e.get('disappearFrame')} fadeOut={e.get('fadeOut')}" if e.get('disappearFrame') is not None else '') + (f" states={J(st)}" if st else '') + f" text={e.get('text')!r}")
        return rows

    def sync_lines():
        rows = []
        o = rows
        for s, e in els(pred=lambda e: bool(e.get('sync'))):
            fr = [e.get('appearFrame')] + [k['frame'] for k in (e.get('stateKeyframes') or [])[1:]]
            vals = [e.get('text') or e.get('w')] + [k.get('text') or k.get('w') for k in (e.get('stateKeyframes') or [])[1:]]
            o.append(f"- 镜 {s['scriptShot']} `{e['id']}`（{e['sync']}）帧 {fr} → {J(vals)}")
        return rows

    def cover_size_lines():
        rows = []
        o = rows
        for name, sz in cv['sizes'].items():
            pg = next(e for e in sz['elements'] if e['id'] == 'page')
            pl = [e for e in sz['elements'] if e.get('priceLine')]
            first = min(v[1] for v in pg['boxes'].values()) - (pg['y'] + 83)
            line = f"- {name} {sz['width']}×{sz['height']} bottom15Y={sz.get('bottom15Y')} 窗口 [{pg['x']},{pg['y']},{pg['w']},{pg['h']}] backTabs={pg['backTabs']} 首行离页头 {first} px"
            if pl:
                line += f"；价格行 y {pl[0]['y']} h {pl[0]['h']}：" + '、'.join(f"{e['text']!r}[{e['x']},{e['w']}] fs{e['fontSize']} {e['color']}" for e in pl)
            o.append(line)
        return rows

    def section5_lines():
        rows = []
        o = rows
        o.append(f"boxShots = {d['meta']['boxShots']}（{d['meta']['boxShotRule']}）")
        o.append(f"discussionQuestion = {d['meta']['discussionQuestion']!r}")
        o.append(f"nextEpisode = {J(d['meta']['nextEpisode'])}")
        return rows

    ctx = type('Ctx', (), {})()
    ctx.d = d
    ctx.cv = cv
    ctx.sbb = sbb
    ctx.cvb = cvb
    ctx.shots = shots
    ctx.total = total
    ctx.sha = sha
    ctx.J = J
    ctx.els = els
    ctx.IGN = IGN
    ctx.strike = strike
    ctx.epdir = R
    ctx.file_sha8 = file_sha8
    ctx.ignore_line = ignore_line
    ctx.strike_line = strike_line
    ctx.frame_table = frame_table
    ctx.canvas_line = canvas_line
    ctx.typing_summary = typing_summary
    ctx.keyframe_lines = keyframe_lines
    ctx.overlay_lines = overlay_lines
    ctx.sync_lines = sync_lines
    ctx.cover_size_lines = cover_size_lines
    ctx.section5_lines = section5_lines
    return ctx


def _forbid(txt, words):
    for w in words:
        if w and w in txt:
            raise SystemExit(f'forbidden word: {w}')


def skeleton(ctx):
    d = ctx.d
    meta = d['meta']
    sha = ctx.sha
    o = []
    ep = meta.get('episode', 'N')
    slug = meta.get('slug', '')
    o.append(f"# EP.{ep} {slug} （待填：这一版画面在回答什么）\n")
    parts = []
    for label, names in (
        ('script', ('script.md', 'script')),
        ('voice', ('voice.wav', 'remotion/public/audio/voice.wav')),
        ('words', ('words.json',)),
        ('cues', ('voice/cues.json', 'cues.json')),
        ('shot_frames', ('voice/shot_frames.json', 'shot_frames.json')),
    ):
        parts.append(f"{label} {ctx.file_sha8(names, '无')}")
    o.append(f"依据：storyboard.json {sha(ctx.sbb)}；covers.json {sha(ctx.cvb)}。{' / '.join(parts)}，{ctx.total} 帧，{len(ctx.shots)} 镜。")
    o.append('所有帧号从本镜第 0 帧算。画面坐标是 1920×1080。封面用该尺寸的画布坐标。')
    o.append(ctx.ignore_line())
    o.append(ctx.strike_line() + '\n')
    o.append('## 本版相对 （待填：上一冻结 sha） 的变化（必填）')
    o.append('（待填：本版变化）\n')
    o.append('## 相对上一期的变化——Knoll 必读（必填）')
    o.append('（待填：Knoll 必读）')
    if meta.get('durationExceptions'):
        o.append(f"- 段长例外：{ctx.J(meta['durationExceptions'])}")
    else:
        o.append('- 段长例外：无')
    o.append('')
    o.append('## 0. 画面类型 `frame`（必填）')
    o.extend(ctx.frame_table())
    o.append(ctx.canvas_line())
    o.append('## 1. 页型与状态帧（有 browser 镜则必填）')
    pages = {}
    for s, e in ctx.els(component='BrowserChrome'):
        pages.setdefault(e.get('page'), []).append((s, e))
    if not pages:
        o.append('无')
    for page, items in pages.items():
        o.append(f"### page: {page!r}")
        o.append('（待填：页型字段表）')
        for s, e in items:
            o.append(
                f"- 镜 {s['scriptShot']} `{e['id']}` [{e['x']},{e['y']},{e['w']},{e['h']}] scale={e.get('scale')}："
                f"初始 view={e.get('view')} url={e.get('url')!r} title={e.get('title')!r} backTabs={e.get('backTabs')} afterTabs={e.get('afterTabs')}"
            )
            o.extend(ctx.keyframe_lines(e))
    o.append('（待填：标签延续）\n')
    o.append('## 2. 页外角标与叠字（必填）')
    overs = ctx.overlay_lines()
    o.extend(overs or ['无'])
    o.append('')
    o.append('## 3. 计数与同步（必填）')
    syncs = ctx.sync_lines()
    o.extend(syncs or ['无'])
    o.append('')
    o.append('## 4. 封面 `covers.json`（必填）')
    o.append(f"covers.json {sha(ctx.cvb)}。")
    o.append('（待填：封面版式）')
    o.extend(ctx.cover_size_lines())
    o.append('')
    o.append('## 5. 方框加文字镜 / 讨论题 / 下期（必填）')
    o.extend(ctx.section5_lines())
    return '\n'.join(o) + '\n'


def _load_spec(path):
    path = Path(path)
    spec = importlib.util.spec_from_file_location('knoll_props_spec', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def render(epdir, spec_path=None, require_frozen=False, forbid=''):
    ctx = load_episode(epdir, require_frozen=require_frozen)
    words = [w for w in forbid.split(',') if w]
    if spec_path:
        mod = _load_spec(spec_path)
        txt = mod.build(ctx)
        for w in getattr(mod, 'FORBID', ()):
            if w not in words:
                words.append(w)
    else:
        txt = skeleton(ctx)
    _forbid(txt, words)
    return ctx, txt


def selftest():
    d = Path(tempfile.mkdtemp(prefix='knoll-props-'))
    sb = {
        'meta': {
            'episode': 1,
            'slug': 'synth-v1',
            'durationInFrames': 200,
            'durationExceptions': [{'shot': '01', 'frames': 120, 'max': 100, 'reason': '超长'}],
            'boxShots': ['02-canvas'],
            'boxShotRule': '方框只在说明镜',
            'discussionQuestion': '这是讨论题',
            'nextEpisode': {'episode': 2, 'title': '下一题', 'teaser': '预告'},
        },
        'scenes': [{'shots': [
            {
                'id': '01-browser', 'scriptShot': 1, 'frame': 'browser', 'from': 0,
                'durationInFrames': 100, 'boxShot': False,
                'elements': [{
                    'id': 'page', 'component': 'BrowserChrome', 'page': 'shopPrice',
                    'x': 80, 'y': 60, 'w': 1000, 'h': 700, 'scale': 1,
                    'view': 'search', 'url': 'https://shop.example/', 'title': '搜索',
                    'stateKeyframes': [
                        {'frame': 0, 'state': 'base', 'url': ''},
                        {'frame': 12, 'state': 'lit', 'cueText': '亮起'},
                        {'frame': 20, 'state': 'type1', 'url': 'a'},
                        {'frame': 21, 'state': 'type2', 'url': 'ab'},
                        {'frame': 22, 'state': 'type3', 'url': 'abc'},
                    ],
                }],
            },
            {
                'id': '02-canvas', 'scriptShot': 2, 'frame': 'canvas', 'from': 100,
                'durationInFrames': 100, 'boxShot': True,
                'elements': [
                    {
                        'id': 'badge', 'component': 'CornerBadge', 'outsidePage': True,
                        'x': 1400, 'y': 90, 'w': 172, 'h': 48, 'fontSize': 28,
                        'color': '#86EFAC', 'background': '#14532D', 'appearFrame': 4,
                        'text': '示例角标',
                    },
                    {
                        'id': 'meter', 'type': 'rect', 'sync': 'res-free',
                        'x': 100, 'y': 200, 'w': 800, 'h': 40, 'appearFrame': 0, 'text': '满',
                        'stateKeyframes': [
                            {'frame': 0, 'state': 'a', 'text': '满'},
                            {'frame': 10, 'state': 'b', 'w': 640},
                            {'frame': 20, 'state': 'c', 'w': 480},
                        ],
                    },
                ],
            },
        ]}],
    }
    cv = {
        'sizes': {
            '16x9': {
                'width': 1920, 'height': 1080, 'bottom15Y': 918,
                'elements': [
                    {'id': 'page', 'x': 100, 'y': 80, 'w': 800, 'h': 600, 'backTabs': [],
                     'boxes': {'query': [10, 200, 100, 40]}},
                    {'id': 'price', 'priceLine': True, 'text': '199', 'x': 10, 'y': 700, 'w': 80,
                     'h': 40, 'fontSize': 48, 'color': '#F59E0B'},
                ],
            },
        },
    }
    (d / 'storyboard.json').write_text(json.dumps(sb, ensure_ascii=False), encoding='utf-8')
    (d / 'covers.json').write_text(json.dumps(cv, ensure_ascii=False), encoding='utf-8')
    out = d / 'knoll-props.md'
    rc = main(['--dir', str(d), '--out', str(out), '--forbid', '熔断'])
    assert rc == 0, rc
    txt = out.read_text(encoding='utf-8')
    headings = [
        '## 本版相对 （待填：上一冻结 sha） 的变化（必填）',
        '## 相对上一期的变化——Knoll 必读（必填）',
        '## 0. 画面类型 `frame`（必填）',
        '## 1. 页型与状态帧（有 browser 镜则必填）',
        '## 2. 页外角标与叠字（必填）',
        '## 3. 计数与同步（必填）',
        '## 4. 封面 `covers.json`（必填）',
        '## 5. 方框加文字镜 / 讨论题 / 下期（必填）',
    ]
    for h in headings:
        assert h in txt, h
    assert '`"browser"`' in txt and '`"canvas"`' in txt
    assert '| 1 | 01-browser |' in txt and '| 2 | 02-canvas |' in txt and '| 是 |' in txt
    assert '逐字输入 type1..type3：帧 20–22（每帧一字），`url` 依次为 `abc` 前 1..3 个字符' in txt
    assert 'CornerBadge' in txt and "text='示例角标'" in txt
    assert '（res-free）' in txt and '640' in txt
    assert '（待填：本版变化）' in txt and '（待填：页型字段表）' in txt and '（待填：标签延续）' in txt and '（待填：封面版式）' in txt
    sb['scenes'][0]['shots'][1]['elements'][0]['text'] = '出现熔断'
    (d / 'storyboard.json').write_text(json.dumps(sb, ensure_ascii=False), encoding='utf-8')
    try:
        main(['--dir', str(d), '--out', str(d / 'nope.md'), '--forbid', '熔断'])
    except SystemExit as e:
        assert e.code != 0
    else:
        raise AssertionError('--forbid must raise when the word is in the note')
    assert not (d / 'nope.md').exists()
    print('knoll selftest ok')
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='.')
    ap.add_argument('--spec', default=None)
    ap.add_argument('--out', default=None)
    ap.add_argument('--require-frozen', action='store_true')
    ap.add_argument('--forbid', default='')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    ctx, txt = render(a.dir, spec_path=a.spec, require_frozen=a.require_frozen, forbid=a.forbid)
    out = Path(a.out or Path(a.dir) / 'knoll-props.md')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(txt, encoding='utf-8', newline='\n')
    print('knoll-props ok', ctx.sha(ctx.sbb), 'lines', txt.count('\n'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
