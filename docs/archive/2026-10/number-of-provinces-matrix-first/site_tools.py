"""Bounded LC547 matrix-first revision delivery. Never render or mutate frozen inputs."""
from pathlib import Path
from datetime import datetime, timezone
from html.parser import HTMLParser
from zoneinfo import ZoneInfo
import argparse, hashlib, io, json, math, re, shutil, subprocess, tarfile, tempfile, time, urllib.request
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
SLUG='number-of-provinces'; EP=ROOT/'episodes-codex'/SLUG/'revisions/matrix-first'/SLUG; CAN=ROOT/'episodes'/SLUG
OUT=Path(__file__).resolve().parent; BASE='https://linhongcun.github.io/video-studio/'
PERSISTENT_META=['slug','ep','problemNumber','title','createdAt','publishedAt','firstRelease','platforms','series','related','tags','video','poster']
PERSISTENT_ASSETS=['cover-16x9.jpg','cover-4x3.jpg','cover-3x4.jpg','poster.jpg','cover-style.json']
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(b): return hashlib.sha256(b).hexdigest()
def save(p,v): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def git(*a): return subprocess.check_output(['git',*a],cwd=ROOT)
def gh(p): return json.loads(subprocess.check_output(['gh','api',f'repos/linhongcun/video-studio/{p}'],cwd=ROOT))
def now():return datetime.now(timezone.utc).isoformat()
def baseline_meta(base):return json.loads(git('show',base+':'+f'episodes/{SLUG}/meta.json'))
def revision_identity(base,meta):
 old=baseline_meta(base)
 assert {k:meta.get(k) for k in PERSISTENT_META}=={k:old.get(k) for k in PERSISTENT_META},'Persistent episode identity changed'
 for n in PERSISTENT_ASSETS:assert sha(CAN/n)==digest(git('show',base+':'+f'episodes/{SLUG}/'+n)),n
 assert datetime.fromisoformat(meta['updatedAt'])>datetime.fromisoformat(old['updatedAt']),'Revision date must advance'
 assert meta['sourcePath']==str((EP/'remotion').relative_to(ROOT)) and meta['burnedInCaptions'] is True
 return {'metadata':{k:old.get(k) for k in PERSISTENT_META},'assets':{n:sha(CAN/n) for n in PERSISTENT_ASSETS}}
def frozen():
 m=read(EP/'source-sha256.json')
 for n,h in m.items():assert sha(EP/n)==h,n
 return {'count':len(m),'sha256':sha(EP/'source-sha256.json')}
def preserved(base):
 hashes={};meta=[]
 proc=subprocess.Popen(['git','archive','--format=tar',base,'episodes'],cwd=ROOT,stdout=subprocess.PIPE)
 with tarfile.open(fileobj=proc.stdout,mode='r|') as archive:
  for x in archive:
   if x.isdir() or x.name.startswith(f'episodes/{SLUG}/'):continue
   old=x.linkname.encode() if x.issym() else archive.extractfile(x).read()
   actual=(ROOT/x.name).read_bytes() if not x.issym() else str((ROOT/x.name).readlink()).encode()
   assert digest(actual)==digest(old),x.name
   hashes[x.name]=digest(old)
   if re.fullmatch(r'episodes/[^/]+/meta.json',x.name):meta.append(json.loads(old))
 assert proc.wait()==0
 assert {str(p.relative_to(ROOT)) for p in (ROOT/'episodes').glob('*/meta.json') if p.parent.name!=SLUG}=={f"episodes/{x['slug']}/meta.json" for x in meta}
 return {'baseline':base,'fileCount':len(hashes),'publishedCourses':sum(not x.get('draft') and not x.get('archived') for x in meta),'oldLeetcodeOrder':[x['slug'] for x in sorted(meta,key=lambda x:(x['ep'],x.get('lessonOrder',0))) if x.get('series')=='leetcode' and not x.get('draft') and not x.get('archived')],'sha256':hashes}
