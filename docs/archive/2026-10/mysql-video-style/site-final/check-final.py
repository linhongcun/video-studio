from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse, atexit, hashlib, json, subprocess, sys, urllib.request
from urllib.parse import quote, urljoin
import yaml
from playwright.sync_api import sync_playwright

EPISODES = {
    'db-index': 90.0,
    'db-transaction': 68.0,
    'db-lock': 74.0,
    'db-replication': 77.0,
}

parser = argparse.ArgumentParser()
parser.add_argument('--root', default='/workspace/work/video-studio-sitecheck')
parser.add_argument('--base', default='http://127.0.0.1:4322/video-studio')
parser.add_argument('--candidate', required=True)
parser.add_argument('--expected-date', required=True)
parser.add_argument('--out', required=True)
parser.add_argument('--reuse-http-report')
args = parser.parse_args()
root = Path(args.root).resolve()
out = Path(args.out).resolve()
out.mkdir(parents=True, exist_ok=True)
report = {
    'candidate': args.candidate, 'base': args.base,
    'scope': list(EPISODES),
    'browser': 'Headless Chromium /usr/bin/chromium; desktop and 390px viewport simulation, not physical-device testing',
    'httpMedia': [], 'viewports': [], 'errors': [],
    'scopeNote':'MySQL display names with stable database IDs/URLs; four current videos/figures/covers and two simulated viewports only.',
}
http_cache = {}
if args.reuse_http_report:
    previous = Path(args.reuse_http_report).resolve()
    prior_report = json.loads(previous.read_text())
    assert prior_report['candidate']==args.candidate and prior_report['base']==args.base
    http_cache = {entry['slug']:entry for entry in prior_report['httpMedia']}
    assert set(http_cache)==set(EPISODES)
    report['reusedHTTPMedia'] = {'report':str(previous),'sha256':hashlib.sha256(previous.read_bytes()).hexdigest(),'reason':'Complete HTTP hashes were already acquired from this exact unchanged candidate build before the first browser attempt; only browser presentation waits and article-only chapter expectations were corrected.'}
