"""Read-only final-site QA for the frozen LeetCode visual-continuity batch.

Run only after a complete candidate was checked out and built once in a separate
worktree. HTTP retries may reuse an identical candidate/base report. This script
never installs media, changes production files or pretends viewport simulation
is a physical-device test.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import quote, urljoin
import argparse, atexit, hashlib, json, re, subprocess, sys, urllib.request
import yaml
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--root', default='/workspace/work/video-studio-sitecheck')
parser.add_argument('--base', default='http://127.0.0.1:4323/video-studio')
parser.add_argument('--baseline', default='d04a30c12b1ce0fb5743f20ce61f9db8908311ad')
parser.add_argument('--candidate', required=True)
parser.add_argument('--expected-date', required=True)
parser.add_argument('--out', required=True)
parser.add_argument('--reuse-http-report')
args = parser.parse_args()
root, out = Path(args.root).resolve(), Path(args.out).resolve()
out.mkdir(parents=True, exist_ok=True)
catalog = json.loads((root/'episodes-codex/_shared/leetcode-covers/catalog.json').read_text())
EPISODES = {e['slug']:e for e in catalog['episodes']}
assert len(EPISODES) == 11
series = json.loads((root/'site/src/content/series.json').read_text())['leetcode']
series_title = series['title']
report = {'candidate':args.candidate, 'baseline':args.baseline, 'base':args.base,
    'scope':list(EPISODES), 'browser':'Headless Chromium /usr/bin/chromium; 1440 and 390 px viewport simulation only',
    'httpMedia':[], 'coverPreservation':[], 'viewports':[], 'errors':[],
    'scopeNote':'Read-only LeetCode site/player, original covers and current article figures. Full decoding/audio analysis and canonical hosting checks are separate.'}
http_cache = {}
if args.reuse_http_report:
    previous = Path(args.reuse_http_report).resolve()
    prior = json.loads(previous.read_text())
    assert prior['candidate'] == args.candidate and prior['base'] == args.base
    http_cache = {entry['slug']:entry for entry in prior['httpMedia']}
    assert set(http_cache) == set(EPISODES)
    report['reusedHTTPMedia'] = {'report':str(previous), 'sha256':hashlib.sha256(previous.read_bytes()).hexdigest(),
        'reason':'Full HTTP hashes from this exact unchanged candidate/base; browser-only retry.'}
atexit.register(lambda:(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n'))
def exception_hook(kind, value, tb):
    report['errors'].append(str(value));sys.__excepthook__(kind,value,tb)
sys.excepthook = exception_hook
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip() == args.candidate
assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=root,text=True).strip()

def sha_file(p):
    d=hashlib.sha256()
    with p.open('rb') as f:
        while block:=f.read(1024*1024):d.update(block)
    return d.hexdigest()
def git_blob(rev,path):
    return subprocess.check_output(['git','rev-parse',f'{rev}:{path}'],cwd=root,text=True).strip()
def full_http_sha(url):
    d=hashlib.sha256();size=0
    with urllib.request.urlopen(urllib.request.Request(url,headers={'Accept-Encoding':'identity'}),timeout=60) as r:
        assert r.status == 200,(url,r.status)
        length=int(r.headers['Content-Length']) if r.headers.get('Content-Length') else None
        while block:=r.read(1024*1024):d.update(block);size+=len(block)
        assert length is None or length==size,(url,length,size)
        return {'url':url,'sha256':d.hexdigest(),'bytes':size,'status':r.status}

def article_data(text):
    frontmatter=yaml.safe_load(text.split('---',2)[1]) if text.startswith('---\n') else {}
    assert isinstance(frontmatter,dict)
    headings=[{'level':len(level),'title':title.strip(),'id':ident} for level,title,ident in re.findall(r'^(#{2,3})\s+(.+?)\s+\{#([\w-]+)\}\s*$',text,re.M)]
    figures=[]
    for tag in re.findall(r'<Figure\b[^>]+>',text,re.S):
        src=re.search(r'\bsrc="([^"]+)"',tag);seek=re.search(r'\bseekTo=\{([0-9.]+)\}',tag)
        assert src and seek,tag
        figures.append({'src':src.group(1),'seek':float(seek.group(1))})
    assert headings and figures
    return {'frontmatter':frontmatter,'headings':headings,'figures':figures}

inputs={}
for slug,entry in EPISODES.items():
    directory=root/'episodes'/slug
    meta=json.loads((directory/'meta.json').read_text());article=article_data((directory/'article.mdx').read_text())
    sb=json.loads((directory/'storyboard.json').read_text());card=sb['meta']['unvoicedEndCard']
    result=json.loads((directory/'render-result.json').read_text());receipt=json.loads((directory/meta['referenceAppendix']['manifest']).read_text())
    raw=str(result.get('fps',30)).split('/');fps=float(raw[0])/(float(raw[1]) if len(raw)==2 else 1)
    final=meta['finalVideoFrames'];reference=meta['referenceAppendix']['from']
    assert result.get('finalVideoFrames',result.get('frames')) == final == receipt['finalVideoFrames']
    assert receipt['appendix']['from'] == reference
    assert card['kind']=='full-python-solution' and card['durationInFrames']==150 and card['from']+150==reference,(slug,card,reference)
    expected_sha=result['sha256'];assert receipt['outputSHA256']==expected_sha
    assert sha_file(directory/meta['video'])==expected_sha
    modified=datetime.fromisoformat(meta['updatedAt']);day=modified.astimezone(ZoneInfo('Asia/Shanghai')).date().isoformat() if modified.tzinfo else modified.date().isoformat()
    assert day==args.expected_date,(slug,day,args.expected_date)
    assert meta['series']=='leetcode' and meta['problemNumber']==entry['number'] and 'LeetCode' in meta['tags']
    # All three original covers, the vertical poster and the cover identity stay byte-identical.
    original={}
    for filename in ['cover-16x9.jpg','cover-4x3.jpg','cover-3x4.jpg','poster.jpg','cover-style.json']:
        path=f'episodes/{slug}/{filename}';now=git_blob(args.candidate,path);before=git_blob(args.baseline,path)
        assert now==before,(slug,filename,'cover changed')
        original[filename]=now
    report['coverPreservation'].append({'slug':slug,'gitBlobsUnchanged':original})
    cached=http_cache.get(slug)
    video=cached['video'] if cached else full_http_sha(f"{args.base}/episodes/{slug}/{meta['video']}")
    assert video['sha256']==expected_sha and (result.get('bytes') is None or video['bytes']==result['bytes'])
    cover=cached['cover'] if cached else full_http_sha(f"{args.base}/episodes/{slug}/{meta['poster']}")
    style=json.loads((directory/'cover-style.json').read_text())
    assert cover['sha256']==sha_file(directory/meta['poster'])==style['covers']['16x9']['jpgSha256']
    images=[]
    for i,figure in enumerate(article['figures']):
        image=cached['articleImages'][i] if cached else full_http_sha(urljoin(args.base+'/',figure['src']))
        local=directory/'article'/Path(figure['src']).name
        assert image['sha256']==sha_file(local),(slug,'article figure SHA mismatch',figure)
        images.append(image)
    report['httpMedia'].append({'slug':slug,'video':video,'cover':cover,'articleImages':images})
    inputs[slug]={'meta':meta,'article':article,'result':result,'receipt':receipt,'fps':fps,
        'expectedSeconds':final/fps,'codeFromSeconds':card['from']/fps,'referenceFromSeconds':reference/fps}

# The cover catalog is ordered by problem number; existing course navigation is
# deliberately ordered by lessonOrder or historical EP, which this batch preserves.
SERIES_ORDER=sorted(EPISODES,key=lambda slug:inputs[slug]['meta'].get('lessonOrder',inputs[slug]['meta']['ep']))
report['expectedSeriesOrder']=SERIES_ORDER

def overflow(page):
    d=page.evaluate('({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth})')
    assert d['scroll']<=d['client']+1,d
    return d

def visible_video(page):
    v=page.locator('video')
    v.evaluate('(v)=>v.scrollIntoView({block:"center",inline:"nearest"})')
    page.wait_for_timeout(120)
    box=v.bounding_box();assert box
    size=page.viewport_size
    assert box['x']>=-1 and box['y']>=-1 and box['x']+box['width']<=size['width']+1 and box['y']+box['height']<=size['height']+1,(box,size)
    return box

def seek_paused(page,t):
    visible_video(page)
    presented=page.locator('video').evaluate('''async(v,t)=>{
      v.pause();
      // Move away first when repeating the same seek; a paused unchanged frame may not emit a callback.
      if(Math.abs(v.currentTime-t)<.075){v.currentTime=Math.max(0,t-.15);await new Promise((r,j)=>{const n=setTimeout(()=>j(new Error('reset seek timeout')),10000);v.addEventListener('seeked',()=>{clearTimeout(n);r()},{once:true})})}
      const frame=await new Promise((resolve,reject)=>{
        const timer=setTimeout(()=>reject(new Error('No presented frame at '+t)),10000);
        const capture=(now,m)=>{if(Math.abs(m.mediaTime-t)<.075){clearTimeout(timer);resolve({mediaTime:m.mediaTime,presentedFrames:m.presentedFrames})}else v.requestVideoFrameCallback(capture)};
        v.requestVideoFrameCallback(capture);v.currentTime=t;
      });
      await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
      return frame;
    }''',t)
    page.wait_for_function('(t)=>{const v=document.querySelector("video");return !v.seeking&&v.readyState>=3&&Math.abs(v.currentTime-t)<.05}',arg=t)
    page.wait_for_timeout(350)
    state=page.locator('video').evaluate('(v)=>({time:v.currentTime,active:[...v.textTracks].flatMap(t=>[...(t.activeCues??[])].map(c=>c.text))})')
    state['presentedFrame']=presented
    return state

def snap(page,name):
    overflow(page);page.screenshot(path=str(out/name))
def links(locator):return locator.evaluate_all('(as)=>[...new Set(as.map(a=>a.getAttribute("href")).filter(Boolean))]')
def visible_library(page):return page.locator('#library-grid > ul > li:not([hidden]) a.card').evaluate_all('(as)=>as.map(a=>new URL(a.href).pathname.split("/").filter(Boolean).at(-1)).sort()')

def taxonomy(page,width):
    r={};response=page.goto(args.base+'/series/leetcode/',wait_until='networkidle');assert response and response.status==200
    assert page.locator('h1').inner_text().strip()==series_title
    entries=page.locator('ol.lesson-list a.lesson')
    slugs=entries.evaluate_all('(as)=>as.map(a=>new URL(a.href).pathname.split("/").filter(Boolean).at(-1))')
    assert slugs==SERIES_ORDER,(slugs,SERIES_ORDER)
    numbers=entries.locator('.lesson-meta .num').all_text_contents();assert numbers==[f'LC.{EPISODES[slug]["number"]}' for slug in SERIES_ORDER],numbers
    r['series']={'slugs':slugs,'numbers':numbers,'overflow':overflow(page)};snap(page,f'series-{width}.png')
    page.goto(args.base+'/learn/#algorithms',wait_until='networkidle');track=page.locator('section#algorithms')
    assert track.locator('h2').inner_text().strip()=='算法可视化'
    assert track.locator('a.chapter-heading').get_attribute('href').endswith('/series/leetcode/')
    r['learn']={'title':track.locator('h2').inner_text(),'series':track.locator('a.chapter-heading').inner_text(),'overflow':overflow(page)}
    page.goto(args.base+'/library/?track=algorithms&series=leetcode',wait_until='networkidle')
    assert page.locator('select[name="series"] option[value="leetcode"]').inner_text()==series_title
    assert visible_library(page)==sorted(EPISODES)
    page.locator('select[name="tag"]').select_option('LeetCode');assert visible_library(page)==sorted(EPISODES)
    cards=page.locator('#library-grid > ul > li:not([hidden]) a.card')
    card_numbers=cards.locator('.date-row > span.num').all_text_contents();assert sorted(card_numbers)==sorted(f'LC.{e["number"]}' for e in EPISODES.values())
    r['library']={'slugs':visible_library(page),'numbers':card_numbers,'overflow':overflow(page)}
    if width==1440:snap(page,'library-1440.png')
    page.goto(args.base+'/tags/LeetCode/',wait_until='networkidle');assert page.locator('h1').inner_text().strip()=='#LeetCode'
    tag_links=links(page.locator('a.card'));assert len(tag_links)==11 and all(any('/episodes/'+s+'/' in u for u in tag_links) for s in EPISODES)
    r['tag']={'links':tag_links,'overflow':overflow(page)}
    page.goto(args.base+'/search/?q=LeetCode',wait_until='networkidle');page.locator('.pagefind-ui__result-link').first.wait_for(state='visible',timeout=30000)
    search=page.evaluate("""async()=>{const api=await import(new URL('../pagefind/pagefind.js',location.href).href);const r=await api.search('LeetCode');return await Promise.all(r.results.map(async x=>{const d=await x.data();return {url:d.url,title:d.meta.title}}))}""")
    assert all(any('/episodes/'+s+'/' in item['url'].rstrip('/')+'/' for item in search) for s in EPISODES),search
    r['search']={'query':'LeetCode','results':search,'overflow':overflow(page)}
    if width==1440:snap(page,'search-1440.png')
    return r

with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
    report['chromiumVersion']=browser.version
    for width,height in [(1440,1000),(390,844)]:
        context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
        page=context.new_page();vr={'width':width,'height':height,'episodes':[]};report['viewports'].append(vr)
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append('console: '+m.text) if m.type=='error' else None)
        vr['taxonomy']=taxonomy(page,width)
        for slug,entry in EPISODES.items():
            start_errors=len(errors);d=inputs[slug];meta=d['meta'];item={'slug':slug};vr['episodes'].append(item)
            response=page.goto(f'{args.base}/episodes/{slug}/',wait_until='networkidle');assert response and response.status==200
            assert page.locator('header.eh h1').inner_text().strip()==meta['title']
            label=f'LC.{entry["number"]}';bc=page.locator('nav[aria-label="面包屑"]')
            assert bc.get_by_role('link',name=series_title,exact=True).count()==1 and label in bc.inner_text()
            version=page.locator('.episode-version time');assert version.get_attribute('datetime')==meta['updatedAt'] and args.expected_date in version.inner_text()
            source_links=page.locator('.source-links a').evaluate_all('(as)=>as.map(a=>a.href)')
            assert len(source_links)==3 and all(args.candidate in u for u in source_links) and source_links[-1].endswith(quote(meta['sourcePath'],safe='/'))
            directory=page.locator('#course-directory nav a');order=links(directory)
            assert len(order)==11 and all(any('/episodes/'+s+'/' in u for u in order) for s in EPISODES)
            assert page.locator('#course-directory nav a[aria-current="page"]').get_attribute('href').endswith('/episodes/'+slug+'/')
            neighbors=links(page.locator('nav.pager a'));idx=SERIES_ORDER.index(slug);expected_neighbors=[s for j,s in enumerate(SERIES_ORDER) if abs(j-idx)==1]
            assert len(neighbors)==len(expected_neighbors) and all(any('/episodes/'+s+'/' in u for u in neighbors) for s in expected_neighbors),(slug,neighbors)
            related=links(page.locator('aside.rel a.rc'));expected_related=[]
            for raw in meta.get('related',[]):
                s=raw if isinstance(raw,str) else raw['slug'];target=root/'episodes'/s/'meta.json'
                if target.exists():
                    m=json.loads(target.read_text())
                    if not m.get('draft') and not m.get('archived'):expected_related.append(s)
            assert len(related)==len(expected_related) and all(any('/episodes/'+s+'/' in u for u in related) for s in expected_related),(slug,related,expected_related)
            related_http=[]
            for href in related:
                target=page.request.get(urljoin(args.base+'/',href));assert target.status==200;related_http.append({'href':href,'status':target.status});target.dispose()
            item['page']={'status':response.status,'label':label,'version':version.inner_text(),'sourceLinks':source_links,'neighbors':neighbors,'related':related_http,'directoryLinks':order,'overflow':overflow(page)}
            video=page.locator('video');page.wait_for_function('document.querySelector("video").readyState>=1')
            vm=video.evaluate('(v)=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,currentSrc:v.currentSrc})')
            assert vm['width']==1920 and vm['height']==1080 and abs(vm['duration']-d['expectedSeconds'])<=1/d['fps']+.001
            assert vm['currentSrc'].endswith('/episodes/'+slug+'/'+meta['video'])
            page.wait_for_function('([...document.querySelector("video").textTracks].some(t=>t.kind==="captions"&&t.cues?.length>0))')
            tracks=video.evaluate('(v)=>[...v.textTracks].map(t=>({kind:t.kind,language:t.language,mode:t.mode,cues:t.cues?.length??0,first:t.cues?.[0]?{start:t.cues[0].startTime,end:t.cues[0].endTime,text:t.cues[0].text}:null,lastEnd:t.cues?.[t.cues.length-1]?.endTime??null}))')
            captions=next(t for t in tracks if t['kind']=='captions');assert captions['language']=='zh' and captions['mode']=='showing'
            assert captions['lastEnd']<=d['codeFromSeconds']+1/d['fps'],(slug,'caption overlaps Python card',captions,d['codeFromSeconds'])
            body_time=(captions['first']['start']+captions['first']['end'])/2;body=seek_paused(page,body_time);assert body['active']
            video.evaluate('(v)=>{v.muted=true;return v.play()}');page.wait_for_function('(t)=>!document.querySelector("video").paused&&document.querySelector("video").currentTime>t+.2',arg=body_time)
            page.keyboard.press('k');page.wait_for_function('document.querySelector("video").paused');paused=video.evaluate('(v)=>v.currentTime');page.wait_for_timeout(180);assert abs(video.evaluate('(v)=>v.currentTime')-paused)<.01
            item['player']={'metadata':vm,'tracks':tracks,'bodySubtitleSeek':body,'played':True,'keyboardPaused':True,'pauseTime':paused}
            visible_video(page);video.evaluate('(v)=>v.addEventListener("click",()=>v.requestFullscreen(),{once:true})');video.click(position={'x':80,'y':45});page.wait_for_function('document.fullscreenElement===document.querySelector("video")')
            fs=page.evaluate('({entered:!!document.fullscreenElement,width:document.fullscreenElement.getBoundingClientRect().width,height:document.fullscreenElement.getBoundingClientRect().height,viewportWidth:innerWidth,viewportHeight:innerHeight})')
            assert abs(fs['width']-fs['viewportWidth'])<=1 and abs(fs['height']-fs['viewportHeight'])<=1
            if width==1440 and slug in ['two-sum','number-of-islands','daily-temperatures']:snap(page,f'{slug}-fullscreen-1440.png')
            page.evaluate('document.exitFullscreen()');page.wait_for_function('!document.fullscreenElement');video.evaluate('(v)=>v.pause()');fs['exited']=True;item['fullscreen']=fs
            chapters=json.loads(page.locator('#player').get_attribute('data-chapters'));fm=d['article']['frontmatter'].get('chapters',[])
            fm_ids={c['id'] for c in fm};assert [(c['id'],c['title']) for c in chapters if c['id'] in fm_ids]==[(c['id'],c['title']) for c in fm]
            # The player serializes id/title/start only; derive inArticle from the unchanged frontmatter.
            for c in chapters:c['inArticle']=c['id'] in fm_ids
            assert chapters and chapters[0]['start']==0 and [c['start'] for c in chapters]==sorted(set(c['start'] for c in chapters)) and chapters[-1]['start']<d['referenceFromSeconds']
            heading_ids=[]
            for heading in d['article']['headings']:
                assert page.locator(f'article.article-body [id="{heading["id"]}"]').count()==1,(slug,heading)
                heading_ids.append(heading['id'])
            item['articleExplicitAnchorIDs']=heading_ids;item['chapters']=[]
            for index,c in enumerate(chapters):
                selector='.vp .side a.ch' if width>=768 else '.vp .chips a.chip';link=page.locator(selector+f'[data-index="{index}"]')
                assert link.get_attribute('href')==('#'+c['id'] if c['inArticle'] else '#player'),(slug,c)
                link.click();page.wait_for_function('(t)=>{const v=document.querySelector("video");return !v.seeking&&Math.abs(v.currentTime-t)<1.5}',arg=c['start']);video.evaluate('(v)=>v.pause()')
                assert link.get_attribute('aria-current')=='true'
                h=page.evaluate('location.hash');assert h.startswith('#t=') and abs(float(h[3:])-c['start'])<1e-9,(slug,c,h)
                item['chapters'].append({**c,'actualSeekSeconds':video.evaluate('(v)=>v.currentTime'),'hash':h,'active':True})
            item['articleChapterSeeks']=[]
            for c in chapters:
                if not c['inArticle']:continue
                button=page.locator('article.article-body [data-seek="'+c['id']+'"]');assert button.count()==1;button.click()
                page.wait_for_function('(t)=>{const v=document.querySelector("video");return !v.seeking&&Math.abs(v.currentTime-t)<1.5}',arg=c['start']);video.evaluate('(v)=>v.pause()')
                item['articleChapterSeeks'].append({'id':c['id'],'expected':c['start'],'actual':video.evaluate('(v)=>v.currentTime')})
            item['figureSeeks']=[]
            for index,expected in enumerate(d['article']['figures']):
                suffix='/episodes/'+slug+'/article/'+Path(expected['src']).name
                figure=page.locator('figure.fig').filter(has=page.locator(f'img[src$="{suffix}"]')).first;assert figure.count()==1
                figure.scroll_into_view_if_needed();img=figure.locator('img');img.wait_for(state='visible');img.evaluate('async i=>{await i.decode();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))}')
                seek=figure.locator('[data-seek-time]');assert seek.count()==1 and abs(float(seek.get_attribute('data-seek-time'))-expected['seek'])<1e-8
                seek.click();page.wait_for_function('(t)=>{const v=document.querySelector("video");return !v.seeking&&Math.abs(v.currentTime-t)<1.5}',arg=expected['seek']);video.evaluate('(v)=>v.pause()')
                h=page.evaluate('location.hash');assert h.startswith('#t=') and abs(float(h[3:])-expected['seek'])<1e-8
                state=seek_paused(page,expected['seek'])
                if width==390:snap(page,f'{slug}-figure-seek-390.png')
                item['figureSeeks'].append({'expected':expected['seek'],'actual':state['time'],'presentedFrame':state['presentedFrame'],'imageLoaded':True,'hash':h})
            trigger=page.locator('[data-source-trigger]').first;assert trigger.count()==1;ident=trigger.get_attribute('data-source-trigger');trigger.focus();page.keyboard.press('Enter');panel=page.locator(f'[data-source-panel="{ident}"]');panel.wait_for(state='visible');assert panel.locator('blockquote').inner_text().strip();identity=panel.locator('.source-identity').inner_text()
            if slug=='two-sum' and width==1440:snap(page,'source-quote-1440.png')
            page.keyboard.press('Escape');panel.wait_for(state='hidden');item['sourceQuote']={'sourceId':ident,'keyboardOpened':True,'escapedClosed':True,'identity':identity}
            code=[]
            for offset in [.2,2.5,4.8]:
                state=seek_paused(page,d['codeFromSeconds']+offset);assert not state['active'],(slug,'native captions on Python card',state);code.append(state)
                if width==1440 and offset==2.5:snap(page,f'{slug}-python-1440.png')
            item['pythonCard']={'fromSeconds':d['codeFromSeconds'],'durationSeconds':5,'samples':code,'nativeCaptionsAbsent':True}
            references=[];appendix=d['receipt']['appendix'];per_page=appendix['framesPerPage']/d['fps']
            for index in range(len(appendix['pages'])):
                t=d['referenceFromSeconds']+(index+.5)*per_page;state=seek_paused(page,t);assert not state['active'],(slug,'native captions on references',state);references.append(state)
                if width==1440:snap(page,f'{slug}-references-{index+1}-1440.png')
            restored=seek_paused(page,body_time);assert restored['active'];item['references']={'fromSeconds':d['referenceFromSeconds'],'pages':references,'captionsRestoredOnReturn':True}
            item['pageErrors']=errors[start_errors:];assert not item['pageErrors'];item['overflow']=overflow(page)
            print(json.dumps({'viewport':width,'episode':slug,'status':'passed'},ensure_ascii=False),flush=True)
        vr['pageErrors']=errors;assert not errors;context.close()
    browser.close()
report['status']='passed'
print(json.dumps({'status':'passed','episodes':len(EPISODES),'viewports':2,'httpVideosVerified':len(report['httpMedia']),'report':str(out/'report.json')},ensure_ascii=False))
