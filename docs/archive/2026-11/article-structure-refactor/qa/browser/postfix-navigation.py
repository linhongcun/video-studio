"""Focused real-browser follow-up for the TOC current-section fix.
Run only after the main agent confirms the rebuilt static site is ready.
"""
import argparse,asyncio,hashlib,json,time
from pathlib import Path
from playwright.async_api import async_playwright
Q=Path('/workspace/work/article-structure-refactor/browser-qa')
async def main(args):
    cases=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for slug,width,height,theme,needle in [
            ('egg-drop',1440,1000,'light','深入核对：全阈值与端点怎样核验'),
            ('binary-search',390,844,'dark','深入阅读：实现与演示怎样核对')]:
            context=await browser.new_context(viewport={'width':width,'height':height},color_scheme=theme,reduced_motion='reduce')
            await context.add_init_script('localStorage.setItem("vs:theme",'+json.dumps(theme)+');')
            page=await context.new_page()
            await page.goto(args.base_url.rstrip('/')+'/episodes/'+slug+'/',wait_until='domcontentloaded')
            await page.evaluate('document.fonts.ready')
            directory=page.locator('details.toc')
            await directory.wait_for(state='visible')
            default_open=await directory.evaluate('e=>e.open')
            assert default_open==(width>=1200)
            if not default_open:await directory.locator('summary').click()
            links=page.locator('[data-toc]')
            link=links.filter(has_text=needle)
            assert await link.count()==1
            target_id=await link.get_attribute('data-toc')
            video=page.locator('video')
            before=await video.evaluate('v=>({time:v.currentTime,paused:v.paused})')
            # Native link activation, without setting location/hash or scrolling in test code.
            await link.click()
            await page.wait_for_function('id=>decodeURIComponent(location.hash)==="#"+id',arg=target_id)
            await page.wait_for_function('id=>document.querySelector("[data-toc][aria-current]")?.dataset.toc===id',arg=target_id)
            await page.wait_for_timeout(250)
            async def observation():
                return await page.evaluate('id=>{const target=document.getElementById(id),r=target.getBoundingClientRect(),a=document.querySelector("[data-toc][aria-current]");return {hash:decodeURIComponent(location.hash),targetBounds:{x:r.x,y:r.y,width:r.width,height:r.height},active:a?.dataset.toc,video:{time:document.querySelector("video").currentTime,paused:document.querySelector("video").paused},horizontalOverflow:document.documentElement.scrollWidth-document.documentElement.clientWidth};}',target_id)
            first=await observation()
            assert first['active']==target_id and 0<=first['targetBounds']['y']<height-20
            assert abs(first['video']['time']-before['time'])<.1 and first['horizontalOverflow']<=1
            screenshot=Q/f'{slug}-{width}-{theme}-navigation-fixed.png'
            await page.screenshot(path=str(screenshot),full_page=False)
            # A second native anchor creates a hash-history entry; Back must restore
            # the first heading and corresponding current-section state.
            summary=links.filter(has_text='小结')
            summary_id=await summary.get_attribute('data-toc')
            await summary.click()
            await page.wait_for_function('id=>decodeURIComponent(location.hash)==="#"+id&&document.querySelector("[data-toc][aria-current]")?.dataset.toc===id',arg=summary_id)
            summary_observed=await page.evaluate('id=>{const r=document.getElementById(id).getBoundingClientRect();return {hash:decodeURIComponent(location.hash),active:document.querySelector("[data-toc][aria-current]")?.dataset.toc,targetY:r.y,video:{time:document.querySelector("video").currentTime,paused:document.querySelector("video").paused}};}',summary_id)
            assert abs(summary_observed['video']['time']-before['time'])<.1 and 0<=summary_observed['targetY']<height-20
            await page.go_back(wait_until='domcontentloaded')
            await page.wait_for_function('id=>decodeURIComponent(location.hash)==="#"+id&&document.querySelector("[data-toc][aria-current]")?.dataset.toc===id',arg=target_id)
            await page.wait_for_timeout(250)
            restored=await observation()
            assert restored['active']==target_id and 0<=restored['targetBounds']['y']<height-20
            assert abs(restored['video']['time']-before['time'])<.1
            cases.append({'slug':slug,'width':width,'height':height,'theme':theme,'defaultDirectoryOpen':default_open,'mobileDirectoryOpened':width<1200,'targetId':target_id,'beforeVideo':before,'afterNativeClick':first,'summaryId':summary_id,'afterSummaryClick':summary_observed,'afterSummaryThenBrowserBack':restored,'screenshot':str(screenshot),'screenshotSha256':hashlib.sha256(screenshot.read_bytes()).hexdigest(),'actualVisualReview':'pending'})
            await context.close()
        await browser.close()
    report={'observedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'baseUrl':args.base_url,'scope':'Focused current-section fix only. Existing 236 matrix and 12 media/quote workflows are reused by exact source-difference scope. No full matrix rerun. Two actual native directory clicks followed by summary click and browser Back, in desktop/light and mobile/dark.','cases':cases,'failures':[]}
    (Q/'postfix-navigation-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--base-url',default='http://127.0.0.1:4328/video-studio');asyncio.run(main(parser.parse_args()))
