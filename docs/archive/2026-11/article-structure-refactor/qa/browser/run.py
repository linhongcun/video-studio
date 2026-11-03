#!/usr/bin/env python3
"""Actual Chromium QA for the final built article structure/navigation release.

Run only after the main agent confirms the final v0.100.0 build. No application
files or served responses are changed. Browser viewport/theme preferences are
test inputs; this is not a physical mobile-device test.
"""
import argparse
import asyncio
import hashlib
import http.server
import json
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from playwright.async_api import async_playwright

ROOT = Path('/workspace/video-studio')
QA = Path('/workspace/work/article-structure-refactor/browser-qa')
COMBOS = [
    ('desktop-light', 1440, 1000, 'light'),
    ('desktop-dark', 1440, 1000, 'dark'),
    ('mobile-light', 390, 844, 'light'),
    ('mobile-dark', 390, 844, 'dark'),
]
REPRESENTATIVES = ['dns', 'kafka-consumer-idempotency', 'binary-search', 'egg-drop', 'adapter-pattern']
SHOTS = [
    ('dns', 'mobile-light', 'opening'),
    ('dns', 'mobile-light', 'directory'),
    ('kafka-consumer-idempotency', 'mobile-dark', 'opening'),
    ('kafka-consumer-idempotency', 'desktop-dark', 'deep'),
    ('adapter-pattern', 'desktop-light', 'opening'),
    ('binary-search', 'mobile-light', 'directory'),
    ('egg-drop', 'desktop-light', 'deep'),
    ('monty-hall', 'mobile-dark', 'summary'),
]


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT / 'site/dist'), **kw)

    def translate_path(self, path):
        parts = urlsplit(path)
        route = parts.path
        if route == '/video-studio':
            route = '/'
        elif route.startswith('/video-studio/'):
            route = route[len('/video-studio'):]
        return super().translate_path(urlunsplit(('', '', route, parts.query, parts.fragment)))

    def log_message(self, *a):
        pass

    def handle(self):
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError):
            pass


DOM = r'''() => {
 const article=document.querySelector('#article');
 const toc=document.querySelector('details.toc');
 if(!article||!toc)throw Error('Missing article or article directory');
 const visible=e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0;};
 const blocked='figure,svg,pre,code,script,style,template,details,.article-end,.footnotes,[data-footnotes],[hidden],[aria-hidden="true"]';
 const hs=[...article.querySelectorAll('h2,h3')].filter(h=>!h.closest(blocked)&&visible(h));
 const norm=s=>s.replace(/\s+/g,' ').trim();
 const label=h=>{const c=h.cloneNode(true);c.querySelectorAll('.anchor,.from,[data-seek]').forEach(n=>n.remove());return norm(c.textContent);};
 const links=[...toc.querySelectorAll('[data-toc]')];
 if(!hs.length||links.length!==hs.length)throw Error(`Directory count ${links.length} differs from real visible headings ${hs.length}`);
 const mapped=[];
 for(let i=0;i<hs.length;i++){
   const h=hs[i],a=links[i],id=a.dataset.toc;
   if(!id||h.id!==id)throw Error(`Directory order/target mismatch at ${i}: ${id} / ${h.id}`);
   if(document.querySelectorAll('#'+CSS.escape(id)).length!==1)throw Error(`Target ${id} is not unique`);
   if(a.hash!=='#'+encodeURI(id)&&decodeURIComponent(a.hash)!=='#'+id)throw Error(`Link hash does not target ${id}`);
   if(a.hasAttribute('data-seek')||a.hasAttribute('data-seek-time')||a.hasAttribute('data-start'))throw Error('Article directory incorrectly seeks video');
   if(norm(a.textContent)!==label(h))throw Error(`Directory title differs from rendered title: ${norm(a.textContent)} / ${label(h)}`);
   mapped.push({id,title:label(h),depth:Number(h.tagName[1])});
 }
 const first=hs[0];
 const before=[...article.querySelectorAll('p')].filter(p=>!p.closest(blocked)&&(p.compareDocumentPosition(first)&Node.DOCUMENT_POSITION_FOLLOWING)&&visible(p));
 const opening=before.map(p=>norm(p.textContent)).filter(Boolean);
 if(!opening.length||opening.join('').length<30)throw Error('Missing visible opening before the first H2');
 const viewportOverflow=document.documentElement.scrollWidth-document.documentElement.clientWidth;
 const articleOverflow=article.scrollWidth-article.clientWidth;
 const tocOverflow=toc.scrollWidth-toc.clientWidth;
 if(viewportOverflow>1||articleOverflow>1||tocOverflow>1)throw Error(`Horizontal overflow: page ${viewportOverflow}, article ${articleOverflow}, toc ${tocOverflow}`);
 const chapters=JSON.parse(document.querySelector('#player').dataset.chapters);
 return {opening,openingParagraphs:opening.length,firstHeading:{id:first.id,title:label(first)},headings:mapped,headingCount:hs.length,deepTargets:mapped.filter(h=>/深入|附录|拓展|复现|核验/.test(h.title)),summaryTargets:mapped.filter(h=>/小结|回看主线|三种差异各管什么|记住这个排除依据/.test(h.title)),chapters,viewportOverflow,articleOverflow,tocOverflow,directoryOpen:toc.open,theme:document.documentElement.dataset.theme,footerVersion:document.querySelector('footer .num')?.textContent,localScrollable:[...article.querySelectorAll('pre,table')].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>({tag:e.tagName,width:e.clientWidth,scrollWidth:e.scrollWidth}))};
}'''


