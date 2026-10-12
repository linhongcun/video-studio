import json,re,os
d=json.load(open('storyboard.json'));src=open('/workspace/sorkin-backup/https/script.md').read()
narr=re.findall(r'- 旁白：(.+)',src);err=[];g=0;M=80
BANNED=["面试","八股","校招","满分","求职","面试官","考点","背诵","高频题","公钥加密会话密钥","用公钥加密","SSL 是","PUBLIC","PRIVATE"]
ALLOW={"CA","TLS","HTTP","HTTPS","ClientHello","ServerHello"}
def lum(h):
    c=[int(h[i:i+2],16)/255 for i in (1,3,5)];c=[x/12.92 if x<=0.03928 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
def cr(a,b): A,B=sorted([lum(a),lum(b)],reverse=True); return (A+0.05)/(B+0.05)
BG=d['meta']['palette']['bg'];PANEL=d['meta']['palette']['panel'];minc=99;assets=set()
assert len(d['scenes'])==8
for i,s in enumerate(d['scenes']):
    if s['from']!=g: err.append(('scene gap',s['id']))
    f=g
    for sh in s['shots']:
        if sh['from']!=f: err.append(('shot gap',sh['id']))
        L=sh['durationInFrames'];ids={e['id'] for e in sh['elements']}
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
            if e['type']=='image':
                assets.add(e['asset'])
                if not os.path.isfile(e['asset']): err.append(('asset missing',e['asset']))
            for t in [e.get('text'),e.get('label')]:
                if e.get('role')=='subtitle' or not t: continue
                for w in re.findall(r'[A-Za-z][A-Za-z0-9\-]*',t):
                    if w not in ALLOW: err.append(('english',sh['id'],e['id'],w))
            if e['type']=='text' and e['color']:
                c=cr(e['color'],BG);minc=min(minc,c)
                if c<4.5: err.append(('contrast',sh['id'],e['id'],round(c,2)))
            if e['type']=='rect' and e.get('label'):
                c=cr(d['meta']['palette']['text'],e['color']);minc=min(minc,c)
                if c<4.5: err.append(('contrast',sh['id'],e['id'],round(c,2)))
        f+=L
    if f-g!=s['durationInFrames']: err.append(('scene sum',s['id']))
    if "".join(x['narration'] for x in s['shots']).replace(' ','')!=narr[i].replace(' ',''): err.append(('narr',s['id']))
    g+=s['durationInFrames']
if g!=d['meta']['durationInFrames']: err.append('total')
raw=open('storyboard.json').read()
for b in BANNED:
    if b in raw: err.append(('banned',b))
for k in range(1,7):
    if not os.path.isfile(f'assets/ecdhe-step{k}.svg'): err.append(('ecdhe step file missing',k))
for a in ('assets/ecdhe-step4.svg','assets/ecdhe-combine.svg','assets/ecdhe-step6.svg'):
    if a not in assets: err.append(('ecdhe state unused',a))
for ch in ('plaintext','recap'):
    sc=[s for s in d['scenes'] if s['chapterId']==ch][0]
    if 'assets/postcard.svg' not in json.dumps(sc): err.append(('postcard missing',ch))
print(err or 'ALL OK', 'frames',g,'shots',sum(len(s['shots']) for s in d['scenes']),'min contrast',round(minc,2),'assets used',len(assets))
