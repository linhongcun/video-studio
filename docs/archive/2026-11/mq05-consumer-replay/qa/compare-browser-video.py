#!/usr/bin/env python3
"""Read-only same-integer-frame Chromium canvas versus final FFmpeg RGB checks."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'AGENTS.md').is_file())
D=ROOT/'episodes/message-queue/kafka-consumer-idempotency/production/revisions/consumer-replay-v2'
ap=argparse.ArgumentParser();ap.add_argument('site_report',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.site_report=a.site_report.resolve();a.out=a.out.resolve();assert not a.out.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads(a.site_report.read_text());f=json.loads((D/'qa-final-independent/encoded-independent.json').read_text());assert s['pass']is True and f['machinePass']is True and s['videoSha256']==f['videoSHA256'];frames={v['frame']:v for v in f['samples']};rows=[]
for v in s['exactFrames']:
 n=v['frame'];assert n in frames,('Missing final integer-n reference',n)
 fp=D/frames[n]['retainedFile'];cp=a.site_report.parent/v['file'];assert sha(fp)==frames[n]['sha256']and sha(cp)==v['sha256'];x=np.asarray(Image.open(fp).convert('RGB'),dtype=np.int16);y=np.asarray(Image.open(cp).convert('RGB'),dtype=np.int16);assert x.shape==y.shape==(1080,1920,3);delta=np.abs(x-y);corners=[(50,400),(1870,400),(50,900),(1870,900)];patch=max(int(delta[yy,xx].max())for xx,yy in corners);mean=float(delta.mean());p95=float(np.percentile(delta,95));rows.append({'width':v['width'],'frame':n,'finalPNG':fp.relative_to(ROOT).as_posix(),'browserPNG':cp.relative_to(ROOT).as_posix(),'finalSHA256':sha(fp),'browserSHA256':sha(cp),'meanAbsoluteChannelError':mean,'p95AbsoluteChannelError':p95,'maxBackgroundPointChannelError':patch,'pass':mean<=1.5 and p95<=3 and patch<=3})
r={'kind':'actual-native-canvas-vs-final-ffmpeg-rgb','pass':bool(rows)and all(x['pass']for x in rows),'videoSHA256':f['videoSHA256'],'siteReportSHA256':sha(a.site_report),'finalAuditSHA256':sha(D/'qa-final-independent/encoded-independent.json'),'thresholds':{'meanAbsoluteChannelErrorMax':1.5,'p95AbsoluteChannelErrorMax':3,'backgroundPointChannelErrorMax':3},'checks':rows,'scope':'Exact RVFC-PTS frames, intrinsic1920x1080 decoded pixels. Excludes native controls and viewport screenshot color; no physical-device or other-browser claim.'};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':r['pass'],'comparisons':len(rows),'worstMean':max(x['meanAbsoluteChannelError']for x in rows),'worstP95':max(x['p95AbsoluteChannelError']for x in rows),'worstBackground':max(x['maxBackgroundPointChannelError']for x in rows)}));assert r['pass']
