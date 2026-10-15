# EP.20：整轨 narration.wav（/workspace/share/ep20，sha 457d3369…）按分镜停顿插静音 → remotion/public/audio/voice.wav
# 插点 = snowflake-3 hold：原音帧 1989 ≈ ch7-1 起点；落在下一句开口前 0.1 s（句间静音），不切到字
import json,subprocess,numpy as np,wave
SR=48000;NAR='/workspace/share/ep20/narration.wav'
x=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',NAR,'-f','s16le','-ac','1','-ar',str(SR),'-'],capture_output=True,check=True).stdout,np.int16)
tl=json.load(open('/workspace/share/ep20/timeline.json'))['sentences']
# verify sha prefix
import hashlib
sha=hashlib.sha256(open(NAR,'rb').read()).hexdigest()
assert sha.startswith('457d3369'), sha
INS=[(1989,40)]  # original-audio frame → hold frames
pts=[]
for f,n in INS:
  s=min(tl,key=lambda q:abs(q['start']*30-f)); print('nearest',s['id'],s['start']*30,'target',f)
  assert abs(s['start']*30-f)<1.5,(f,s['id'],s['start']*30)
  p=int((s['start']-0.1)*SR)
  peak=int(np.abs(x[max(0,p-480):p+480]).max())
  assert peak<800,(f,s['id'],peak)  # must be in silence
  pts.append((p,n,s['id']))
out=[];prev=0
for p,n,_ in pts:out+=[x[prev:p],np.zeros(n*SR//30,np.int16)];prev=p
out.append(x[prev:]);y=np.concatenate(out)
w=wave.open('remotion/public/audio/voice.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(y.tobytes());w.close()
print('inserted before',[q[2] for q in pts],'voice frames',round(len(y)/SR*30,2),'samples',len(y),'sha',sha[:16])
# align check vs timing (with hold already in snowflake-3)
def mapped(sec):return sec*30+sum(n for p,n,_ in pts if p<=sec*SR)
t=json.load(open('timing.json'));sb=json.load(open('storyboard.json'));bad=0
for sc in sb['scenes']:
  for sh in sc['shots']:
    # compute global from
    pass
# compute shot starts from timing order
acc=0; starts={}
for sc in sb['scenes']:
  for sh in sc['shots']:
    starts[sh['id']]=acc; acc+=t[sh['id']]['duration']
for sc in sb['scenes']:
  for sh in sc['shots']:
    for s in t[sh['id']]['sentences']:
      q=[z for z in tl if z['id']==s['src']][0]
      # sentence global frame in storyboard = shot.from + s.start*30, but after hold insertion in audio
      # For shots after hold, storyboard already includes hold in snowflake-3 duration
      exp=starts[sh['id']]+s['start']*30
      got=mapped(q['start'])
      if abs(exp-got)>2.0:print('ALIGN',sh['id'],s['src'],'exp',exp,'got',got);bad+=1
print('align errors',bad,'totalFrames',acc)
