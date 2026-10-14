import json,subprocess,numpy as np,sys,re
from faster_whisper import WhisperModel
M={'medium':WhisperModel('medium',device='cpu',compute_type='int8',cpu_threads=8)}
M['small']=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=8)
P='以下是普通话的句子。'
def clip(f,a,d): return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-ss',str(a),'-t',str(d),'-i',f,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True,check=True).stdout,np.float32)
pad=lambda y:np.concatenate([np.zeros(3200,np.float32),y,np.zeros(3200,np.float32)])
T={'熔断':'[熔融容荣溶][断段锻]','雪崩':'[雪血][崩蹦绷]','级联故障':'[级及急集即][联连廉][故固][障章张]','关闭':'[关官][闭必毕]','打开':'打[开凯]','半开':'[半伴办][开凯]','超时':'[超抄][时十实是]','跳闸':'[跳条][闸扎炸札铡]','合闸':'[合和何][闸扎炸札铡]','库存服务':'[库酷裤][存村][服福][务物]','限流':'[限线现][流留]','降级':'[降将奖][级及急集即]','系统繁忙':'[系细][统通][繁凡烦][忙盲]'}
for f in sys.argv[1:]:
  for i,s in enumerate(json.load(open(f+'.json'))):
    x=clip(f+'.wav',s['start'],s['dur'])
    r={n:''.join(g.text for g in m.transcribe(x,language='zh',beam_size=5,initial_prompt=P)[0]) for n,m in M.items()}
    print(f,i+1,'|M:',r['medium'],'|S:',r['small'],flush=True)
    terms=[k for k in T if k in s['text'] or (k=='合闸' and '合上闸' in s['text'])]
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
