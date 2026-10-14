import json,re,os,sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
d=json.load(open('storyboard.json'));src=open('/workspace/sorkin-backup/cookie-session/script.md').read();TM=json.load(open('timing.json'))
narr=re.findall(r'- 旁白：(.+)',src);err=[];g=0;M=80
BANNED=["面试","八股","校招","满分","求职","考点","背诵","高频题","所有浏览器默认","默认 Lax","第三方","读你电脑","读取你电脑","电脑里的文件"]
ALLOW_PHR=["example.com","Set-Cookie"]
ALLOW={"Cookie","Session","HTTP","HTTPS","HttpOnly","Secure","SameSite","Lax","Token","ID","JS","URL"}
SEG=["stateless","set-cookie","send","session","protect","recap"]
art=open("/workspace/sorkin-backup/cookie-session/article.mdx").read()
for x in SEG:
    if not re.search(r"id=[\"']"+re.escape(x)+r"[\"']|#\s*.*\{#"+re.escape(x)+r"\}|"+re.escape(x),art): err.append(("article id",x))
def lum(h):
    c=[int(h[i:i+2],16)/255 for i in (1,3,5)];c=[x/12.92 if x<=0.03928 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
def cr(a,b): A,B=sorted([lum(a),lum(b)],reverse=True); return (A+0.05)/(B+0.05)
def width(t,fs): return sum(fs if re.match(r'[\u3000-\uffff]',ch) else 0.6*fs for ch in t)
BG=d['meta']['palette']['bg'];minc=99;assets=set()
assert [s['chapterId'] for s in d['scenes']]==SEG
for i,s in enumerate(d['scenes']):
    if s['from']!=g: err.append(('scene gap',s['id']))
    f=g
    for sh in s['shots']:
        if sh['from']!=f: err.append(('shot gap',sh['id']))
        L=sh['durationInFrames'];ids={e['id'] for e in sh['elements']}
        te=TM.get(sh['id']);exp=te['duration']+(0 if 'extraHold' in te else 0) if te else None
        if L!=exp: err.append(('timing',sh['id'],L,exp))
        if len(ids)!=len(sh['elements']): err.append(('dup id',sh['id']))
        prev=-1
        for st in sh['subtitles']:
            if not(prev<st['from']<=st['to']<L): err.append(('sub',sh['id']))
            prev=st['to']
        for a in sh['animations']:
            if a['elementId'] not in ids: err.append(('ref',sh['id'],a['elementId']))
            for k in a['keyframes']:
                if not 0<=k['frame']<L: err.append(('kf',sh['id']))
        for e in sh['elements']:
            if e['x']<M or e['y']<M or e['x']+e['w']>1920-M or e['y']+e['h']>1080-M: err.append(('safe',sh['id'],e['id']))
            if e.get('role')!='subtitle' and e['y']+e['h']>880: err.append(('subband',sh['id'],e['id']))
            if e['type']=='image' and e.get('placeholder'):
                if not(e.get('src','').startswith('ep01:') and e.get('reuse') and e.get('note')): err.append(('placeholder',sh['id'],e['id']))
            elif e['type']=='image':
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
# extraHold：句子全局起点 = Knoll 原始起点 + 之前累计 hold（+ 本镜头插入点之前不加）
K=json.load(open('timing.mimo.json'));GS={}
for sc in d['scenes']:
    for sh in sc['shots']: GS[sh['id']]=sh['from']
ksent=[(v['chapterOffsetFrames'],q) for k,v in K.items() for q in v['sentences']]
mine=[]
for sid,v in TM.items():
    for q in v['sentences']: mine.append((sid,GS[sid]*1/30+q['start'],q['text']))
order=list(TM)
for (co,kq),(sid,st,tx) in zip(ksent,mine):
    v=TM[sid]; before=sum(TM[x].get('extraHold',0)+TM[x].get('labelHold',0) for x in order[:order.index(sid)])  # labelHold：2026-10-14 标签 hold（镜头末尾）
    lk=round(30*kq['start'])-v['knollChapterOffsetFrames']  # Knoll 句子在本镜头内的帧（knollChapterOffsetFrames=镜头在章内的偏移）
    inner=v.get('extraHold',0) if 'holdAt' in v and v['holdAt']<v['origDuration'] and lk>=v['holdAt'] else 0
    exp=co/30+kq['start']+(before+inner)/30
    if kq['text']!=tx or abs(st-exp)>0.02: err.append(('sent start',sid,tx[:8],round(st,3),round(exp,3)))
if g!=sum(v['duration'] for v in K.values())+sum(v.get('extraHold',0)+v.get('labelHold',0) for v in TM.values()): err.append('hold total')
raw=open('storyboard.json').read()
for b in BANNED:
    if b in raw: err.append(('banned',b))
for a in ('tag','locker','thief'):
    if f'assets/{a}.svg' not in assets: err.append(('new icon unused',a))
    elif re.search(r'<text',open(f'assets/{a}.svg').read()): err.append(('text inside icon',a))
P=d['meta'].get('poster') or {}
if not P or not any(x['id']==P.get('shotId') and x['from']+P['localFrame']==P['frame'] and P['localFrame']<x['durationInFrames'] for sc in d['scenes'] for x in sc['shots']): err.append('poster')
# 红线：SameSite 不写默认值；保护章四个标签按序出现
pr=[x for sc in d['scenes'] for x in sc['shots'] if x['id']=='protect-2'][0]
labs=" ".join(e.get('label','') for e in pr['elements'])
for w in ("HttpOnly","Secure","SameSite","过期"):
    if w not in labs: err.append(('protect label',w))
print(err or 'ALL OK','frames',g,'shots',sum(len(s['shots']) for s in d['scenes']),'min contrast',round(minc,2),'assets used',len(assets))
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
            if e['type']=='image' and not e.get('placeholder'):
                r=ET.parse(e['asset']).getroot();vb=[float(x) for x in r.get('viewBox').split()];s=min(e['w']/vb[2],e['h']/vb[3])
                for t in r.iter('{http://www.w3.org/2000/svg}text'):
                    v=float(t.get('font-size'))*s;px.append(v)
                    if v<28: perr.append((sh['id'],e['id'],round(v,1)))
        for a in sh['animations']:
            k=a['keyframes']
            if a['elementId'] in tx and a['property']=='opacity' and k[0]['value']==0 and k[-1]['value']==1 and k[-1]['frame']-k[0]['frame']>15: perr.append(('slow fade',sh['id'],a['elementId']))
if perr: print('FONT/FADE:',perr)
print('min on-screen px',round(min(px),1))
if err or perr: sys.exit(1)
