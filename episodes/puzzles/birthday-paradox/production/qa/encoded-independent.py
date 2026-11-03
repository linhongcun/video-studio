#!/usr/bin/env python3
"""Independent decoded-frame sample extraction; writes only QA outputs/report."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone

D = Path(__file__).resolve().parents[1]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--video', type=Path, default=D/'video.mp4')
    ap.add_argument('--name', default='final-v1')
    args = ap.parse_args()
    video = args.video.resolve()
    sb = json.loads((D/'storyboard.json').read_text())
    shots = [s for scene in sb['scenes'] for s in scene['shots']]
    body = sum(s['durationInFrames'] for s in shots)
    probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],text=True))
    stream = next(s for s in probe['streams'] if s['codec_type']=='video')
    assert stream['width']==1920 and stream['height']==1080 and stream['r_frame_rate']=='30/1'
    assert stream['color_range']=='tv' and stream['color_space']=='bt709' and stream['color_transfer']=='bt709' and stream['color_primaries']=='bt709'
    frames = int(stream['nb_frames'])
    assert frames == body+150, (frames,body)
    points = sorted(set([p for s in shots for p in [s['from'], s['from']+s['durationInFrames']//2,s['from']+s['durationInFrames']-1]]+[606,2508,2510,2520,2530,2544,2565,2859,body,body+75,frames-1]))
    out = D/'qa/out'/args.name
    out.mkdir(parents=True,exist_ok=True)
    expr = '+'.join(f'eq(n\\,{f})' for f in points)
    vf = 'select='+expr+',scale=in_range=tv:out_range=pc:in_color_matrix=bt709:out_color_matrix=bt601,format=rgb24'
    subprocess.run(['ffmpeg','-v','error','-i',str(video),'-vf',vf,'-fps_mode','vfr',str(out/'sample-%03d.png')],check=True)
    files = sorted(out.glob('sample-*.png'))
    assert len(files)==len(points),(len(files),len(points))
    samples = []
    for frame,path in zip(points,files):
        samples.append({'frame':frame,'pts':frame/30,'file':str(path.relative_to(D)),'sha256':sha(path)})
    report = {'checkedAt':datetime.now(timezone.utc).isoformat(),'executor':'Codex independent QA','video':str(video.relative_to(D)) if video.is_relative_to(D) else str(video),'videoSHA256':sha(video),'frames':frames,'bodyFrames':body,'referenceFrames':[body,frames-1],'probe':probe,'decodeFilter':vf,'samples':samples,'pass':False,'visualReviewed':False,'limitations':['Selected decoded frames are not full realtime playback or semantic audio audition.']}
    (D/'qa'/f'{args.name}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    from PIL import Image, ImageDraw, ImageFont
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
    for k in range(0,len(samples),9):
        sheet=Image.new('RGB',(1440,900),'#171326');draw=ImageDraw.Draw(sheet)
        for j,sample in enumerate(samples[k:k+9]):
            im=Image.open(D/sample['file']);im.thumbnail((480,270));x=j%3*480;y=j//3*300;sheet.paste(im,(x,y));draw.text((x+8,y+273),f"encoded frame {sample['frame']}",font=font,fill='white')
        sheet.save(out/f'sheet-{k//9}.jpg',quality=94)
    print(json.dumps({'samples':len(samples),'frames':frames,'videoSHA256':report['videoSHA256'],'report':str(D/'qa'/f'{args.name}.json')}))

if __name__=='__main__':
    main()
