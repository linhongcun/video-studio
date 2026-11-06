from pathlib import Path
import urllib.request,hashlib,json,datetime
from html.parser import HTMLParser
R=Path('/workspace/video-studio'); D=R/'episodes/puzzles/pirate-gold/production/revisions/clarity-20261106/pirate-gold'; P=R/'episodes/puzzles/pirate-gold/publication'
BASE='https://linhongcun.github.io/video-studio/'
checks=[]
def get(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'video-studio-pirate-clarity-qa','Cache-Control':'no-cache'})
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
  if tag in ('video','source','track','img','button'):self.tags.append([tag,dict(attrs)])
t=Tags();t.feed(html)
assert any(tag=='video' and 'controls' in a for tag,a in t.tags)
assert any(tag=='source' and a.get('src','').endswith('/pirate-gold/video.mp4') for tag,a in t.tags)
assert any(tag=='track' and a.get('kind')=='captions' and 'default' not in a for tag,a in t.tags)
meta=json.loads((P/'meta.json').read_text())
assert meta['sourcePath'] in html
assert '2026-11-06' in html
changelog=get('changelog/').decode();assert 'v0.105.1' in changelog
series=get('series/puzzles/').decode();assert '/episodes/pirate-gold/' in series
report={'status':'passed','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'canonicalFullGETs':checks,'playerHTML':{'nativeControls':True,'correctVideoSource':True,'captionsDefaultOffForBurnedInVideo':True,'currentRevisionSourceLink':True,'versionDate':'2026-11-06'},'release':'v0.105.1','limitations':['HTTP, exact asset identity and HTML checks only. No browser interaction/fullscreen or real-device playback was available in this session.']}
(D/'qa/online-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'passed','fullGETs':len(checks),'videoSHA256':checks[0]['sha256']}))
