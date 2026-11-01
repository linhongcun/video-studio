#!/usr/bin/env python3
"""Validate actual short encoded transition clips; visual viewing is separate."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
from fractions import Fraction
import hashlib, json, subprocess
from PIL import Image,ImageChops,ImageStat
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    raw=json.loads((D/'remotion/out/height-preflight/samples.json').read_text())
    dom=json.loads((D/'qa-height-dom.json').read_text())
    assert raw['status']=='completed' and dom['status']=='passed'
    images={r['frame']:r for r in raw['samples']};checks=Counter();failures=[];rows=[]
    def test(v,label,detail=None):
        checks[label]+=1
        if not v:failures.append({'label':label,'detail':detail})
    for clip in raw['clips']:
        test(sha(clip['file'])==clip['sha256'],'actual-clip-identity',clip['name'])
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',clip['file']]))
        videos=[v for v in probe['streams'] if v['codec_type']=='video'];v=videos[0]
        test(len(videos)==1 and not any(v['codec_type']=='audio' for v in probe['streams']),'actual-silent-single-video-stream',clip['name'])
        expected=clip['range'][1]-clip['range'][0]+1
        test(int(v['nb_frames'])==expected,'every-short-clip-frame-encoded',clip['name'])
        test((v['width'],v['height'],v['r_frame_rate'])==(960,540,'30/1'),'actual-short-clip-format',clip['name'])
        frames=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=pts','-of','json',clip['file']]))['frames']
        test(len(frames)==expected,'actual-decoded-frame-count',clip['name'])
        base=Fraction(v['time_base']);start=int(frames[0]['pts'])
        for i,f in enumerate(frames):test((int(f['pts'])-start)*base==Fraction(i,30),'actual-frame-PTS-continuous-and-exact',{'clip':clip['name'],'index':i})
        decoded=[]
        for item in clip['decodedReviewFrames']:
            frame=item['globalFrame'];test(sha(item['file'])==item['sha256'],'actual-decoded-PNG-identity',frame)
            test(item['subtitleBandForegroundPixels']==0,'actual-encoded-subtitle-band-clear',frame)
            test(frame in images,'decoded-stage-also-has-real-DOM-still',frame)
            mae=None
            if True:
                a=Image.open(item['file']).convert('RGB');b=Image.open(images[frame]['file']).convert('RGB').resize((960,540),Image.Resampling.LANCZOS);roi=(35,155,890,390)
                mae=sum(ImageStat.Stat(ImageChops.difference(a.crop(roi),b.crop(roi))).mean)/3
                test(mae<3,'actual-encoded-graph-matches-same-frame-real-still',{'frame':frame,'mae':mae})
            decoded.append({'frame':frame,'sha256':item['sha256'],'diagramROIAt960x540':[35,155,890,390] if mae is not None else None,'diagramMeanAbsolutePixelDifference':mae,'bridgeTextHandledByDirectViewing':mae is None})
        rows.append({'name':clip['name'],'range':clip['range'],'sha256':clip['sha256'],'frames':expected,'durationSeconds':float(probe['format']['duration']),'decodedReviewFrames':decoded})
    out={'status':'numerically-passed-awaiting-recorded-visual-review' if not failures else 'failed','checkedAtUTC':datetime.now(timezone.utc).isoformat(),'scope':'Two actual short encoded visual transition clips,529 frames total; no full-video or full listening conclusion.','assertionsExecuted':sum(checks.values()),'assertionsByCategory':dict(checks),'clips':rows,'failures':failures,'samplesSHA256':sha(D/'remotion/out/height-preflight/samples.json'),'checkerSHA256':sha(__file__),'limits':['The actual graph ROI retains the three-unit encoding/rasterization threshold for all selected decoded height/reset/upper-write stages.','Rendered clips are silent QA evidence; actual narration is the newe631 fresh3/reused17 track and is proven separately.']}
    (D/'qa-height-motion.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'assertions':sum(checks.values()),'failures':len(failures),'decodedStages':sum(len(x['decodedReviewFrames']) for x in rows)}))
    if failures:raise SystemExit(1)
if __name__=='__main__':main()
