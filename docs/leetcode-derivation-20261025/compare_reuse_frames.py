"""Compare final-source stills to baseline MP4 at explicitly mapped local frames."""
from pathlib import Path
import hashlib,json,subprocess,sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
EP=ROOT/'episodes-codex'/sys.argv[1]
request=json.loads((EP/'remotion/out/approach-qa-request.json').read_text())
manifest=EP/'qa-motion-approach.json'
preview=json.loads(manifest.read_text());by_frame={x['frame']:Path(x['file']) for x in preview['samples']}
rows=request['reuseSamples'];frames=sorted({r['oldFrame'] for r in rows});out=EP/'remotion/out/approach-preflight/baseline-frames';out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=EP/'remotion/out/approach-baseline/video.mp4';decoded={}
for start in range(0,len(frames),40):
 group=frames[start:start+40];expression='+'.join(f'eq(n\\,{n})' for n in group);pattern=out/f'b{start:03}-%04d.png'
 subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-i',str(old),'-vf',f'select={expression},scale=960:540','-vsync','0','-threads','1',str(pattern)],check=True)
 decoded.update({f:out/f'b{start:03}-{i:04}.png' for i,f in enumerate(group,1)})
results=[]
for row in rows:
 a,b=by_frame[row['frame']],decoded[row['oldFrame']];x=np.array(Image.open(a).convert('RGB'),dtype=float);y=np.array(Image.open(b).convert('RGB'),dtype=float);assert x.shape==y.shape==(540,960,3);error=float(np.abs(x-y).mean());assert error<8,(row,error)
 results.append({**row,'currentFile':str(a),'baselineFile':str(b),'currentSHA256':sha(a),'baselineFrameSHA256':sha(b),'meanAbsoluteRGBDifference':error})
report={'status':'passed','scope':'Actual current-source captioned PNG versus actual baseline MP4 decoded at same local frame, including explicit tail-frame mappings; pixel fidelity supports the independent semantic review and is not a teaching score.','baselineVideoSHA256':sha(old),'currentPreviewManifestSHA256':sha(manifest),'preflightSourceManifestSHA256':sha(EP/'revisions/approach-first/preflight-source-sha256.json'),'samples':results,'maxMeanAbsoluteRGBDifference':max(x['meanAbsoluteRGBDifference'] for x in results)}
(EP/'revisions/approach-first/reuse-frame-comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(f'{EP.name}: {len(results)} baseline frame comparisons; maxMAE={report["maxMeanAbsoluteRGBDifference"]:.5f}',flush=True)
