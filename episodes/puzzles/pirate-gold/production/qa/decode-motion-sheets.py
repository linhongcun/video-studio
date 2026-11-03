"""Decode existing preview MP4s for independent sequence review.

This is a viewing aid, not a production renderer or a pixel-color truth source.
Outputs and all writes remain under the episode qa directory.
"""
from pathlib import Path
import argparse, json, subprocess, hashlib
from PIL import Image, ImageOps, ImageDraw, ImageFont

ap=argparse.ArgumentParser()
ap.add_argument('clips', nargs='+')
ap.add_argument('--name', default='decoded-preflight-v1')
ap.add_argument('--every', type=int, default=6)
args=ap.parse_args()
D=Path(__file__).resolve().parent.parent
out=D/'qa/out'/args.name
out.mkdir(parents=True, exist_ok=True)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
reports=[]
for rel in args.clips:
    clip=(D/rel).resolve()
    assert clip.is_relative_to(D/'qa'), 'Only existing QA clips may be decoded'
    folder=out/clip.stem
    folder.mkdir(parents=True,exist_ok=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=nb_read_frames,nb_frames,width,height','-of','json',str(clip)]))['streams'][0]
    frames=int(probe.get('nb_read_frames') or probe.get('nb_frames'))
    subprocess.run(['ffmpeg','-v','error','-i',str(clip),'-vf',f'select=not(mod(n\\,{args.every}))','-vsync','0',str(folder/'%05d.png')],check=True)
    pngs=sorted(folder.glob('*.png'))
    assert len(pngs)==(frames+args.every-1)//args.every
    sheets=[]
    for start in range(0,len(pngs),12):
        chosen=pngs[start:start+12]
        sheet=Image.new('RGB',(3*640,4*390),'#171326')
        draw=ImageDraw.Draw(sheet)
        for i,p in enumerate(chosen):
            image=Image.open(p).convert('RGB')
            thumb=ImageOps.contain(image,(640,360))
            x=(i%3)*640;y=(i//3)*390
            sheet.paste(thumb,(x,y))
            draw.text((x+12,y+365),f'{clip.stem} | local n={(start+i)*args.every}',font=font,fill='white')
        target=folder/f'sheet-{start//12+1:02d}.jpg'
        sheet.save(target,quality=92)
        sheets.append(str(target.relative_to(D)))
    reports.append({'clip':str(clip.relative_to(D)),'clipSHA256':hashlib.sha256(clip.read_bytes()).hexdigest(),'actualFrames':frames,'sampleEvery':args.every,'decodedImages':len(pngs),'sheets':sheets})
report={'scope':'Decoded QA preview sequences; contact sheets are viewing aids, not production media or a color-reference claim.','visualReviewed':False,'clips':reports}
(D/'qa'/f'{args.name}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'report':str(D/'qa'/f'{args.name}.json'),'clips':len(reports),'sheets':sum(len(r['sheets']) for r in reports)},ensure_ascii=False))
