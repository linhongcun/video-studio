#!/usr/bin/env python3
"""P06 complete ordinary HTTPS GET identity checks, separate from native browser QA.

Pages exposes derived HTML/VTT and media, not raw meta/storyboard JSON. Those
JSON bytes are additionally read from the declared Git commit on GitHub.
"""
from pathlib import Path
from datetime import datetime, timezone
from html.parser import HTMLParser
import argparse,hashlib,importlib.util,json,math,re,subprocess,traceback,urllib.request
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
D=Path(__file__).resolve().parents[1];P=D.parent/'publication';SLUG=D.parent.name
BASE='https://linhongcun.github.io/video-studio'
spec=importlib.util.spec_from_file_location('served_html_checks',ROOT/'scripts/verify-online.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
sha=lambda b:hashlib.sha256(b).hexdigest()
class EpisodeHTML(HTMLParser):
 def __init__(self,body):
  super().__init__();self.video=[];self.source=[];self.track=[];self.replays=[];self.images=[];self.triggers=[];self.feed(body.decode())
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='video':self.video.append(a)
  if tag=='source':self.source.append(a)
  if tag=='track':self.track.append(a)
  if 'data-seek-time' in a:self.replays.append(float(a['data-seek-time']))
  if tag=='img':self.images.append(a)
  if 'data-source-trigger' in a:self.triggers.append(a['data-source-trigger'])
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--version',required=True);ap.add_argument('--commit',required=True);ap.add_argument('--out',type=Path,default=D/'qa/site-online-http-verification.json');a=ap.parse_args()
 assert re.fullmatch(r'[0-9a-f]{40}',a.commit),'Use full deployment commit SHA'
 assert re.fullmatch(r'v\d+\.\d+\.\d+',a.version),'Use actual release version'
 assert not a.out.exists(),'Preserve a previous receipt; choose a fresh --out'
 report={'startedAtUTC':datetime.now(timezone.utc).isoformat(),'passed':False,'httpChecks':[],'deploymentCommit':a.commit,'version':a.version,'scope':'Complete ordinary canonical Pages GET bytes plus raw meta/storyboard at declared Git commit. No cache-busting, route fulfillment, TLS bypass or browser-result claims.','limitations':['Raw metadata/storyboard are not Pages endpoints; they are verified separately at the deployment Git commit.','Native playback, visual reading, source semantics, ASR and hearing are separate reviews.']}
 def get(url,scope):
  with urllib.request.urlopen(url,timeout=120)as r:
   body=r.read();report['httpChecks'].append({'scope':scope,'url':url,'status':r.status,'bytes':len(body),'sha256':sha(body)});assert r.status==200
  return body
 try:
  meta=json.loads((P/'meta.json').read_text());sb=json.loads((P/'storyboard.json').read_text());receipt=json.loads((D/'reference-appendix.json').read_text())
  assert meta['slug']==SLUG and meta['ep']==56 and meta['series']=='puzzles' and not meta.get('draft')
  assert meta['title']=='12球称重：轻重未知，怎样只称3次找出异常球？' and meta['firstRelease']==a.version
  assert sha((P/meta['video']).read_bytes())==sha((D/'video.mp4').read_bytes())==receipt['outputSHA256']
  assert (P/'references.json').read_bytes()==(D/'references.json').read_bytes() and sha((D/'references.json').read_bytes())==receipt['inputs']['referencesSHA256']
  assert (P/'article.mdx').read_bytes()==(D/'article.mdx').read_bytes()
  for name in [meta['video'],meta['poster'],'article/01.jpg','article/02.jpg']:
   assert sha(get(BASE+f'/episodes/{SLUG}/'+name,'canonical Pages'))==sha((P/name).read_bytes()),name
  publication_rel=P.relative_to(ROOT)
  for name in ['meta.json','storyboard.json']:
   url=f'https://raw.githubusercontent.com/linhongcun/video-studio/{a.commit}/{publication_rel}/{name}'
   assert get(url,'raw repository bytes at deployment commit')==(P/name).read_bytes(),name
  _,groups,frames=module.frozen_vtt_and_chapters(sb)
  fps=sb['meta']['fps'];card=meta['referenceAppendix']['from'];cues=[]
  assert card==receipt['bodyFrames']==frames and meta['finalVideoFrames']==receipt['finalVideoFrames']
  def stamp(ms):return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d}.{ms%1000:03d}'
  for scene in sb['scenes']:
   for shot in scene['shots']:
    for row in shot['subtitles']:
     start=shot['from']+row['from'];end=shot['from']+row['to']+1
     start_ms=round(start*1000/fps);end_ms=math.ceil(end*1000/fps)-1 if end==card else round(end*1000/fps)
     cues.append(f"{stamp(start_ms)} --> {stamp(end_ms)}\n{row['text']}")
  vtt=('WEBVTT\n\n'+'\n\n'.join(cues)+'\n').encode();served=get(BASE+f'/episodes/{SLUG}/captions.vtt','canonical Pages')
  assert served==vtt==(ROOT/f'site/dist/episodes/{SLUG}/captions.vtt').read_bytes()
  html=get(BASE+f'/episodes/{SLUG}/','canonical Pages');page=module.Page(html);detail=EpisodeHTML(html)
  assert page.h1==meta['title'] and len(page.chapters)==len(groups)
  for actual,group in zip(page.chapters,groups):assert actual['id']in group['ids'] and abs(actual['start']-group['start'])<1e-6
  assert f'https://github.com/linhongcun/video-studio/tree/{a.commit}/{meta["sourcePath"]}'in page.links
  assert len(detail.video)==1 and detail.video[0]['poster']==f'/video-studio/episodes/{SLUG}/{meta["poster"]}'
  assert any(s.get('src')==f'/video-studio/episodes/{SLUG}/{meta["video"]}'for s in detail.source)
  assert len(detail.track)==1 and 'default' not in detail.track[0] and meta['burnedInCaptions']
  assert detail.track[0]['src']==f'/video-studio/episodes/{SLUG}/captions.vtt'
  article=(P/'article.mdx').read_text();figure_times=[float(t)for t in re.findall(r'<Figure\b[^>]*seekTo=\{([0-9.]+)\}',article)]
  assert len(cues)==30 and len(groups)==5
  assert len(figure_times)==2 and detail.replays==figure_times
  assert all(0<t<card/fps for t in figure_times)
  assert set(detail.triggers)=={'R1','R2'}
  for name in ['01.jpg','02.jpg']:assert any(x.get('src')==f'/video-studio/episodes/{SLUG}/article/{name}'for x in detail.images)
  assert meta['finalVideoFrames']==frames+receipt['appendix']['durationInFrames']
  for path in ['/series/puzzles/','/library/','/rss.xml']:assert SLUG in get(BASE+path,'canonical Pages').decode()
  changelog=module.Page(get(BASE+'/changelog/','canonical Pages'));assert changelog.contains_version(a.version)
  assert f'https://github.com/linhongcun/video-studio/releases/tag/{a.version}'in changelog.links
  release=json.loads(subprocess.check_output(['gh','api',f'repos/linhongcun/video-studio/releases/tags/{a.version}'],text=True));assert release['tag_name']==a.version and not release['draft']
  report.update(passed=True,captions=len(cues),chapters=page.chapters,bodyFrames=frames,finalFrames=meta['finalVideoFrames'],figureTimes=figure_times,videoSHA256=receipt['outputSHA256'],metadataSHA256=sha((P/'meta.json').read_bytes()),storyboardSHA256=sha((P/'storyboard.json').read_bytes()),release={k:release[k]for k in ['tag_name','html_url','published_at','target_commitish']})
 except Exception as e:
  report['failure']={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()};raise
 finally:
  report['finishedAtUTC']=datetime.now(timezone.utc).isoformat();a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'passed':True,'canonicalGETs':sum(c['scope']=='canonical Pages'for c in report['httpChecks']),'rawCommitGETs':sum(c['scope'].startswith('raw repository')for c in report['httpChecks']),'videoSHA256':report['videoSHA256'],'release':release['html_url']},ensure_ascii=False))
if __name__=='__main__':main()
