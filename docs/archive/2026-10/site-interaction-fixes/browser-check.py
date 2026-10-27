import functools,http.server,json,pathlib,re,threading,traceback
from urllib.parse import unquote,urlsplit
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[4]; OUT=pathlib.Path('/tmp/grok-ui'); OUT.mkdir(exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
 def translate_path(self,path):
  if path.startswith('/video-studio/'):
   path=path[len('/video-studio'):]
  return super().translate_path(path)
 def send_error(self,code,message=None,explain=None):
  if code==404:
   data=(ROOT/'site/dist/404.html').read_bytes();self.send_response(404);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
  else:super().send_error(code,message,explain)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT/'site/dist')))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/video-studio/'
report={'base':BASE,'scope':'isolated Chromium on built site, local 404 fallback emulates Pages; remote production not covered','checks':[],'screenshots':[],'errors':[]}
def record(name,detail=None): report['checks'].append({'name':name,'detail':detail})
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(1440,1000),(390,844)]:
  for theme in ['light','dark']:
   label=f'{width}-{theme}'; ctx=browser.new_context(viewport={'width':width,'height':height},color_scheme=theme)
   ctx.add_init_script(f"localStorage.setItem('vs:theme','{theme}');")
   page=ctx.new_page(); page.set_default_timeout(12000)
   errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
   def go(route):
    response=page.goto(BASE+route,wait_until='domcontentloaded');
    assert response.status==200,(route,response.status)
    assert page.locator('html').get_attribute('data-theme')==theme
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'overflow {route}'
    record(f'{label}:route+theme+no-overflow',route)
   def snap(name,full=False):
    path=OUT/f'{label}-{name}.png';page.screenshot(path=str(path),full_page=full);report['screenshots'].append(str(path))
   try:
    for route in ['', 'library/']:
     go(route)
     cards=page.locator('a.card'); assert cards.count()>0
     data=cards.evaluate_all("els=>els.map(e=>({timeCount:e.querySelectorAll('time').length,time:e.querySelector('time')?.textContent,text:e.querySelector('.meta').textContent}))")
     for c in data:
      assert c['timeCount']==1,c
      assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',c['time']),c
      assert '更新于' in c['text'] and not re.search(r'创建于|修改于|版|\d{2}:\d{2}',c['text']),c
     record(f'{label}:cards-one-day-only',{'route':route or '/', 'count':len(data),'sample':data[0]})
     cards.first.scroll_into_view_if_needed();snap('home-cards' if not route else 'library-cards')
    go('learn/');directory=page.locator('nav[aria-label="系列直达"]');assert directory.count()==1
    links=directory.locator('a');assert links.count()>=8
    targets=links.evaluate_all('els=>els.map(e=>({label:e.textContent,href:e.getAttribute("href")}))')
    assert all(re.fullmatch(r'/video-studio/series/[a-z0-9-]+/',x['href']) for x in targets)
    page.evaluate('scrollTo(0,1500)');page.wait_for_timeout(150)
    bounds=directory.bounding_box();assert bounds and 0<=bounds['y']<120,bounds
    assert directory.evaluate("e=>getComputedStyle(e).position")=='sticky'
    record(f'{label}:sticky-series-directory',{'targets':targets,'scrolledY':bounds['y']});snap('learn-sticky')
    directory.locator('a[href$="/series/message-queue/"]').scroll_into_view_if_needed();directory.locator('a[href$="/series/message-queue/"]').click();page.wait_for_load_state('domcontentloaded')
    assert page.url.endswith('/series/message-queue/')
    assert page.locator('[data-episode-numbering]').is_visible()
    assert '完整路线' not in page.locator('main').inner_text()
    record(f'{label}:series-direct-navigation+numbering',page.url)
    go('series/design-patterns/');note=page.locator('[data-episode-numbering]');assert note.is_visible()
    assert '历史发布编号' in note.inner_text() and '重号' in note.inner_text()
    assert page.locator('.lesson-number').all_text_contents()==['01','02','03']
    record(f'{label}:design-series-order+EP-note');snap('design-numbering')
    for slug in ['message-queue','observer-pattern']:
     go(f'episodes/{slug}/')
     top=page.locator('nav.source-links');assert top.is_visible();assert top.locator('a').count()==3
     topHrefs=top.locator('a').evaluate_all('els=>els.map(e=>e.href)')
     assert all(re.search(r'/(blob|tree)/[0-9a-f]{40}/',href) for href in topHrefs),topHrefs
     assert all('GitHub' in t for t in top.locator('a').all_text_contents())
     bottomHrefs=page.locator('.bts a.b').evaluate_all('els=>els.map(e=>e.href)');assert topHrefs==bottomHrefs
     rawHrefs=page.locator('.bts a.raw').evaluate_all('els=>els.map(e=>e.href)');assert len(rawHrefs)==2
     assert all(re.search(r'^https://raw\.githubusercontent\.com/linhongcun/video-studio/[0-9a-f]{40}/',x) for x in rawHrefs),rawHrefs
     topBox=top.bounding_box();playerBox=page.locator('#player').bounding_box();assert topBox['y']<playerBox['y']
     page.wait_for_function("document.querySelector('video').textTracks.length===1&&document.querySelector('video').textTracks[0].mode==='showing'")
     track=page.locator('video track');assert track.get_attribute('default') is not None
     page.wait_for_function("document.querySelector('video track').readyState===2")
     cueCount=page.locator('video').evaluate('e=>e.textTracks[0].cues.length');assert cueCount>0
     record(f'{label}:{slug}:sources+default-loaded-caption',{'top':topHrefs,'raw':rawHrefs,'cues':cueCount})
     if slug=='message-queue':
      top.scroll_into_view_if_needed();snap('mq-top-sources')
      page.locator('.bts').scroll_into_view_if_needed();snap('mq-bottom-sources')
      page.locator('[data-open-course]').click();assert page.locator('#course-directory').get_attribute('open') is not None
      assert page.locator('#course-directory [data-episode-numbering]').is_visible()
      assert '本系列第 1 / 1 课' in page.locator('#course-directory summary').inner_text()
      record(f'{label}:course-directory-order-note')
    go('episodes/distributed-tx/');crumb=page.locator('nav[aria-label="面包屑"]')
    assert '系统原理' in crumb.inner_text() and '分布式' in crumb.inner_text()
    assert crumb.locator('a[href="/video-studio/series/distributed/"]').count()==1
    assert crumb.locator('a[href*="/tags/"]').count()==0
    record(f'{label}:historical-breadcrumb');snap('archive-breadcrumb')
    go('changelog/');text=page.locator('main').inner_text()
    assert not re.search(r'\]\(https?://|\bSHA\b|冻结|质检',text),text
    recent=page.locator('section[aria-labelledby="recent-releases"] .rl>li');assert recent.count()==5
    archive=page.locator('details.archive');assert archive.count()>0
    assert all(archive.nth(i).get_attribute('open') is None for i in range(archive.count()))
    assert page.locator('a.full:visible').count()==5
    assert page.locator('.eps a').count()>0 and page.locator('.resources a').count()>0
    countBefore=page.locator('a.full:visible').count();archive.first.locator('summary').click();assert page.locator('a.full:visible').count()>countBefore
    record(f'{label}:changelog-clean-links+closed-older',{'recent':5,'olderGroups':archive.count(),'expandedReleaseLinks':page.locator('a.full:visible').count()})
    archive.first.locator('summary').click();page.evaluate('scrollTo(0,0)');snap('changelog')
    go('404.html');assert '404' in page.locator('main').inner_text()
    assert page.locator('.recovery-links a').count()==3
    snap('404')
    page.locator('#missing-page-search').fill('消息队列');page.locator('button[type="submit"]').click();page.wait_for_url('**/search/?q=*')
    page.wait_for_selector('.pagefind-ui__result-link');results=page.locator('.pagefind-ui__result-link')
    assert '消息队列' in page.locator('.pagefind-ui__search-input').input_value()
    hrefs=results.evaluate_all('els=>els.map(e=>e.href)');assert any('/episodes/message-queue/' in h for h in hrefs),hrefs
    record(f'{label}:404-search-pagefind',{'results':len(hrefs),'hrefs':hrefs});snap('404-search-results')
    response=page.goto(BASE+'nonexistent/',wait_until='domcontentloaded');assert response.status==404
    assert page.locator('#missing-page-search').is_visible()
    record(f'{label}:local-404-fallback',404)
    if errors:report['errors'].append({'context':label,'pageErrors':errors})
   except Exception as err:
    report['errors'].append({'context':label,'error':str(err),'trace':traceback.format_exc(),'url':page.url});snap('failure')
   finally:ctx.close()
 browser.close()
server.shutdown()
report['passed']=not report['errors'];(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'screenshots':len(report['screenshots']),'errors':report['errors'],'report':str(OUT/'report.json')},ensure_ascii=False))
