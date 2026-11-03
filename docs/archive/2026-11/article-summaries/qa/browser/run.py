#!/usr/bin/env python3
"""Local built-site summary QA; run only after the final v0.99.2 build."""
import argparse, asyncio, hashlib, http.server, json, re, threading, time
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from playwright.async_api import async_playwright

ROOT=Path('/workspace/video-studio')
QA=Path('/workspace/work/article-summaries/browser-qa')
REPORTS=Path('/workspace/work/article-summaries/reports')
COMBOS=[('desktop-light',1440,1000,'light'),('desktop-dark',1440,1000,'dark'),('mobile-light',390,844,'light'),('mobile-dark',390,844,'dark')]
REPRESENTATIVES={'adapter-pattern':'desktop-light','kafka-consumer-idempotency':'mobile-dark','binary-search':'mobile-light','monty-hall':'desktop-dark'}

class LocalHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=str(ROOT/'site/dist'),**kw)
    def translate_path(self,path):
        split=urlsplit(path)
        route=split.path
        if route=='/video-studio': route='/'
        elif route.startswith('/video-studio/'): route=route[len('/video-studio'):]
        return super().translate_path(urlunsplit(('', '',route,split.query,split.fragment)))
    def log_message(self,*a): pass
    def handle(self):
        try: super().handle()
        except (BrokenPipeError,ConnectionResetError): pass

DOM_CHECK=r'''({heading, requiredCard}) => {
 const article=document.querySelector('#article');
 if (!article) throw Error('Missing article DOM');
 const headings=[...article.querySelectorAll('h2,h3')].filter(h=>!h.closest('.article-end,.footnotes,[data-footnotes]'));
 const label=(h)=>{const c=h.cloneNode(true); c.querySelectorAll('a,button,.chh-actions').forEach(x=>x.remove()); return c.textContent.trim();};
 const matches=headings.filter(h=>label(h)===heading);
 if(matches.length!==1) throw Error(`Expected one summary heading ${heading}, found ${matches.length}`);
 const h=matches[0];
 const card=h.closest('section.summary');
 if(requiredCard&&!card) throw Error('New summary missing shared section.summary');
 const start=card||h;
 const following=headings.filter(n=>h.compareDocumentPosition(n)&Node.DOCUMENT_POSITION_FOLLOWING);
 const h2after=following.filter(n=>n.tagName==='H2').map(label);
 const reference=/参考资料|来源与验证范围/;
 if(h2after.length===0||!reference.test(h2after[0])) throw Error(`Next main section is not references: ${JSON.stringify(h2after)}`);
 const other=h2after.filter(t=>!reference.test(t));
 if(other.length) throw Error(`Body section follows summary: ${JSON.stringify(other)}`);
 const s=getComputedStyle(start),r=start.getBoundingClientRect();
 if(s.display==='none'||s.visibility==='hidden'||r.width===0||r.height===0) throw Error('Summary not rendered visibly');
 const viewportOverflow=document.documentElement.scrollWidth-document.documentElement.clientWidth;
 // Page overflow is separately reported; an unchanged reference-list SHA is a known unrelated limitation.
 let summaryOverflow=0;
 if(card){
  summaryOverflow=card.scrollWidth-card.clientWidth;
  if(summaryOverflow>1) throw Error(`Summary horizontal overflow ${summaryOverflow}px`);
 }
 return {heading,headingId:h.id,tag:h.tagName,sharedCard:!!card,summaryText:card?.innerText||h.nextElementSibling?.innerText||'',afterHeadings:following.map(n=>({tag:n.tagName,text:label(n)})),viewportOverflow,summaryOverflow,theme:document.documentElement.dataset.theme,summaryBounds:{x:r.x,y:r.y,width:r.width,height:r.height},background:s.backgroundColor,borderTop:s.borderTopColor,footerVersion:document.querySelector('footer .num')?.textContent};
}'''

