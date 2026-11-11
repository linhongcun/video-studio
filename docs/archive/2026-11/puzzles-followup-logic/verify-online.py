#!/usr/bin/env python3
"""Canonical full GET and HTML identity checks; browser QA is separate."""
from pathlib import Path
from html.parser import HTMLParser
from datetime import datetime,timezone
import argparse,hashlib,json,re,urllib.request
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
TASK=Path(__file__).resolve().parent
BASE='https://linhongcun.github.io/video-studio/'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text())
class Tags(HTMLParser):
 def __init__(self):super().__init__();self.tags=[]
 def handle_starttag(self,t,attrs):self.tags.append((t,dict(attrs)))
def player_chapters(tags,label):
 players=[a for t,a in tags.tags if a.get('id')=='player']
 assert len(players)==1 and 'data-chapters' in players[0],label+': missing or duplicate player chapter data'
 chapters=json.loads(players[0]['data-chapters'])
 assert isinstance(chapters,list) and chapters,label+': chapter data must be a nonempty list'
 assert all(isinstance(c,dict) and set(c)=={'id','title','start'} and isinstance(c['id'],str) and isinstance(c['title'],str) and type(c['start']) in (int,float) for c in chapters),label+': invalid id/title/start chapter data'
 return chapters
def local_chapter_expectation(slug,publication):
 local=ROOT/'site/dist/episodes'/slug/'index.html'
 body=local.read_bytes();tags=Tags();tags.feed(body.decode('utf-8'))
 expected=player_chapters(tags,'local '+slug)
 sb=read(publication/'storyboard.json');fps=sb['meta']['fps']
 assert type(fps) in (int,float) and fps>0,'Invalid storyboard fps: '+slug
 positions=[{'id':c['id'],'start':c['start']} for c in expected]
 storyboard_positions=[{'id':c['id'],'start':c['from']/fps} for c in sb['scenes']]
 assert positions==storyboard_positions,'Local built chapter ids/starts differ from current publication storyboard: '+slug
 # Display titles may be supplied by article frontmatter. Preserve the actual
 # locally reviewed player labels while checking their timing independently.
 return expected,{'path':str(local.relative_to(ROOT)),'sha256':sha(body),'bytes':len(body),'storyboardSHA256':sha((publication/'storyboard.json').read_bytes()),'storyboardFPS':fps,'idsAndStartsMatchStoryboard':True}
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--merge-sha',required=True);parser.add_argument('--version',default='v0.105.3');parser.add_argument('--run',default='canonical-v1')
 args=parser.parse_args();assert re.fullmatch(r'[0-9a-f]{40}',args.merge_sha)
 assert re.fullmatch(r'[a-zA-Z0-9_-]+',args.run)
 output=TASK/'online'/(args.run+'.json');assert not output.exists(),'Preserve previous verification attempts'
 output.parent.mkdir(parents=True,exist_ok=True)
 report={'status':'running','startedAt':datetime.now(timezone.utc).isoformat(),'mergeCommit':args.merge_sha,'release':args.version,'canonicalFullGETs':[],'pages':[],'scope':'Online full-asset HTTP and HTML identity only; actual local Chromium actions and screenshots are separate. No online browser/device/listening/user-acceptance claim.'}
 def save():output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 def get(rel,local=None):
  req=urllib.request.Request(BASE+rel,headers={'User-Agent':'video-studio-puzzles-followup-qa','Cache-Control':'no-cache'})
  with urllib.request.urlopen(req,timeout=60) as response:
   body=response.read();assert response.status==200
   row={'url':BASE+rel,'status':response.status,'bytes':len(body),'sha256':sha(body)}
   report['canonicalFullGETs'].append(row);save()
   if local is not None:
    assert row['sha256']==sha(local.read_bytes()),'Full SHA mismatch: '+rel
    row['matchesLocalFullSHA256']=True;save()
  return body
 save()
 try:
  for slug in ['twelve-balls','prisoners-light','hat-parity']:
   p=ROOT/'episodes/puzzles'/slug/'publication';meta=read(p/'meta.json')
   expected,local_html=local_chapter_expectation(slug,p)
   get('episodes/'+slug+'/video.mp4',p/'video.mp4')
   if slug!='hat-parity':
    for rel,local in [('cover-16x9.jpg',p/'cover-16x9.jpg'),('captions.vtt',ROOT/'site/dist/episodes'/slug/'captions.vtt'),('article/01.jpg',p/'article/01.jpg'),('article/02.jpg',p/'article/02.jpg')]:
     get('episodes/'+slug+'/'+rel,local)
   html=get('episodes/'+slug+'/').decode();tags=Tags();tags.feed(html)
   assert any(t=='video' and 'controls' in a for t,a in tags.tags)
   assert any(t=='source' and a.get('src','').endswith('/'+slug+'/video.mp4') for t,a in tags.tags)
   assert any(t=='track' and a.get('kind')=='captions' and 'default' not in a for t,a in tags.tags)
   expected_source='https://github.com/linhongcun/video-studio/tree/'+args.merge_sha+'/'+meta['sourcePath']
   assert any(t=='a' and a.get('href')==expected_source for t,a in tags.tags)
   assert any(t=='time' and a.get('aria-label')=='当前版本' and a.get('datetime')==meta['updatedAt'] for t,a in tags.tags)
   footer=re.search(r'<footer\b[^>]*>(.*?)</footer>',html,re.S);assert footer and args.version in footer.group(1)
   chapters=player_chapters(tags,'online '+slug)
   assert chapters==expected,'Online chapter ids/titles/starts differ from reviewed local player: '+slug
   expected_figs={float(s) for s in re.findall(r'<Figure\s+[^>]*?seekTo=\{([0-9.]+)\}',(p/'article.mdx').read_text(),re.S)}
   actual_figs={float(a['data-seek-time']) for t,a in tags.tags if 'data-seek-time' in a}
   assert expected_figs==actual_figs and len(actual_figs)==2
   report['pages'].append({'slug':slug,'updatedAt':meta['updatedAt'],'currentRevisionSourceLink':expected_source,'footerVersion':args.version,'chapters':chapters,'expectedLocalChapters':expected,'localDistHTML':local_html,'figureSeekSeconds':sorted(actual_figs),'nativeControls':True,'captionsDefaultOff':True,'mediaChangedInThisBatch':slug!='hat-parity'});save()
  series=get('series/puzzles/').decode();assert all('/episodes/'+s+'/' in series for s in ['hat-parity','twelve-balls','prisoners-light'])
  changelog=get('changelog/').decode();assert args.version in changelog
  report.update(status='passed',checkedAt=datetime.now(timezone.utc).isoformat());save()
  print(json.dumps({'status':'passed','fullGETs':len(report['canonicalFullGETs']),'report':str(output.relative_to(ROOT))}))
 except Exception as exc:
  report.update(status='failed',failedAt=datetime.now(timezone.utc).isoformat(),error=str(exc));save();raise
if __name__=='__main__':main()
