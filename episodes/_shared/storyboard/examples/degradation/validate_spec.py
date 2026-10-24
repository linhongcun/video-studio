"""EP.14 degradation (slug degradation-v1) validate spec — ported from the episode-dir validate.py (frozen result: 6623 checks / 0 errors,
onset 91/91, 标注表 59/0). Generic checks run in episodes/_shared/storyboard/validate.py from the constants below; checks(v) holds the
EP.14-only ones (shopPrice pages, tab chain, shot-by-shot facts, cover price line, RFC 2606 in the article).
Run:  python3 -B episodes/_shared/storyboard/validate.py --spec episodes/_shared/storyboard/examples/degradation/validate_spec.py \
        --episode-dir episodes/degradation --inputs episodes/_shared/storyboard/examples/degradation/repo-inputs.json \
        --storyboard OUT/storyboard.json --covers OUT/covers.json"""
import json, re
TITLE = '搜索页和结算页，为什么两个价不一样？'; EPISODE = 14; SLUG = 'degradation-v1'
WAVLEN = 5152; NSHOT = 20; NSENT = 24; MIN = 180; MAX = 300; TR = 10
Q = '要是搜索页和结算页都把红包计算一起关掉，下单还能不能顺利完成？评论区说说。'
TEASER = '下期，加个索引，为啥就快了？'; NEXT = (15, TEASER)
KNOLL = [(0, 314), (314, 595), (595, 865), (865, 1131), (1131, 1395), (1395, 1650), (1650, 1905), (1905, 2148), (2148, 2382), (2382, 2632), (2632, 2858), (2858, 3115), (3115, 3375), (3375, 3601), (3601, 3827), (3827, 4103), (4103, 4363), (4363, 4630), (4630, 4883), (4883, 5152)]
URL_S, URL_C = 'shop.example/search', 'shop.example/checkout'; URL_DOMAIN = 'shop.example'; MAX_EXC = {1: 314}
BROWSER_SHOTS = [1, 3, 4, 13, 14, 17, 19]
BOX_SHOTS = [10, 11, 18, 20]; BOX_NOCARD_OK = (20,)   # shot 20 (ending) is a box shot without a boxCard
SHA = {'narration.py': '013cfb9b', 'voice/cues.json': '751217cb', 'voice/shot_frames.json': 'f8f03b6c', 'voice.wav': '9e70470c', 'words.json': '36bccee8'}
NARRATION_FILE = 'narration.py'; WORDS_SCRIPT_SHA = '629b5042'
DEVTOOLS = []; MAP_SHOTS = []
PAGE_VIEWS = ('search', 'checkout', 'success')
FAKE_COMP = ('NotepadWindow', 'Terminal', 'LogWindow', 'Dashboard', 'DevToolsNetwork', 'BlockHighlight')
FAKE_TEXT = ('记事本', '终端', '命令行', '日志', '监控', '后台管理', '服务状态页', '开发者工具', 'Network', '开关', '拉杆', '电闸', '保险丝', '水管', '阀门',
             '淘宝', '京东', '拼多多', 'Azure', 'AWS', 'feature flag', '雪崩', '半开', '熔断')
FILM_BANNED = ('熔断',)   # not in any on-screen text, cover, title, question or narration
SAMPLE_RE = r'(199|179|129|−20|\d+%|请求：\d+)'; SAMPLE_SPLIT = r'["，、；]'; SAMPLE_MARK = '示例'
TERMS = (('核心链路', 10), ('降级', 11))   # term may not be on screen before this shot
WATERMARK = (1680, 30, 1880, 100); SUBTITLE_TOP = 900; SAMPLE_UNTIL = 20; SAMPLE_TEXT = '示例数据'; DARK = '#0B1020'; RIPPLE_MIN = 12
SCREEN_CUT = r'[；;]地址栏'; SCREEN_STRIP = r'（以上压暗背景）|（划掉）|（依口播顺序出现）|。$|〔换行〕.*'; SCREEN_COVER_SHOTS = (1,)
STRUCT_HOOK = {(1, '大促时'): '脚本要求开场冲突第 0 帧全部可见（结果预置），按结构元素处理',
               (7, '红包服务'): '标注表写明中间唯一一个「红包服务」与「搜索页 →」镜首即在（结构元素 svc-node）'}