async def context_for(browser, combo):
    name, width, height, theme = combo
    context = await browser.new_context(
        viewport={'width': width, 'height': height}, device_scale_factor=1,
        color_scheme=theme, reduced_motion='reduce',
    )
    await context.add_init_script(f"localStorage.setItem('vs:theme',{json.dumps(theme)});")
    return context


async def open_page(context, base, slug, version):
    page = await context.new_page()
    response = await page.goto(f'{base}/episodes/{slug}/', wait_until='domcontentloaded', timeout=30000)
    assert response and response.status == 200, f'Page response {response.status if response else None}'
    await page.evaluate('document.fonts.ready')
    await page.locator('#article').wait_for(state='visible')
    await page.wait_for_function("document.querySelector('footer .num')?.textContent=== " + json.dumps('v' + version))
    return page


async def anchor_click(page, target_id):
    directory = page.locator('details.toc')
    if not await directory.evaluate('(e)=>e.open'):
        await directory.locator('summary').click()
    before = await page.locator('video').evaluate('(v)=>({time:v.currentTime,paused:v.paused})')
    link = page.locator('[data-toc='+json.dumps(target_id,ensure_ascii=False)+']')
    await link.click()
    await page.wait_for_function('id=>decodeURIComponent(location.hash)==="#"+id', arg=target_id)
    after = await page.locator('video').evaluate('(v)=>({time:v.currentTime,paused:v.paused})')
    assert abs(after['time'] - before['time']) < .1, f'Directory changed video time {before} / {after}'
    target = page.locator('#article [id='+json.dumps(target_id,ensure_ascii=False)+']')
    rect = await target.bounding_box()
    assert rect and 0 <= rect['y'] < page.viewport_size['height'] - 20, f'Anchor not visible: {rect}'
    return {'id': target_id, 'hash': await page.evaluate('decodeURIComponent(location.hash)'), 'beforeVideo': before, 'afterVideo': after, 'targetBounds': rect}


async def chapter_seek(page, old_chapters):
    await page.wait_for_function("document.querySelector('video').readyState>=1", timeout=20000)
    controls = await page.locator('#article [data-seek]').evaluate_all('(es)=>es.map(e=>e.dataset.seek)')
    chapter = next((c for c in old_chapters if c['id'] in controls and c['start'] > 0), None)
    assert chapter, 'No non-zero old chapter control available'
    button = page.locator('#article [data-seek='+json.dumps(chapter['id'],ensure_ascii=False)+']').first
    await button.click()
    await page.wait_for_function('s=>Math.abs(document.querySelector("video").currentTime-s)<1.5', arg=chapter['start'], timeout=10000)
    actual = await page.locator('video').evaluate('(v)=>({time:v.currentTime,readyState:v.readyState,duration:v.duration,paused:v.paused})')
    await page.locator('video').evaluate('(v)=>v.pause()')
    assert abs(actual['time'] - chapter['start']) < 1.5
    return {'id': chapter['id'], 'expectedStart': chapter['start'], 'observed': actual}


