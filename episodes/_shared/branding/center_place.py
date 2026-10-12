# 中央淡水印逐镜头选位：避开所有镜头元素框（含 24px 余量）、字幕带与右上水印框；找不到就隐藏
import json,re
FS=120; BW,BH=380,150; PAD=24; YMIN,YMAX=140,860   # 水印框 380×150（IT小村 120px 粗体实测约 360×130）
TR=(1700,80,1840,130)
eps={"EP.01":"/workspace/video-studio/episodes/http-request/storyboard.json","EP.02":"../https/storyboard.json","EP.03":"../dns/storyboard.json","EP.04":"../cookie-session/storyboard.json"}
def tw(t,fs): return sum(fs if re.match(r'[\u3000-\uffff]',c) else 0.6*fs for c in t)
def box(e):
    x,y,w,h=e['x'],e['y'],e['w'],e['h']
    if e.get('type')=='text' and e.get('text') and e.get('align')=='center':
        a=min(w,tw(e['text'],e.get('fontSize',40))); x=x+(w-a)/2; w=a
    return (x-PAD,y-PAD,x+w+PAD,y+h+PAD)
def inter(a,b): return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
def place(sh):
    B=[box(e) for e in sh['elements'] if e.get('role')!='subtitle' and all(k in e for k in 'xywh')]+[TR]
    cands=[(cx,cy) for cx in range(80+BW//2,1840-BW//2+1,20) for cy in range(YMIN+BH//2,YMAX-BH//2+1,20)]
    cands.sort(key=lambda c:(c[0]-960)**2+(c[1]-480)**2)
    for cx,cy in cands:
        r=(cx-BW/2,cy-BH/2,cx+BW/2,cy+BH/2)
        if not any(inter(r,b) for b in B): return dict(x=cx,y=cy)
    return None
if __name__=="__main__":
    out={};tot=0;none=0
    for ep,p in eps.items():
        d=json.load(open(p));out[ep]={}
        for sc in d['scenes']:
            for sh in sc['shots']:
                r=place(sh);out[ep][sh['id']]=r;tot+=1;none+=r is None
        n=sum(v is None for v in out[ep].values());print(ep,'shots',len(out[ep]),'无空位(隐藏)',n,[k for k,v in out[ep].items() if v is None])
    print('合计',tot,'隐藏',none)
    json.dump(out,open('center_placement.json','w'),ensure_ascii=False,indent=1)
