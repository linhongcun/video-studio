# EP.12 分镜校验（沿用 EP.11）；EP.11 分镜校验（沿用 EP.10）；EP.10 分镜校验（沿用 EP.09）；EP.05 分镜校验（沿用 EP.04 validate.py，去掉 extraHold，加水印留空区 / 片尾 / 暂定 timing 键校验）
import json,re,os,sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from common_split import ids as SEG,SPLIT,SCRIPT
d=json.load(open('storyboard.json'));src=open(SCRIPT).read();TM=json.load(open('timing.json'))
narr=re.findall(r'- 旁白：(.+)',src);err=[];g=0;M=80
BANNED=["面试","八股","满分","考点","阿里云","腾讯云","华为云","AWS","ELB","SLB","Nginx","HAProxy","原创","片尾"]
ALLOW_PHR=[]
ALLOW={"bug"}
WM=(1700,80,1840,130)
AP="/workspace/sorkin-backup/circuit-breaker/article.mdx"  # EP.10：文章还没出，有了再校验锚点
if os.path.isfile(AP):
    art=open(AP).read()
    for x in SEG:
        if "{#"+x+"}" not in art: err.append(('article id',x))
def lum(h):
    c=[int(h[i:i+2],16)/255 for i in (1,3,5)];c=[x/12.92 if x<=0.03928 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
def cr(a,b): A,B=sorted([lum(a),lum(b)],reverse=True); return (A+0.05)/(B+0.05)
def width(t,fs): return sum(fs if re.match(r'[\u3000-\uffff]',ch) else 0.6*fs for ch in t)
BG=d['meta']['palette']['bg'];minc=99;assets=set()
assert [s['chapterId'] for s in d['scenes']]==SEG
m=d['meta']
if (m['width'],m['height'],m['fps'])!=(1920,1080,30): err.append('format')
if m['provisionalTiming']!=any(v.get('provisional') for v in TM.values()): err.append('provisional flag')
exp_keys=[f"{c}-{k+1}" for c in SEG for k in range(len(SPLIT[c]))]
if list(TM)!=exp_keys: err.append(('timing keys',list(TM)))
for i,s in enumerate(d['scenes']):
    if s['from']!=g: err.append(('scene gap',s['id']))
    f=g
    for sh in s['shots']:
        if sh['from']!=f: err.append(('shot gap',sh['id']))
        L=sh['durationInFrames'];ids={e['id'] for e in sh['elements']}
        te=TM.get(sh['id'])
        if not te or L!=te['duration']: err.append(('timing',sh['id']))
        if te and te['audioFrames']>L: err.append(('audio over shot',sh['id']))
        if len(ids)!=len(sh['elements']): err.append(('dup id',sh['id']))
        prev=-1
        for st in sh['subtitles']:
            if not(prev<st['from']<=st['to']<L): err.append(('sub',sh['id']))
            if width(st['text'],44)>1600: err.append(('sub too long',sh['id'],st['text']))
            prev=st['to']
        for a in sh['animations']:
            if a['elementId'] not in ids: err.append(('ref',sh['id'],a['elementId']))
            for k in a['keyframes']:
                if not 0<=k['frame']<L: err.append(('kf',sh['id']))
        for e in sh['elements']:
            if e['x']<M or e['y']<M or e['x']+e['w']>1920-M or e['y']+e['h']>1080-M: err.append(('safe',sh['id'],e['id']))
            if e.get('role')!='subtitle' and e['y']+e['h']>880: err.append(('subband',sh['id'],e['id']))
            if e.get('role')!='subtitle':
                x,y,w,h=e['x'],e['y'],e['w'],e['h']
                if e['type']=='text' and e.get('align')=='center': a_=min(w,width(e['text'],e['fontSize']));x+=(w-a_)/2;w=a_
                if e['type']=='arrow' and e.get('label'): y-=e.get('fontSize',32)+8  # 箭头标签画在箭头上方
                if x<WM[2] and x+w>WM[0] and y<WM[3] and y+h>WM[1]: err.append(('watermark zone',sh['id'],e['id']))
            if e['type']=='image':
                assets.add(e['asset'])
                if not os.path.isfile(e['asset']): err.append(('asset missing',e['asset']))
            for t in [e.get('text'),e.get('label')]:
                if e.get('role')=='subtitle' or not t: continue
                tt=t
                for p in ALLOW_PHR: tt=tt.replace(p,' ')
                for w in re.findall(r'[A-Za-z][A-Za-z0-9\-\.]*',tt):
                    if w not in ALLOW: err.append(('english',sh['id'],e['id'],w))
                fs=e.get('fontSize',40); room=e['w'] if e['type']!='arrow' else max(e['w'],400)
                if width(t,fs)>room+1: err.append(('text overflow',sh['id'],e['id'],round(width(t,fs)),e['w']))
                if e['type']=='rect' and fs*1.2>e['h']: err.append(('label too tall',sh['id'],e['id']))
            if e['type']=='text' and e['color']:
                c=cr(e['color'],BG);minc=min(minc,c)
                if c<4.5: err.append(('contrast',sh['id'],e['id'],round(c,2)))
            if e['type'] in('rect','arrow') and e.get('label'):
                c=cr(e['color'] if e['type']=='arrow' else d['meta']['palette']['text'],BG if e['type']=='arrow' else e['color']);minc=min(minc,c)
                if c<4.5: err.append(('contrast',sh['id'],e['id'],round(c,2)))
        f+=L
    if f-g!=s['durationInFrames']: err.append(('scene sum',s['id']))
    if "".join(x['narration'] for x in s['shots']).replace(' ','')!=narr[i].replace(' ',''): err.append(('narr',s['id']))
    g+=s['durationInFrames']
if g!=d['meta']['durationInFrames'] or g!=sum(v['duration'] for v in TM.values()): err.append('total')
raw=json.dumps(d['scenes'],ensure_ascii=False)  # 只查镜头内容（meta 说明里会提到片尾）
for b in BANNED:
    if b in raw: err.append(('banned/endcard',b))
for a in ('breaker-box','breaker-tripped','switch-on','switch-off','spark','aircon','lamp','socket','meter','fridge','phone','ticket','gate','queue','guest','timer','hourglass'):
    if f'assets/{a}.svg' not in assets: err.append(('new icon unused',a))
for a in assets:
    if re.search(r'<text',open(a).read()): err.append(('text inside icon',a))
# EP.08（沿用 EP.07）：英文术语只上屏不进旁白；画面文字不重复字幕句子（≥6 字画面文字去标点后，与本镜头旁白最长公共子串 ≥60% 或二元组重合 >60%，或按序字符覆盖 ≥75% 即报错）
NORM=lambda t:re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]','',t)
def LCS(a,b):
    m=0;p=[0]*(len(b)+1)
    for x in a:
        q=[0]*(len(b)+1)
        for j,y in enumerate(b):
            if x==y: q[j+1]=p[j]+1; m=max(m,q[j+1])
        p=q
    return m
