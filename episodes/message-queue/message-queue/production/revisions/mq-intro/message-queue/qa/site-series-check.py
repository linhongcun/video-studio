import json
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path('/workspace/video-studio'); OUT=Path('/workspace/work/mq-intro')
ids={'request','cache','peak','message-queue','database','distributed'}
metas=[json.loads(p.read_text()) for p in (R/'episodes').glob('*/meta.json')]
expected=len({m['slug'] for m in metas if not m.get('draft') and not m.get('archived') and (m.get('series') in ids or ids.intersection(m.get('additionalSeries',[])))})
checks=[]
def check(name,condition,details=None):
 checks.append({'name':name,'passed':bool(condition),'details':details})
 if not condition: raise AssertionError((name,details))
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(1440,1000),(390,844)]:
  page=browser.new_page(viewport={'width':width,'height':height})
  base='http://127.0.0.1:4326/video-studio/'
  response=page.goto(base+'series/message-queue/',wait_until='domcontentloaded')
  check(f'{width}: MQ directory responds',response.status==200)
  lessons=page.locator('.lesson-list>li')
  check(f'{width}: only the released intro is listed',lessons.count()==1,lessons.count())
  check(f'{width}: same canonical episode URL',lessons.locator('a.lesson').get_attribute('href')=='/video-studio/episodes/message-queue/')
  check(f'{width}: honest release count','已发布 1 篇' in page.locator('.course-count').inner_text())
  check(f'{width}: independent viewing explained','可以独立观看' in page.locator('.series-overview').inner_text())
  check(f'{width}: no horizontal overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
  page.screenshot(path=str(OUT/f'series-mq-{width}.png'),full_page=True)
  page.goto(base+'series/peak/',wait_until='domcontentloaded')
  check(f'{width}: old peak directory retains intro',page.locator('.lesson-list a.lesson[href="/video-studio/episodes/message-queue/"]').count()==1)
  page.goto(base+'episodes/message-queue/',wait_until='domcontentloaded')
  check(f'{width}: MQ series entry reachable',page.locator('.reading-links a[href="/video-studio/series/message-queue/"]').count()==1)
  check(f'{width}: primary directory still peak','扛住高峰' in page.locator('#course-directory summary').inner_text())
  check(f'{width}: prior lesson unchanged',page.locator('.pager a.p').first.get_attribute('href')=='/video-studio/episodes/cache-consistency/')
  check(f'{width}: next lesson unchanged',page.locator('.pager a.p').last.get_attribute('href')=='/video-studio/episodes/rate-limit/')
  check(f'{width}: detail no horizontal overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
  page.goto(base+'learn/',wait_until='domcontentloaded')
  text=page.locator('#systems .published').inner_text()
  check(f'{width}: unique lesson count',f'已发布 {expected} 篇' in text,text)
  check(f'{width}: MQ listed in learning track',page.locator('#systems a.chapter-heading[href="/video-studio/series/message-queue/"]').count()==1)
  page.goto(base+'library/?series=message-queue',wait_until='domcontentloaded')
  page.wait_for_selector('.catalog-controls:not([hidden])')
  visible=page.locator('#library-grid>ul>li:not([hidden])')
  check(f'{width}: library MQ filter lists one canonical intro',visible.count()==1,visible.count())
  check(f'{width}: filtered card retains primary identity',visible.locator('a.card').get_attribute('data-series')=='peak')
  check(f'{width}: filtered card is the same episode',visible.locator('a.card').get_attribute('href')=='/video-studio/episodes/message-queue/')
  page.select_option('select[name="series"]','peak')
  peakExpected=sum(not m.get('draft') and not m.get('archived') and m.get('series')=='peak' for m in metas)
  check(f'{width}: primary peak filter still works',visible.count()==peakExpected,visible.count())
  page.click('button.reset')
  allExpected=sum(not m.get('draft') and not m.get('archived') for m in metas)
  check(f'{width}: resetting filters preserves unique library',visible.count()==allExpected,visible.count())
  page.close()
 browser.close()
report={'scope':'Real built site; existing released media unchanged during series verification. This does not verify the new revision video.','expectedUniqueSystemEpisodes':expected,'checks':checks}
(OUT/'site-series-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':len(checks),'expectedUniqueSystemEpisodes':expected,'failed':sum(not c['passed'] for c in checks)},ensure_ascii=False))
