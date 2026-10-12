# EP8：章节 MiMo timing → 12 镜头（Miyazaki 句数），切镜头音频，无 extraHold
import json,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;A=H/"remotion/public/audio";K=json.load(open(H/"timing.mimo.json"))
MAP=[("hook","hook",[2,2]),("warehouse","no-cache",[2,2]),("prep","hit-miss",[2,2]),("ttl","ttl",[1,2]),("invalidate","invalidate",[2,2]),("recap","recap",[1,2])]
out={};g=0
for ch,sh,n in MAP:
    k=K[f"{ch}-1"];S=k["sentences"];assert len(S)==sum(n),ch
    st=[];j=0
    for m in n: st.append(round(30*S[j]["start"]));j+=m
    en=st[1:]+[k["duration"]];i=0
    for x,(m,a,b) in enumerate(zip(n,st,en)):
        q=[dict(text=s["text"],start=round(s["start"]-a/30,3),dur=s["dur"]) for s in S[i:i+m]];i+=m
        af=round(30*(q[-1]["start"]+q[-1]["dur"]))
        sid=f"{sh}-{x+1}"
        out[sid]=dict(start=g,duration=b-a,audioFrames=af,audioSec=round(af/30,3),chapter=ch,chapterOffsetFrames=a,engine="mimo",model="mimo-v2.5-tts",voice="冰糖",gap=0.28,scale=1,provisional=False,sentences=q)
        assert af<=b-a,(sid,af,b-a)
        subprocess.run(["ffmpeg","-y","-v","error","-i",str(A/f"ch/{ch}.wav"),"-af",f"atrim={a/30:.4f}:{b/30:.4f},asetpts=N/SR/TB,apad,atrim=0:{(b-a)/30:.4f}","-ar","48000",str(A/f"{sid}.wav")],check=True)
        g+=b-a
json.dump(out,open(H/"timing.json","w"),ensure_ascii=False,indent=1)
json.dump(dict(fps=30,total=g,shots=out),open("/workspace/share/ep8-timing.json","w"),ensure_ascii=False,indent=1)
L=A/"list.txt";L.write_text("".join(f"file '{A}/{s}.wav'\n" for s in out))
subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",str(L),"-c:a","libmp3lame","-b:a","192k","/workspace/share/ep8-voice.mp3"],check=True);L.unlink()
for s,v in out.items(): print(s,v["start"],v["duration"],v["audioFrames"],v["chapterOffsetFrames"],len(v["sentences"]))
print("total",g)
