# EP.05 分镜校验（沿用 EP.04 validate.py，去掉 extraHold，加水印留空区 / 片尾 / 暂定 timing 键校验）
import json,re,os,sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from common_split import ids as SEG,SPLIT,SCRIPT
d=json.load(open('storyboard.json'));src=open(SCRIPT).read();TM=json.load(open('timing.json'))
narr=re.findall(r'- 旁白：(.+)',src);err=[];g=0;M=80
BANNED=["面试","八股","满分","考点","阿里云","腾讯云","华为云","AWS","ELB","SLB","Nginx","HAProxy","原创","片尾"]
ALLOW_PHR=[]
ALLOW={"CDN","Cache-Control","max-age","ETag","Not","Modified","logo.v1.png","logo.v2.png"}
WM=(1700,80,1840,130)
art=open("/workspace/sorkin-backup/browser-cache/article.mdx").read()
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
for a in ('fridge','fridge-open','photo','tag','box-amber','store','counter-idle'):
    if f'assets/{a}.svg' not in assets: err.append(('new icon unused',a))
for a in assets:
    if re.search(r'<text',open(a).read()): err.append(('text inside icon',a))
# EP.07：英文术语只上屏不进旁白；画面文字不重复字幕句子（≥6 字的画面文字不能是本镜头旁白的子串）
NORM=lambda t:re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]','',t)
for t in ("Cache-Control","max-age","ETag","304","Not Modified"):
    if any(t in n for n in narr): err.append(('english in narration',t))
for sc in d['scenes']:
    for sh in sc['shots']:
        nn=NORM(sh['narration'])
        for e in sh['elements']:
            if e.get('role')=='subtitle': continue
            for t in (e.get('text'),e.get('label')):
                if t and len(NORM(t))>=6 and NORM(t) in nn: err.append(('screen repeats subtitle',sh['id'],e['id'],t))
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
if err or perr: sys.exit(1)
