# EP.21 暂定时间轴（配音未录）：按约 4.3 字/秒估每句时长（汉字 1；MySQL≈5、Redis≈5、ID≈2；八点四=3）；
# 句间 0.28 s、章间 0.6 s（同 Knoll 拼接规则）→ 写 timeline.estimate.json（Knoll timeline.json 同格式），再交给 map_timing.py
# （镜头边界按时间轴：章 = 本章首句起 → 下一章首句起；只在全片结尾补 60 帧）。Knoll 的 timeline.json 到后 realign.sh 自动改用它。
import json,re,subprocess,sys
from pathlib import Path
from common_split import ids,narration,SENT
H=Path(__file__).resolve().parent;RATE=4.3;GAP=0.28;CGAP=0.6
def cnt(s):
    s=s.replace("MySQL","麦麦麦麦麦").replace("Redis","雷雷雷雷雷").replace("ID","艾地").replace("八点四","八点四")
    return len(re.findall(r'[\u4e00-\u9fff]',s))+1.5*len(re.findall(r'[A-Za-z0-9]+',s))
t=0;S=[]
for ci,s in enumerate(narration()):
    for j,x in enumerate(SENT(s)):
        d=round(cnt(x)/RATE,3);S.append(dict(id=f"ch{ci+1}-{j+1}",chapter=ci+1,text=x.strip(),tts_text=x.strip(),start=round(t,3),end=round(t+d,3)));t+=d+GAP
    t+=CGAP-GAP
json.dump(dict(estimate=True,basis=f"字数估算 {RATE} 字/秒，句间 {GAP}s，章间 {CGAP}s",duration=S[-1]["end"],sentences=S),open(H/"timeline.estimate.json","w"),ensure_ascii=False,indent=1)
print('estimate',len(S),'sentences',S[-1]['end'],'s')
subprocess.run([sys.executable,'-B',str(H/'map_timing.py'),str(H/'timeline.estimate.json')],check=True)
