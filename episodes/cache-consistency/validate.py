# EP.22 cache-consistency 分镜自检（Miyazaki）。python3 -B validate.py → 全过打印 ALL OK
import json,re,os,sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'_audit'));from labelcore import full
from common_split import ids,SPLIT,SCRIPT,tts,narration
H=os.path.dirname(os.path.abspath(__file__));_p=os.path.join(H,'storyboard.json')
if not os.path.isfile(_p): sys.exit('预备阶段：还没有 storyboard.json')
d=json.load(open(_p));err=[];M=80
TERMS=['缓存','一致性','旁路缓存','更新缓存','删缓存','延迟双删','消息队列','变更日志','主从延迟','过期时间','最终一致']
Q1='你有没有遇到过：明明改了，刷新还是旧的？';Q2='评论区说说是哪个网站或 App。';RM='点个关注不迷路，觉得有用就点赞收藏。'
BANNED=['下期','上期','我是','拆库','全村','窗口','官方推荐','复制延迟','下次见','EP']
_EN=re.compile(r'[A-Za-z0-9０-９]')
class _L:   # 画面：不许字母数字；字幕照念旁白，放行「MySQL」「Redis」「ID」（字母专名，版本用汉字「八点四」）
    def search(self,t): return _EN.search(t.replace('MySQL','').replace('Redis','').replace('TTL','').replace('App','').replace('Cache-Aside','').replace('binlog',''))
LVL=_L()
N=lambda t:re.sub(r'[\s，。：；？！、,.:;?!]','',t)
def lines_px(e):   # 真实 Main.tsx：rect 标签首行 fs（默认 32），其余行 round(fs×(fs>40?0.5:0.85))；text 用 fontSize
    if e['type']=='rect':
        L=(e.get('label') or '').split('\n');fs=e.get('fontSize') or 32
        return [(l,fs if i==0 or len(L)==1 else round(fs*(0.5 if fs>40 else 0.85))) for i,l in enumerate(L) if l.strip()]
    if e['type']=='text': return [(e['text'],e['fontSize'])]
    return []
narr=narration(); assert len(narr)==11
g=0;nsh=0;subsAll=[]
for sc in d['scenes']:
    assert sc['from']==g,('scene from',sc['id']);f=g
    for sh in sc['shots']:
        nsh+=1;L=sh['durationInFrames']
        if sh['from']!=f: err.append(('shot from',sh['id']))
        f+=L;S=sh['subtitles']
        if S[0]['from']!=0 or S[-1]['to']!=L-1 or any(a['to']+1!=b['from'] for a,b in zip(S,S[1:])): err.append(('subs cover',sh['id']))
        subsAll+= [N(x['text']) for x in S if x['text']]
        if sh['id']=='hook-1' and S[0]['from']!=0: err.append('hook sub0')
        for x in S:
            if len(x['text'])>24: err.append(('sub long',sh['id'],x['text']))
        ids_=[e['id'] for e in sh['elements']]
        if len(set(ids_))!=len(ids_): err.append(('dup id',sh['id']))
        for e in sh['elements']:
            if e.get('role')=='subtitle': continue
            if e['x']<M or e['y']<M or e['x']+e['w']>1920-M or e['y']+e['h']>880: err.append(('safe',sh['id'],e['id']))
            if e['x']<1840 and e['x']+e['w']>1700 and e['y']<130 and e['y']+e['h']>80: err.append(('watermark zone',sh['id'],e['id']))
            for l,px in lines_px(e):
                if px<28: err.append(('font<28',sh['id'],e['id'],l,px))
                if any(b in l for b in BANNED) or (LVL.search(l) and l not in TERMS): err.append(('banned',sh['id'],e['id'],l))
                if re.search(r'[0-9０-９]',l): err.append(('digit on screen',sh['id'],e['id'],l))
                if re.search(r'[A-Za-z]',l.replace('App','') if e.get('quote') else l): err.append(('latin on screen',sh['id'],e['id'],l))
            if e['type']=='image' and not os.path.isfile(os.path.join(H,e['asset'])): err.append(('asset',e['asset']))
            if e['type'] in('icon',): err.append(('icon type not used this ep',e['id']))
        for a in sh['animations']:
            if a['elementId'] not in ids_: err.append(('anim target',sh['id'],a['elementId']))
            if any(not 0<=k['frame']<L for k in a['keyframes']): err.append(('kf range',sh['id'],a['elementId']))
        for x in S:
            if any(b in x['text'] for b in BANNED) or LVL.search(x['text']): err.append(('banned sub',sh['id'],x['text']))
    g=f
    if sc['durationInFrames']!=g-sc['from']: err.append(('scene dur',sc['id']))
