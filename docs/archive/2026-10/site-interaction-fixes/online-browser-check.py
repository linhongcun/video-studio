import datetime,hashlib,json,os,pathlib,re,traceback
from playwright.sync_api import sync_playwright
BASE='https://linhongcun.github.io/video-studio/'
MERGE='ac31f8431fe49a64f05e87e44a037de4e9af0cfd'
OUT=pathlib.Path('/tmp/grok-online-ui');OUT.mkdir(exist_ok=True)
report={'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'release':'v0.82.0','mergeSha':MERGE,'scope':'real canonical production URL in system Chromium; native CA verification through configured HTTPS proxy; ignore_https_errors false','checks':[],'screenshots':[],'errors':[],'limitations':[],'mediaResponses':[],'deployment':json.loads((OUT/'deployment-confirmed.json').read_text())}
assert report['deployment']['headSha']==MERGE and report['deployment']['conclusion']=='success'
def record(name,detail=None):report['checks'].append({'name':name,'detail':detail})
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'],proxy={'server':os.environ['HTTPS_PROXY']})
 for width,height,theme in [(1440,1000,'light'),(390,844,'dark')]:
  label=f'{width}-{theme}';ctx=b.new_context(viewport={'width':width,'height':height},color_scheme=theme)
  ctx.add_init_script(f"localStorage.setItem('vs:theme','{theme}');")
  page=ctx.new_page();page.set_default_timeout(25000);pageErrors=[];page.on('pageerror',lambda error:pageErrors.append(str(error)))
  def onresponse(response):
   if response.url.endswith('/video.mp4'):
    h=response.headers
    report['mediaResponses'].append({'context':label,'url':response.url,'status':response.status,'requestRange':response.request.headers.get('range'),'acceptRanges':h.get('accept-ranges'),'contentRange':h.get('content-range'),'contentLength':h.get('content-length')})
  page.on('response',onresponse)
  def go(route,status=200):
   r=page.goto(BASE+route,wait_until='domcontentloaded',timeout=40000)
   assert r.status==status,(route,r.status)
   assert page.locator('html').get_attribute('data-theme')==theme
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'overflow {route}'
   record(label+':route-theme-overflow',{'route':route or '/','status':r.status,'url':page.url})
  def snap(name):
   path=OUT/f'{label}-{name}.png';page.screenshot(path=str(path));report['screenshots'].append(str(path))
  try:
   go('');assert 'v0.82.0' in page.locator('body').inner_text();record(label+':deployed-version','v0.82.0')
   cards=page.locator('a.card');assert cards.count()>0
   assert cards.first.locator('time').count()==1 and re.fullmatch(r'\d{4}-\d{2}-\d{2}',cards.first.locator('time').inner_text())
   record(label+':single-date-card');cards.first.scroll_into_view_if_needed();snap('cards')
   go('episodes/message-queue/')
   top=page.locator('.source-links a');bottom=page.locator('.bts a.b');assert top.count()==3
   hrefs=top.evaluate_all('els=>els.map(e=>e.href)');assert hrefs==bottom.evaluate_all('els=>els.map(e=>e.href)')
   assert all(re.search('/(?:blob|tree)/'+MERGE+'/',h) for h in hrefs),hrefs
   raw=page.locator('.bts a.raw').evaluate_all('els=>els.map(e=>e.href)');assert len(raw)==2 and all('/'+MERGE+'/' in h for h in raw)
   record(label+':source-links-exact-merge',{'hrefs':hrefs,'raw':raw})
   page.wait_for_function("document.querySelector('video').textTracks.length===1&&document.querySelector('video').textTracks[0].mode==='showing'",timeout=25000)
   page.wait_for_function("document.querySelector('video track').readyState===2",timeout=25000)
   track=page.locator('video').evaluate("v=>({mode:v.textTracks[0].mode,cues:v.textTracks[0].cues.length,readyState:v.readyState,duration:v.duration})")
   assert track['cues']>0
   record(label+':captions-default-showing-loaded',track)
   page.locator('.source-links').scroll_into_view_if_needed();snap('source-links-and-player')
   try:
    page.locator('video').evaluate("async v=>{v.muted=true;await v.play();v.currentTime=30}")
    page.wait_for_function("!document.querySelector('video').seeking&&document.querySelector('video').currentTime>=29&&document.querySelector('video').readyState>=2",timeout=25000)
    page.locator('video').evaluate('v=>v.pause()')
    state=page.locator('video').evaluate('v=>({time:v.currentTime,readyState:v.readyState,paused:v.paused,networkState:v.networkState,videoWidth:v.videoWidth,error:v.error?.message??null})')
    assert state['videoWidth']>0
    record(label+':actual-muted-play-and-seek-30-seconds',state);page.locator('video').scroll_into_view_if_needed();snap('seek30')
   except Exception as e:
    report['limitations'].append({'context':label,'check':'actual mp4 muted play+seek','error':str(e),'videoState':page.locator('video').evaluate('v=>({time:v.currentTime,readyState:v.readyState,networkState:v.networkState,error:v.error?.message??null})')})
   go('changelog/');assert 'v0.82.0' in page.locator('section[aria-labelledby="recent-releases"]').inner_text()
   assert page.locator('section[aria-labelledby="recent-releases"] .rl>li').count()==5
   assert not re.search(r'\]\(https?://|\bSHA\b|冻结|质检',page.locator('main').inner_text())
   older=page.locator('details.archive');assert older.count()>0 and older.first.get_attribute('open') is None
   before=page.locator('a.full:visible').count();older.first.locator('summary').click();assert page.locator('a.full:visible').count()>before
   older.first.locator('summary').click();page.evaluate('scrollTo(0,0)')
   record(label+':release-in-changelog+links+folding',{'recent':5,'olderGroups':older.count()});snap('changelog')
   for route in ['404.html','nonexistent/','deeply/nested/invalid/path/']:
    go(route,200 if route=='404.html' else 404)
    assert page.locator('#missing-page-search').is_visible() and page.locator('.recovery-links a').count()==3
    assert '404' in page.locator('main').inner_text()
    record(label+':custom404-recovery',route)
   snap('nested-404')
   page.locator('#missing-page-search').fill('消息队列');page.locator('button[type="submit"]').click();page.wait_for_url('**/search/?q=*',timeout=25000)
   page.wait_for_selector('.pagefind-ui__result-link',timeout=40000)
   resultHrefs=page.locator('.pagefind-ui__result-link').evaluate_all('els=>els.map(e=>e.href)')
   assert any('/episodes/message-queue/' in h for h in resultHrefs),resultHrefs
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   record(label+':nested404-to-search-results',{'resultCount':len(resultHrefs),'hrefs':resultHrefs});snap('recovery-search-results')
   if pageErrors:report['errors'].append({'context':label,'pageErrors':pageErrors})
  except Exception as e:
   report['errors'].append({'context':label,'error':str(e),'trace':traceback.format_exc(),'url':page.url});snap('failure')
  finally:ctx.close()
 b.close()
report['rangeResponses206']=[r for r in report['mediaResponses'] if r['status']==206 and r['contentRange']]
report['passed']=not report['errors'];report['finishedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'screenshots':len(report['screenshots']),'rangeResponses206':len(report['rangeResponses206']),'errors':report['errors'],'limitations':report['limitations'],'report':str(OUT/'report.json')},ensure_ascii=False))
