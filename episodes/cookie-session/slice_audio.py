# 按 timing.json 把每章 MiMo 音频（remotion/public/audio/ch/<章>-1.wav）切成镜头音频；extraHold 在 holdAt 处插入静音（纯画面停留，配音不动）
import json,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;A=H/"remotion/public/audio";T=json.load(open(H/"timing.json"))
for k,v in T.items():
    ch=k.rsplit('-',1)[0];s=v["chapterOffsetFrames"]/30;d=v.get("origDuration",v["duration"])/30;src=str(A/f"ch/{ch}-1.wav");out=str(A/f"{k}.wav")
    if "extraHold" not in v:
        subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{s:.3f}","-t",f"{d:.3f}","-i",src,"-ar","48000",out],check=True);continue
    at=v["holdAt"]/30;h=v["extraHold"]/30
    f=f"[0]atrim=0:{at:.4f},asetpts=N/SR/TB,apad=pad_dur={h:.4f}[a];[0]atrim={at:.4f}:{d:.4f},asetpts=N/SR/TB[b];[a][b]concat=n=2:v=0:a=1"
    subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{s:.3f}","-t",f"{d:.3f}","-i",src,"-filter_complex",f,"-ar","48000",out],check=True)
print("sliced",len(T))
