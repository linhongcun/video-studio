import asyncio,importlib.util,json,threading,http.server
from pathlib import Path
spec=importlib.util.spec_from_file_location('qa','/workspace/work/article-summaries/browser-qa/run.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
async def run():
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),q.LocalHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 async with q.async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page=await browser.new_page(viewport={'width':390,'height':844},color_scheme='light')
  await page.goto(f'http://127.0.0.1:{server.server_port}/video-studio/episodes/kafka-consumer-groups/',wait_until='domcontentloaded')
  await page.evaluate('document.fonts.ready')
  data=await page.evaluate('''()=>({w:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,items:[...document.querySelectorAll('html,body,body *')].map(e=>({tag:e.tagName,cls:typeof e.className==='string'?e.className:'',id:e.id,txt:e.textContent.slice(0,130),rect:e.getBoundingClientRect().toJSON(),sw:e.scrollWidth,cw:e.clientWidth,overflow:getComputedStyle(e).overflowX})).filter(e=>e.sw>e.cw+1||e.rect.right>391||e.rect.left< -1).slice(0,100)})''')
  q.QA.joinpath('overflow-diagnostic.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
  print(json.dumps(data,ensure_ascii=False,indent=2))
  await browser.close()
 server.shutdown()
asyncio.run(run())
