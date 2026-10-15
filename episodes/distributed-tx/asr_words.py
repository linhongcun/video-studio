# Knoll words.json（narration.wav 整轨秒）→ asr_words.json（成片秒，给 _audit/asrcue.py 用）。map_timing 之后跑。EP.20 distributed-tx
# 成片时间 = 镜头全局起点 + 句子在镜头内的 start；同一句的词按「句子整轨起点」平移。
# 宁晚勿早（Knoll：句首字可能早 ~0.1 s）：词开始不早于句子起点，再整体加 BIAS 秒
import json,sys
from pathlib import Path
H=Path(__file__).resolve().parent;BIAS=0.05   # EP.16：medium 词级 + 已按句子起点钳位，偏置 0.05 s 即可保证 0..+4
import os
_w=sys.argv[1] if len(sys.argv)>1 else '/workspace/share/ep21/words.json'
if os.environ.get('FORCE_ESTIMATE') or any(v.get('provisional') for v in json.load(open(H/'timing.json')).values()) or not os.path.isfile(_w) or not any(v.get('src') for v in json.load(open(H/'timing.json')).values() for v in v['sentences']):
    json.dump({},open(H/'asr_words.json','w'));print('asr_words: 无 words.json 或暂定 timing → 空');sys.exit(0)
W=json.load(open(_w))
# 2026-10-15 Knoll 新格式：[{id,asr,words:[{w,start,end}]}]（整轨秒）→ 拍平成旧格式 [{sentence,word,start}]
if W and isinstance(W[0],dict) and 'words' in W[0]: W=[dict(sentence=q['id'],word=x['w'],start=x['start']) for q in W for x in q['words']]
K=json.load(open(sys.argv[2] if len(sys.argv)>2 else '/workspace/share/ep21/timeline.json'));NS={q['id']:q['start'] for q in K['sentences']}
TM=json.load(open(H/'timing.json'));g=0;VS={}
for sid,v in TM.items():
    for q in v['sentences']: VS[q['src']]=g/30+q['start']
    g+=v['duration']
out={}
# 改名待重配（主从延迟）：旧录音里的「复制」两字按位置换成「主从」，时间沿用旧录音（只为 cue 对齐；重配到后自然消失）
_R={};_ws={}
for i,w in enumerate(W): _ws.setdefault(w['sentence'],[]).append(i)
for s_,ix in _ws.items():
    txt=''.join(W[i]['word'] for i in ix)
    for a,b in _R.items():
        j=txt.find(a)
        while j>=0:
            pos=0
            for i in ix:
                L_=len(W[i]['word'])
                if pos<j+len(a) and pos+L_>j: W[i]=dict(W[i],word=''.join(b[k-j] if j<=k<j+len(a) else W[i]['word'][k-pos] for k in range(pos,pos+L_)))
                pos+=L_
            txt=''.join(W[i]['word'] for i in ix);j=txt.find(a)
for w in W:
    s=w['sentence'];o=out.setdefault(s,dict(hyp='',words=[]))
    t=max(w['start'],NS[s])-NS[s]+VS[s]+BIAS
    o['hyp']+=w['word'];o['words'].append([w['word'],round(t,3)])
# 2026-10-15：Knoll 逐句 ASR 有乱码句（如 v2 ch1-2「划划…」）→ 与脚本字符重合率 <0.7 的句子丢掉，回退到按字数插值
import re as _re
TX={q['id']:q['text'] for q in K['sentences']};DROP=[]
for k in list(out):
    h=_re.sub(r'[^\u4e00-\u9fff]','',out[k]['hyp']);t=_re.sub(r'[^\u4e00-\u9fff]','',TX.get(k,''))
    r=sum(1 for c in h if c in t)/max(1,len(h))
    cv=sum(1 for c in t if c in h)/max(1,len(t))   # 脚本字被覆盖的比例（漏掉半句的也算乱码）
    if r<0.7 or cv<0.7 or len(h)>1.3*max(1,len(t)): DROP.append((k,round(r,2)));del out[k]
if DROP: print('asr_words 丢弃乱码句',DROP)
out['_bias']=BIAS
json.dump(out,open(H/'asr_words.json','w'),ensure_ascii=False,indent=1)
print('asr_words',len(W),'bias',BIAS)
