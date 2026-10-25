"""Reuse immutable prior player QA and check a new website candidate after unrelated upstream changes."""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from facts import *

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--revision-tag',required=True)
parser.add_argument('--preservation-base',required=True)
parser.add_argument('--previous-candidate',required=True)
parser.add_argument('--base',default='http://127.0.0.1:4399/video-studio/')
a=parser.parse_args()
prior=OUT/'candidates'/a.previous_candidate
old=read_json(prior/'qa-site.json')
assert old['status']=='passed' and old['revisionTag']==a.previous_candidate
identity=read_json(prior/'reuse-inputs.json')
for name,value in identity.items():
 assert sha((ROOT/name).read_bytes())==value,('prior QA input changed',name)
# Prove that UI source existed unchanged at the actual prior QA baseline too.
sources={}
for name in identity:
 if name.startswith('site/src/'):
  before=sha(git_bytes(old['preservationBaseline'],name));now=sha((ROOT/name).read_bytes())
  assert before==now,(name,'UI source changed since prior real playback')
  sources[name]=now
x=facts();files=check_identity(x,a.preservation_base)
assert files==old['files'],'Any EP01 artifact change requires reviewing the affected checks'
assert (DIST/f'episodes/{SLUG}/captions.vtt').read_bytes()==(prior/'http-request-captions.vtt').read_bytes()
current_page=Document((DIST/f'episodes/{SLUG}/index.html').read_text())
episode=check_episode(current_page,(DIST/f'episodes/{SLUG}/captions.vtt').read_bytes(),x,a.revision_tag)
rss=check_rss((DIST/'rss.xml').read_bytes(),x)
assert episode==old['episode']
# Preserve and include the parallel EP20 release, including its exact new media.
ep20={}
for name in ['meta.json','article.mdx','storyboard.json','video.mp4','cover-16x9.jpg']:
 body=(ROOT/'episodes/global-id'/name).read_bytes()
 assert body==git_bytes(a.preservation_base,'episodes/global-id/'+name)
 if name in ('video.mp4','cover-16x9.jpg'):
  assert body==(DIST/'episodes/global-id'/name).read_bytes()
 ep20[name]={'sha256':sha(body),'bytes':len(body)}
ep20_meta=read_json(ROOT/'episodes/global-id/meta.json')
assert ep20_meta['title'] in Document((DIST/'episodes/global-id/index.html').read_text()).text
rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for w,h in [(1440,1000),(390,844)]:
  ctx=b.new_context(viewport={'width':w,'height':h});p=ctx.new_page();errors=[]
  p.on('pageerror',lambda e:errors.append(str(e)))
  response=p.goto(a.base+f'episodes/{SLUG}/',wait_until='networkidle');assert response.status==200
  assert p.locator('h1').inner_text()==x['meta']['title']
  assert p.locator('.episode-version time').inner_text()==date_version(x['meta']['updatedAt'])
  assert p.locator('.episode-version time').get_attribute('datetime')==x['meta']['updatedAt']
  assert date_display(x['meta']['createdAt']) in p.locator('header.eh .meta').inner_text()
  assert p.locator('#player').evaluate('e=>JSON.parse(e.dataset.chapters)')==[{k:c[k] for k in ('id','title','start')}for c in x['chapters']]
  p.wait_for_function('document.querySelector("video").readyState>=1')
  media=p.locator('video').evaluate('''async v=>{const i=new Image();i.src=v.poster;await i.decode();return {duration:v.duration,controls:v.controls,width:v.videoWidth,height:v.videoHeight,poster:v.poster,posterWidth:i.naturalWidth}}''')
  assert abs(media['duration']-x['frames']/x['fps'])<.1 and media['controls'] and media['posterWidth']>0
  assert not p.evaluate('document.documentElement.scrollWidth>innerWidth+1')
  p.screenshot(path=str(OUT/f'site-qa/episode-{w}.png'))
  p.goto(a.base+'library/',wait_until='networkidle');card=p.locator(f'a.card[href="/video-studio/episodes/{SLUG}/"]');card.scroll_into_view_if_needed()
  card.locator('img').evaluate('i=>i.decode()')
  assert card.locator('time[aria-label="当前版本"]').inner_text()==date_version(x['meta']['updatedAt'])
  assert card.get_attribute('data-date')==x['meta']['publishedAt']
  assert date_display(x['meta']['createdAt']) in card.locator('.dates').inner_text()
  assert date_display(x['meta']['updatedAt']) in card.locator('.dates').inner_text()
  assert not p.evaluate('document.documentElement.scrollWidth>innerWidth+1')
  p.screenshot(path=str(OUT/f'site-qa/library-dates-{w}.png'))
  assert not errors
  rows.append({'viewport':{'width':w,'height':h},'mediaMetadataAndDecodedPoster':media,'currentDateVersion':date_version(x['meta']['updatedAt']),'pageErrors':errors,'overflow':False,'scope':'Fresh candidate title, date version, structure, poster decoding and card. Playback/34 cues/28 seeking actions explicitly reused below.'})
  ctx.close()
 b.close()
report={'status':'passed','checkedAtUTC':utc_now(),'revisionTag':a.revision_tag,'preservationBaseline':a.preservation_base,
 'files':files,'episode':episode,'rss':rss,'viewports':rows,'parallelEP20Preserved':ep20,
 'reusedBrowserChecks':{'originalCandidate':a.previous_candidate,'report':str((prior/'qa-site.json').relative_to(ROOT)),
 'reportSha256':sha((prior/'qa-site.json').read_bytes()),'immutableFiles':identity,'unchangedUISourcesAtOriginalBaseline':sources,
 'scope':'Actual 1440/390 playback/natural-ended, all 34 native subtitle cue texts and times, 7 chapters plus article controls (28 seek actions), course directory and zero errors reused from the original candidate; complete artifact/SB/VTT/media and player/date source identity checked. No new claim of replaying those actions.',
 'playbackViewports':2,'nativeCues':34,'seekActions':28},
 'limits':'No media recopy, new updatedAt, render, narration listening or teaching-outcome claim. New upstream EP20 exact artifacts are present.'}
(OUT/'qa-site.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'passed','revisionTag':a.revision_tag,'targetedViewports':len(rows),'reusedCues':34,'reusedSeekActions':28,'parallelEP20Preserved':True}))
