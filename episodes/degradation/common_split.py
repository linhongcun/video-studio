# EP.12 降级（脚本第 4 版：只讲降级；到手价计算 → 商品价格 / 优惠券 / 红包；红包卡住）镜头拆分（按句数，句子不拆开）——make_timing / map_timing / gen / validate 共用；章节 id 用 Sorkin 建议的（文章锚点）
ids=["hook","problem","auto-degrade","active-degrade"]
SPLIT={"hook":[3,2],"problem":[3,2],"auto-degrade":[3,3],"active-degrade":[2,2,2]}
SCRIPT='/workspace/sorkin-backup/degradation/script.md'
# Nolan：第 1 章送 TTS 的旁白把「bug」换成「出故障了吗」，字幕仍是「bug？」原句（只改配音文字）
TTS={"这是出 bug 了吗？":"这是出故障了吗？"}
def tts(s):
    for a,b in TTS.items(): s=s.replace(a,b)
    return s
HOLDS={"hook-1":18,"hook-2":7,"problem-2":5,"auto-degrade-2":26,"active-degrade-2":22}  # 第 4 版（只讲降级）：估算 timing 下按「术语/短标签完全淡入（opacity 与 scale 动画结束）后到镜头末 ≥60 帧」按需填；镜头尾单侧停留，Knoll timing 不含；已有 extraHold/origDuration/holdIncluded 则不重复加
def _label_holds():  # 2026-10-14 Nolan：术语标签不得早于旁白，不够 60 帧时由 _audit/labelfix.py 算出最短 hold 写进 label_holds.json（镜头末尾静音，Knoll 同步插静音）
    import json as _j,os as _o
    p=_o.path.join(_o.path.dirname(_o.path.abspath(__file__)),'label_holds.json')
    return _j.load(open(p)) if _o.path.isfile(p) else {}
def apply_holds(out):
    LH=_label_holds()
    for sid in list(HOLDS)+[x for x in LH if x not in HOLDS]:
        v=out[sid]
        if v.get("holdIncluded"): continue
        h=HOLDS.get(sid,0); h0=v.get("extraHold",0) if "origDuration" in v else 0   # Knoll timing 已含旧 hold 时只补差额
        lh=LH.get(sid,0); add=max(0,h-h0)+lh
        if not add: continue
        v.setdefault("origDuration",v["duration"]); v.setdefault("holdAt",v["origDuration"])
        v["duration"]+=add; v["extraHold"]=max(h,h0)+lh; v["labelHold"]=lh
    return out
