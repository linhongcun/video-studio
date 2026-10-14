# 用法：python chk2.py <medium|small> take...  （一个进程只加载一个模型；medium、small 依次跑，不并行）
import json,subprocess,numpy as np,sys,re
from faster_whisper import WhisperModel
name=sys.argv[1];m=WhisperModel(name,device='cpu',compute_type='int8',cpu_threads=4)
P='以下是普通话的句子。'
def clip(f,a,d): return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-ss',str(max(0,a)),'-t',str(d),'-i',f,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True,check=True).stdout,np.float32)
pad=lambda y:np.concatenate([np.zeros(8000,np.float32),y,np.zeros(8000,np.float32)])
def tr(x,**k): return ''.join(g.text for g in m.transcribe(pad(x),language='zh',beam_size=5,initial_prompt=P,condition_on_previous_text=False,**k)[0]).strip()
T={'运费险':'[运云][费飞废][险线现显]','故障':'[故固][障章张]','雪崩':'[雪血][崩蹦绷]','级联故障':'[级及急集即吉][联连廉莲][故固][障章张]','超时':'[超抄][时十实是]','熔断':'[熔融容荣溶红][断段锻]','半开':'[半伴办搬][开凯]','降级':'[降将奖][级及急集即]'}
KEY={'合闸':'合上闸'}
for f in sys.argv[2:]:
  for i,s in enumerate(json.load(open(f+'.json'))):
    x=clip(f+'.wav',s['start'],s['dur']);txt=tr(x)
    print(name,f,i+1,'|',txt,flush=True)
    for k in T:
      if KEY.get(k,k) not in s['text']: continue
      W=[w for g in m.transcribe(pad(x),language='zh',beam_size=5,initial_prompt=P,word_timestamps=True,condition_on_previous_text=False)[0] for w in g.words]
      t2='';pos=[]
      for j,w in enumerate(W): t2+=w.word;pos+=[j]*len(w.word)
      ms=list(re.finditer(T[k],t2))
      if not ms: print('  ISO',k,'NOTFOUND',flush=True)
      for mm in ms:
        a,b=W[pos[mm.start()]].start-0.5,W[pos[mm.end()-1]].end-0.5
        out=[''.join(g.text for g in m.transcribe(pad(clip(f+'.wav',s['start']+a-d,b-a+2*d)),language='zh',beam_size=5)[0]).strip() for d in (0.03,0.12)]
        print(f'  ISO {k} heard={mm.group()} tight={out[0]} wide={out[1]}',flush=True)
