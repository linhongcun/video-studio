import hashlib,json,os,subprocess,urllib.request
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright
R=Path('/workspace/video-studio')
OUT=R/'episodes-codex/message-queue/revisions/mq-intro/message-queue/qa/online-series'
OUT.mkdir(parents=True,exist_ok=True)
RUN='40473036363'; HEAD='34b8e306a5665ea08e61aa17c9a0e8e58ab1c87c'
run=json.loads(subprocess.check_output(['gh','run','view',RUN,'--repo','linhongcun/video-studio','--json','status,conclusion,url,headSha,updatedAt'],text=True))
assert run['status']=='completed' and run['conclusion']=='success',run
assert run['headSha']==HEAD,run
ids={'request','cache','peak','message-queue','database','distributed'}
metas=[json.loads(p.read_text()) for p in (R/'episodes').glob('*/meta.json')]
expected=len({m['slug'] for m in metas if not m.get('draft') and not m.get('archived') and (m.get('series') in ids or ids.intersection(m.get('additionalSeries',[])))})
checks=[]; http=[]; browser_transport=[]; response_cache={}
def check(name,condition,details=None):
 checks.append({'name':name,'passed':bool(condition),'details':details})
 if not condition: raise AssertionError((name,details))
base='https://linhongcun.github.io/video-studio/'
# Ordinary canonical GETs; no cache-bypass query or hash-only shortcuts.
for suffix in ['series/message-queue/','series/peak/','learn/','library/','episodes/message-queue/']:
 u=base+suffix
 with urllib.request.urlopen(u,timeout=40) as r:
  data=r.read(); entry={'url':u,'status':r.status,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'hasVersion0790':b'v0.79.0' in data or b'0.79.0' in data}
  http.append(entry)
  check('GET '+suffix,r.status==200,entry)
  check('version '+suffix,entry['hasVersion0790'])
with sync_playwright() as p:
 args={'executable_path':'/usr/bin/chromium','headless':True,'args':['--no-sandbox']}
 browser=p.chromium.launch(**args)
 for width,height in [(1440,1000),(390,844)]:
  context=browser.new_context(viewport={'width':width,'height':height},ignore_https_errors=False,service_workers='block')
  def verified_route(route):
   u=route.request.url
   if u not in response_cache:
    with urllib.request.urlopen(u,timeout=40) as remote:
     body=remote.read()
     headers={k:v for k,v in remote.headers.items() if k.lower() not in {'content-length','content-encoding','transfer-encoding','connection'}}
     response_cache[u]=(remote.status,headers,body)
     browser_transport.append({'url':u,'status':remote.status,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()})
   status,headers,body=response_cache[u]
   route.fulfill(status=status,headers=headers,body=body)
  context.route('https://linhongcun.github.io/**',verified_route)
  page=context.new_page()
  response=page.goto(base+'series/message-queue/',wait_until='domcontentloaded',timeout=60000)
  check(f'{width}: MQ directory HTTP',response.status==200)
  lessons=page.locator('.lesson-list>li')
  check(f'{width}: only one released intro',lessons.count()==1,lessons.count())
  check(f'{width}: canonical episode reused',lessons.locator('a.lesson').get_attribute('href')=='/video-studio/episodes/message-queue/')
  check(f'{width}: only one published episode advertised','已发布 1 篇' in page.locator('.course-count').inner_text())
  check(f'{width}: independent viewing clear','可以独立观看' in page.locator('.series-overview').inner_text())
  check(f'{width}: MQ no overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
  page.screenshot(path=str(OUT/f'mq-directory-{width}.png'),full_page=True)
  page.goto(base+'series/peak/',wait_until='domcontentloaded',timeout=60000)
  check(f'{width}: old peak still retains intro',page.locator('.lesson-list a.lesson[href="/video-studio/episodes/message-queue/"]').count()==1)
  page.goto(base+'learn/',wait_until='domcontentloaded',timeout=60000)
  text=page.locator('#systems .published').inner_text()
  check(f'{width}: systems count uses unique slugs',f'已发布 {expected} 篇' in text,text)
  check(f'{width}: MQ directory in learning track',page.locator('#systems a.chapter-heading[href="/video-studio/series/message-queue/"]').count()==1)
  page.goto(base+'library/?series=message-queue',wait_until='domcontentloaded',timeout=60000)
  page.wait_for_selector('.catalog-controls:not([hidden])',timeout=15000)
  visible=page.locator('#library-grid>ul>li:not([hidden])')
  check(f'{width}: MQ library filter has one card',visible.count()==1,visible.count())
  check(f'{width}: card remains primary peak',visible.locator('a.card').get_attribute('data-series')=='peak')
  check(f'{width}: library canonical URL reused',visible.locator('a.card').get_attribute('href')=='/video-studio/episodes/message-queue/')
  page.screenshot(path=str(OUT/f'library-mq-{width}.png'),full_page=True)
  page.select_option('select[name="series"]','peak')
  peak_expected=sum(not m.get('draft') and not m.get('archived') and m.get('series')=='peak' for m in metas)
  check(f'{width}: peak filter remains available',visible.count()==peak_expected,visible.count())
  context.close()
 browser.close()
report={'checkedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'deployment':run,'release':'v0.79.0','expectedUniqueSystemEpisodes':expected,'scope':'Live Pages after the Release-after deployment; small series/directory/library browser checks only. Does not repeat video/media/source-popover checks. Canonical origin and actual interactions retained; Chromium requests are fulfilled by ordinary urllib GETs with configured CA validation because the Chromium trust store lacks the environment proxy CA. HTTPS verification was not disabled.','browserTransport':browser_transport,'http':http,'checks':checks,'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks)}
(OUT/'check.py').write_text(Path(__file__).read_text())
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(OUT/'README.md').write_text('# 线上MQ系列收录核验\n\n'+f"核验时间：{report['checkedAt']}；Release：v0.79.0；Release后Pages：{RUN}。\n\n"+f"实际普通canonical GET与1440/390浏览器共{len(checks)}项通过，0失败。MQ仅1期，与旧peak/内容库共用同一episode URL；系统方向按{expected}个唯一slug计数。这里只检查系列、学习目录与筛选，不重测媒体或引用浮层。浏览器保留canonical origin及实际交互；远端HTML/JS/图片由Python urllib普通GET并用环境CA验证后回填，不关闭TLS验证。详情见report.json及本目录实际截图。\n")
print(json.dumps({'passed':report['passed'],'failed':report['failed'],'report':str(OUT/'report.json')},ensure_ascii=False))
