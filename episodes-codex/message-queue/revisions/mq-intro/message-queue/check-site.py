#!/usr/bin/env python3
"""Check this revision's actual built player/article at a supplied base URL."""
from pathlib import Path
import argparse
import hashlib
import json
from playwright.sync_api import sync_playwright

D = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--base', default='http://127.0.0.1:4326/video-studio/')
parser.add_argument('--out', default=str(D / 'qa/site'))
args = parser.parse_args()
out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
checks, errors = [], []
def check(name, passed, details=None):
    checks.append(dict(name=name, passed=bool(passed), details=details))
    assert passed, (name, details)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
    for width, height in [(1440, 1000), (390, 844)]:
        page = browser.new_page(viewport=dict(width=width, height=height), reduced_motion='reduce')
        page.on('pageerror', lambda error: errors.append(str(error)))
        response = page.goto(args.base + 'episodes/message-queue/', wait_until='networkidle')
        check(f'{width}: episode responds', response.status == 200)
        video = page.locator('video')
        video.evaluate('(v) => {v.muted=true; v.load()}')
        page.wait_for_function('document.querySelector("video").readyState >= 1')
        duration = video.evaluate('(v) => v.duration')
        check(f'{width}: new final duration', abs(duration - 3700/30) < .1, duration)
        check(f'{width}: MQ collection entry', page.locator('.reading-links a[href="/video-studio/series/message-queue/"]').count() == 1)
        chapters = page.locator('.vp').evaluate('(e) => JSON.parse(e.dataset.chapters)')
        check(f'{width}: four exact chapter starts', [round(c['start']*30) for c in chapters] == [0, 649, 1327, 2607], chapters)
        check(f'{width}: old article anchors remain', all(page.locator('#'+anchor).count() == 1 for anchor in ['enqueue', 'retry', 'recap']))
        check(f'{width}: new source project linked', page.locator('a[href*="mq-intro/message-queue/remotion"]').count() >= 1)
        video.evaluate('(v) => {v.currentTime=0; return v.play()}')
        page.wait_for_function('document.querySelector("video").currentTime > .35')
        video.evaluate('(v) => v.pause()')
        check(f'{width}: actual playback advances', video.evaluate('(v) => v.currentTime') > .35)
        visible_chapters = page.locator('.ch' if width > 767 else '.chip')
        for i, chapter in enumerate(chapters):
            visible_chapters.nth(i).click()
            page.wait_for_function('(t) => Math.abs(document.querySelector("video").currentTime-t)<1', arg=chapter['start'])
            video.evaluate('(v) => v.pause()')
            check(f'{width}: chapter {i+1} seeks', abs(video.evaluate('(v) => v.currentTime') - chapter['start']) < 1)
        figures = page.locator('figure.fig')
        check(f'{width}: four explanatory figures', figures.count() == 4)
        for i in range(4):
            figure = figures.nth(i)
            image = figure.locator('img')
            image.scroll_into_view_if_needed()
            page.wait_for_function('(e) => e.complete && e.naturalWidth>0', arg=image.element_handle())
            check(f'{width}: figure {i+1} loads', image.evaluate('(e) => e.naturalWidth') == 1920)
            original = figure.locator('a.fig-image-link').get_attribute('href')
            check(f'{width}: figure {i+1} original responds', page.request.get(args.base.split('/video-studio/')[0] + original).status == 200)
            seek = figure.locator('a[data-seek-time]')
            t = float(seek.get_attribute('data-seek-time'))
            seek.click()
            page.wait_for_function('(t) => Math.abs(document.querySelector("video").currentTime-t)<1', arg=t)
            video.evaluate('(v) => v.pause()')
            check(f'{width}: figure {i+1} returns to correct video time', abs(video.evaluate('(v) => v.currentTime')-t) < 1)
        triggers = page.locator('.source-trigger')
        check(f'{width}: three original-source popovers', triggers.count() == 3)
        for i in range(3):
            trigger = triggers.nth(i)
            trigger.scroll_into_view_if_needed()
            trigger.click()
            panel = page.locator('.source-panel:popover-open')
            panel.wait_for(state='visible')
            check(f'{width}: source {i+1} opens with original words', len(panel.locator('blockquote').inner_text()) > 20)
            check(f'{width}: source {i+1} has direct source link', panel.locator('cite a').get_attribute('href').startswith('https://www.rabbitmq.com/'))
            box = panel.bounding_box()
            check(f'{width}: source {i+1} stays in viewport', box['x'] >= 0 and box['x']+box['width'] <= width+1)
            page.keyboard.press('Escape')
            check(f'{width}: source {i+1} Escape closes', page.locator('.source-panel:popover-open').count() == 0)
        first = triggers.first
        first.scroll_into_view_if_needed()
        if width > 767:
            first.hover()
            page.locator('.source-panel:popover-open').wait_for(state='visible')
            check(f'{width}: desktop hover preview', True)
            page.mouse.move(1, 1)
            page.wait_for_timeout(500)
        page.keyboard.press('Escape')
        first.focus()
        page.keyboard.press('Enter')
        page.locator('.source-panel:popover-open').wait_for(state='visible')
        check(f'{width}: keyboard opens source', True)
        page.keyboard.press('Escape')
        for theme in ['light', 'dark']:
            page.evaluate('(theme) => document.documentElement.dataset.theme=theme', theme)
            first.click()
            page.locator('.source-panel:popover-open').wait_for(state='visible')
            check(f'{width}: {theme} quote layout no overflow', page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'))
            page.keyboard.press('Escape')
        video.scroll_into_view_if_needed()
        video.evaluate('''(v) => new Promise(resolve => {
          v.pause(); if(v.textTracks[0]) v.textTracks[0].mode='showing';
          v.addEventListener('seeked', resolve, {once:true}); v.currentTime=3550/30+.025;
        })''')
        page.wait_for_function('document.querySelector("video track").readyState === 2')
        page.wait_for_timeout(250)
        check(f'{width}: all native caption cues loaded', video.evaluate('(v) => v.textTracks[0].cues.length') == 24)
        check(f'{width}: native captions absent at first reference frame', video.evaluate('(v) => !v.textTracks[0] || v.textTracks[0].activeCues.length===0'))
        check(f'{width}: paused reference frame decoded', video.evaluate('(v) => v.readyState>=2 && v.paused'))
        page.screenshot(path=str(out / f'reference-paused-{width}.png'))
        video.click(position=dict(x=30, y=30))
        video.evaluate('(v) => {v.pause(); return v.requestFullscreen()}')
        page.wait_for_function('document.fullscreenElement === document.querySelector("video")')
        check(f'{width}: native video fullscreen', True)
        page.screenshot(path=str(out / f'reference-fullscreen-{width}.png'))
        if width == 390:
            page.set_viewport_size(dict(width=844, height=390))
            page.wait_for_timeout(200)
            check('844: landscape fullscreen retains video', page.evaluate('document.fullscreenElement === document.querySelector("video")'))
            page.screenshot(path=str(out / 'reference-fullscreen-landscape-844.png'))
            page.set_viewport_size(dict(width=width, height=height))
        page.evaluate('document.exitFullscreen()')
        check(f'{width}: no horizontal page overflow', page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'))
        page.close()
    browser.close()
check('no browser page errors', not errors, errors)
report = dict(base=args.base, checks=checks, passed=True,
              scope='Real Chromium playback, chapter/image seeking, original-source popovers, narrow/desktop viewports and native fullscreen. Not physical mobile devices or full human listening.',
              scriptSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(out / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'checks':len(checks),'passed':True,'out':str(out)}))
