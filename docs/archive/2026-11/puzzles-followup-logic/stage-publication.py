#!/usr/bin/env python3
"""Stage the two audited puzzle revisions locally; no GitHub mutation."""
from pathlib import Path
from fractions import Fraction
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse,hashlib,json,re,shutil,subprocess,tempfile

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
TASK=Path(__file__).resolve().parent
SLUGS=('twelve-balls','prisoners-light')
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def run(args,capture=False):
 return subprocess.run([str(x) for x in args],cwd=ROOT,check=True,text=True,capture_output=capture)
def paths(slug):
 p=ROOT/'episodes/puzzles'/slug
 return p/'production/revisions/logic-20261111'/slug,p/'publication'
def validate(slug):
 d,p=paths(slug)
 run(['python3',d/'freeze.py','--verify'])
 run(['python3',d/'verify.py','--final'])
 result=read(d/'render-result.json');receipt=read(d/'reference-appendix.json');media=read(d/'reference-appendix-media-check.json')
 assert sha(d/'video.mp4')==result['sha256']==receipt['outputSHA256']==media['outputSHA256']
 assert media['passed'] and result['frames']==receipt['finalVideoFrames']==result['publicationMetadata']['finalVideoFrames']
 assert result['publicationMetadata']['referenceAppendix']['from']==receipt['bodyFrames']
 assert receipt['finalVideoFrames']-receipt['bodyFrames']==150
 a=(d/'article.mdx').read_text();old=(p/'article.mdx').read_text()
 quotes=lambda text:re.findall(r'<SourceQuote .*?/>',text,re.S)
 assert len(quotes(a))==len(quotes(old))==2 and quotes(a)==quotes(old)
 figures=re.findall(r'<Figure\s+src="/video-studio/episodes/'+slug+r'/article/([^"/]+)"[^>]*seekTo=\{([0-9.]+)\}',a,re.S)
 assert len(figures)==2
 probe=json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',d/'video.mp4'],True).stdout)['streams'][0]
 assert probe['color_range']=='tv' and probe['color_space']=='bt709' and int(probe['nb_frames'])==result['frames']
 for name,t in figures:
  frame=Fraction(t)*30
  assert frame.denominator==1 and 0<=int(frame)<receipt['bodyFrames']
 return result,figures
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--apply',action='store_true')
 parser.add_argument('--expected-main')
 parser.add_argument('--version',default='0.105.3')
 args=parser.parse_args()
 if not args.apply:
  print(json.dumps({'mode':'plan','episodes':SLUGS,'version':args.version,'preserveHatParity':True,'publishes':False}));return
 assert args.expected_main
 run(['git','fetch','origin','main'])
 latest=run(['git','rev-parse','origin/main'],True).stdout.strip()
 assert latest==args.expected_main
 run(['git','merge-base','--is-ancestor',latest,'HEAD'])
 pkg=read(ROOT/'site/package.json');lock=read(ROOT/'site/package-lock.json')
 parts=list(map(int,pkg['version'].split('.')))
 assert args.version=='.'.join(map(str,[parts[0],parts[1],parts[2]+1]))
 tag=subprocess.run(['git','ls-remote','--exit-code','--tags','origin','refs/tags/v'+args.version],cwd=ROOT,capture_output=True,text=True)
 assert tag.returncode==2,'Version tag exists or lookup failed'
 validations={s:validate(s) for s in SLUGS}
 baseline=read(TASK/'baseline.json')
 assert all(sha(ROOT/p)==v for e in baseline['episodes'] for p,v in e['sha256'].items()),'Historical production or current baseline assets changed before staging'
 work=Path(tempfile.mkdtemp(prefix='video-studio-puzzles-publication-',dir=ROOT.parent))
 stamp=datetime.now(ZoneInfo('Asia/Shanghai')).replace(microsecond=0).isoformat()
 attempt=work.name.removeprefix('video-studio-puzzles-publication-')
 backup=work/'backup';candidate=work/'candidate'
 packagePaths=[ROOT/'site/package.json',ROOT/'site/package-lock.json']
 packageBytes={f:f.read_bytes() for f in packagePaths}
 reportPaths=[paths(slug)[0]/'qa/publication-stage.json' for slug in SLUGS]+[TASK/'publication-stage.json']
 previousReports={f:f.read_bytes() if f.exists() else None for f in reportPaths}
 tree=lambda directory:{str(f.relative_to(directory)):sha(f) for f in directory.rglob('*') if f.is_file()}
 reports=[];mutated=False
 try:
  # All old bytes and complete candidates stay outside the repository.
  for slug in SLUGS:
   _,pub=paths(slug)
   shutil.copytree(pub,backup/slug)
  for f in packagePaths:
   target=backup/'site'/f.name;target.parent.mkdir(parents=True,exist_ok=True)
   shutil.copy2(f,target)
   assert target.read_bytes()==packageBytes[f],'Site version backup differs from original bytes'
  for slug in SLUGS:
   d,pub=paths(slug);result,figures=validations[slug]
   oldDir=backup/slug;targetDir=candidate/slug
   shutil.copytree(oldDir,targetDir)
   before=tree(oldDir);old=read(oldDir/'meta.json');export=[]
   coverNames=['cover-16x9.jpg','cover-4x3.jpg','cover-3x4.jpg','poster.jpg','cover-style.json']
   coverHashes={n:sha(oldDir/n) for n in coverNames if (oldDir/n).is_file()}
   for name,t in figures:
    frame=int(Fraction(t)*30);target=targetDir/'article'/name;target.parent.mkdir(parents=True,exist_ok=True)
    filt=f'select=eq(n\\,{frame}),scale=in_range=tv:out_range=pc:in_color_matrix=bt709:out_color_matrix=bt601,format=yuvj420p'
    command=['ffmpeg','-v','error','-y','-i',d/'video.mp4','-vf',filt,'-frames:v','1','-q:v','2',target]
    prior=d/'qa/article-image-export.json';existing=next((p for p in [d/'publication-stage/article'/name,d/'article'/name] if p.is_file()),d/'publication-stage/article'/name);reused=False
    if prior.is_file() and existing.is_file():
     imageReceipt=read(prior)
     row=next((r for r in imageReceipt.get('figures',[]) if r['filename']==name),None)
     assert imageReceipt.get('passed') and imageReceipt['sourceSHA256']==result['sha256'] and imageReceipt['articleSHA256']==sha(d/'article.mdx')
     assert row and row['frame']==frame and row['sha256']==sha(existing)
     assert 'BT.709' in imageReceipt['colorOperation'] and 'BT.601' in imageReceipt['colorOperation']
     shutil.copy2(existing,target);reused=True
    else:run(command)
    export.append({'filename':name,'seconds':t,'frame':frame,'sha256':sha(target),'oldSHA256':sha(oldDir/'article'/name),'reusedVerifiedExactFrameExport':reused,'command':[str(x) for x in command]})
   for name in ['video.mp4','script.md','captions.srt','storyboard.json','words.json','references.json','reference-appendix.json','reference-appendix-media-check.json','article.mdx']:
    assert (d/name).is_file(),name
    shutil.copy2(d/name,targetDir/name)
    assert sha(targetDir/name)==sha(d/name),'Candidate asset copy differs: '+name
   assert sha(targetDir/'video.mp4')==result['sha256']
   meta=dict(old);meta.update(result['publicationMetadata'])
   meta.update(sourcePath=str(d.relative_to(ROOT)/'remotion'),updatedAt=stamp,targetDuration=result['seconds'],burnedInCaptions=True)
   if slug=='twelve-balls':
    meta['summary']='先按剩余称数限制候选，再解释混合分组和平衡分支3／3／2的安排，逐路确定异常球及轻重。'
    meta['description']='从24种候选推导分组，补明首称平衡后为何用三个可疑球对三个正常球，让每个结果留下最后一称分得开的候选。'
   else:
    meta['summary']='先解释灯只保存一份待收信号、固定计数员保存累计，再走完四人十二次来访，说明为何99份对应99个不同的人。'
    meta['description']='从一次性贡献推导固定接收者和等待规则，再用四人完整过程解释不重复接收与最终确认所有人来过。'
   dump(targetDir/'meta.json',meta)
   assert all(meta.get(k)==old.get(k) for k in ['ep','slug','title','createdAt','publishedAt','firstRelease','platforms'])
   assert all(sha(targetDir/n)==v for n,v in coverHashes.items())
   reports.append({'status':'local-publication-staged','deployed':False,'slug':slug,'version':args.version,'stagedAt':stamp,'upstreamSHA':latest,'revision':str(d.relative_to(ROOT)),'videoSHA256':result['sha256'],'frozenManifestSHA256':sha(d/'source-sha256.json'),'before':before,'after':tree(targetDir),'sourceQuoteBodiesPreserved':True,'preservedCovers':coverHashes,'preservedMetadata':{k:meta.get(k) for k in ['ep','slug','title','createdAt','publishedAt','firstRelease','platforms']},'figures':export,'figureVisualReviewSeparate':True})
  pkg['version']=lock['version']=lock['packages']['']['version']=args.version
  dump(candidate/'site/package.json',pkg);dump(candidate/'site/package-lock.json',lock)
  # Check that nothing changed while the two candidates were prepared.
  for report in reports:
   assert tree(paths(report['slug'])[1])==report['before'],'Publication changed during preparation'
  assert all(f.read_bytes()==raw for f,raw in packageBytes.items()),'Site version files changed during preparation'
  # Installation is a transaction: any partial copy or final check rolls both back.
  mutated=True
  for slug in SLUGS:shutil.copytree(candidate/slug,paths(slug)[1],dirs_exist_ok=True)
  for f in packagePaths:shutil.copy2(candidate/'site'/f.name,f)
  run(['npm','--prefix','site','run','check:references']);run(['npm','--prefix','site','run','check:articles'])
  for report in reports:
   assert tree(paths(report['slug'])[1])==report['after'],'Installed publication differs from prepared candidate'
  assert all(sha(ROOT/p)==v for e in baseline['episodes'] for p,v in e['sha256'].items() if e['slug']=='hat-parity' or '/publication/' not in p),'P08 or historical production changed during staging'
  # Success receipts are emitted only after both episodes and all checks succeed.
  for report in reports:dump(paths(report['slug'])[0]/'qa/publication-stage.json',report)
  dump(TASK/'publication-stage.json',{'status':'local-staged','version':args.version,'episodes':reports,'hatParityPreserved':True,'temporaryWorkspace':str(work),'temporaryWorkspaceRemovedAfterSuccess':True,'rollbackOnFailure':True})
 except Exception as exc:
  rollbackErrors=[]
  if mutated:
   for slug in SLUGS:
    pub=paths(slug)[1]
    try:
     if pub.exists():shutil.rmtree(pub)
     shutil.copytree(backup/slug,pub)
    except Exception as rollback:rollbackErrors.append({'path':str(pub),'error':repr(rollback)})
   for f in packagePaths:
    try:shutil.copy2(backup/'site'/f.name,f)
    except Exception as rollback:rollbackErrors.append({'path':str(f),'error':repr(rollback)})
   for f,raw in previousReports.items():
    try:
     if raw is None:f.unlink(missing_ok=True)
     else:f.write_bytes(raw)
    except Exception as rollback:rollbackErrors.append({'path':str(f),'error':repr(rollback)})
   for report in reports:
    try:assert tree(paths(report['slug'])[1])==report['before']
    except Exception as rollback:rollbackErrors.append({'path':str(paths(report['slug'])[1]),'error':repr(rollback)})
   for f,raw in packageBytes.items():
    try:assert f.read_bytes()==raw
    except Exception as rollback:rollbackErrors.append({'path':str(f),'error':repr(rollback)})
  failure={'status':'failed-with-rollback' if not rollbackErrors else 'failed-rollback-incomplete','failedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'version':args.version,'episodes':list(SLUGS),'error':repr(exc),'publicationInstallationStarted':mutated,'rollbackRequired':mutated,'rollbackComplete':not rollbackErrors,'rollbackErrors':rollbackErrors,'temporaryWorkspaceRetained':str(work),'note':'Preparation errors occur before publication writes; installation/check errors restore both complete publication trees and exact site package/lock bytes.'}
  dump(TASK/('publication-stage-failed-'+attempt+'.json'),failure)
  raise
 else:
  try:shutil.rmtree(work)
  except OSError as cleanup:
   completed=read(TASK/'publication-stage.json')
   completed.update(temporaryWorkspaceRemovedAfterSuccess=False,temporaryWorkspaceCleanupError=repr(cleanup))
   dump(TASK/'publication-stage.json',completed)
 print(json.dumps({'staged':True,'version':args.version,'episodes':list(SLUGS),'hatParityPreserved':True,'deployed':False},ensure_ascii=False))
if __name__=='__main__':main()