async def quote_and_figure(page):
    trigger = page.locator('[data-source-trigger]').first
    source_id = await trigger.get_attribute('data-source-trigger')
    panel = page.locator('[data-source-panel='+json.dumps(source_id,ensure_ascii=False)+']')
    await trigger.scroll_into_view_if_needed()
    await page.mouse.move(0, 0)
    await trigger.focus()
    await page.keyboard.press('Enter')
    await panel.wait_for(state='visible')
    keyboard = await panel.evaluate('(e)=>({open:e.matches(":popover-open"),bounds:(()=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height}})(),links:[...e.querySelectorAll("a")].map(a=>a.href)})')
    assert keyboard['open'] and keyboard['links']
    await page.keyboard.press('Escape')
    await panel.wait_for(state='hidden')
    await trigger.click()
    await panel.wait_for(state='visible')
    clicked = await panel.evaluate('(e)=>({open:e.matches(":popover-open"),state:e.dataset.sourceState})')
    assert clicked['open'] and clicked['state'] == 'pinned'
    await page.keyboard.press('Escape')
    await panel.wait_for(state='hidden')
    image = page.locator('.fig .fig-image-link').first
    src = await image.get_attribute('href')
    await image.click()
    await page.wait_for_url('**'+src)
    await page.wait_for_function('document.images.length>0&&document.images[0].complete&&document.images[0].naturalWidth>0')
    original = await page.evaluate('({url:location.href,width:document.images[0].naturalWidth,height:document.images[0].naturalHeight})')
    await page.go_back(wait_until='domcontentloaded')
    await page.wait_for_function("document.querySelector('video').readyState>=1", timeout=20000)
    seek = page.locator('.fig [data-seek-time]').first
    seconds = float(await seek.get_attribute('data-seek-time'))
    await seek.click()
    await page.wait_for_function('s=>Math.abs(document.querySelector("video").currentTime-s)<1.5', arg=seconds, timeout=10000)
    observed = await page.locator('video').evaluate('(v)=>({time:v.currentTime,readyState:v.readyState})')
    await page.locator('video').evaluate('(v)=>v.pause()')
    return {'sourceId': source_id, 'keyboard': keyboard, 'click': clicked, 'originalImage': original, 'figureSeek': {'expected': seconds, 'observed': observed}}


