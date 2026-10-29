"""Bounded replay of catalog and standalone-image navigation with detailed errors."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
candidate='1a26027d7d6e2f4c50574604b8f37b56ecb7b7b4'
base='http://127.0.0.1:4327/video-studio'; result={'candidate':candidate,'events':[],'navigation':[]}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000})
 page.on('console',lambda m:result['events'].append({'kind':'console','text':m.text,'location':m.location,'document':page.url}) if m.type=='error' else None)
 page.on('response',lambda r:result['events'].append({'kind':'response','status':r.status,'url':r.url,'document':page.url}) if r.status>=400 else None)
 page.on('requestfailed',lambda r:result['events'].append({'kind':'requestfailed','url':r.url,'reason':r.failure,'document':page.url}))
 for route in ['/series/peak/','/library/#learning-series','/library/?series=peak&sort=learning']:
  r=page.goto(base+route,wait_until='networkidle');result['navigation'].append({'route':route,'status':r.status})
 for slug in ['rate-limit','idempotency','circuit-breaker','degradation']:
  r=page.goto(base+'/episodes/'+slug+'/',wait_until='networkidle');result['navigation'].append({'route':page.url,'status':r.status})
  for i in range(2):
   page.locator('figure.fig').get_by_role('link',name='查看大图',exact=True).click();page.wait_for_load_state('networkidle')
   result['navigation'].append({'route':page.url,'imageDecoded':page.locator('img').evaluate('async i=>{await i.decode();return i.complete}')})
   page.go_back(wait_until='networkidle')
 b.close()
result['interpretation']='Standalone image documents have no site HTML link rel=icon and Chromium requests origin-root favicon.ico. Canceled MP4 loading when leaving a lesson is ERR_ABORTED; these are not failed full HTTP checks.'
path=Path(__file__).with_name('trace-navigation.json');path.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
