# EP.19 分库分表（脚本 v0.24.0 定稿）镜头拆分：按句数，句子不拆开。章节 id = script.md「## n. id｜」（cross-query / cross-tx 记作 xquery / xtx，镜头 id 不带连字符）
import re
ids=["hook","bridge","station","table","database","key","strategy","vertical","xquery","xtx","id","reshard","recap"]
ALIAS={"cross-query":"xquery","cross-tx":"xtx"}
SPLIT={"hook":[1,1],"bridge":[1,1],"station":[1,1],"table":[1,1],"database":[1,1,1],"key":[1,2],"strategy":[2],"vertical":[2],
       "xquery":[1,1],"xtx":[1,2],"id":[1],"reshard":[1,1],"recap":[2]}
SCRIPT='/workspace/sorkin-backup/db-sharding/script.md'
TTS={}   # pronunciation.md：多音字换字只在 Knoll 送 TTS 的文本里做；稿子 / 字幕保持原字
def tts(s):
    for a,b in TTS.items(): s=s.replace(a,b)
    return s
def subtext(s): return s
def narration():   # 本期脚本格式：第一个 --- 与「## 待确认」前的 --- 之间，每章「## n. id｜标题」下的正文段落
    t=open(SCRIPT).read().split('---',1)[1].split('\n---')[0];out={}
    for m in re.finditer(r'^## \d+\. ([\w-]+)｜.*?\n(.*?)(?=^## |\Z)',t,re.S|re.M): out[ALIAS.get(m.group(1),m.group(1))]=''.join(x.strip() for x in m.group(2).splitlines())
    assert list(out)==ids,list(out); return [out[c] for c in ids]
SENT=lambda s:re.findall(r'[^。？]+[。？]',s)
HOLDS={}
def _label_holds():
    import json as _j,os as _o
    p=_o.path.join(_o.path.dirname(_o.path.abspath(__file__)),'label_holds.json')
    return _j.load(open(p)) if _o.path.isfile(p) else {}
def apply_holds(out):
    for sid,lh in _label_holds().items():
        v=out[sid]
        if v.get("holdIncluded") or not lh: continue
        v.setdefault("origDuration",v["duration"]); v.setdefault("holdAt",v["origDuration"])
        v["duration"]=v["origDuration"]+lh; v["extraHold"]=lh; v["labelHold"]=lh
    return out
if __name__=='__main__':
    for c,s in zip(ids,narration()):
        S=SENT(s); assert len(S)==sum(SPLIT[c]),(c,len(S)); print(c,SPLIT[c],len(S))
