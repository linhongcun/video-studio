# EP.15 db-transaction（骨架） 分镜自检（Miyazaki）。python3 -B validate.py → 全过打印 ALL OK
import json,re,os,sys
from common_split import ids,SPLIT,SCRIPT,tts,narration
H=os.path.dirname(os.path.abspath(__file__));_p=os.path.join(H,'storyboard.json')
if not os.path.isfile(_p): sys.exit('预备阶段：还没有 storyboard.json')
d=json.load(open(_p));err=[];M=80
TERMS=['事务','提交','回滚','原子性']
BANNED=['COMMIT','ROLLBACK','ACID','commit','rollback','acid','Commit','Rollback','MySQL','InnoDB','倍','我是','下期见']
N=lambda t:re.sub(r'[\s，。：；？！、,.:;?!]','',t)
def lines_px(e):   # 真实 Main.tsx：rect 标签首行 fs（默认 32），其余行 round(fs×(fs>40?0.5:0.85))；text 用 fontSize
    if e['type']=='rect':
        L=(e.get('label') or '').split('\n');fs=e.get('fontSize') or 32
        return [(l,fs if i==0 or len(L)==1 else round(fs*(0.5 if fs>40 else 0.85))) for i,l in enumerate(L) if l.strip()]
    if e['type']=='text': return [(e['text'],e['fontSize'])]
    return []
narr=narration(); assert len(narr)==7
g=0;nsh=0;subsAll=[]
for sc in d['scenes']:
    assert sc['from']==g,('scene from',sc['id']);f=g
    for sh in sc['shots']:
        nsh+=1;L=sh['durationInFrames']
        if sh['from']!=f: err.append(('shot from',sh['id']))
        f+=L;S=sh['subtitles']
        if S[0]['from']!=0 or S[-1]['to']!=L-1 or any(a['to']+1!=b['from'] for a,b in zip(S,S[1:])): err.append(('subs cover',sh['id']))
        subsAll+= [N(x['text']) for x in S]
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
                if any(b in l for b in BANNED): err.append(('banned',sh['id'],e['id'],l))
                if re.search(r'\d{2,}',l) and not any('示例' in (x.get('text') or x.get('label') or '') for x in sh['elements']): err.append(('number w/o 示例',sh['id'],l))
            if e['type']=='image' and not os.path.isfile(os.path.join(H,e['asset'])): err.append(('asset',e['asset']))
            if e['type'] in('icon',): err.append(('icon type not used this ep',e['id']))
        for a in sh['animations']:
            if a['elementId'] not in ids_: err.append(('anim target',sh['id'],a['elementId']))
            if any(not 0<=k['frame']<L for k in a['keyframes']): err.append(('kf range',sh['id'],a['elementId']))
        for x in S:
            if any(b in x['text'] for b in BANNED): err.append(('banned sub',sh['id'],x['text']))
    g=f
    if sc['durationInFrames']!=g-sc['from']: err.append(('scene dur',sc['id']))
if d['meta']['durationInFrames']!=g: err.append('total')
# 画面文字不重复字幕（术语除外）：标签文字 == 某条字幕（去标点）或是 ≥8 字的字幕子串 → 报
for sc in d['scenes']:
    for sh in sc['shots']:
        for e in sh['elements']:
            if e.get('role')=='subtitle': continue
            for l,_ in lines_px(e):
                n=N(l)
                if not n or l in TERMS: continue
                if n in subsAll or (len(n)>=6 and any(n in s for s in subsAll)): err.append(('repeats subtitle',sh['id'],l))
P=d['meta'].get('poster') or {}
if not P or not any(x['id']==P.get('shotId') and x['from']+P['localFrame']==P['frame'] and P['localFrame']<x['durationInFrames'] for sc in d['scenes'] for x in sc['shots']): err.append('poster')
print(err if err else 'ALL OK',g,nsh,'provisionalTiming',d['meta']['provisionalTiming'])
sys.exit(1 if err else 0)
