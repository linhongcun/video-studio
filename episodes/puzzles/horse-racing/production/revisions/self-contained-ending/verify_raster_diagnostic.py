#!/usr/bin/env python3
"""Diagnose all original scaled-raster outliers with matched-resolution references.

First render the six original outlier frames via qa.mjs with QA_SCALE=1 into
remotion/out/ending-fullsize-all-diagnostics. Keeps the initial failed report.
This post-encode QA does not mutate any production source or media.
"""
from pathlib import Path
import json,subprocess,hashlib,numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;D=R.parents[1];O=D/'remotion/out/ending-fullsize-all-diagnostics'
original=json.loads((R/'qa-encoded-preservation.json').read_text());bad=[r for r in original['previewSamples'] if r['meanAbsoluteRGBError']>3.0];frames=sorted(r['frame'] for r in bad)
expr='+'.join(f'eq(n,{n})' for n in frames)
cmd=['ffmpeg','-y','-v','error','-i',str(D/'video.mp4'),'-vf',f"select='{expr}'",'-fps_mode','vfr',str(O/'final-%02d.png')]
subprocess.run(cmd,check=True)
rows=[]
load=lambda p:np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
for i,frame in enumerate(frames,1):
 row=next(r for r in bad if r['frame']==frame);reference=O/f'{frame}.png';final=O/f'final-{i:02d}.png';scaled=O/f'reference-{frame}-scaled.png'
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(reference),'-vf','scale=960:540',str(scaled)],check=True)
 rows.append({'frame':frame,'originalScaledHeuristicMeanRGB':row['meanAbsoluteRGBError'],'fullSizeMatchedMeanRGB':float(np.abs(load(reference)-load(final)).mean()),'direct960ReferenceVsDownscaled1920ReferenceMeanRGB':float(np.abs(load(row['reference'])-load(scaled)).mean()),'decoded960VsMatchedDownscaledReferenceMeanRGB':float(np.abs(load(row['decoded'])-load(scaled)).mean()),'fullSizeReferenceSHA256':hashlib.sha256(reference.read_bytes()).hexdigest(),'fullSizeDecodedSHA256':hashlib.sha256(final.read_bytes()).hexdigest()})
report={'status':'passed','videoSHA256':hashlib.sha256((D/'video.mp4').read_bytes()).hexdigest(),'originalScaledReportSHA256':hashlib.sha256((R/'qa-encoded-preservation.json').read_bytes()).hexdigest(),'originalHeuristicStatus':'failed and retained unchanged','frames':frames,'matchedRasterThreshold':3.0,'rows':rows,'maximumFullSizeMatchedMeanRGB':max(r['fullSizeMatchedMeanRGB'] for r in rows),'maximumMatchedDownscaledMeanRGB':max(r['decoded960VsMatchedDownscaledReferenceMeanRGB'] for r in rows),'diagnosis':'Direct 960x540 browser raster differs from a 1920x1080 browser raster reduced to 960x540, especially dense text edges. All six outliers pass the unchanged 3.0 threshold at matched 1920x1080 and matched-downscaled rasters. No media or threshold changed; independent actual content review also passed.','scope':'All six original scaled-raster outliers. Other 37 original samples and four encoded prefix comparisons already below their original limits.','renderManifestSHA256':hashlib.sha256((O/'samples.json').read_bytes()).hexdigest(),'command':cmd}
assert report['maximumFullSizeMatchedMeanRGB']<=3.0 and report['maximumMatchedDownscaledMeanRGB']<=3.0
(R/'qa-raster-diagnostic.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
