# EP.12 熔断降级（脚本第 2 版：一条下单链路 下单→库存→支付→积分）镜头拆分（按句数，句子不拆开）——make_timing / map_timing / gen / validate 共用；章节 id 用 Sorkin 建议的（文章锚点）
ids=["hook","avalanche","breaker","half-open","degrade","recap"]
SPLIT={"hook":[3,2],"avalanche":[2,2],"breaker":[2,2],"half-open":[2,2],"degrade":[2,3],"recap":[2,1]}
SCRIPT='/workspace/sorkin-backup/circuit-breaker/script.md'
# Nolan：第 1 章送 TTS 的旁白把「bug」换成「出故障了吗」，字幕仍是「bug？」原句（只改配音文字）
TTS={"这是出 bug 了吗？":"这是出故障了吗？"}
def tts(s):
    for a,b in TTS.items(): s=s.replace(a,b)
    return s
HOLDS={}  # 第 2 版：v1 停留作废（旧 timing）。等 Knoll 新 timing 到后按「短标签完全淡入后 ≥60 帧」重算；分镜侧加，Knoll timing 不含；已有 extraHold/origDuration/holdIncluded 则不重复加
def apply_holds(out):
    for sid,h in HOLDS.items():
        v=out[sid]
        if "extraHold" in v or "origDuration" in v or v.get("holdIncluded"): continue
        v["origDuration"]=v["duration"]; v["duration"]+=h; v["extraHold"]=h; v["holdAt"]=v["origDuration"]
    return out
