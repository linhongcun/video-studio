# 分镜（含 extraHold）→ remotion/src/timing.json：duration=分镜镜头帧数，音频帧取实测
import json
from pathlib import Path
H=Path(__file__).resolve().parent;T=json.load(open(H/"timing.json"));sb=json.load(open(H/"storyboard.json"));o={}
for sc in sb["scenes"]:
    for sh in sc["shots"]: o[sh["id"]]={**T[sh["id"]],"duration":sh["durationInFrames"],"extraHold":sh["durationInFrames"]-T[sh["id"]]["duration"]}
json.dump(o,open(H/"remotion/src/timing.json","w"),ensure_ascii=False,indent=1);print(sum(v["duration"] for v in o.values()),{k:v["extraHold"] for k,v in o.items() if v["extraHold"]})
