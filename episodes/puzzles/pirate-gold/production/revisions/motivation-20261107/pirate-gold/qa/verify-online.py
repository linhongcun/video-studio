from pathlib import Path
import urllib.request,hashlib,json,datetime,re
from html.parser import HTMLParser
R=Path('/workspace/video-studio'); D=R/'episodes/puzzles/pirate-gold/production/revisions/motivation-20261107/pirate-gold'; P=R/'episodes/puzzles/pirate-gold/publication'
BASE='https://linhongcun.github.io/video-studio/'
checks=[]
def get(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'video-studio-pirate-motivation-qa','Cache-Control':'no-cache'})
 with urllib.request.urlopen(req,timeout=60) as r:
  data=r.read(); checks.append({'url':BASE+path,'status':r.status,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
  assert r.status==200
 return data
for rel,local in [('episodes/pirate-gold/video.mp4',P/'video.mp4'),('episodes/pirate-gold/cover-16x9.jpg',P/'cover-16x9.jpg'),('episodes/pirate-gold/article/01.jpg',P/'article/01.jpg'),('episodes/pirate-gold/article/02.jpg',P/'article/02.jpg'),('episodes/pirate-gold/captions.vtt',R/'site/dist/episodes/pirate-gold/captions.vtt')]:
 data=get(rel); assert hashlib.sha256(data).hexdigest()==hashlib.sha256(local.read_bytes()).hexdigest(),rel
 checks[-1]['matchesLocalFullSHA256']=True
html=get('episodes/pirate-gold/').decode()
class Tags(HTMLParser):
 def __init__(self):super().__init__();self.tags=[]
 def handle_starttag(self,tag,attrs):
  self.tags.append([tag,dict(attrs)])
t=Tags();t.feed(html)
assert any(tag=='video' and 'controls' in a for tag,a in t.tags)
assert any(tag=='source' and a.get('src','').endswith('/pirate-gold/video.mp4') for tag,a in t.tags)
assert any(tag=='track' and a.get('kind')=='captions' and 'default' not in a for tag,a in t.tags)
meta=json.loads((P/'meta.json').read_text())
assert meta['sourcePath'] in html
assert any(tag=='time' and a.get('aria-label')=='当前版本' and a.get('datetime')==meta['updatedAt'] for tag,a in t.tags)
merge=json.loads(Path('/workspace/work/pirate-motivation/merge-result.json').read_text())['sha']
expected_source='https://github.com/linhongcun/video-studio/tree/'+merge+'/'+meta['sourcePath']
assert any(tag=='a' and a.get('href')==expected_source for tag,a in t.tags)
footer=re.search(r'<footer\b[^>]*>(.*?)</footer>',html,re.S)
assert footer and 'v0.105.2' in footer.group(1)
expected_chapters=json.loads((R/'site/dist/episodes/pirate-gold/index.html').read_text().split('data-chapters="',1)[1].split('"',1)[0].replace('&#34;','"'))
actual_chapters=json.loads(next(a['data-chapters'] for tag,a in t.tags if a.get('id')=='player'))
assert actual_chapters==expected_chapters
assert any(c['id']=='backwards' and c['title']=='为什么从两人局倒推' and c['start']==35.9 for c in actual_chapters)
assert {a['data-seek-time'] for tag,a in t.tags if 'data-seek-time' in a}=={'114','159.5'}
changelog=get('changelog/').decode();assert 'v0.105.2' in changelog
series=get('series/puzzles/').decode();assert '/episodes/pirate-gold/' in series
report={'status':'passed','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'canonicalFullGETs':checks,'playerHTML':{'nativeControls':True,'correctVideoSource':True,'captionsDefaultOffForBurnedInVideo':True,'currentRevisionSourceLink':expected_source,'updatedAt':meta['updatedAt'],'footerVersion':'v0.105.2','chapters':actual_chapters,'figureSeekSeconds':[114,159.5]},'release':'v0.105.2','limitations':['HTTP, exact asset identity and HTML checks only. Actual local Chromium playback, seek, figure return and fullscreen checks are recorded separately; no physical device claim.']}
(D/'qa/online-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'passed','fullGETs':len(checks),'videoSHA256':checks[0]['sha256']}))
