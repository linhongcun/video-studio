# EP.13 熔断（v0.18.0，扛住高峰 05）镜头拆分（按句数，句子不拆开）——make_timing / map_timing / gen / validate 共用；章节 id = 文章锚点
ids=["hook","cascade","breaker","states","half-open","recap"]
SPLIT={"hook":[2,2],"cascade":[2,2],"breaker":[2,1,3],"states":[3],"half-open":[2,1],"recap":[1,2]}
SCRIPT='/workspace/sorkin-backup/circuit-breaker/script.md'
# 第十三期：读音表无需改送 TTS 文字（一百次 / 一半 / 三十秒口播即中文）；备用替换见 pronunciation.md
TTS={}
def tts(s):
    for a,b in TTS.items(): s=s.replace(a,b)
    return s
HOLDS={"hook-2":12,"cascade-2":19,"half-open-1":19}  # 第十三期：估算 timing 下按「术语/短标签完全淡入（opacity 与 scale 动画结束）后到镜头末 ≥60 帧」按需填；镜头尾单侧停留，Knoll timing 不含；已有 extraHold/origDuration/holdIncluded 则不重复加
def apply_holds(out):
    for sid,h in HOLDS.items():
        v=out[sid]
        if "extraHold" in v or "origDuration" in v or v.get("holdIncluded"): continue
        v["origDuration"]=v["duration"]; v["duration"]+=h; v["extraHold"]=h; v["holdAt"]=v["origDuration"]
    return out
