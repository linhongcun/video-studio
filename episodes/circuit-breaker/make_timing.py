# 暂定 timing.json（新稿 v2「运费险服务」还没配音）：按 Knoll 的 EP.13 旧稿 MiMo 冰糖实测（/workspace/share/ep13-timing.json，只读）校准——
# 句内语速 = 旧稿总字数 / 总句长；句间 0.28 秒（同 Knoll）；每个镜头尾留白 = 旧稿同一镜头 duration - audioFrames（不含分镜停留）。新配音到后：sh run.sh <Knoll 新 timing> 覆盖（旧 timing 会被脚本比对守卫拒绝）
import json,re
from pathlib import Path
from common_split import ids,SPLIT,apply_holds,SCRIPT,tts
HERE=Path(__file__).resolve().parent
cnt=lambda s:len(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',s))
sentences=lambda s:re.findall(r'[^。？]+[。？]',s)
REF='/workspace/share/ep13-timing.json'
K=json.load(open(REF))["shots"]
C=sum(cnt(q['text']) for v in K.values() for q in v['sentences']); D=sum(q['dur'] for v in K.values() for q in v['sentences'])
RATE=C/D; GAP=0.28
N=lambda t:re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]','',t); OLD={N(q['text']):q['dur'] for v in K.values() for q in v['sentences']}  # 和旧稿一字不差的句子直接用实测句长
narr=re.findall(r'- 旁白：(.+)',open(SCRIPT).read()); assert len(narr)==6
out={}; chapF=0; same=0
for ch,s in zip(ids,narr):
    S=sentences(tts(s)); assert len(S)==sum(SPLIT[ch]),(ch,len(S)); i=0; off=0
    for k,m in enumerate(SPLIT[ch]):
        sid=f"{ch}-{k+1}"; t=0; q=[]
        for x in S[i:i+m]:
            d=OLD.get(N(x)) or round(cnt(x)/RATE,3); same+=N(x) in OLD; q.append(dict(text=x.strip(),start=round(t,3),dur=d)); t+=d+GAP
        i+=m; af=round(30*(t-GAP)); old=K[sid]; pad=old["duration"]-old["audioFrames"]
        out[sid]=dict(audioSec=round(af/30,3),audioFrames=af,duration=af+pad,chapterOffsetFrames=off,chapter=ch,provisional=True,engine="estimate",
            basis=f"EP.13 旧稿 MiMo 冰糖实测 {C} 字/{D:.1f} 秒（同句沿用实测句长，新句按句内 {RATE:.3f} 字/秒，句间 {GAP} 秒，镜头尾留白沿用旧稿 {sid} 的 {pad} 帧）",realignWhen="Knoll 新稿 timing 到后必须重对",sentences=q)
        off+=af+pad
apply_holds(out)
json.dump(out,open(HERE/"timing.json","w"),ensure_ascii=False,indent=1)
json.dump(out,open(HERE/"timing.provisional.json","w"),ensure_ascii=False,indent=1)
print('same sentences',same,C,round(D,1),round(RATE,3),len(out),sum(v['duration'] for v in out.values()),{k:v['duration'] for k,v in out.items()})
