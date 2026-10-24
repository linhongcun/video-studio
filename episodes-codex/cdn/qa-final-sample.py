"""Decode reproducible samples from this revision's verified real MP4, not stills."""
from pathlib import Path
import hashlib,json,subprocess,time
from PIL import Image,ImageDraw

D=Path(__file__).resolve().parent
deadline=time.monotonic()+1800
while not (D/'render-result.json').exists():
    if time.monotonic()>deadline:raise SystemExit('Timed out waiting for final measured output')
    time.sleep(2)
r=json.loads((D/'render-result.json').read_text())
assert r['frames']==3989 and r['fullDecode']=='passed'
assert r['voiceSha256']=='6088567423edeb390abff33169b26e26c3a845222884e274c272f42ce67617cf'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(D/'video.mp4')==r['sha256']
frames=[0,515,629,630,864,1033,1034,1035,1096,1097,1204,1294,1295,1335,1423,1498,
        1608,1648,1677,1678,1703,1727,1728,1818,1819,1866,1930,1931,1993,1994,
        2045,2082,2083,2230,2479,2613,2670,2671,2677,2678,2821,2822,2851,2871,
        2872,2948,3189,3497,3593,3913,3925,3938,3951,3988]
out=D/'remotion/out/final-map';out.mkdir(parents=True,exist_ok=True)
assert not list(out.glob('*.png')),'Use a new evidence path rather than mixing candidate frames'
selection='+'.join('eq(n\\,%d)'%f for f in frames)
cmd=['ffmpeg','-v','error','-i',str(D/'video.mp4'),'-vf','select='+selection,'-vsync','0',str(out/'%03d.png')]
subprocess.run(cmd,check=True)
paths=sorted(out.glob('*.png'));assert len(paths)==len(frames)
records=[];sheet=Image.new('RGB',(1440,235*((len(paths)+3)//4)),'#0F172A');draw=ImageDraw.Draw(sheet)
for i,(p,f) in enumerate(zip(paths,frames)):
    im=Image.open(p).convert('RGB');im.thumbnail((360,203));x=i%4*360;y=i//4*235
    sheet.paste(im,(x,y));draw.text((x+5,y+209),f'final MP4: {f}',fill='white')
    records.append(dict(frame=f,file=str(p),sha256=sha(p),videoSha256=r['sha256']))
sheet.save(out/'contact.jpg')
(D/'encoded-frames.json').write_text(json.dumps(records,indent=2)+'\n')
(out/'command.json').write_text(json.dumps(dict(command=cmd,sourceVideoSha256=r['sha256'],frames=frames),indent=2)+'\n')
assert sha(D/'video.mp4')==r['sha256']
print('Current final MP4 decoded',len(records),'frames; SHA',r['sha256'],flush=True)
