#!/usr/bin/env python3
"""Materialize byte-identical draft publication and actual final-media JPEGs."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse,hashlib,json,shutil,subprocess
R=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
A=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('slug',choices=['redis-sentinel','redis-cluster-failover','redis-lru']);ap.add_argument('--production',type=Path);args=ap.parse_args()
 base=R/'episodes/redis'/args.slug/'production';D=args.production.resolve() if args.production else base;assert D.is_relative_to(base);P=base.parent/'publication'
 result=json.loads((D/'render-result.json').read_text());receipt=json.loads((D/'reference-appendix.json').read_text())
 assert sha(D/'video.mp4')==result['sha256']==receipt['outputSHA256']
 subprocess.run(['/workspace/.venvs/video-studio/bin/python',str(D/'freeze.py'),'--verify'],check=True,cwd=R)
 meta=json.loads((P/'meta.json').read_text());assert meta['draft'] is True and not meta.get('publishedAt') and not meta.get('firstRelease')
 history=A/'qa/publication-history'/args.slug;copied=[]
 def preserve_existing(path):
  if path.is_file():
   saved=history/(sha(path)[:16]+'-'+path.name);saved.parent.mkdir(parents=True,exist_ok=True)
   if not saved.exists():shutil.copyfile(path,saved)
 for name in ['video.mp4','article.mdx','script.md','storyboard.json','words.json','captions.srt','research.md','pronunciation.md','references.json','article-sources.json','reference-appendix.json','reference-appendix-media-check.json','render-result.json','source-sha256.json','covers.json','knoll-props.md']:
  src=D/name
  if src.is_file():
   if (P/name).is_file() and sha(P/name)!=sha(src):preserve_existing(P/name)
   shutil.copyfile(src,P/name);assert sha(src)==sha(P/name);copied.append({'file':name,'sha256':sha(src)})
 figures=json.loads((D/'article-figure-plan.json').read_text())['figures'];images=[]
 for f in figures:
  assert f['file'].startswith('article/') and abs(f['seconds']-f['frame']/30)<1e-8
  out=P/f['file'];out.parent.mkdir(parents=True,exist_ok=True);preserve_existing(out);candidate=Path('/workspace/work/redis-batch/publication-candidates')/args.slug/f['file'];candidate.parent.mkdir(parents=True,exist_ok=True)
  if candidate.exists():candidate.unlink()
  cmd=['ffmpeg','-v','error','-i',str(D/'video.mp4'),'-vf',f"select=eq(n\\,{f['frame']}),scale=in_range=tv:out_range=pc:in_color_matrix=bt709:out_color_matrix=bt601,format=yuvj420p",'-frames:v','1','-q:v','2',str(candidate)]
  subprocess.run(cmd,check=True);shutil.copyfile(candidate,out);images.append({**f,'sha256':sha(out),'bytes':out.stat().st_size,'command':cmd})
 meta.update(result['publicationMetadata']);meta['sourcePath']=(D/'remotion').relative_to(R).as_posix();meta.update(video='video.mp4',poster='cover-16x9.jpg',burnedInCaptions=True,targetDuration=round(result['frames']/30),updatedAt=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='milliseconds'))
 (P/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 report={'slug':args.slug,'preparedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='milliseconds'),'draft':True,'copiedByteIdentity':copied,'actualEncodedFigures':images,'finalFrames':result['frames'],'visualReviewed':False,'scope':'Draft materialization only; independent final-media and actual JPEG/browser review required before release.'}
 report_path=A/'qa'/f'{args.slug}-publication-prepared.json'
 if report_path.exists():preserve_existing(report_path)
 report['sourceProductionPath']=D.relative_to(R).as_posix()
 report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'slug':args.slug,'draft':True,'figures':len(images),'frames':result['frames']}))
if __name__=='__main__':main()
