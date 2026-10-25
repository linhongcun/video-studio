#!/usr/bin/env python3
"""Run only after formal delivery and a complete Astro/Pagefind build.

Checks built byte copies and real Chromium playback/navigation at two widths.
It does not build, freeze, copy, render or publish anything.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

from sync_site import PRODUCTION, ROOT, SITE, DIST, SLUG, RETIRED_SLUGS, load_facts, check_local_delivery, agent_slugs, sha_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='http://127.0.0.1:4331/video-studio/')
    args = parser.parse_args()
    base = args.base.rstrip('/') + '/'
    facts = load_facts()
    meta, manifest = check_local_delivery(facts)
    assert meta['firstRelease'] == 'v' + json.loads((ROOT / 'site/package.json').read_text())['version']
    frames, fps, chapters = facts['frames'], facts['fps'], facts['chapters']
    expected_links = ['/video-studio/episodes/' + slug + '/' for slug in agent_slugs()]
    assert agent_slugs()[0] == SLUG
    for slug in RETIRED_SLUGS:
        assert not (DIST / 'episodes' / slug).exists()
    assert '/episodes/' + SLUG + '/' in (DIST / 'rss.xml').read_text()
    output = PRODUCTION / 'out/site-qa'
    output.mkdir(parents=True, exist_ok=True)
    expected_source = 'https://github.com/linhongcun/video-studio/tree/main/episodes-codex/agent-skills/remotion'
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                    args=['--no-sandbox', '--autoplay-policy=no-user-gesture-required'])
        for width, height in ((1440, 1000), (390, 844)):
            context = browser.new_context(viewport={'width': width, 'height': height})
            page = context.new_page()
            page.set_default_timeout(20000)
            errors, failed = [], []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('response', lambda response: failed.append({'url': response.url, 'status': response.status})
                    if response.status >= 400 else None)
            response = page.goto(base + 'episodes/' + SLUG + '/', wait_until='networkidle')
            assert response.status == 200
            assert page.locator('h1').inner_text() == meta['title']
            assert page.locator(f'a[href="{expected_source}"]').count() > 0
            assert page.locator('.pl').count() == 0
            assert page.locator('#course-directory a').evaluate_all('(ns)=>ns.map(a=>a.getAttribute("href"))') == expected_links
            actual = page.locator('#player').evaluate('(e)=>JSON.parse(e.dataset.chapters)')
            assert actual == [{key: c[key] for key in ('id', 'title', 'start')} for c in chapters]
            page.wait_for_function('document.querySelector("video").readyState >= 1')
            video = page.locator('video')
            info = video.evaluate('''v=>{v.muted=true;v.textTracks[0].mode='hidden';
                return {duration:v.duration,controls:v.controls,width:v.videoWidth,height:v.videoHeight};}''')
            assert abs(info['duration'] - frames / fps) < 0.1
            assert info['controls'] and (info['width'], info['height']) == (1920, 1080)
            page.wait_for_function('document.querySelector("track").readyState === 2')
            cues = video.evaluate('v=>Array.from(v.textTracks[0].cues,c=>({text:c.text,start:c.startTime,end:c.endTime}))')
            assert len(cues) == len(facts['subtitles'])
            for cue, sub in zip(cues, facts['subtitles']):
                assert cue['text'] == sub['text']
                assert abs(cue['start'] - sub['from'] / fps) <= 0.00051
                assert abs(cue['end'] - sub['to'] / fps) <= 0.00051
            seek_checks = []
            for chapter in chapters:
                assert page.locator('#article #' + chapter['id']).count() == 1
                for selector in (f'{".chip" if width < 768 else ".ch"}[data-id="{chapter["id"]}"]',
                                 f'[data-seek="{chapter["id"]}"]'):
                    page.locator(selector).click()
                    video.evaluate('v=>v.pause()')
                    page.wait_for_function('!document.querySelector("video").seeking')
                    current = video.evaluate('v=>v.currentTime')
                    assert abs(current - chapter['start']) < 0.2, (width, selector, current)
                    seek_checks.append({'id': chapter['id'], 'control': selector, 'frame': chapter['frame'],
                                        'expected': chapter['start'], 'actual': current})
            video.evaluate('async v=>{v.currentTime=0;await v.play();}')
            page.wait_for_timeout(500)
            playback = video.evaluate('v=>({time:v.currentTime,paused:v.paused,error:v.error?.code??null})')
            assert playback['time'] > 0.1 and not playback['paused'] and playback['error'] is None
            video.evaluate('v=>v.pause()')
            sample = facts['subtitles'][0]
            video.evaluate('(v,t)=>{v.currentTime=t;v.textTracks[0].mode="showing";}', (sample['from'] + sample['to']) / (2 * fps))
            page.wait_for_function('!document.querySelector("video").seeking && document.querySelector("video").textTracks[0].activeCues.length > 0')
            assert video.evaluate('v=>v.textTracks[0].activeCues[0].text') == sample['text']
            video.evaluate('v=>{v.textTracks[0].mode="hidden";}')
            page.wait_for_function('!document.querySelector(".vwrap").classList.contains("stuck")')
            page.evaluate('scrollTo(0,0)')
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
            screenshots = [output / f'episode-{width}.png']
            page.screenshot(path=str(screenshots[-1]))
            video.evaluate('async(v,t)=>{v.currentTime=t;await v.play();}', max(0, info['duration'] - 0.4))
            page.wait_for_function('document.querySelector("video").ended')
            ended = video.evaluate('v=>({time:v.currentTime,ended:v.ended,error:v.error?.code??null})')
            assert ended['ended'] and ended['error'] is None
            for chapter in chapters:
                heading = page.locator('#article #' + chapter['id'])
                heading.scroll_into_view_if_needed()
                heading.evaluate('e=>e.scrollIntoView({block:"start"})')
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                screenshots.append(output / f'article-{chapter["id"]}-{width}.png')
                page.screenshot(path=str(screenshots[-1]))
            if width == 1440:
                for name in (meta['video'], meta['poster'], 'captions.vtt'):
                    asset = context.request.get(base + 'episodes/' + SLUG + '/' + name)
                    assert asset.status == 200
                    expected = sha_file(DIST / 'episodes' / SLUG / name)
                    assert hashlib.sha256(asset.body()).hexdigest() == expected
            page.goto(base, wait_until='networkidle')
            assert page.locator('a.track-agent').count() == 1
            assert page.locator(f'a.card[href="/video-studio/episodes/{SLUG}/"]').count() == 1
            page.goto(base + 'series/agent/', wait_until='networkidle')
            assert page.locator('.lesson-list a.lesson').evaluate_all('(ns)=>ns.map(a=>a.getAttribute("href"))') == expected_links
            page.goto(base + 'learn/#agent', wait_until='networkidle')
            assert page.locator('#agent .chapter-lessons a').evaluate_all('(ns)=>ns.map(a=>a.getAttribute("href"))') == expected_links
            page.goto(base + 'library/?track=agent', wait_until='networkidle')
            assert page.locator('select[name="track"]').input_value() == 'agent'
            assert page.locator('#library-grid li:not([hidden]) a[data-series]').evaluate_all('(ns)=>ns.map(a=>a.getAttribute("href"))') == expected_links
            page.goto(base + 'search/?q=Agent%20Skills', wait_until='networkidle')
            page.locator(f'.pagefind-ui__result-link[href$="/episodes/{SLUG}/"]').wait_for()
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
            screenshots.append(output / f'search-{width}.png')
            page.screenshot(path=str(screenshots[-1]))
            assert not errors and not failed, (errors, failed)
            results.append({'viewport': [width, height], 'video': info, 'chapterSeeks': seek_checks,
                'captionCount': len(cues), 'allCaptionTextsAndTimingsExact': True,
                'activeCaption': sample['text'], 'playback': playback, 'naturalEnd': ended,
                'agentNavigationAndSearch': True, 'horizontalOverflow': False,
                'runtimeErrors': errors, 'failedResponses': failed,
                'screenshots': [str(p.relative_to(ROOT)) for p in screenshots]})
            context.close()
        browser.close()
    report = {'status': 'passed', 'checkedAtUTC': datetime.now(timezone.utc).isoformat(), 'base': base,
              'candidateVersion': meta['firstRelease'], 'frames': frames, 'fps': fps,
              'chapters': chapters, 'sourceUrl': expected_source, 'agentDirectory': agent_slugs(),
              'deliveryFileCount': len(manifest['filesSHA256']),
              'mediaSHA256': {n: manifest['filesSHA256'][n] for n in (meta['video'], meta['poster'])},
              'viewports': results,
              'scope': 'Built byte copies and actual Chromium UI/playback. Not full narration listening or a measured learning-outcome experiment.'}
    (PRODUCTION / 'qa-site.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    (PRODUCTION / 'qa-site.md').write_text(f"Skills local site QA passed at 1440×1000 and 390×844.\n\n{frames} frames / {fps} fps; {len(facts['subtitles'])} exact captions; four timed chapters. Player and article seeks, playback and natural ending, source entry, Agent learning/series/library navigation, search, mobile overflow and full media hashes checked. Evidence paths and limitations: qa-site.json.\n")
    print(json.dumps({'status': 'passed', 'frames': frames, 'captions': len(facts['subtitles']), 'chapters': len(chapters)}))


if __name__ == '__main__':
    main()