async def run(args):
    inventory=json.loads((ROOT/'docs/archive/2026-11/article-summaries/inventory.json').read_text())
    rows=inventory['articles']
    rows=[r for r in rows if r['action']!='skipped_archived']
    assert len(rows)==59 and len({r['slug'] for r in rows})==59
    for row in rows:
        row['normalizedHeading']=re.sub(r'\s*\{#[\w-]+\}\s*$','',re.sub(r'^#+\s*','',row['summaryHeading'])).strip()
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),LocalHandler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=args.base_url.rstrip('/') if args.base_url else f'http://127.0.0.1:{server.server_port}/video-studio'
    started=time.time()
    previous=json.loads(Path(args.retry_from).read_text()) if args.retry_from else None
    retry_keys={(r['slug'],r['combination']) for r in previous['failures']} if previous else None
    results=list(previous['results']) if previous else []; errors=[]; screenshots=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        async def combo(name,width,height,theme):
            context=await browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1,color_scheme=theme)
            await context.add_init_script(f"localStorage.setItem('vs:theme',{json.dumps(theme)});")
            page=await context.new_page()
            for row in rows:
                if retry_keys is not None and (row['slug'],name) not in retry_keys: continue
                slug=row['slug']; url=f'{base}/episodes/{slug}/'
                try:
                    response=await page.goto(url,wait_until='domcontentloaded',timeout=30000)
                    assert response and response.status==200, f'Unexpected response {response.status if response else None}'
                    await page.locator('#article').wait_for(state='visible')
                    await page.evaluate('document.fonts.ready')
                    data=await page.evaluate(DOM_CHECK,{'heading':row['normalizedHeading'],'requiredCard':row['action']!='retained'})
                    assert data['theme']==theme,(data['theme'],theme)
                    assert data['footerVersion']==f'v{args.expected_version}', f"Wrong build {data['footerVersion']}"
                    # Scroll the real summary into the viewport; no source/CSS or content changes.
                    heading=page.locator('#article').locator('[id='+json.dumps(data['headingId'])+']')
                    await heading.scroll_into_view_if_needed()
                    await page.evaluate('''h=>window.scrollBy(0,(h.closest('section.summary')||h).getBoundingClientRect().top-96)''',await heading.element_handle())
                    visible=await heading.is_visible()
                    assert visible,'Summary heading hidden after scrolling'
                    data.update({'slug':slug,'combination':name,'viewport':{'width':width,'height':height},'action':row['action'],'url':url,'scrolledHeadingVisible':visible})
                    results.append(data)
                except Exception as e:
                    errors.append({'slug':slug,'combination':name,'error':str(e)})
            await context.close()
            print(name,'complete',flush=True)
        await asyncio.gather(*(combo(*c) for c in COMBOS))
        for slug,combo_name in REPRESENTATIVES.items():
            _,width,height,theme=next(c for c in COMBOS if c[0]==combo_name)
            context=await browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1,color_scheme=theme)
            await context.add_init_script(f"localStorage.setItem('vs:theme',{json.dumps(theme)});")
            page=await context.new_page()
            await page.goto(f'{base}/episodes/{slug}/',wait_until='domcontentloaded')
            await page.evaluate('document.fonts.ready')
            heading=page.locator('#article').get_by_role('heading',name='小结',exact=True)
            await heading.scroll_into_view_if_needed()
            await page.evaluate('''h=>window.scrollBy(0,(h.closest('section.summary')||h).getBoundingClientRect().top-96)''',await heading.element_handle())
            await page.wait_for_timeout(150)
            shot=QA/f'{slug}-{combo_name}.png'
            await page.screenshot(path=str(shot),full_page=False)
            screenshots.append({'slug':slug,'combination':combo_name,'path':str(shot),'sha256':hashlib.sha256(shot.read_bytes()).hexdigest()})
            await context.close()
        await browser.close()
    server.shutdown()
    report={'startedUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(started)),'elapsedSeconds':round(time.time()-started,2),'baseUrl':base,'expectedVersion':args.expected_version,'browser':'system Chromium /usr/bin/chromium; headless Playwright','scope':'59 current pages × desktop1440/mobile390 × light/dark; simulated viewports; summary layout and final heading/reference ordering only. Videos and full citation/figure interaction are outside this focused check. Screenshot visual inspection is separately recorded after images are opened.','expectedPages':59,'expectedChecks':236,'passedChecks':len(results),'retryFrom':args.retry_from or None,'inheritedPageOverflow':[{'slug':r['slug'],'combination':r['combination'],'pixels':r['viewportOverflow']} for r in results if r['viewportOverflow']>1],'failures':errors,'screenshots':screenshots,'results':results}
    (QA/('online-result.json' if args.base_url else 'local-result.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':len(results),'failed':len(errors),'screenshots':len(screenshots),'seconds':report['elapsedSeconds']},ensure_ascii=False),flush=True)
    if errors:
        print(json.dumps(errors,ensure_ascii=False,indent=2),flush=True)
        raise SystemExit(1)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--expected-version',default='0.99.2')
    parser.add_argument('--base-url',default='')
    parser.add_argument('--retry-from',default='')
    asyncio.run(run(parser.parse_args()))