def LSEQ(a,b):
    p=[0]*(len(b)+1)
    for x in a:
        q=[0]
        for j,y in enumerate(b): q.append(p[j]+1 if x==y else max(p[j+1],q[j]))
        p=q
    return p[-1]
TERMS=["熔断降级","消息队列","雪崩","熔断","降级","半开","超时","幂等","限流"]
def STRIP(t):
    for w in sorted(TERMS,key=len,reverse=True): t=t.replace(w,'')  # 长词先删（RabbitMQ 先于 MQ）
    return NORM(t)
def OVL(t,n):  # 改严：最长公共子串 ≥ 画面文字 60%，或字符二元组重合率 > 60%
    l=LCS(t,n)/len(t); bg=[t[i:i+2] for i in range(len(t)-1)]; b=sum(g in n for g in bg)/len(bg)
    sq=LSEQ(t,n)/len(t)  # 补充：按顺序的字符覆盖（可跳字的公共子序列）≥75%，抓「改几个字的复述」
    return f'lcs {l:.0%} bigram {b:.0%} seq {sq:.0%}' if l>=0.6 or b>0.6 or sq>=0.75 else None
# EP.10：旁白念术语（QPS 按字母读）；EP.09：旁白念术语（MQ 按字母读，Kafka/RabbitMQ 各一次）；Message Queue 只上屏
for t in ():
    if any(t in n for n in narr): err.append(('screen-only english in narration',t))
for sc in d['scenes']:
    for sh in sc['shots']:
        nn=NORM(sh['narration'])
        for e in sh['elements']:
            if e.get('role')=='subtitle': continue
            for t in (e.get('text'),e.get('label')):
                if t and len(STRIP(t))>=6:   # v0.12.1：术语白名单词不计（术语标签和旁白重复算强调），只查剩下的长句
                    r=OVL(STRIP(t),STRIP(sh['narration']))
                    if r: err.append(('screen repeats subtitle',sh['id'],e['id'],t,r))
