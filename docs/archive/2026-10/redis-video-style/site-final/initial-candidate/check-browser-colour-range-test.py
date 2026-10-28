from pathlib import Path
import json,sys
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).parent));import helpers
out=Path(__file__).parent/'browser-colour/range-test';out.mkdir(exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':1000});page.goto('http://127.0.0.1:4325/video-studio/episodes/redis-skiplist/',wait_until='networkidle');page.wait_for_function('document.querySelector("video").readyState>=1');page.locator('video').evaluate("v=>{v.src='/video-studio/episodes/redis-skiplist/range-test.mp4';v.load()}");page.wait_for_function('document.querySelector("video").readyState>=3');helpers.seek_paused(page,.1)
 d=page.locator('video').evaluate('''v=>{let c=document.createElement('canvas');c.width=v.videoWidth;c.height=v.videoHeight;let x=c.getContext('2d');x.drawImage(v,0,0);return {pixel:Array.from(x.getImageData(960,270,1,1).data),data:c.toDataURL('image/png'),width:v.videoWidth,height:v.videoHeight}}''')
 import base64
 (out/'canvas.png').write_bytes(base64.b64decode(d.pop('data').split(',',1)[1]));(out/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(d);b.close()
