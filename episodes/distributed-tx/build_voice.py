# EP.21 v4：narration.wav（sha c3f65e55…）按分镜插静音 → remotion/public/audio/voice.wav；插点 = 下一句开口前 0.1 s
import json,subprocess,numpy as np,wave,hashlib
SR=48000;NAR='/workspace/share/ep21/narration.wav'
assert hashlib.sha256(open(NAR,'rb').read()).hexdigest().startswith('c3f65e55')
x=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',NAR,'-f','s16le','-ac','1','-ar',str(SR),'-'],capture_output=True,check=True).stdout,np.int16)
tl=json.load(open('/workspace/share/ep21/timeline.json'))['sentences'];byid={s['id']:s for s in tl}
INS=[('ch4-1',78,'card-1'),('ch9-1',78,'card-2'),('ch14-1',78,'card-3'),('ch19-1',14+78,'saga-wrap 补偿事务 hold 14 + card-4 78'),('ch25-1',10,'msg-wrap 可靠消息 hold 10')]
pts=[]
for sid,n,sh in INS:
  s=byid[sid];prev=tl[tl.index(s)-1]
  p=int(round((s['start']-0.1)*SR));assert prev['end']<s['start']-0.1
  pk=int(np.abs(x[p-480:p+480]).max());assert pk<300,(sh,pk)
  pts.append((p,n,sh,sid));print(sh,'insert',n,'f before',sid,'at %.3fs (原音)'%(p/SR),'prev end',prev['end'],'peak',pk)
out=[];pr=0
for p,n,_,_ in pts:out+=[x[pr:p],np.zeros(n*SR//30,np.int16)];pr=p
out+=[x[pr:],np.zeros(92*SR//30,np.int16)]  # recap-2 末尾 92 帧
y=np.concatenate(out)
w=wave.open('remotion/public/audio/voice.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(y.tobytes());w.close()
print('voice frames',len(y)/SR*30)
json.dump([dict(shot=a[2],before=a[3],orig_sec=a[0]/SR,frames=a[1]) for a in pts]+[dict(shot='recap-2',before='end',frames=92)],open('holds_applied.json','w'),ensure_ascii=False,indent=1)
