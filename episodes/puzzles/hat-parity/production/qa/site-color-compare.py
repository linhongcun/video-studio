#!/usr/bin/env python3
"""Compare exact native Canvas PNGs against explicit accurate BT.709 RGB.

This is a native-decoder comparison at full 1920x1080, separate from preview
lossy comparisons on any reduced sampling grid.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,subprocess,traceback
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--browser',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 assert not a.out.exists(),'Preserve existing results and choose a fresh --out';a.out.mkdir(parents=True)
 report={'startedAtUTC':datetime.now(timezone.utc).isoformat(),'passed':False,'scope':'Full-resolution native Chromium Canvas vs accurate limited-BT.709 to RGB24 reference at identical integer PTS frames. No preview-resizing metrics or semantic review claim.','thresholdsUnchanged':{'meanAbsoluteChannelErrorMax':1.5,'p95AbsoluteChannelErrorMax':3,'backgroundPointChannelErrorMax':3},'referenceDecoder':'scale=in_range=tv:out_range=pc:in_color_matrix=bt709:flags=accurate_rnd+full_chroma_int,format=rgb24','comparisons':[]}
 try:
  browser=json.loads((a.browser/'report.json').read_text());assert browser['pass'];assert sha(D/'video.mp4')==browser['videoSha256'];report['videoSHA256']=browser['videoSha256'];report['browserReportSHA256']=sha(a.browser/'report.json')
  rows=browser['exactFrames'];frames=sorted({r['frame']for r in rows});report['uniqueFrames']=frames;refs={};batches=[]
  for batch_no,start in enumerate(range(0,len(frames),40)):
   batch=frames[start:start+40];terms=['eq(n'+chr(92)+f',{n})'for n in batch]
   while len(terms)>1:terms=[('('+terms[i]+'+'+terms[i+1]+')')if i+1<len(terms)else terms[i]for i in range(0,len(terms),2)]
   prefix=f'reference-{batch_no:02}-';cmd=['ffmpeg','-v','error','-threads','2','-filter_threads','1','-i',str(D/'video.mp4'),'-vf',f"select={terms[0]},"+report['referenceDecoder'],'-fps_mode','passthrough','-threads','1',str(a.out/(prefix+'%03d.png'))]
   subprocess.run(cmd,check=True);files=sorted(a.out.glob(prefix+'*.png'));assert len(files)==len(batch);refs.update(zip(batch,files));batches.append({'frames':batch,'command':cmd})
  report['extractionBatches']=batches
  for row in rows:
   path=a.browser/row['file'];assert sha(path)==row['sha256'];left=np.asarray(Image.open(path).convert('RGB'),dtype=np.int16);right=np.asarray(Image.open(refs[row['frame']]).convert('RGB'),dtype=np.int16);assert left.shape==right.shape==(1080,1920,3)
   diff=np.abs(left-right);mean=float(diff.mean());p95=float(np.percentile(diff,95));points=[(40,500),(1880,500)];background=max(int(diff[y,x].max())for x,y in points)
   ok=mean<=1.5 and p95<=3 and background<=3;report['comparisons'].append({'width':row['width'],'frame':row['frame'],'nativePNG':str(path),'nativeSHA256':row['sha256'],'referencePNG':str(refs[row['frame']]),'referenceSHA256':sha(refs[row['frame']]),'meanAbsoluteChannelError':mean,'p95AbsoluteChannelError':p95,'samplePointMaxChannelError':background,'samplePointsXY':points,'passed':ok})
  report.update(passed=all(r['passed']for r in report['comparisons']),worstMean=max(r['meanAbsoluteChannelError']for r in report['comparisons']),worstP95=max(r['p95AbsoluteChannelError']for r in report['comparisons']),worstPoint=max(r['samplePointMaxChannelError']for r in report['comparisons']))
  assert report['passed'],'Native-vs-reference fixed tolerance exceeded; diagnose reference matrix before production changes'
 except Exception as e:
  report['failure']={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()};raise
 finally:
  report['finishedAtUTC']=datetime.now(timezone.utc).isoformat();(a.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'passed':report['passed'],'comparisons':len(report['comparisons']),'uniqueFrames':len(frames),'worstMean':report['worstMean'],'worstP95':report['worstP95'],'worstPoint':report['worstPoint']}))
if __name__=='__main__':main()
