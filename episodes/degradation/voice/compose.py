import json,sys,numpy as np,soundfile as sf
ch,picks=sys.argv[1],sys.argv[2].split(',')  # picks per sentence tag
out=[];segs=[];t=0;sr=48000
for i,tag in enumerate(picks):
    S=json.load(open(f'{ch}-{tag}.json'));x,sr=sf.read(f'{ch}-{tag}.wav',dtype='float32');s=S[i]
    c=x[round(s['start']*sr):round(s['start']*sr)+round(s['dur']*sr)]
    segs.append(dict(s,start=round(t,3),dur=round(len(c)/sr,3),take=tag));t+=len(c)/sr+0.28
    out+=[c,np.zeros(round(0.28*sr),np.float32)]
sf.write(f'{ch}-final.wav',np.concatenate(out[:-1]),sr);json.dump(segs,open(f'{ch}-final.json','w'),ensure_ascii=False,indent=1)
print(ch,round(t-0.28,3))
