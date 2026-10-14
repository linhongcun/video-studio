# 2026-10-14：Knoll 重配音 ep7（= 本期 cookie-session）给的是已映射的 11 镜头格式（同本目录 timing.json），map_timing / validate 要的是每章一条的 timing.mimo.json。
# 本脚本把镜头格式还原成章格式（去掉 extraHold、句子起点还原到章内），写 timing.mimo.json；之后 map_timing.py 会得到与 Knoll 文件一致的 timing.json。
# 用法：python3 -B unmap_timing.py <镜头格式 timing 路径>
import json,sys
from pathlib import Path
from common_split import ids,SPLIT
H=Path(__file__).resolve().parent;K=json.load(open(sys.argv[1]));out={};co=0
for ch in ids:
    sh=[K[f"{ch}-{x+1}"] for x in range(len(SPLIT[ch]))];S=[]
    for v in sh:
        h=v["duration"]-v.get("origDuration",v["duration"]);at=v.get("holdAt",10**9)  # Knoll 文件里 extraHold 记成 0，但时长已含 hold：按 duration-origDuration 取
        for q in v["sentences"]:
            st=q["start"]-(h/30 if h and round(30*q["start"])>=at+0 and at<v.get("origDuration",v["duration"]) else 0)
            S.append(dict(text=q["text"],start=round(v["knollChapterOffsetFrames"]/30+st,3),dur=q["dur"]))
    dur=sum(v.get("origDuration",v["duration"]) for v in sh);q=S[-1];af=round(30*(q["start"]+q["dur"]))
    out[f"{ch}-1"]=dict(audioSec=round(af/30,3),audioFrames=af,duration=dur,chapterOffsetFrames=co,provisional=False,engine="mimo",voice="冰糖",scale=1,source=f"{sys.argv[1]} 还原",sentences=S);co+=dur
json.dump(out,open(H/"timing.mimo.json","w"),ensure_ascii=False,indent=1);print("unmapped",{k:v["duration"] for k,v in out.items()})
