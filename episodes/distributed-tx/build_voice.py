# EP.21：narration.wav（sha 8d663d45…）按分镜停顿插静音 → remotion/public/audio/voice.wav；插点 = 下一句开口前 0.1 s
import json,subprocess,numpy as np,wave,hashlib
SR=48000;NAR='/workspace/share/ep21/narration.wav'
assert hashlib.sha256(open(NAR,'rb').read()).hexdigest().startswith('8d663d45')
x=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',NAR,'-f','s16le','-ac','1','-ar',str(SR),'-'],capture_output=True,check=True).stdout,np.int16)
tl=json.load(open('/workspace/share/ep21/timeline.json'))['sentences']
INS=[(66.63,36,'commit-2'),(94.37,50,'message-3'),(101.47,49,'eventual-1')]
pts=[]
for t,n,sh in INS:
  s=min(tl,key=lambda q:abs(q['start']-t));assert abs(s['start']-t)<0.02,(t,s['id'])
  prev=[q for q in tl if q['end']<=s['start']][-1]
  p=int((s['start']-0.1)*SR);assert prev['end']<s['start']-0.1
  pk=int(np.abs(x[p-480:p+480]).max());assert pk<300,(sh,pk)
  pts.append((p,n,sh,s['id']));print(sh,'insert',n,'f before',s['id'],'at %.3fs (原音)'%(p/SR),'prev end',prev['end'],'peak',pk)
out=[];pr=0
for p,n,_,_ in pts:out+=[x[pr:p],np.zeros(n*SR//30,np.int16)];pr=p
out+=[x[pr:],np.zeros(1*SR//30,np.int16)]  # recap-1 末尾 1 帧
y=np.concatenate(out)
w=wave.open('remotion/public/audio/voice.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(y.tobytes());w.close()
print('voice frames',len(y)/SR*30)
json.dump([dict(shot=a[2],before=a[3],orig_sec=a[0]/SR,frames=a[1]) for a in pts],open('holds_applied.json','w'),ensure_ascii=False,indent=1)
