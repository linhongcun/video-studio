from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse, atexit, hashlib, json, subprocess, sys, urllib.request
from urllib.parse import quote
from playwright.sync_api import sync_playwright

EPISODES = {
    'horse-racing': 139.0,
    'bridge-torch': 120.0,
    'water-jug': 148.7,
    'monty-hall': 170.5,
    'egg-drop': 110.0,
}
parser = argparse.ArgumentParser()
parser.add_argument('--root', default='/workspace/work/video-studio-sitecheck')
parser.add_argument('--base', default='http://127.0.0.1:4321/video-studio')
parser.add_argument('--candidate', required=True)
parser.add_argument('--expected-date', required=True)
parser.add_argument('--out', required=True)
args = parser.parse_args()
root = Path(args.root).resolve()
out = Path(args.out).resolve()
out.mkdir(parents=True, exist_ok=True)
report = {
    'candidate': args.candidate, 'base': args.base,
    'scope': list(EPISODES),
    'browser': 'Headless Chromium /usr/bin/chromium; desktop and 390px viewport simulation, not physical-device testing',
    'httpMedia': [], 'viewports': [], 'errors': [],
}
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
    media = full_http_sha(f"{args.base}/episodes/{slug}/{meta['video']}")
    assert media['sha256'] == expected_sha, (slug, 'HTTP/render hash mismatch', media)
    if result.get('bytes') is not None:
        assert media['bytes'] == result['bytes'], (slug, 'HTTP/render bytes mismatch')
    image = full_http_sha(f'{args.base}/episodes/{slug}/article/01.jpg')
    assert image['sha256'] == sha_file(directory/'article/01.jpg'), (slug, 'HTTP/candidate article image mismatch')
    report['httpMedia'].append({'slug': slug, 'video': media, 'articleImage': image})
    inputs[slug] = {'meta': meta, 'result': result, 'receipt': receipt, 'fps': fps, 'expectedSeconds': final_frames/fps}


def check_overflow(page):
    size = page.evaluate('({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth})')
    assert size['scroll'] <= size['client']+1, size
    return size

def seek_paused(page, time):
    page.locator('video').evaluate('(v,t)=>{v.pause();v.currentTime=t;}', time)
    page.wait_for_function('(t)=>{const v=document.querySelector("video");return !v.seeking&&v.readyState>=2&&Math.abs(v.currentTime-t)<.05}', arg=time)
    page.wait_for_timeout(120)
    return page.locator('video').evaluate('(v)=>({time:v.currentTime,active:[...v.textTracks].flatMap(t=>[...(t.activeCues??[])].map(c=>c.text))})')

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
        response = page.goto(args.base+'/series/puzzles/', wait_until='networkidle')
        assert response and response.status == 200
        links = page.locator('a[href]').evaluate_all('(as)=>[...new Set(as.map(a=>a.getAttribute("href")).filter(h=>h&&h.includes("/episodes/")))]')
        assert all(any('/episodes/'+slug+'/' in link for link in links) for slug in EPISODES), links
        viewport_report['series'] = {'status': response.status, 'episodeLinks': links, 'overflow': check_overflow(page)}
        page.screenshot(path=str(out/f'series-{width}.png'))
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

            figure = page.locator('figure.fig').filter(has=page.locator(f'img[src$="/episodes/{slug}/article/01.jpg"]')).first
            assert figure.count() == 1, (slug, 'missing article/01.jpg figure')
            figure.scroll_into_view_if_needed()
            figure.locator('img').wait_for(state='visible')
            page.wait_for_function('(slug)=>{const i=document.querySelector(`img[src$="/episodes/${slug}/article/01.jpg"]`);return i&&i.complete&&i.naturalWidth>0}', arg=slug)
            seek_link = figure.locator('[data-seek-time]')
            assert seek_link.count() == 1
            assert abs(float(seek_link.get_attribute('data-seek-time'))-expected_seek) < 1e-8, (slug, seek_link.get_attribute('data-seek-time'), expected_seek)
            page.screenshot(path=str(out/f'{slug}-figure-{width}.png'))
            seek_link.click()
            page.wait_for_function('(t)=>{const v=document.querySelector("video");return !v.seeking&&Math.abs(v.currentTime-t)<1.5}', arg=expected_seek)
            actual_seek = video.evaluate('(v)=>v.currentTime')
            video.evaluate('(v)=>v.pause()')
            assert page.evaluate('location.hash') == f'#t={expected_seek:g}'
            page.wait_for_timeout(150)
            video.scroll_into_view_if_needed()
            page.screenshot(path=str(out/f'{slug}-figure-seek-{width}.png'))
            item['figureSeek'] = {'expected':expected_seek, 'actual':actual_seek, 'hash':page.evaluate('location.hash'), 'imageLoaded':True, 'overflow':check_overflow(page)}

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