if d['meta']['durationInFrames']!=g: err.append('total')
# 画面文字不重复字幕（术语除外）：标签文字 == 某条字幕（去标点）或是 ≥8 字的字幕子串 → 报
for sc in d['scenes']:
    for sh in sc['shots']:
        for e in sh['elements']:
            if e.get('role')=='subtitle' or e.get('quote'): continue   # v4 四格对比：每格是旁白原句（Nolan 定），不算重复字幕
            for l,_ in lines_px(e):
                n=N(l)
                if not n or l in TERMS: continue
                # 2026-10-14（Nolan 审 EP.16）：删掉开场封面大字例外。≥6 字子串改为按时间查——标签可见（完整显示）期间同镜头正在显示的字幕含它才报；与任何字幕完全相同仍全片报
                vis=[f for f in range(sh['durationInFrames']) if full(sh,e['id'],f)]
                live=[N(x['text']) for x in sh['subtitles'] if vis and x['from']<=vis[-1] and x['to']>=vis[0] and any(x['from']<=f<=x['to'] for f in vis)]
                if n in subsAll or (len(n)>=6 and any(n in s for s in live)): err.append(('repeats subtitle',sh['id'],l))
# 2026-10-15（Nolan / Knoll）：直接读 storyboard 节点 fontSize（不经检查渲染器）——数字小标签（「+100」「100」「200」等）≥40 且框高 ≥2×字号；行号角标（「1」…「4」「3 号」）≥32；「（示例）」≥32
for sc in d['scenes']:
    for sh in sc['shots']:
        for e in sh['elements']:
            t=(e.get('label') or e.get('text') or '').strip();fs=e.get('fontSize') or (32 if e['type']=='rect' else 0)
            if e['type']=='rect' and re.fullmatch(r'[+−-]?\d{2,}',t) and (fs<40 or e['h']<2*fs): err.append(('num tag font',sh['id'],e['id'],t,fs,e['h']))
            if e['type']=='rect' and re.fullmatch(r'\d( 号)?',t) and fs<32: err.append(('row tag font',sh['id'],e['id'],t,fs))
            if '示例' in t and fs<32: err.append(('示例 font',sh['id'],e['id'],fs))
_lab={(e.get('label') or '') for sc in d['scenes'] for sh in sc['shots'] for e in sh['elements']}
for t in TERMS:
    if t not in _lab: err.append(('term label missing',t))
# 字幕 = 旁白原文（去标点逐镜头比对）
for sc in d['scenes']:
    for sh in sc['shots']:
        if N(''.join(x['text'] for x in sh['subtitles']))!=N(sh['narration']): err.append(('subs != narration',sh['id']))
P=d['meta'].get('poster') or {}
if not P or not any(x['id']==P.get('shotId') and x['from']+P['localFrame']==P['frame'] and P['localFrame']<x['durationInFrames'] for sc in d['scenes'] for x in sc['shots']): err.append('poster')
# EP.22：章节卡、开场第 0 帧、片尾原句、旁白禁用说法
CARDN={"card-1":"第一层 · 删而不改","card-2":"第二层 · 先改库再删","card-3":"第三层 · 删失败了怎么办","card-4":"第四层 · 主从延迟","card-5":"兜底 · 过期时间"}
import itertools
for sc in d['scenes']:
    for sh in sc['shots']:
        if sh['id'] in CARDN:
            labs=[e.get('label') for e in sh['elements'] if e.get('role')!='subtitle']
            if labs!=[CARDN[sh['id']]]: err.append(('card',sh['id'],labs))
            run=max((sum(1 for _ in g_) for k_,g_ in itertools.groupby(full(sh,'nm',f) for f in range(sh['durationInFrames'])) if k_),default=0)-sh['transition']['durationInFrames']
            if run<69: err.append(('card full<69',sh['id'],run))
            if sh['narration'] or not sh.get('chapterCard',{}).get('insertBeforeSentence'): err.append(('card hold meta',sh['id']))
h1=d['scenes'][0]['shots'][0]
labs0={e.get('label') for e in h1['elements'] if e['type']=='rect' and full(h1,e['id'],0)}
if not {'后台','页面'}<=labs0: err.append(('hook frame0',labs0))
if not h1['subtitles'][0]['text'].startswith('老板'): err.append('hook first words')
allnarr=''.join(narr)
if '答案马上来' not in narr[0]: err.append('答案马上来')
if Q1+Q2+RM not in narr[-1] or not narr[-1].endswith(RM): err.append('ending order/text')
for b_ in ('上期','EP.8','官方推荐','下期','提交之后','天然','最多活到','写库比读库慢','乱序','后厨','备菜台','厨师','分仓库','master','slave'):
    if b_ in allnarr: err.append(('narration banned',b_))
if re.search(r'[0-9]',allnarr): err.append('digit in narration')
EL=[e.get('label') for sc in d['scenes'] for sh in sc['shots'] for e in sh['elements'] if e.get('quote') and not e.get('dimmed')]
if Q1+'\n'+Q2 not in EL or RM not in EL: err.append(('end card text',EL))
if d['scenes'][-1]['shots'][-1].get('camera') is None: err.append('last shot push-in')
print(err if err else 'ALL OK',g,nsh,'provisionalTiming',d['meta']['provisionalTiming'])
sys.exit(1 if err else 0)