async def run(args):
    QA.mkdir(parents=True, exist_ok=True)
    inventory = json.loads(Path(args.inventory).read_text())
    rows = [r for r in inventory['articles'] if not r.get('archived') and not r.get('draft')]
    assert len(rows) == 59 and len({r['slug'] for r in rows}) == 59
    old = {r['slug']: r['chapters'] for r in json.loads((QA.parent/'previous-rendering.json').read_text())}
    assert len(old) == 60
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = args.base_url.rstrip('/') if args.base_url else f'http://127.0.0.1:{server.server_port}/video-studio'
    started = time.time()
    previous=json.loads(Path(args.retry_interactions).read_text()) if args.retry_interactions else None
    results=list(previous['results']) if previous else []
    failures,actions=[],[]
    shots=list(previous['screenshots']) if previous else []
    archived=list(previous['archivedMapChecks']) if previous else []
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
        async def combo_run(combo):
            name, width, height, theme = combo
            context = await context_for(browser, combo)
            page = await context.new_page()
            for row in rows:
                slug = row['slug']
                try:
                    response = await page.goto(f'{base}/episodes/{slug}/', wait_until='domcontentloaded', timeout=30000)
                    assert response and response.status == 200
                    await page.evaluate('document.fonts.ready')
                    directory = page.locator('details.toc')
                    await directory.wait_for(state='visible')
                    initially_open = await directory.evaluate('(e)=>e.open')
                    assert initially_open == (width >= 1200), f'Directory initial layout: {initially_open}'
                    if width < 1200:
                        await directory.locator('summary').click()
                        assert await directory.evaluate('(e)=>e.open')
                    data = await page.evaluate(DOM)
                    assert data['theme'] == theme and data['footerVersion'] == 'v'+args.expected_version
                    assert data['chapters'] == old[slug], 'Video chapter map changed'
                    if width < 1200:
                        await directory.locator('summary').click()
                        assert not await directory.evaluate('(e)=>e.open')
                    data.update(slug=slug, combination=name, width=width, height=height, initialDirectoryOpen=initially_open, mobileToggleChecked=width<1200)
                    results.append(data)
                except Exception as exc:
                    failures.append({'kind': 'matrix', 'slug': slug, 'combination': name, 'error': str(exc)})
            if name == 'desktop-light':
                for slug in old.keys()-{r['slug'] for r in rows}:
                    try:
                        await page.goto(f'{base}/episodes/{slug}/', wait_until='domcontentloaded')
                        actual=await page.locator('#player').evaluate('(e)=>JSON.parse(e.dataset.chapters)')
                        assert actual == old[slug]
                        archived.append({'slug':slug,'chapterMapUnchanged':True})
                    except Exception as exc:
                        failures.append({'kind':'archived-map','slug':slug,'error':str(exc)})
            await context.close()
            print(name, 'matrix complete', flush=True)
        if not previous:
            await asyncio.gather(*(combo_run(combo) for combo in COMBOS))
        for combo in [COMBOS[0], COMBOS[3]]:
            context=await context_for(browser,combo)
            for slug in REPRESENTATIVES:
                page=None
                try:
                    page=await open_page(context,base,slug,args.expected_version)
                    targets=await page.locator('[data-toc]').evaluate_all('(es)=>es.map(e=>({id:e.dataset.toc,title:e.textContent.trim()}))')
                    target=next((t for t in targets if '小结' in t['title']),None) or next(t for t in targets if t['id'] not in {c['id'] for c in old[slug]})
                    anchor=await anchor_click(page,target['id'])
                    chapter=await chapter_seek(page,old[slug])
                    actions.append({'kind':'directory-and-old-chapter','slug':slug,'combination':combo[0],'directory':anchor,'chapter':chapter})
                except Exception as exc:
                    failures.append({'kind':'directory-and-old-chapter','slug':slug,'combination':combo[0],'error':str(exc)})
                finally:
                    if page:await page.close()
            page=None
            try:
                page=await open_page(context,base,'dns',args.expected_version)
                interaction=await quote_and_figure(page)
                actions.append({'kind':'quote-and-figure','slug':'dns','combination':combo[0],**interaction})
            except Exception as exc:
                failures.append({'kind':'quote-and-figure','slug':'dns','combination':combo[0],'error':str(exc)})
            finally:
                if page:await page.close()
            await context.close()
        for slug,combo_name,kind in ([] if previous else SHOTS):
            context=await context_for(browser,next(c for c in COMBOS if c[0]==combo_name))
            page=None
            try:
                page=await open_page(context,base,slug,args.expected_version)
                if kind=='directory':
                    target=page.locator('details.toc')
                    if not await target.evaluate('(e)=>e.open'):await target.locator('summary').click()
                elif kind=='opening':
                    target=page.locator('#article')
                else:
                    target=page.locator('#article h2,#article h3').filter(has_text='深入').first if kind=='deep' else page.locator('#article section.summary')
                    if await target.count()==0 and kind=='deep':
                        target=page.locator('#article [id="bounds"]')
                    assert await target.count()>0,'Screenshot target absent'
                await target.scroll_into_view_if_needed()
                await page.evaluate('(e)=>window.scrollBy(0,e.getBoundingClientRect().top-96)',await target.element_handle())
                await page.wait_for_timeout(120)
                for image in await page.locator('#article img').all():
                    # Only wait for images that naturally entered this viewport.
                    if await image.evaluate('(e)=>{const r=e.getBoundingClientRect();return r.top<innerHeight&&r.bottom>0;}'):
                        await image.evaluate('(e)=>e.decode().catch(()=>{})')
                path=QA/f'{slug}-{combo_name}-{kind}.png'
                await page.screenshot(path=str(path),full_page=False)
                shots.append({'slug':slug,'combination':combo_name,'kind':kind,'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'actualVisualReview':'pending'})
            except Exception as exc:
                failures.append({'kind':'screenshot','slug':slug,'combination':combo_name,'targetKind':kind,'error':str(exc)})
            finally:
                if page:await page.close()
                await context.close()
        await browser.close()
    server.shutdown()
    report={'startedUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(started)),'elapsedSeconds':round(time.time()-started,2),'baseUrl':base,'version':args.expected_version,'scope':'Actual system Chromium via Playwright; 59 current article pages × 1440/390 simulated viewports × light/dark; visible opening presence, exact real H2/H3 directory mapping, independent article anchors and unchanged old video chapter maps. Focused actual clicks for five articles in two viewport/theme combinations; one quote and figure workflow in both combinations. Not physical devices, full playback/ASR or reader comprehension testing.','expectedMatrixChecks':236,'passedMatrixChecks':len(results),'archivedMapChecks':archived,'actions':actions,'screenshots':shots,'failures':failures,'results':results}
    report['matrixReusedFrom']=args.retry_interactions or None
    out=QA/args.output
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'matrixPassed':len(results),'actionsPassed':len(actions),'screenshots':len(shots),'failures':len(failures),'seconds':report['elapsedSeconds']},ensure_ascii=False),flush=True)
    if failures:
        print(json.dumps(failures,ensure_ascii=False,indent=2),flush=True)
        raise SystemExit(1)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--expected-version',default='0.100.0')
    parser.add_argument('--base-url',default='')
    parser.add_argument('--retry-interactions',default='')
    parser.add_argument('--output',default='local-result.json')
    parser.add_argument('--inventory',default=str(ROOT/'docs/archive/2026-11/article-structure-refactor/inventory.json'))
    asyncio.run(run(parser.parse_args()))
