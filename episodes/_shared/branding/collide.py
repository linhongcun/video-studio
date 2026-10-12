import json,re
def tw(t,fs): return sum(fs if re.match(r'[\u3000-\uffff]',c) else 0.6*fs for c in t)  # 居中文字按实际字宽收窄（真实碰撞）
WM=(1700,80,1840,130)  # 水印占位框（含 ~20px 余量）
eps={"EP.01":"/workspace/video-studio/episodes/http-request/storyboard.json","EP.02":"../https/storyboard.json","EP.03":"../dns/storyboard.json","EP.04":"../cookie-session/storyboard.json"}
def walk(o):
    if isinstance(o,dict):
        if 'elements' in o and 'id' in o: yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o,list):
        for v in o: yield from walk(v)
for ep,p in eps.items():
    d=json.load(open(p));n=0;hits=[]
    for sh in walk(d):
        n+=1
        for e in sh['elements']:
            if not all(k in e for k in 'xywh'): continue
            x,y,w,h=e['x'],e['y'],e['w'],e['h']
            if e.get('type')=='text' and e.get('text') and e.get('align')=='center':
                a=min(w,tw(e['text'],e.get('fontSize',40)));x+= (w-a)/2;w=a
            if x<WM[2] and x+w>WM[0] and y<WM[3] and y+h>WM[1]: hits.append((sh['id'],e['id'],e.get('type'),x,y,w,h,e.get('text') or e.get('label')))
    print(ep,'shots',n,'hits',len(hits));[print('  ',h) for h in hits]