COVER_HEADER = 80; COVER_FIRST_ROW_GAP = 24
MIN_QUOTES = 8; ARTICLE_NEEDS = ('降级', '核心链路', '示例', '199', '179')


def checks(V):   # V = validator (validate.V); the body below keeps the original local names, incl. a local `v`
    check, wid, E, pages, final, at, seq, kf, frames, texts_of = V.check, V.wid, V.E, V.pages, V.final, V.at, V.seq, V.kf, V.frames, V.texts_of
    shots, m, SCRIPT_FRAME, cv, art, srcs, nrm, SL = V.shots, V.m, V.SCRIPT_FRAME, V.cv, V.art, V.srcs, V.nrm, V.SL
    PRODUCT = '商品：卫衣 ×1　199 元（示例）'; ADDRESS = '收货地址：示例路 1 号（示例）'; COUPON = '红包抵扣：−20 元（示例）'
    ITEM0 = '卫衣　到手价 199 元（示例）'
    for n in BROWSER_SHOTS:
        ps = pages(n); check(len(ps) == (2 if n in (1, 17) else 1), f'镜 {n} 窗口数 {len(ps)}')
        for pg in ps:
            check(pg.get('page') == 'shopPrice' and pg.get('sampleData') is True and 'boxes' in pg, f'镜 {n}/{pg["id"]} 页型 shopPrice')
            check(pg.get('appearFrame') == 0 and pg.get('timingRole') == 'structural', f'镜 {n}/{pg["id"]} 网页第 0 帧在场')
            av = pg['w'] - 182 - min(160, pg['w'] * .2)
            for u in {URL_S, URL_C}:
                check(av >= wid(u, 19.2) + 24 if u == URL_S else av >= 403.27 + 24, f'镜 {n}/{pg["id"]} 地址栏放不下 {u}（可用 {av}）')
            for k in [pg] + (pg.get('stateKeyframes') or []):
                v = k.get('view', None)
                u = k.get('url')
                if u: check(u in (URL_S, URL_C) or URL_S.startswith(u) or URL_C.startswith(u), f'镜 {n} 网址 {u}')
                co = k.get('checkout')
                if co:
                    cp = co['coupon']
                    check(co['product'] == PRODUCT and co['address'] == ADDRESS and co['button'] == '提交订单', f'镜 {n} 结算固定文字')
                    check(co['total'] == ('应付：179 元（示例）' if cp['applied'] else '应付：199 元（示例）'), f'镜 {n} 应付与红包计入不一致')
                    check(cp['text'] == (COUPON if cp['visible'] else '') and (cp['visible'] or not cp['applied']), f'镜 {n} 红包抵扣行')
                se = k.get('search')
                if se: check(se['items'][0]['text'] == ITEM0 and se['query'] == '搜索：卫衣', f'镜 {n} 搜索页首行')
                if k.get('view') and pg.get('state') != k.get('state'):
                    pass
            sk = pg.get('stateKeyframes') or []
            nt = [k for k in sk if k.get('state') == 'newTab']
            if nt:
                ty = [k for k in sk if str(k.get('state', '')).startswith('type')]; ld = kf(pg, 'loaded'); U = ld['url']
                check(nt[0].get('pageBlank') is True and nt[0].get('url') == '', f'镜 {n} 新开空白标签页')
                check([k['url'] for k in ty] == [U[:i+1] for i in range(len(U))], f'镜 {n} 地址栏逐字输入')
                check(all(b['frame'] > a['frame'] for a, b in zip([nt[0]] + ty, ty)), f'镜 {n} 输入帧递增')
                check(ld['frame'] > ty[-1]['frame'] and ld.get('pageBlank') is False, f'镜 {n} 回车后才加载')
    # 标签延续（Deming 可选 7：不留旧结算标签）：镜 3 唯一空白标签 → 输入搜索 → 镜 4 按加购后新开结算（搜索在左）→ 镜 13 搜索标签（结算在右）→ 镜 14 切到结算 → 镜 19 成功页
    p3 = pages(3)[0]; p4 = pages(4)[0]; p13 = pages(13)[0]; p14 = pages(14)[0]; p19 = pages(19)[0]
    ty3 = [k for k in p3['stateKeyframes'] if str(k.get('state', '')).startswith('type')]
    check(p3['pageBlank'] is True and p3['url'] == '' and p3['backTabs'] == [] and p3['afterTabs'] == [] and ty3[0].get('cueText') == '打开搜索页' and [k['url'] for k in ty3] == [URL_S[:i+1] for i in range(len(URL_S))] and kf(p3, 'loaded')['frame'] > ty3[-1]['frame'], '镜 3 第 0 帧唯一空白标签，「打开搜索页」起逐字输入，输完才加载')
    check(p4['view'] == 'search' and p4['backTabs'] == [] and kf(p4, 'newTab')['backTabs'] == ['搜索'] and kf(p4, 'loaded')['url'] == URL_C, '镜 4 新开结算标签（左侧保留搜索）')
    check(kf(p4, 'press')['cueText'] == '加购进结算页' and kf(p4, 'press')['ripples'][0]['center'] == 'item0Button' and kf(p4, 'press')['frame'] < kf(p4, 'newTab')['frame'], '镜 4 先按加购再新开')
    ld4 = kf(p4, 'loaded'); cr4 = kf(p4, 'couponRow'); ap4 = kf(p4, 'applied')
    check(not ld4['checkout']['coupon']['visible'] and ld4['checkout']['total'] == '应付：199 元（示例）', '镜 4 加载时应付 199、无红包行')
    check(cr4['cueText'] == '多出一行红包抵扣' and cr4['checkout']['coupon']['visible'] and not cr4['checkout']['coupon']['applied'], '镜 4 红包抵扣行随「多出一行红包抵扣」')
    check(ap4['cueText'] == '红包这时才真正算上' and ap4['checkout']['total'] == '应付：179 元（示例）', '镜 4 应付 199→179 随「红包这时才真正算上」')
    check([k['checkout']['total'] for k in p4['stateKeyframes'] if 'checkout' in k].count('应付：179 元（示例）') == 1, '镜 4 金额只变一次')
    check(p13['view'] == 'search' and p13['url'] == URL_S and not any('view' in k or k.get('state') == 'newTab' for k in p13.get('stateKeyframes') or []), '镜 13 第 0 帧即搜索标签（不新开、不闪结算页）')
    check(E(13)['works']['cueText'] == '降级之后', '镜 13「能搜、能加购」挂「降级之后」')
    t14 = kf(p14, 'tabCheckout'); check(t14['cueText'] == '结算页照常' and t14['checkout']['total'] == '应付：179 元（示例）' and kf(p14, 'press')['frame'] < kf(p14, 'success')['frame'] and final(p14, 'view') == 'success', '镜 14 切结算、提交 → 成功')
    check(p14['success'] == {'headline': '订单已提交，付款成功（示例）', 'paid': '已付：179 元（示例）'}, '镜 14 成功页文字')
    check(p19['view'] == 'success' and kf(p19, 'successDim')['cueText'] == '要是' and kf(p19, 'successDim')['dimPage'] < 1 and 'view' not in kf(p19, 'successDim'), '镜 19 第 0 帧即成功页，「要是」处压暗')
    def tabset(e, f): return list(at(e, 'backTabs', f) or []) + [at(e, 'title', f)] + list(at(e, 'afterTabs', f) or [])
    SL = {s_['scriptShot']: s_['durationInFrames'] for s_ in shots}
    for a_, b_ in ((4, 13), (13, 14), (14, 19)):
        A = pages(a_)[0]; B = pages(b_)[0]
        check(tabset(A, SL[a_]) == tabset(B, 0), f'镜 {b_} 第 0 帧标签 {tabset(B, 0)} ≠ 镜 {a_} 结尾 {tabset(A, SL[a_])}')
    check(tabset(p3, SL[3]) == tabset(p4, 0) and at(p3, 'view', SL[3]) == p4['view'], '镜 4 第 0 帧 = 镜 3 结尾搜索页')
    check(at(p14, 'view', SL[14]) == p19['view'] == 'success', '镜 19 第 0 帧 = 镜 14 结尾成功页（不闪未付款结算页）')
    check(at(p4, 'view', SL[4]) == 'checkout' and p13['view'] == 'search', '镜 13 首帧搜索页，与旁白「降级之后，搜索页照样能搜商品」一致')
    check(E(4)['svc']['text'] == '结算页红包计算：正常（示例）', '镜 4 页外角标')
    # 镜 1 / 17：两窗对照
    e1 = E(1)
    check(all(e1[k]['appearFrame'] == 0 for k in ('page', 'page2', 'cover-title', 'series-tag', 'sample')), '镜 1 第 0 帧冲突全部在场')
    check(e1['cover-title']['text'] == TITLE and e1['series-tag']['text'] == '扛住高峰', '镜 1 标题与系列角标')
    check(e1['page']['view'] == 'search' and e1['page']['url'] == URL_S and e1['page2']['view'] == 'checkout' and e1['page2']['url'] == URL_C and e1['page2']['checkout']['total'] == '应付：179 元（示例）', '镜 1 左搜索 199、右结算 179')
    check(e1['why']['text'] == '怎么回事？（示例）' and e1['why']['cueText'] == '这是怎么回事', '镜 1 怎么回事')
    e17 = E(17); check('cover-title' not in e17 and e17['page']['view'] == 'search' and e17['page2']['view'] == 'checkout' and e17['deg']['text'] == '降级：关搜索页红包计算（示例）' and e17['core']['text'] == '核心链路：结算下单照常（示例）', '镜 17 回放对照 + 叠字，不重复封面')
    for n in (1, 17):
        a, b = pages(n); check(a['x'] + a['w'] <= b['x'], f'镜 {n} 两窗不重叠')
    # ---------- 计数同步不跳（镜 6） ----------
    e6 = E(6)
    check(seq(e6['reqs']) == [f'请求：{10*i}（示例）' for i in (1, 2, 3, 4)] and seq(e6['res']) == [f'红包服务可用资源：{p}%（示例）' for p in (100, 80, 60, 40)], '镜 6 请求 10→40、资源 100→40 逐档')
    check(frames(e6['reqs'])[1:] == frames(e6['res'])[1:] == frames(e6['res-free'])[1:] and e6['res']['appearFrame'] == e6['res-free']['appearFrame'], '镜 6 请求/资源/横条同帧')
    check([e6['res-free']['w']] + [k['w'] for k in e6['res-free']['stateKeyframes'][1:]] == [800 * p // 100 for p in (100, 80, 60, 40)], '镜 6 横条长度与百分比一致')
    check(e6['reqs']['appearFrame'] < e6['res']['appearFrame'], '镜 6 先计数后资源')
    # ---------- 子流程在父节点 x 之后 ----------
    e5 = E(5); check(all(e5[k]['x'] >= e5['calc']['x'] and e5[k]['y'] >= e5['calc']['y'] + e5['calc']['h'] for k in ('spine', 'svc1', 'svc2', 'svc3', 'sum')), '镜 5 三行服务在「到手价计算」下方、x 不小于父节点')
    check(e5['svc1']['appearFrame'] < e5['svc2']['appearFrame'] < e5['svc3']['appearFrame'] < e5['sum']['appearFrame'], '镜 5 依次出现再合流')
    check(e5['spine']['x'] < min(e5[k]['x'] for k in ('svc1', 'svc2', 'svc3')), '镜 5 竖线在服务行左侧')
    check(e5['spine']['y'] + e5['spine']['h'] >= e5['sum']['y'] + 16 and e5['spine']['h'] == 340, '镜 5 竖线须延到「= 到手价」（合流）')
    # ---------- 镜 7–9 ----------
    e7 = E(7); check(e7['a-search']['appearFrame'] == 0 and e7['a-checkout']['cueText'] == '结算页下单也要问' and kf(e7['a-search'], 'warm')['frame'] == kf(e7['a-checkout'], 'warm')['frame'], '镜 7 两线同帧变暖')
    e8 = E(8); check(kf(e8['a-search'], 'struck')['frame'] == e8['off']['appearFrame'] and kf(e8['a-search'], 'struck')['strike'] and kf(e8['a-checkout'], 'bold')['frame'] == e8['keep']['appearFrame'], '镜 8 划掉与关闭同帧、加粗与留给结算页同帧')
    e9 = E(9); check(e9['a-search'].get('strike') and e9['prio']['cueText'] == '主要只给结算页用' and e9['noask']['cueText'] == '搜索页不再去问', '镜 9 沿用关闭态')
    # Deming 必改 1：旁白说「同一个 X 服务」时，画面上该服务只画一个节点，箭头都指向它
    SHARED = re.findall(r'同一个(\S{2,4}服务)', ''.join(s_['narration'] for s_ in shots))
    check(SHARED == ['红包服务'], f'「同一个…服务」识别 {SHARED}')
    for n in (7, 8, 9):
        en = E(n); nodes = [e for e in en.values() if e.get('role') != 'subtitle' and any(t.strip() == SHARED[0] or re.search('→\\s*' + SHARED[0] + '$', t) or re.search('^' + SHARED[0] + '\\s*←', t) for t in texts_of(e))]
        check([e['id'] for e in nodes] == ['svc-node'] and en['svc-node']['appearFrame'] == 0, f'镜 {n}「{SHARED[0]}」须只有一个节点（实际 {[e["id"] for e in nodes]}）')
        nd = en['svc-node']; a_, b_ = en['a-search'], en['a-checkout']
        check(a_['x'] + a_['w'] <= nd['x'] and b_['x'] >= nd['x'] + nd['w'] and a_['y'] == nd['y'] == b_['y'] and a_['text'].endswith('→') and b_['text'].startswith('←') and a_.get('pointsTo') == b_.get('pointsTo') == 'svc-node', f'镜 {n} 两条箭头左右指向同一节点')
        check((a_['x'], nd['x'], b_['x'], nd['y']) == (420, 700, 980, 300), f'镜 {n} 三列位置')
    check(E(7)['slow']['x'] == 980 and E(8)['keep']['x'] == 980 and (E(9)['prio']['x'], E(9)['prio']['y']) == (700, 440) and E(9)['prio']['y'] >= E(9)['svc-node']['y'] + E(9)['svc-node']['h'], '镜 7/8 右列叠字 x980；镜 9 优先行在节点正下方')
    e10 = E(10); check(e10['term']['text'] == '核心链路' and e10['term']['cueText'] == '核心链路' and e10['path']['appearFrame'] < e10['plain']['appearFrame'] < e10['term']['appearFrame'], '镜 10 白话先于术语')
    e11 = E(11); check(e11['term']['text'] == '降级' and e11['term']['cueText'] == '降级' and e11['l1']['appearFrame'] < e11['l2']['appearFrame'] < e11['term']['appearFrame'], '镜 11 白话先于术语')
    e12 = E(12); check(e12['also']['text'] == '也算一种降级' and e12['prev']['dimFrom'] == 0, '镜 12 承接')
    # Deming 必改 2：「核心链路」标签放在核心链路（结算）那一侧正下方
    e16 = E(16); kp = e16['keep']; pc = e16['p-check']
    check((kp['x'], kp['y']) == (1000, 420) and kp['x'] == pc['x'] and kp['y'] >= pc['y'] + pc['h'] and kp['x'] >= e16['p-search']['x'] + e16['p-search']['w'], '镜 16「保核心链路」须在「结算 179」正下方')
    check(E(17)['core']['x'] >= pages(17)[1]['x'] and E(17)['core']['x'] + E(17)['core']['w'] <= pages(17)[1]['x'] + pages(17)[1]['w'], '镜 17「核心链路」叠字在结算窗下方')
    check(E(18)['term']['x'] >= E(18)['rcard']['x'], '镜 18「核心链路」在「保住」右卡')
    check(kf(e16['wrong'], 'struck')['frame'] > e16['wrong']['appearFrame'] and e16['p-search']['text'] == '搜索 199 元（示例）' and e16['p-check']['text'] == '结算 179 元（示例）', '镜 16 对照 + 划掉算错了？')
    e18 = E(18); check(e18['l']['text'].startswith('舍掉：') and e18['r']['text'].startswith('保住：') and e18['term']['text'] == '核心链路', '镜 18 两卡')
    e19 = E(19)
    check(e19['question']['text'] + e19['question2']['text'] == Q and all(e19[k].get('reveal', {}).get('mode') == 'readAlong' for k in ('question', 'question2')), '镜 19 题干两行跟读')
    check(not any(w in json.dumps({k: v for k, v in e19.items() if k != 'page'}, ensure_ascii=False) for w in ('答案', '能完成', '不能完成')), '镜 19 不给答案')
    e20 = E(20)
    check(e20['series-tag']['text'] == '扛住高峰' and e20['wrap']['text'] == '降级就讲到这里。' and e20['next-episode-title']['text'] == TEASER and e20['follow']['text'] == '关注我，觉得有用就点赞、收藏一下吧。', '镜 20 片尾')
    check(all(e20[k].get('reveal', {}).get('mode') == 'readAlong' for k in ('next-episode-title', 'follow')), '镜 20 跟读')
    for n in (3, 13):
        pg = pages(n)[0]
        for nid in [k for k in ('nocoupon', 'works') if k in E(n)]:
            nt_ = E(n)[nid]
            for bk in ('item0Button', 'item1Button', 'item0', 'item1'):
                bx, by, bw, bh = pg['boxes'][bk]
                gapx = max(bx - (nt_['x'] + nt_['w']), nt_['x'] - (bx + bw)); gapy = max(by - (nt_['y'] + nt_['h']), nt_['y'] - (by + bh))
                check(max(gapx, gapy) >= 16, f'镜 {n}/{nid} 离 {bk} 不足 16 px')
    # ---------- covers (EP.14) ----------
    check(cv['title'] == TITLE and cv['seriesTag'] == '扛住高峰' and '降级' in cv['conclusion'] and '核心链路' in cv['conclusion'], '封面标题/结论')
    for name, sz in cv['sizes'].items():
        els = {e['id']: e for e in sz['elements']}
        pg = els['page']; sb = els['sample']
        check(pg['page'] == 'shopPrice' and pg['frame'] == 'browser' and pg['view'] == 'checkout' and pg['checkout']['total'] == '应付：179 元（示例）' and pg['checkout']['coupon']['applied'], f'封面 {name} 结算页（红包已计入）')
        check(sum(e.get('component') == 'BrowserChrome' for e in sz['elements']) == 1 and cv.get('layout') == 'single-window', f'封面 {name} 单窗（Nolan 退路：双窗 4:3 放不下）')
        check(pg['backTabs'] == [] and pg['afterTabs'] == [], f'封面 {name} 只一个标签（backTabs: []）')
        # 地址栏（渲染器 BrowserChrome.tsx：url 框宽 = 窗宽 − Σ标签 − 132 − 锁 34，标签默认 min(160, .2w)；flex 实宽 = 窗宽 − Σ标签 − 12·标签数 − 136；取小者）
        nt = 1 + len(pg['backTabs']) + len(pg['afterTabs']); tabs = nt * min(160, pg['w'] * .2)
        av = min(pg['w'] - tabs - 132 - 34, pg['w'] - tabs - 12 * nt - 136); tw = max(403.27, 21 * 32 * .61)
        check(pg['w'] >= 600 and pg['url'] == URL_C and av >= tw + 24, f'封面 {name} 地址栏 32px 放不下（可用 {av}，字宽 {tw}）')
        # 价格行：同一行、199/179 大号异色（≥ 小字 2 倍）、原字号放得下、不压窗口
        pl = [e for e in sz['elements'] if e.get('priceLine')]
        check(''.join(e['text'] for e in pl).replace(' ', '') == cv['priceLine'].replace(' ', '') and len({e['y'] for e in pl}) == 1, f'封面 {name} 价格行')
        big = [e for e in pl if e['priceRole'] == 'big']; sm = [e for e in pl if e['priceRole'] == 'small']
        check([e['text'] for e in big] == ['199', '179'] and big[0]['color'] != big[1]['color'] and min(e['fontSize'] for e in big) >= 2 * max(e['fontSize'] for e in sm), f'封面 {name} 199/179 不够醒目')
        for e in pl:
            check(sum(e['fontSize'] if ord(c) > 255 else e['fontSize'] * .58 for c in e['text']) * 1.03 <= e['w'] - 12, f'封面 {name}/{e["id"]} 价格行文字会缩')
            check(e['y'] >= pg['y'] + pg['h'] or e['y'] + e['h'] <= pg['y'], f'封面 {name}/{e["id"]} 价格行压窗口')
    # ---------- article (EP.14) ----------
    check('RFC 2606' in art and 'https://www.rfc-editor.org/rfc/rfc2606.html' in art and nrm('".example" is recommended for use in documentation or as examples.') in srcs and '".example" is recommended for use in documentation or as examples.' in art, '文章 RFC 2606 出处与原句')