atexit.register(lambda: (out/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n'))
def exception_hook(kind, value, tb):
    report['errors'].append(str(value))
    sys.__excepthook__(kind, value, tb)
sys.excepthook = exception_hook

head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
assert head == args.candidate, ('QA worktree is not the candidate', head, args.candidate)

def sha_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while block := stream.read(1024*1024):
            digest.update(block)
    return digest.hexdigest()

def full_http_sha(url):
    digest = hashlib.sha256()
    size = 0
    request = urllib.request.Request(url, headers={'Accept-Encoding': 'identity'})
    with urllib.request.urlopen(request, timeout=60) as response:
        assert response.status == 200, (url, response.status)
        length = int(response.headers['Content-Length']) if response.headers.get('Content-Length') else None
        while block := response.read(1024*1024):
            digest.update(block)
            size += len(block)
        assert length is None or length == size, (url, length, size)
        return {'url': url, 'sha256': digest.hexdigest(), 'bytes': size, 'status': response.status}

inputs = {}
for slug, seek_time in EPISODES.items():
    directory = root/'episodes'/slug
    meta = json.loads((directory/'meta.json').read_text())
    frontmatter = yaml.safe_load((directory/'article.mdx').read_text().split('---',2)[1])
    result = json.loads((directory/'render-result.json').read_text())
    receipt = json.loads((directory/meta['referenceAppendix']['manifest']).read_text())
    raw_fps = str(result.get('fps', '30')).split('/')
    fps = float(raw_fps[0]) / (float(raw_fps[1]) if len(raw_fps) == 2 else 1)
    final_frames = meta['finalVideoFrames']
    assert result.get('finalVideoFrames', result.get('frames')) == final_frames, (slug, result, meta)
    assert receipt['finalVideoFrames'] == final_frames
    assert receipt['appendix']['from'] == meta['referenceAppendix']['from']
    expected_sha = result['sha256']
    assert receipt['outputSHA256'] == expected_sha, (slug, 'render/receipt hash mismatch')
    assert sha_file(directory/meta['video']) == expected_sha, (slug, 'candidate file/render hash mismatch')
    modified = datetime.fromisoformat(meta['updatedAt'])
    if modified.tzinfo:
        date = modified.astimezone(ZoneInfo('Asia/Shanghai')).date().isoformat()
    else:
        date = modified.date().isoformat()
    assert date == args.expected_date, (slug, 'unexpected current version date', date)
    media = http_cache[slug]['video'] if http_cache else full_http_sha(f"{args.base}/episodes/{slug}/{meta['video']}")
    assert media['sha256'] == expected_sha, (slug, 'HTTP/render hash mismatch', media)
    if result.get('bytes') is not None:
        assert media['bytes'] == result['bytes'], (slug, 'HTTP/render bytes mismatch')
    image = http_cache[slug]['articleImage'] if http_cache else full_http_sha(f'{args.base}/episodes/{slug}/article/01.jpg')
    assert image['sha256'] == sha_file(directory/'article/01.jpg'), (slug, 'HTTP/candidate article image mismatch')
    poster = http_cache[slug]['cover'] if http_cache else full_http_sha(f"{args.base}/episodes/{slug}/{meta['poster']}")
    assert poster['sha256'] == sha_file(directory/meta['poster']), (slug, 'HTTP/candidate cover mismatch')
    cover_style = json.loads((directory/'cover-style.json').read_text())
    assert poster['sha256'] == cover_style['covers']['16x9']['jpgSha256'], (slug, 'cover manifest mismatch')
    assert meta['series'] == 'database' and 'MySQL' in meta['tags'] and 'MySQL 8.4' in meta['summary']
    report['httpMedia'].append({'slug': slug, 'video': media, 'articleImage': image, 'cover':poster})
    inputs[slug] = {'meta': meta, 'article':frontmatter, 'result': result, 'receipt': receipt, 'fps': fps, 'expectedSeconds': final_frames/fps}


def check_overflow(page):
    size = page.evaluate('({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth})')
    assert size['scroll'] <= size['client']+1, size
    return size

def seek_paused(page, time):
    presented = page.locator('video').evaluate('''async (v,t)=>{
      v.pause();
      const frame = await new Promise((resolve,reject)=>{
        const timer=setTimeout(()=>reject(new Error('No presented frame at requested seek '+t)),10000);
        const capture=(now,m)=>{if(Math.abs(m.mediaTime-t)<.075){clearTimeout(timer);resolve({mediaTime:m.mediaTime,presentedFrames:m.presentedFrames})}else v.requestVideoFrameCallback(capture)};
        v.requestVideoFrameCallback(capture);v.currentTime=t;
      });
      await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
      return frame;
    }''',time)
    page.wait_for_function('(t)=>{const v=document.querySelector("video");return !v.seeking&&v.readyState>=3&&Math.abs(v.currentTime-t)<.05}', arg=time)
    page.wait_for_timeout(350)
    state = page.locator('video').evaluate('(v)=>({time:v.currentTime,active:[...v.textTracks].flatMap(t=>[...(t.activeCues??[])].map(c=>c.text))})')
    state['presentedFrame'] = presented
    return state

def links_for_episode_nodes(locator):
    return locator.evaluate_all('(as)=>[...new Set(as.map(a=>a.getAttribute("href")).filter(Boolean))]')

def visible_library_slugs(page):
    return page.locator('#library-grid > ul > li:not([hidden]) a.card').evaluate_all('(as)=>as.map(a=>new URL(a.href).pathname.split("/").filter(Boolean).at(-1)).sort()')

def check_taxonomy(page,width):
    result={}
    response=page.goto(args.base+'/',wait_until='networkidle')
    assert response and response.status==200
    home=page.locator('a[href$="/learn/#database"]')
    assert home.count()==1 and home.locator('h2').inner_text().strip()=='MySQL'
    result['home']={'href':home.get_attribute('href'),'title':home.locator('h2').inner_text(),'overflow':check_overflow(page)}
    page.screenshot(path=str(out/f'home-{width}.png'))
    response=page.goto(args.base+'/learn/#database',wait_until='networkidle')
    assert response and response.status==200
    track=page.locator('section#database')
    assert track.locator('h2').inner_text().strip()=='MySQL'
    chapter=track.locator('a.chapter-heading')
    assert chapter.count()==1 and chapter.locator('h4').inner_text().strip()=='MySQL'
    assert chapter.get_attribute('href').endswith('/series/database/')
    result['learn']={'title':track.locator('h2').inner_text(),'description':track.locator('.track-description').inner_text(),'overflow':check_overflow(page)}
    page.screenshot(path=str(out/f'learn-{width}.png'))
    page.goto(args.base+'/library/?track=database&series=database',wait_until='networkidle')
    assert page.locator('select[name="track"] option[value="database"]').inner_text()=='MySQL'
    assert page.locator('select[name="series"] option[value="database"]').inner_text()=='MySQL'
    assert visible_library_slugs(page)==sorted(EPISODES),visible_library_slugs(page)
    page.screenshot(path=str(out/f'library-series-{width}.png'))
    page.locator('select[name="tag"]').select_option('MySQL')
    assert visible_library_slugs(page)==sorted(EPISODES)
    page.locator('button.reset').click()
    page.locator('select[name="tag"]').select_option('MySQL')
    assert visible_library_slugs(page)==sorted(EPISODES)
    result['library']={'mysqlTagMatches':visible_library_slugs(page),'trackAndSeriesIDs':'database','overflow':check_overflow(page)}
    page.screenshot(path=str(out/f'library-mysql-tag-{width}.png'))
    page.goto(args.base+'/tags/MySQL/',wait_until='networkidle')
    assert page.locator('h1').inner_text().strip()=='#MySQL'
    tag_links=links_for_episode_nodes(page.locator('a.card'))
    assert len(tag_links)==len(EPISODES) and all(any('/episodes/'+slug+'/' in u for u in tag_links) for slug in EPISODES),tag_links
    result['tag']={'links':tag_links,'overflow':check_overflow(page)}
    page.screenshot(path=str(out/f'mysql-tag-{width}.png'))
    page.goto(args.base+'/search/?q=MySQL',wait_until='networkidle')
    page.locator('.pagefind-ui__result-link').first.wait_for(state='visible',timeout=30000)
    search=page.evaluate("""async ()=>{const api=await import(new URL('../pagefind/pagefind.js',location.href).href);const r=await api.search('MySQL');return await Promise.all(r.results.map(async x=>{const d=await x.data();return {url:d.url,title:d.meta.title}}))}""")
    assert all(any('/episodes/'+slug+'/' in item['url'].rstrip('/')+'/' for item in search) for slug in EPISODES),search
    result['search']={'query':'MySQL','results':search,'overflow':check_overflow(page)}
    page.screenshot(path=str(out/f'search-mysql-{width}.png'))
    return result

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
        args=['--no-sandbox', '--autoplay-policy=no-user-gesture-required'])
    report['chromiumVersion'] = browser.version
    for width, height in [(1440,1000), (390,844)]:
        context = browser.new_context(viewport={'width':width, 'height':height}, reduced_motion='reduce')
        page = context.new_page()
        viewport_report = {'width': width, 'height': height, 'episodes': []}
        report['viewports'].append(viewport_report)
        page_errors = []
        page.on('pageerror', lambda error: page_errors.append(str(error)))
        page.on('console', lambda message: page_errors.append('console: '+message.text) if message.type=='error' else None)
        response = page.goto(args.base+'/series/database/', wait_until='networkidle')
        assert response and response.status == 200
        assert page.locator('h1').inner_text().strip() == 'MySQL'
        assert 'MySQL 8.4' in page.locator('.page-intro').inner_text()
        links = page.locator('a[href]').evaluate_all('(as)=>[...new Set(as.map(a=>a.getAttribute("href")).filter(h=>h&&h.includes("/episodes/")))]')
        assert all(any('/episodes/'+slug+'/' in link for link in links) for slug in EPISODES), links
        viewport_report['series'] = {'status': response.status, 'episodeLinks': links, 'overflow': check_overflow(page)}
        page.screenshot(path=str(out/f'series-{width}.png'))
        viewport_report['taxonomy'] = check_taxonomy(page,width)
        for slug, expected_seek in EPISODES.items():
            start_error_count = len(page_errors)
            item = {'slug': slug}
            viewport_report['episodes'].append(item)
            data = inputs[slug]
            meta, receipt = data['meta'], data['receipt']
            response = page.goto(f'{args.base}/episodes/{slug}/', wait_until='networkidle')
            assert response and response.status == 200, (slug, response.status if response else None)
            assert page.locator('h1').inner_text().strip() == meta['title']
            version = page.locator('.episode-version time')
            assert version.get_attribute('datetime') == meta['updatedAt'], (slug, version.get_attribute('datetime'), meta['updatedAt'])
            assert args.expected_date in version.inner_text(), (slug, version.inner_text())
            source_links = page.locator('.source-links a').evaluate_all('(as)=>as.map(a=>a.href)')
            assert len(source_links) == 3 and all(args.candidate in link for link in source_links), (slug, source_links)
            assert source_links[-1].endswith(quote(meta['sourcePath'], safe='/')), (slug, source_links[-1], meta['sourcePath'])
            assert page.locator('nav[aria-label="面包屑"]').get_by_role('link',name='MySQL',exact=True).count() == 1, (slug, 'MySQL breadcrumb missing')
            assert page.locator('.sp > div > a').inner_text().strip() == 'MySQL'
            neighbors = page.locator('nav.pager a').evaluate_all('(as)=>as.map(a=>a.getAttribute("href"))')
            order=list(EPISODES);i=order.index(slug)
            expected_neighbors=[name for j,name in enumerate(order) if abs(j-i)==1]
            assert len(neighbors)==len(expected_neighbors) and all(any('/episodes/'+name+'/' in u for u in neighbors) for name in expected_neighbors), (slug,neighbors,expected_neighbors)
            scope = page.locator('article.article-body > p').first.inner_text()
            assert 'MySQL 8.4' in scope
            if slug=='db-replication':
                assert '单主异步复制' in scope and 'InnoDB' not in scope
            else: assert 'InnoDB' in scope
            item['scope']={'intro':scope,'neighbors':neighbors}
            related = links_for_episode_nodes(page.locator('aside.rel a.rc'))
            expected_related = [entry if isinstance(entry,str) else entry['slug'] for entry in meta.get('related',[])]
            assert len(related)==len(expected_related) and all(any('/episodes/'+name+'/' in u for u in related) for name in expected_related), (slug,related,expected_related)
            related_http = []
            for href in related:
                target = page.request.get(urljoin(args.base+'/',href))
                assert target.status==200, (slug,href,target.status)
                related_http.append({'href':href,'status':target.status})
                target.dispose()
            item['related'] = related_http
            item['page'] = {'status':response.status, 'version':version.inner_text(), 'datetime':version.get_attribute('datetime'), 'sourceLinks':source_links, 'overflow':check_overflow(page)}
            video = page.locator('video')
            page.wait_for_function('document.querySelector("video").readyState>=1')
            metadata = video.evaluate('(v)=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,currentSrc:v.currentSrc})')
            assert metadata['width'] == 1920 and metadata['height'] == 1080, (slug, metadata)
            assert abs(metadata['duration']-data['expectedSeconds']) <= 1/data['fps']+.001, (slug, metadata, data['expectedSeconds'])
            assert metadata['currentSrc'].endswith('/episodes/'+slug+'/'+meta['video'])
            page.wait_for_function('([...document.querySelector("video").textTracks].some(t=>t.kind==="captions"&&t.cues?.length>0))')
            tracks = video.evaluate('(v)=>[...v.textTracks].map(t=>({kind:t.kind,language:t.language,mode:t.mode,cues:t.cues?.length??0,first:t.cues?.[0]?{start:t.cues[0].startTime,end:t.cues[0].endTime,text:t.cues[0].text}:null,lastEnd:t.cues?.[t.cues.length-1]?.endTime??null}))')
            captions = next(track for track in tracks if track['kind']=='captions')
            assert captions['language'] == 'zh' and captions['mode'] == 'showing'
            reference_start = receipt['appendix']['from']/data['fps']
            assert captions['lastEnd'] <= reference_start+1/data['fps'], (slug, captions, reference_start)
            body_time = (captions['first']['start']+captions['first']['end'])/2
            body = seek_paused(page, body_time)
            assert body['active'], (slug, 'no native subtitle in first narration interval', body, captions)
            video.evaluate('(v)=>{v.muted=true;return v.play()}')
            page.wait_for_function('(t)=>{const v=document.querySelector("video");return !v.paused&&v.currentTime>t+.2}', arg=body_time)
            page.keyboard.press('k')
            page.wait_for_function('document.querySelector("video").paused')
            paused = video.evaluate('(v)=>v.currentTime')
            page.wait_for_timeout(180)
            assert abs(video.evaluate('(v)=>v.currentTime')-paused) < .01
            video.scroll_into_view_if_needed()
            page.screenshot(path=str(out/f'{slug}-paused-{width}.png'))
            item['player'] = {'metadata':metadata, 'tracks':tracks, 'bodySubtitleSeek':body, 'played':True, 'keyboardPaused':True, 'pauseTime':paused}

            # Exercise the Fullscreen API with a genuine local click activation.
            video.evaluate('(v)=>v.addEventListener("click",()=>v.requestFullscreen(),{once:true})')
            video.click(position={'x':80,'y':45})
            page.wait_for_function('document.fullscreenElement===document.querySelector("video")')
            fullscreen = page.evaluate('({entered:!!document.fullscreenElement,width:document.fullscreenElement.getBoundingClientRect().width,height:document.fullscreenElement.getBoundingClientRect().height,viewportWidth:innerWidth,viewportHeight:innerHeight})')
            assert abs(fullscreen['width']-fullscreen['viewportWidth']) <= 1 and abs(fullscreen['height']-fullscreen['viewportHeight']) <= 1, (slug, fullscreen)
            page.screenshot(path=str(out/f'{slug}-fullscreen-{width}.png'))
            page.evaluate('document.exitFullscreen()')
            page.wait_for_function('!document.fullscreenElement')
            video.evaluate('(v)=>v.pause()')
            fullscreen['exited'] = True
            item['fullscreen'] = fullscreen
            check_overflow(page)

            chapters = json.loads(page.locator('#player').get_attribute('data-chapters'))
            expected_chapters = data['article']['chapters']
            article_chapter_ids = {c['id'] for c in expected_chapters}
            assert [(c['id'],c['title']) for c in chapters if c['id'] in article_chapter_ids] == [(c['id'],c['title']) for c in expected_chapters], (slug,chapters,expected_chapters)
            assert chapters and [c['start'] for c in chapters]==sorted(set(c['start'] for c in chapters))
            assert chapters[0]['start']==0 and chapters[-1]['start']<reference_start
            item['chapters'] = []
            for index,chapter in enumerate(chapters):
                if chapter['id'] in article_chapter_ids:
                    assert page.locator('article.article-body [id="'+chapter['id']+'"]').count()==1, (slug,chapter)
                selector = '.vp .side a.ch' if width>=768 else '.vp .chips a.chip'
                chapter_link = page.locator(selector+'[data-index="'+str(index)+'"]')
                assert chapter_link.get_attribute('href')==('#'+chapter['id'] if chapter['id'] in article_chapter_ids else '#player'), (slug,chapter)
                chapter_link.click()
                page.wait_for_function('(t)=>{const v=document.querySelector("video");return !v.seeking&&Math.abs(v.currentTime-t)<1.5}',arg=chapter['start'])
                video.evaluate('(v)=>v.pause()')
                assert chapter_link.get_attribute('aria-current')=='true', (slug,chapter,'active chapter missing')
                chapter_hash = page.evaluate('location.hash')
                assert chapter_hash.startswith('#t=') and abs(float(chapter_hash[3:])-chapter['start'])<1e-9, (slug,chapter,chapter_hash)
                item['chapters'].append({**chapter,'actualSeekSeconds':video.evaluate('(v)=>v.currentTime'),'active':True,'hash':page.evaluate('location.hash')})

            figure = page.locator('figure.fig').filter(has=page.locator(f'img[src$="/episodes/{slug}/article/01.jpg"]')).first
            assert figure.count() == 1, (slug, 'missing article/01.jpg figure')
            figure.scroll_into_view_if_needed()
            figure.locator('img').wait_for(state='visible')
            page.wait_for_function('(slug)=>{const i=document.querySelector(`img[src$="/episodes/${slug}/article/01.jpg"]`);return i&&i.complete&&i.naturalWidth>0}', arg=slug)
            figure.locator('img').evaluate('async i=>{await i.decode();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))}')
            seek_link = figure.locator('[data-seek-time]')
            assert seek_link.count() == 1
            assert abs(float(seek_link.get_attribute('data-seek-time'))-expected_seek) < 1e-8, (slug, seek_link.get_attribute('data-seek-time'), expected_seek)
            page.screenshot(path=str(out/f'{slug}-figure-{width}.png'))
            seek_link.click()
            page.wait_for_function('(t)=>{const v=document.querySelector("video");return !v.seeking&&Math.abs(v.currentTime-t)<1.5}', arg=expected_seek)
            actual_seek = video.evaluate('(v)=>v.currentTime')
            video.evaluate('(v)=>v.pause()')
            assert page.evaluate('location.hash') == f'#t={expected_seek:g}'
            figure_presented = seek_paused(page,expected_seek)
            video.scroll_into_view_if_needed()
            page.screenshot(path=str(out/f'{slug}-figure-seek-{width}.png'))
            item['figureSeek'] = {'expected':expected_seek, 'actual':actual_seek, 'presentedFrame':figure_presented['presentedFrame'], 'hash':page.evaluate('location.hash'), 'imageLoaded':True, 'overflow':check_overflow(page)}

            trigger = page.locator('[data-source-trigger]').first
            assert trigger.count()==1
            source_id = trigger.get_attribute('data-source-trigger')
            trigger.focus()
            page.keyboard.press('Enter')
            panel = page.locator(f'[data-source-panel="{source_id}"]')
            panel.wait_for(state='visible')
            assert panel.locator('blockquote').inner_text().strip()
            quote_identity = panel.locator('.source-identity').inner_text()
            page.screenshot(path=str(out/f'{slug}-quote-{width}.png'))
            page.keyboard.press('Escape')
            panel.wait_for(state='hidden')
            item['sourceQuote']={'sourceId':source_id,'keyboardOpened':True,'escapedClosed':True,'identity':quote_identity}

            reference_pages = []
            frames_per_page = receipt['appendix']['framesPerPage']
            for index in range(len(receipt['appendix']['pages'])):
                seconds = reference_start+(index+.5)*frames_per_page/data['fps']
                reference = seek_paused(page, seconds)
                assert not reference['active'], (slug, 'native subtitle crossed into references', reference)
                video.scroll_into_view_if_needed()
                page.screenshot(path=str(out/f'{slug}-references-{index+1}-{width}.png'))
                reference_pages.append(reference)
            # Seeking back into narration restores the appropriate native cue.
            restored = seek_paused(page, body_time)
            assert restored['active'], (slug, 'caption did not return after leaving references', restored)
            item['references'] = {'fromSeconds':reference_start, 'pages':reference_pages, 'captionsRestoredOnReturn':True}
            item['pageErrors'] = page_errors[start_error_count:]
            assert not item['pageErrors'], (slug, item['pageErrors'])
        viewport_report['pageErrors'] = page_errors
        assert not page_errors, page_errors
        context.close()
    browser.close()
report['status'] = 'passed'
print(json.dumps({'status':'passed','episodes':len(EPISODES),'viewports':2,'httpVideosVerified':len(report['httpMedia']),'report':str(out/'report.json')}, ensure_ascii=False))