def contract(base,tag):
 freeze=frozen();meta=read(CAN/'meta.json'); sb=read(EP/'storyboard.json');rr=read(EP/'render-result.json');ref=read(EP/'references.json');receipt=read(EP/'reference-appendix.json')
 assert meta['slug']==SLUG and meta['ep']==41 and meta['problemNumber']==547 and not meta['draft']
 identity=revision_identity(base,meta)
 dates=[datetime.fromisoformat(meta[k].replace('Z','+00:00')) for k in ['createdAt','updatedAt','publishedAt']]
 assert all(d.tzinfo for d in dates) and dates[1]>=dates[0] and dates[2]>=dates[0]
 for n in ['script.md','storyboard.json','references.json','reference-appendix.json','reference-appendix-media-check.json','render-result.json','source-sha256.json',meta['video']]:assert sha(CAN/n)==sha(EP/n),n
 pub=rr['publicationMetadata'];assert meta['finalVideoFrames']==pub['finalVideoFrames']==receipt['finalVideoFrames']
 assert meta['referenceAppendix']==pub['referenceAppendix'];assert rr['sha256']==sha(CAN/meta['video'])==receipt['outputSHA256']
 shots=[x for sc in sb['scenes'] for x in sc['shots']];cues=[{'text':c['text'],'start':(s['from']+c['from'])/30,'end':(s['from']+c['to']+1)/30} for s in shots for c in s['subtitles']]
 assert len(cues)==26 and len(shots)==13 and len(cues)==2*len(shots)
 chapters=[{'id':s['chapterId'],'start':s['from']/30} for s in sb['scenes']];assert len(chapters)==4 and len({x['id'] for x in chapters})==4
 card=sb['meta']['unvoicedEndCard'];assert card['durationInFrames']==150 and card['from']+150==sb['meta']['durationInFrames']
 app=meta['referenceAppendix'];assert app['from']==sb['meta']['durationInFrames'] and app['durationInFrames']==150 and app['from']+150==meta['finalVideoFrames']
 assert ref['presentation']==receipt['presentation']=='title-author' and receipt['inputs']['secondsPerPage']==5
 assert receipt['inputs']['referencesSHA256']==sha(EP/'references.json') and receipt['inputs']['bodySHA256']==sha(EP/'remotion/out/body.mp4')
 assert receipt['bibliography']==[{'id':x['id'],'title':x['title'],'credit':x.get('author') or x['organization']} for x in ref['sources']]
 assert receipt['layout']['renderedFields']==['title','credit'] and receipt['layout']['quotesRendered'] is False
 check=read(EP/'reference-appendix-media-check.json');assert check['passed'] and check['outputSHA256']==rr['sha256'] and check['bodyFrames']==sb['meta']['durationInFrames']
 article=(CAN/'article.mdx').read_text();production=(EP/'article.mdx').read_text()
 if article!=production:
  derivation=read(OUT/'article-derivation.json');assert derivation['status']=='passed' and derivation['canonicalArticleSHA256']==sha(CAN/'article.mdx') and derivation['productionArticleSHA256']==sha(EP/'article.mdx')
 ids=re.findall(r'<SourceQuote\b[^>]*sourceId="([^"]+)"',article);assert ids
 sources={x['id']:x for x in ref['sources']}
 if (CAN/'article-sources.json').exists():sources.update({x['id']:x for x in read(CAN/'article-sources.json')['sources']})
 quotes=[{'id':i,'text':sources[i]['quotation']['text'],'title':sources[i]['title'],'url':sources[i]['url']} for i in ids]
 figures=[]
 for attrs in re.findall(r'<Figure\b(.*?)/>',article,re.S):
  src=re.search(r'\bsrc="([^"]+)"',attrs)[1];seek=float(re.search(r'\bseekTo=\{([\d.]+)\}',attrs)[1]);path=ROOT/src.removeprefix('/video-studio/')
  assert path.is_file() and 0<=seek<card['from']/30
  figures.append({'src':src,'seekTo':seek,'path':str(path.relative_to(ROOT)),'sha256':sha(path)})
 assert figures
 solution=(EP/'solution.py').read_text();assert re.search(r'```python\n(.*?)```',article,re.S)[1].rstrip()==solution.rstrip()
 old=preserved(base);assert len(old['oldLeetcodeOrder'])==10
 opening=[0,shots[1]['from']+math.floor(shots[1]['durationInFrames']*.4),shots[2]['from']+math.floor(shots[2]['durationInFrames']*.85)]
 return {'slug':SLUG,'revisionTag':tag,'meta':meta,'persistentIdentity':identity,'freeze':freeze,'video':{'sha256':rr['sha256'],'bytes':(CAN/meta['video']).stat().st_size,'frames':meta['finalVideoFrames'],'fps':30},'bodyFrames':sb['meta']['durationInFrames'],'card':card,'appendix':app,'chapters':chapters,'cues':cues,'openingSamples':opening,'quotes':quotes,'figures':figures,'canonicalArticleSHA256':sha(CAN/'article.mdx'),'productionArticleSHA256':sha(EP/'article.mdx'),'solution':solution,'preservation':old,'algorithmOrder':old['oldLeetcodeOrder']+[SLUG]}
