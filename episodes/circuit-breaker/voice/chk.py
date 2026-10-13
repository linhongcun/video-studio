import json,subprocess,numpy as np,sys,re
from faster_whisper import WhisperModel
M={n:WhisperModel(n,device='cpu',compute_type='int8') for n in ('medium','small')}
P='以下是普通话的句子。'
def clip(f,a,d): return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-ss',str(a),'-t',str(d),'-i',f,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True,check=True).stdout,np.float32)
pad=lambda y:np.concatenate([np.zeros(3200,np.float32),y,np.zeros(3200,np.float32)])
T={'熔断':'[熔融荣容][断段短锻]','降级':'[降将奖][级及急集即]','雪崩':'[雪血][崩蹦绷]','调用':'[调掉][用]','半开':'[半伴拌][开]','超时':'[超抄][时十实是式]','出 bug 了吗':'出[故古][障章张]','积分':'[积几机基鸡][分份粉]','库存':'[库酷裤][存村]','支付':'[支知之][付服府]','稍后到账':'[稍少烧][后候][到道][账帐张]'}
for f in sys.argv[1:]:
  for i,s in enumerate(json.load(open(f+'.json'))):
    x=clip(f+'.wav',s['start'],s['dur'])
    r={n:''.join(g.text for g in m.transcribe(x,language='zh',beam_size=5,initial_prompt=P)[0]) for n,m in M.items()}
    print(f,i+1,'|M:',r['medium'],'|S:',r['small'],flush=True)
    terms=[k for k in T if k in s['text']]
    if not terms: continue
    W=[w for g in M['medium'].transcribe(x,language='zh',beam_size=5,initial_prompt=P,word_timestamps=True)[0] for w in g.words]
    txt='';pos=[]
    for k,w in enumerate(W): txt+=w.word;pos+=[k]*len(w.word)
    for k in terms:
      for m in re.finditer(T[k],txt):
        a,b=W[pos[m.start()]].start,W[pos[m.end()-1]].end
        out=[]
        for d in (0.03,0.12):
          y=pad(clip(f+'.wav',s['start']+max(0,a-d),b-a+2*d));out.append('/'.join(''.join(g.text for g in mm.transcribe(y,language='zh',beam_size=5)[0]).strip() for mm in M.values()))
        print(f'  ISO {k} heard={m.group()} [{a:.2f}-{b:.2f}] tight={out[0]} wide={out[1]}',flush=True)
      if not re.search(T[k],txt): print('  ISO',k,'NOTFOUND',flush=True)
