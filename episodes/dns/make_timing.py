# 暂定 timing.json（无配音）：按第二期 MiMo「冰糖」实测校准；配音出来后由 Knoll 的实测 timing.json 覆盖
import json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
cnt=lambda s:len(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',s))
ref=json.load(open('/workspace/miyazaki-backup/https/timing.json'))
C=sum(cnt(s['text']) for v in ref.values() for s in v['sentences']);D=sum(s['dur'] for v in ref.values() for s in v['sentences'])
RATE=C/D; GAP=0.28; PAD=30   # 第二期：句内 4.52 字/秒，句间 0.28 秒，每镜头音频外留 30 帧
src=open('/workspace/sorkin-backup/dns/script.md').read();narr=re.findall(r'- 旁白：(.+)',src)
ids=["phonebook","cache","resolver","iterative","ttl","recap"]
SPLIT={0:[2,2],1:[2,1],2:[2,2],3:[4,1],4:[1,1,1],5:[1,1]}
sentences=lambda s:re.findall(r'[^。？]+[。？]',s)
out={}
for si,s in enumerate(narr):
    S=sentences(s);i=0
    for k,n in enumerate(SPLIT[si]):
        q=[];t=0
        for x in S[i:i+n]:
            d=round(cnt(x)/RATE,3);q.append(dict(text=x.strip(),start=round(t,3),dur=d));t+=d+GAP
        i+=n;a=round(t-GAP,3);af=round(a*30)
        out[f"{ids[si]}-{k+1}"]=dict(audioSec=a,audioFrames=af,duration=af+PAD,provisional=True,engine="estimate",basis=f"EP.02 MiMo 冰糖 实测 {C} 字/{D:.1f} 秒 = {RATE:.3f} 字/秒（句内），句间 {GAP} 秒，镜头留白 {PAD} 帧",gap=GAP,sentences=q)
    assert i==len(S),si
json.dump(out,open(HERE/"timing.json","w"),ensure_ascii=False,indent=1)
print(len(out),sum(v['duration'] for v in out.values()))