def integrate_write(a):
 frozen();rr=read(EP/'render-result.json');assert rr['sha256']==a.video_sha==sha(EP/'video.mp4')
 meta=read(CAN/'meta.json');assert not meta['draft'] and meta.get('publishedAt'),'Only an existing published episode revision is supported'
 old=baseline_meta(a.baseline);assert meta==old,'Canonical metadata changed after baseline'
 identity={k:meta.get(k) for k in PERSISTENT_META};assert meta['ep']==41 and meta['problemNumber']==547
 for n in ['article.mdx','script.md','storyboard.json','video.mp4','references.json','reference-appendix.json','reference-appendix-media-check.json','render-result.json','source-sha256.json','research.md','references.md','article-sources.json']:
  if (EP/n).exists():shutil.copy2(EP/n,CAN/n)
 if (EP/'article').exists():shutil.copytree(EP/'article',CAN/'article',dirs_exist_ok=True)
 meta.update(rr['publicationMetadata']);meta.update(updatedAt=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'),sourcePath=str((EP/'remotion').relative_to(ROOT)),burnedInCaptions=True)
 meta['summary']='从二维相连数组逐格建立城市关系图，再推导分组查询与合并；用同一示例解释直接、间接连通及孤城计入。'
 meta['description']='先读懂isConnected二维数组的行列与1/0，再把同一输入画成城市关系图，推导并查集并走完整例；附5秒完整Python、原文引用与成片回看。'
 meta['targetDuration']=math.floor(meta['finalVideoFrames']/30+.5);save(CAN/'meta.json',meta)
 assert identity=={k:meta.get(k) for k in identity}
 target=tuple(map(int,a.revision_tag[1:].split('.')))
 for n in ['site/package.json','site/package-lock.json']:
  p=ROOT/n;d=read(p);old=tuple(map(int,d['version'].split('.')));assert target>old
  d['version']=a.revision_tag[1:]
  if 'packages'in d:d['packages']['']['version']=a.revision_tag[1:]
  save(p,d)
 c=contract(a.baseline,a.revision_tag);save(OUT/'site-contract.json',c);save(OUT/'integration.json',{'status':'integrated-awaiting-qa','at':now(),'revisionTag':a.revision_tag,'preservationBaseline':a.baseline,'identity':identity,'updatedAt':meta['updatedAt'],'publishedAt':meta['publishedAt'],'video':c['video'],'freeze':c['freeze']});print(json.dumps({'status':'integrated','frames':c['video']['frames'],'videoSHA256':a.video_sha}))
def integrate(a):
 # Routine preflight failures must leave the metadata reservation retryable.
 target=tuple(map(int,a.revision_tag[1:].split('.')))
 packages=[ROOT/'site/package.json',ROOT/'site/package-lock.json']
 for p in packages:assert target>tuple(map(int,read(p)['version'].split('.'))),'Publication version must advance latest site'
 assert (CAN/'meta.json').is_file()
 originals={p:p.read_bytes() for p in packages}
 reports={p:p.read_bytes() if p.exists() else None for p in [OUT/'site-contract.json',OUT/'integration.json']}
 with tempfile.TemporaryDirectory(prefix='number-of-provinces-integration-') as tmp:
  backup=Path(tmp)/'canonical';shutil.copytree(CAN,backup)
  try:integrate_write(a)
  except Exception:
   shutil.rmtree(CAN);shutil.copytree(backup,CAN)
   for p,b in originals.items():p.write_bytes(b)
   for p,b in reports.items():
    if b is None:p.unlink(missing_ok=True)
    else:p.write_bytes(b)
   raise
class Document(HTMLParser):
 def __init__(self,b):super().__init__(convert_charrefs=True);self.attrs=[];self.text='';self.items=[];self.stack=[];self.feed(b)
 def handle_starttag(self,t,attrs):
  a=dict(attrs);self.attrs.append((t,a))
  if t=='li':x={'links':[]};self.items.append(x);self.stack.append(x)
  if t=='a':
   for x in self.stack:x['links'].append(a.get('href',''))
 def handle_endtag(self,t):
  if t=='li' and self.stack:self.stack.pop()
 def handle_data(self,t):self.text+=t
 def links(self):return [a.get('href','') for t,a in self.attrs if t=='a']
def online(a):
 history=read(OUT/'online-attempts.json') if (OUT/'online-attempts.json').exists() else {'attempts':[]};attempt={'startedAt':now(),'status':'running','http':[]};history['attempts'].append(attempt)
 try:
  c=contract(a.baseline,a.revision_tag);local_qa=read(OUT/'qa-site.json')
  assert local_qa['status']=='passed' and local_qa['actualScreenshotReviewPending'] is False
  assert local_qa['revisionTag']==a.revision_tag and local_qa['video']==c['video'] and local_qa['freeze']==c['freeze']
  ref=gh(f'git/ref/tags/{a.revision_tag}');assert ref['object']['type']=='tag';tag=gh('git/tags/'+ref['object']['sha']);commit=tag['object']['sha'];release=gh(f'releases/tags/{a.revision_tag}');run=gh(f'actions/runs/{a.run}')
  assert release['tag_name']==a.revision_tag and not release['draft'] and not release['prerelease']
  assert run['head_branch']=='main'
  assert run['status']=='completed' and run['conclusion']=='success' and run['head_sha']==commit and run['event']=='workflow_dispatch'
  assert not git('diff','--name-only',a.baseline,commit,'--','episodes',f':(exclude)episodes/{SLUG}').strip()
  for n in ['meta.json','article.mdx','script.md','storyboard.json','references.json','reference-appendix.json','reference-appendix-media-check.json','render-result.json','source-sha256.json']:
   assert sha(CAN/n)==digest(git('show',commit+':'+f'episodes/{SLUG}/'+n)),n
  assert datetime.fromisoformat(run['created_at'].replace('Z','+00:00'))>datetime.fromisoformat(release['published_at'].replace('Z','+00:00'))
  def get(rel):
   attempt['stage']=BASE+rel
   start=time.monotonic();req=urllib.request.Request(BASE+rel,headers={'User-Agent':'video-studio-number-of-provinces-qa'})
   with urllib.request.urlopen(req,timeout=60) as r:body=r.read();assert r.status==200
   attempt['http'].append({'url':BASE+rel,'status':200,'bytes':len(body),'sha256':digest(body),'seconds':round(time.monotonic()-start,3)});return body
  prefix=f'episodes/{SLUG}/';page=Document(get(prefix).decode());assert c['meta']['title'] in page.text and 'LC.547' in page.text
  for name in [c['meta']['video'],c['meta']['poster']]+[x['path'].split(f'episodes/{SLUG}/',1)[1] for x in c['figures']]:
   b=get(prefix+name);assert digest(b)==sha(CAN/name)==digest(git('show',commit+':'+f'episodes/{SLUG}/'+name))
  vtt=get(prefix+'captions.vtt');local=ROOT/'site/dist/episodes'/SLUG/'captions.vtt';assert digest(vtt)==sha(local);assert len(re.findall(rb' --> ',vtt))==len(c['cues'])
  for q in c['quotes']:assert q['text'] in page.text and q['title'] in page.text and q['url'] in page.links()
  for f in c['figures']:assert any(t=='a' and x.get('data-seek-time')==str(f['seekTo']).rstrip('0').rstrip('.') for t,x in page.attrs) or any(t=='a' and abs(float(x.get('data-seek-time','-1'))-f['seekTo'])<1e-6 for t,x in page.attrs)
  for rel in ['','learn/','series/leetcode/','library/','rss.xml']:
   b=get(rel).decode();assert f'episodes/{SLUG}/' in b if rel!='learn/' else 'LeetCode' in b
  changelog=Document(get('changelog/').decode());items=[i for i in changelog.items if release['html_url'] in i['links']];assert len(items)==1;assert {u for u in items[0]['links'] if re.fullmatch('/video-studio/episodes/[a-z0-9-]+/',u)}=={f'/video-studio/episodes/{SLUG}/'}
  attempt.update(status='passed',finishedAt=now());report={'status':'passed','checkedAt':now(),'revisionTag':a.revision_tag,'taggedCommit':commit,'release':{k:release[k] for k in ['html_url','tag_name','published_at']},'deployment':{k:run[k] for k in ['id','html_url','status','conclusion','head_sha','created_at','updated_at']},'video':c['video'],'http':attempt['http'],'preservedFiles':c['preservation']['fileCount'],'preservedCourses':c['preservation']['publishedCourses'],'limits':['Actual browser/player/citation interaction checks are in qa-site.json. No ASR,human full listening,physical-device or learning-outcome claim.']};save(OUT/'online-verification.json',report);print(json.dumps({'status':'passed','http':len(attempt['http']),'bytes':sum(x['bytes'] for x in attempt['http']),'videoSHA256':c['video']['sha256']}))
 except Exception as error:attempt.update(status='failed',finishedAt=now(),error=f'{type(error).__name__}: {error}');raise
 finally:save(OUT/'online-attempts.json',history)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['integrate','contract','online']);p.add_argument('--baseline',required=True);p.add_argument('--revision-tag',required=True);p.add_argument('--video-sha');p.add_argument('--run',type=int);a=p.parse_args();assert re.fullmatch(r'v\d+\.\d+\.\d+',a.revision_tag);a.baseline=git('rev-parse',a.baseline+'^{commit}').decode().strip()
 if a.mode=='integrate':assert a.video_sha;integrate(a)
 elif a.mode=='contract':save(OUT/'site-contract.json',contract(a.baseline,a.revision_tag));print('contract passed')
 else:assert a.run;online(a)
if __name__=='__main__':main()
