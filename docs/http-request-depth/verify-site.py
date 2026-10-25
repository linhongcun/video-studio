"""Verify built EP.01 bytes, frozen text/timing, and actual local Chromium player behavior."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from facts import (ROOT, OUT, DIST, SLUG, CANONICAL, Document, facts, check_identity,
                   check_episode, check_rss, date_version, date_display, request_slugs, sha, utc_now)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--base', default='http://127.0.0.1:4399/video-studio/')
parser.add_argument('--revision-tag', required=True)
parser.add_argument('--preservation-base', required=True)
args = parser.parse_args()
base = args.base.rstrip('/') + '/'
data = facts()
files = check_identity(data, args.preservation_base)
for name in (data['meta']['video'], data['meta']['poster']):
    assert (DIST / 'episodes' / SLUG / name).read_bytes() == (CANONICAL / name).read_bytes()
vtt = (DIST / 'episodes' / SLUG / 'captions.vtt').read_bytes()
page_check = check_episode(Document((DIST / 'episodes' / SLUG / 'index.html').read_text()), vtt, data, args.revision_tag)
expected_directory = [f'/video-studio/episodes/{slug}/' for slug in request_slugs()]
assert expected_directory[0].endswith('/http-request/') and expected_directory[1].endswith('/https/')
series = Document((DIST / 'series/request/index.html').read_text())
assert set(expected_directory) <= set(series.links)
assert '/video-studio/episodes/http-request/' in Document((DIST / 'library/index.html').read_text()).links
rss_check = check_rss((DIST / 'rss.xml').read_bytes(), data)
screens = OUT / 'site-qa'
screens.mkdir(exist_ok=True)
results = []
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                args=['--no-sandbox', '--autoplay-policy=no-user-gesture-required'])
    for width, height in ((1440, 1000), (390, 844)):
        context = browser.new_context(viewport={'width': width, 'height': height})
        page = context.new_page()
        page.set_default_timeout(25000)
        errors, failures = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('response', lambda response: failures.append({'url': response.url, 'status': response.status})
                if response.status >= 400 else None)
        response = page.goto(base + f'episodes/{SLUG}/', wait_until='networkidle')
        assert response.status == 200
        assert page.locator('h1').inner_text() == data['meta']['title']
        date_label = page.locator('.episode-version time')
        assert date_label.inner_text() == date_version(data['meta']['updatedAt'])
        assert date_label.get_attribute('datetime') == data['meta']['updatedAt']
        assert date_display(data['meta']['createdAt']) in page.locator('header.eh .meta').inner_text()
        assert date_display(data['meta']['updatedAt']) in page.locator('header.eh .meta').inner_text()
        directory = page.locator('#course-directory a').evaluate_all('(nodes)=>nodes.map(a=>a.getAttribute("href"))')
        assert directory == expected_directory
        page.wait_for_function('document.querySelector("video").readyState >= 2')
        video = page.locator('video')
        info = video.evaluate('''v=>{v.muted=true;v.textTracks[0].mode='hidden';
            return {duration:v.duration,width:v.videoWidth,height:v.videoHeight,controls:v.controls,poster:v.poster};}''')
        assert abs(info['duration'] - data['frames'] / data['fps']) < .1
        assert info['controls'] and (info['width'], info['height']) == (1920, 1080)
        page.wait_for_function('document.querySelector("track").readyState === 2')
        actual_cues = video.evaluate('v=>Array.from(v.textTracks[0].cues,c=>({text:c.text,start:c.startTime,end:c.endTime}))')
        assert len(actual_cues) == len(data['cues'])
        for a, e in zip(actual_cues, data['cues']):
            assert a['text'] == e['text'] and abs(a['start'] - e['start']) <= .00051 and abs(a['end'] - e['end']) <= .00051
        seeks = []
        selector = '.chip' if width < 768 else '.ch'
        for chapter in data['chapters']:
            page.locator(f'{selector}[data-id="{chapter["id"]}"]').click()
            video.evaluate('v=>v.pause()')
            page.wait_for_function('!document.querySelector("video").seeking')
            t = video.evaluate('v=>v.currentTime')
            assert abs(t - chapter['start']) < .2, (width, chapter['id'], t)
            assert page.locator(f'{selector}[data-id="{chapter["id"]}"]').get_attribute('aria-current') == 'true'
            seeks.append({'id': chapter['id'], 'expectedSeconds': chapter['start'], 'actualSeconds': t})
        # Exercise article chapter links too, using the rendered existing controls.
        article_seeks = []
        for chapter in data['chapters']:
            control = page.locator(f'[data-seek="{chapter["id"]}"]')
            assert control.count() == 1
            control.click()
            video.evaluate('v=>v.pause()')
            page.wait_for_function('!document.querySelector("video").seeking')
            t = video.evaluate('v=>v.currentTime')
            assert abs(t - chapter['start']) < .2
            article_seeks.append({'id': chapter['id'], 'actualSeconds': t})
        video.evaluate('async v=>{v.currentTime=0;await v.play();}')
        page.wait_for_function('document.querySelector("video").currentTime > .15')
        playing = video.evaluate('v=>({time:v.currentTime,paused:v.paused,error:v.error?.code??null})')
        assert not playing['paused'] and playing['error'] is None
        video.evaluate('v=>v.pause()')
        page.wait_for_function('!document.querySelector(".vwrap").classList.contains("stuck")')
        first = data['cues'][0]
        video.evaluate('(v,t)=>{v.currentTime=t;v.textTracks[0].mode="showing";}', (first['start'] + first['end']) / 2)
        page.wait_for_function('!document.querySelector("video").seeking')
        page.wait_for_function('document.querySelector("video").textTracks[0].activeCues.length > 0')
        assert video.evaluate('v=>v.textTracks[0].activeCues[0].text') == first['text']
        video.evaluate('v=>{v.textTracks[0].mode="hidden";}')
        page.evaluate('scrollTo(0,0)')
        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth+1')
        page.screenshot(path=str(screens / f'episode-{width}.png'))
        # Capture an actual decoded handshake state, rather than the poster.
        shot = next(s for scene in data['storyboard']['scenes'] for s in scene['shots'] if s['scriptShot'] == 8)
        target = (shot['from'] + shot['durationInFrames'] - 2) / data['fps']
        video.evaluate('(v,t)=>{v.currentTime=t;}', target)
        page.wait_for_function('!document.querySelector("video").seeking')
        video.screenshot(path=str(screens / f'handshake-decoded-{width}.png'))
        page.locator('#article').scroll_into_view_if_needed()
        page.screenshot(path=str(screens / f'article-{width}.png'))
        overflow = page.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})')
        assert overflow['scrollWidth'] <= overflow['width'] + 1
        video.evaluate('async(v,t)=>{v.currentTime=t;await v.play();}', max(0, info['duration'] - .4))
        page.wait_for_function('document.querySelector("video").ended')
        ended = video.evaluate('v=>({time:v.currentTime,ended:v.ended,error:v.error?.code??null})')
        assert ended['ended'] and ended['error'] is None
        assert not errors and not failures, (errors, failures)
        page.goto(base + 'library/', wait_until='networkidle')
        card = page.locator(f'a.card[href="/video-studio/episodes/{SLUG}/"]')
        assert card.count() == 1
        assert card.locator('time[aria-label="当前版本"]').inner_text() == date_version(data['meta']['updatedAt'])
        assert card.locator('time[aria-label="当前版本"]').get_attribute('datetime') == data['meta']['updatedAt']
        assert date_display(data['meta']['createdAt']) in card.locator('.dates').inner_text()
        assert date_display(data['meta']['updatedAt']) in card.locator('.dates').inner_text()
        assert card.get_attribute('data-date') == data['meta']['publishedAt']
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
        card.scroll_into_view_if_needed()
        card.locator('img').evaluate('img=>img.decode()')
        assert card.locator('img').evaluate('img=>img.complete&&img.naturalWidth>0')
        page.screenshot(path=str(screens / f'library-dates-{width}.png'))
        assert not errors and not failures, (errors, failures)
        results.append({'viewport': {'width': width, 'height': height}, 'player': info,
                        'captionCues': len(actual_cues), 'chapterSeeks': seeks, 'articleSeeks': article_seeks,
                        'playback': playing, 'ended': ended, 'overflow': overflow,
                        'courseDirectory': directory, 'pageErrors': errors, 'failedResponses': failures})
        context.close()
    browser.close()
report = {'status': 'passed', 'checkedAtUTC': utc_now(), 'revisionTag': args.revision_tag,
          'preservationBaseline': args.preservation_base, 'base': base, 'files': files,
          'episode': page_check, 'viewports': results, 'rss': rss_check, 'cardDateVersionMatches': True,
          'scope': 'Fresh built EP01; real Chromium metadata/decoding/playback/end, all frozen native cues, chapter and article seeking, request directory and responsive overflow.',
          'limits': 'Muted browser playback and screenshots do not establish narration listening or measured teaching outcomes.'}
(OUT / 'qa-site.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': 'passed', 'viewports': len(results), 'chapters': len(data['chapters']),
                  'captions': len(data['cues']), 'frames': data['frames']}, ensure_ascii=False))