first=d['scenes'][0]['shots'][0]['narration'];lastn=d['scenes'][-1]['shots'][-1]['narration']
if '我是' in json.dumps(d['scenes'],ensure_ascii=False): err.append('「我是」 present (branding: 不出现我是 IT小村)')
if any('我是IT小村' in re.sub(r'\s','',q['text']) for v in TM.values() for q in v['sentences']): err.append('timing has 我是 IT小村 sentence')
P=d['meta'].get('poster') or {}
if not P or not any(x['id']==P.get('shotId') and x['from']+P['localFrame']==P['frame'] and P['localFrame']<x['durationInFrames'] for sc in d['scenes'] for x in sc['shots']): err.append('poster')
print(err or 'ALL OK','frames',g,'shots',sum(len(s['shots']) for s in d['scenes']),'min contrast',round(minc,2),'assets used',len(assets),'provisionalTiming',d['meta']['provisionalTiming'])
import xml.etree.ElementTree as ET
px=[];perr=[]
for sc in d['scenes']:
    for sh in sc['shots']:
        tx={e['id'] for e in sh['elements'] if e['type']=='text' and e.get('role')!='subtitle'}
        for e in sh['elements']:
            if e.get('role')=='subtitle': continue
            if e['type']=='text' or e.get('label'):
                fs=e.get('fontSize',40);px.append(fs)
                if fs<28: perr.append((sh['id'],e['id'],fs))
        for a in sh['animations']:
            k=a['keyframes']
            if a['elementId'] in tx and a['property']=='opacity' and k[0]['value']==0 and k[-1]['value']==1 and k[-1]['frame']-k[0]['frame']>15: perr.append(('slow fade',sh['id'],a['elementId']))
if perr: print('FONT/FADE:',perr)
print('min on-screen px',round(min(px),1))
# EP.09：一万单 / 一千单是示意数字，画面上出现必须带「示意」
for sc in d['scenes']:
    for sh in sc['shots']:
        for e in sh['elements']:
            t=e.get('text') or e.get('label') or ''
            if e.get('role')!='subtitle' and any(n in t for n in tuple('0123456789')+('一万','一千','一百','三次','两次')) and '示意' not in t: err.append(('示意 missing',sh['id'],e['id'],t))
# 术语念到时上屏
TERMSHOW={"雪崩":"雪崩","熔断":"熔断","降级":"降级","半开":"半开","超时":"超时","消息队列":"消息队列","限流":"限流","幂等":"幂等"}
for k,v_ in TERMSHOW.items():
    for sc in d['scenes']:
        for sh in sc['shots']:
            if k in sh['narration']:
                if not any(v_ in (e.get('text') or e.get('label') or '') for e in sh['elements'] if e.get('role')!='subtitle'): err.append(('term not on screen',sh['id'],k))
for k in ("半开","超时"):
    n=sum(x.count(k) for x in narr)
    if n!=1: err.append(('tool named times',k,n))
# EP.12：Nolan——TTS 文字「出故障了吗」，字幕保留「bug」
h1=[x for sc in d['scenes'] for x in sc['shots'] if x['id']=='hook-1'][0]
if '出故障了吗' not in h1.get('ttsText','') or 'bug' in h1.get('ttsText',''): err.append('hook-1 ttsText')
if not any('bug' in s['text'] for s in h1['subtitles']): err.append('hook-1 subtitle bug')
if any('故障' in s['text'] for sc in d['scenes'] for x in sc['shots'] for s in x['subtitles']): err.append('subtitle has 故障')
# EP.12 第 2 版：画面不出现「猜你喜欢 / 推荐 / 热销」
BAN=("猜你喜欢","推荐","热销")
for sc in d['scenes']:
    for sh in sc['shots']:
        for e in sh['elements']:
            t=(e.get('text') or '')+(e.get('label') or '')
            if e.get('role')!='subtitle' and any(b in t for b in BAN): err.append(('banned word on screen',sh['id'],e['id'],t))
# EP.12 第 2 版：短标签（去空格 <6 字）与术语标签完全显示（opacity=1，且不在动画中）≥60 帧
def OPA(sh,eid,f):
    v=None
    for a in sh['animations']:
        if a['elementId']!=eid or a['property'] not in('opacity','scale'): continue
        k=a['keyframes']
        if k[0]['frame']<=f<k[-1]['frame']: return -1   # 淡入/弹出动画中不算完全显示
        w=k[0]['value'] if f<k[0]['frame'] else k[-1]['value']   # v2c 修：动画开始前取首帧值（之前误当 1）
        if a['property']=='opacity': v=w if v is None else min(v,w)
        continue
        if f>=k[-1]['frame']: v=k[-1]['value']; continue
        return -1
    return 1 if v is None else v
SHOWN=[]
for sc in d['scenes']:
    for sh in sc['shots']:
        for e in sh['elements']:
            t=e.get('text') or e.get('label') or ''
            if e.get('role')=='subtitle' or not t: continue
            if len(re.sub(r'[\s·：？]','',t))<6 or any(w in t for w in TERMS):
                run=best=0
                for f in range(sh['durationInFrames']):
                    run=run+1 if OPA(sh,e['id'],f)==1 else 0; best=max(best,run)
                SHOWN.append((sh['id'],t,best))
                if best<60: err.append(('label shown <60f',sh['id'],t,best))
print('labels <80f:',sorted([x for x in SHOWN if x[2]<80],key=lambda x:x[2]))
print('short/term labels full-show frames (min):',min(SHOWN,key=lambda x:x[2]))
if err: print('EP12 checks:',err)
if err or perr: sys.exit(1)
