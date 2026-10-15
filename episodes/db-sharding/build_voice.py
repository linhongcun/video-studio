# EP.19：整轨 narration.wav（/workspace/share/ep19，sha b135a8f0…）按分镜停顿插静音 → remotion/public/audio/voice.wav（单条整轨，第 0 帧对齐）
# 插点 = 停顿后那一章首句起点前 0.1 s（落在句间静音里，不切到字）
import json,subprocess,numpy as np,wave
SR=48000;NAR='/workspace/share/ep19/narration.wav'
x=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',NAR,'-f','s16le','-'],capture_output=True).stdout,np.int16)
tl=json.load(open('/workspace/share/ep19/timeline.json'))['sentences']
INS=[(1796,46),(2117,3),(2417,44),(2679,36),(3110,37)]
pts=[]
for f,n in INS:
  s=min(tl,key=lambda q:abs(q['start']*30-f));assert abs(s['start']*30-f)<1.5,(f,s['id'])
  p=int((s['start']-0.1)*SR);assert np.abs(x[p-480:p+480]).max()<300,(f,s['id'],np.abs(x[p-480:p+480]).max());pts.append((p,n,s['id']))
out=[];prev=0
for p,n,_ in pts:out+=[x[prev:p],np.zeros(n*SR//30,np.int16)];prev=p
out.append(x[prev:]);y=np.concatenate(out)
w=wave.open('remotion/public/audio/voice.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(y.tobytes());w.close()
print('inserted before',[q[2] for q in pts],'voice frames',round(len(y)/SR*30,2))
def mapped(sec):return sec*30+sum(n for p,n,_ in pts if p<=sec*SR)
t=json.load(open('timing.json'));sb=json.load(open('storyboard.json'));bad=0
for sc in sb['scenes']:
  for sh in sc['shots']:
    for s in t[sh['id']]['sentences']:
      q=[z for z in tl if z['id']==s['src']][0];exp=sh['from']+s['start']*30;got=mapped(q['start'])
      if abs(exp-got)>1.5:print('ALIGN',sh['id'],s['src'],exp,got);bad+=1
      if mapped(q['end'])>sh['from']+sh['durationInFrames']:print('OVERRUN',sh['id']);bad+=1
print('align errors',bad)
