# EP.12 熔断降级 镜头拆分（按句数，句子不拆开）——make_timing / map_timing / gen / validate 共用；章节 id 用 Sorkin 建议的（文章锚点）
ids=["hook","avalanche","breaker","half-open","degrade","recap"]
SPLIT={"hook":[3,2],"avalanche":[2,2],"breaker":[2,2],"half-open":[2,2],"degrade":[2,2],"recap":[2,1]}
SCRIPT='/workspace/sorkin-backup/circuit-breaker/script.md'
# Nolan：第 1 章送 TTS 的旁白把「bug」换成「出故障了吗」，字幕仍是「bug？」原句（只改配音文字）
TTS={"这是出 bug 了吗？":"这是出故障了吗？"}
def tts(s):
    for a,b in TTS.items(): s=s.replace(a,b)
    return s
HOLDS={"hook-1":40,"recap-1":34,"avalanche-2":47,"breaker-2":49,"degrade-2":37}  # 术语「雪崩」「熔断」「降级」完全淡入后 ≥60 帧（+47/+49/+37）； 分镜侧停留（Knoll timing 不含）：「bug？」「四重防线」完全淡入后 60 帧（+40/+34）；已有 extraHold/origDuration/holdIncluded 则不重复加
def apply_holds(out):
    for sid,h in HOLDS.items():
        v=out[sid]
        if "extraHold" in v or "origDuration" in v or v.get("holdIncluded"): continue
        v["origDuration"]=v["duration"]; v["duration"]+=h; v["extraHold"]=h; v["holdAt"]=v["origDuration"]
    return out
