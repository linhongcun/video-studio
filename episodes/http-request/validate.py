import json,re
d=json.load(open('storyboard.json'));src=open('/workspace/sorkin-backup/http-request-v2/script.md').read()
narr=re.findall(r'- 旁白：(.+)',src);err=[];g=0;M=80
anchors=re.findall(r'\{#(\w+)\}',open('/workspace/sorkin-backup/http-request-v2/article.mdx').read())
assert len(d['scenes'])==10
for i,s in enumerate(d['scenes']):
    if s['from']!=g: err.append(('scene gap',s['id']))
    if i not in(0,9) and s['chapterId'] not in anchors: err.append(('anchor',s['chapterId']))
    f=g
    for sh in s['shots']:
        if sh['from']!=f: err.append(('shot gap',sh['id']))
        L=sh['durationInFrames'];ids={e['id'] for e in sh['elements']}
        for st in sh['subtitles']:
            if not(0<=st['from']<=st['to']<L): err.append(('sub',sh['id']))
        for a in sh['animations']:
            if a['elementId'] not in ids: err.append(('ref',sh['id'],a['elementId']))
            for k in a['keyframes']:
                if not 0<=k['frame']<L: err.append(('kf',sh['id']))
        for e in sh['elements']:
            if e['x']<M or e['y']<M or e['x']+e['w']>1920-M or e['y']+e['h']>1080-M: err.append(('safe',sh['id'],e['id']))
            if e.get('role')!='subtitle' and e['y']+e['h']>880: err.append(('subband',sh['id'],e['id']))
        f+=L
    if f-g!=s['durationInFrames']: err.append(('scene sum',s['id']))
    if "".join(x['narration'] for x in s['shots'])!=narr[i]: err.append(('narr',s['id']))
    g+=s['durationInFrames']
if g!=d['meta']['durationInFrames']: err.append('total')
if '93.184.215.14' in open('storyboard.json').read(): err.append('ip')
print(err or 'ALL OK', g, sum(len(s['shots']) for s in d['scenes']))
