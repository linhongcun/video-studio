# EP.22：narration.wav（sha 2b543b5f…）按分镜插章节卡静音 → remotion/public/audio/voice.wav；插点 = 下一句开口前 0.1 s；末尾补片尾停留 TAIL 帧
import json,subprocess,numpy as np,wave,hashlib,sys
SR=48000;NAR='/workspace/share/ep22/narration.wav';TAIL=int(sys.argv[1]) if len(sys.argv)>1 else 0
assert hashlib.sha256(open(NAR,'rb').read()).hexdigest().startswith('2b543b5f')
x=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',NAR,'-f','s16le','-ac','1','-ar',str(SR),'-'],capture_output=True,check=True).stdout,np.int16)
tl=json.load(open('/workspace/share/ep22/timeline.json'))['sentences'];byid={s['id']:s for s in tl}
sb=json.load(open('storyboard.json'));cards=[sh for sc in sb['scenes'] for sh in sc['shots'] if sh.get('chapterCard')]
pts=[]
for c in cards:
  sid=c['chapterCard']['insertBeforeSentence'];n=c['chapterCard']['holdFrames'];s=byid[sid];prev=tl[tl.index(s)-1]
  p=int(round((s['start']-0.1)*SR));assert prev['end']<s['start']-0.1
  pk=int(np.abs(x[p-480:p+480]).max());assert pk<300,(c['id'],pk)
  pts.append((p,n,c['id'],sid));print(c['id'],'insert',n,'f before',sid,'at %.3fs'%(p/SR),'peak',pk)
out=[];pr=0
for p,n,_,_ in pts:out+=[x[pr:p],np.zeros(n*SR//30,np.int16)];pr=p
out+=[x[pr:],np.zeros(TAIL*SR//30,np.int16)]
y=np.concatenate(out)
w=wave.open('remotion/public/audio/voice.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(y.tobytes());w.close()
print('voice frames',len(y)/SR*30)
json.dump([dict(shot=a[2],before=a[3],orig_sec=a[0]/SR,frames=a[1]) for a in pts]+[dict(shot='ending-2',before='end',frames=TAIL)],open('holds_applied.json','w'),ensure_ascii=False,indent=1)
