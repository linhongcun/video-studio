import hashlib, json, threading, functools, http.server
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path('/workspace/video-studio')
out=Path('/workspace/work/puzzles-site-check');out.mkdir(exist_ok=True)
catalog=json.loads((root/'episodes-codex/_shared/puzzles-covers/catalog.json').read_text())
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def translate_path(self,path):
  if path.startswith('/video-studio/'):
   path=path[len('/video-studio'):]
  return super().translate_path(path)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root/'site/dist')))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/video-studio'
report={'checked':[],'images':[]}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=b.new_page()
 for width,height in [(1440,1000),(390,844)]:
  page.set_viewport_size({'width':width,'height':height})
  page.goto(base+'/series/puzzles/',wait_until='domcontentloaded')
  imgs=page.locator('img[src*="cover-16x9.jpg"]')
  assert imgs.count()==5,imgs.count()
  imgs.evaluate_all('(els)=>els.forEach(e=>e.loading="eager")')
  page.wait_for_function('Array.from(document.querySelectorAll("img[src*=\\\"cover-16x9.jpg\\\"]")).every(i=>i.complete&&i.naturalWidth===1920)')
  imgs.evaluate_all('(els)=>Promise.all(els.map(e=>e.decode()))')
  if width>600:
   for image in imgs.all():
    image.scroll_into_view_if_needed()
    page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
   page.evaluate('scrollTo(0,0)')
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.screenshot(path=str(out/f'series-{width}.png'),full_page=True)
  report['checked'].append({'page':'series/puzzles','width':width,'coverCount':imgs.count(),'visibleCoverCount':sum(i.is_visible() for i in imgs.all()),'overflow':False})
  page.goto(base+'/episodes/bridge-torch/',wait_until='domcontentloaded')
  video=page.locator('video').first
  assert 'cover-16x9.jpg' in video.get_attribute('poster')
  video.scroll_into_view_if_needed()
  page.evaluate('''async()=>{const im=new Image();im.src=document.querySelector("video").poster;await im.decode();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))}''')
  page.screenshot(path=str(out/f'episode-{width}.png'),full_page=False)
  report['checked'].append({'page':'episodes/bridge-torch','width':width,'poster':video.get_attribute('poster')})
 b.close()
server.shutdown()
for ep in catalog['episodes']:
 source=root/'episodes'/ep['slug']/'cover-16x9.jpg'
 public=root/'site/dist/episodes'/ep['slug']/'cover-16x9.jpg'
 assert hashlib.sha256(source.read_bytes()).digest()==hashlib.sha256(public.read_bytes()).digest()
 report['images'].append({'slug':ep['slug'],'sourceEqualsBuilt':True,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
report['passed']=True
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
