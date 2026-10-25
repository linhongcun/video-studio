#!/usr/bin/env python3
"""Check P05's built artifacts and actual Chromium playback at 1440 and 390 px.

Run after the approved final artifacts are synced and npm run build passes.
Serve the current site/dist with Astro preview; this script does not build it.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

from sync_site import PRODUCTION, ROOT, SITE, DIST, SLUG, load_facts, check_local_delivery, puzzle_slugs
from verify_online import Page, check_episode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='http://127.0.0.1:4398/video-studio/')
    args = parser.parse_args()
    base = args.base.rstrip('/') + '/'
    facts = load_facts()
    manifest = check_local_delivery(facts)
    meta, chapters = facts['meta'], facts['chapters']
    frames, fps = facts['frames'], facts['fps']
    duration = frames / fps
    built = DIST / 'episodes' / SLUG
    source = check_episode(Page((built / 'index.html').read_text()), meta, chapters, frames, fps)
    assert SLUG in (DIST / 'rss.xml').read_text()
    expected_links = ['/video-studio/episodes/' + slug + '/' for slug in puzzle_slugs()]
    assert SLUG in puzzle_slugs() and 'monty-hall' in puzzle_slugs()
    output = PRODUCTION / 'out/site-qa'
    output.mkdir(parents=True, exist_ok=True)
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
            directory = page.locator('#course-directory a').evaluate_all('(nodes) => nodes.map(a => a.getAttribute("href"))')
            assert directory == expected_links
            actual_chapters = page.locator('#player').evaluate('(el) => JSON.parse(el.dataset.chapters)')
            assert actual_chapters == [{key: c[key] for key in ('id', 'title', 'start')} for c in chapters]
            assert page.locator('#why-fourteen').count() == 1
            assert page.locator('[data-seek="why-fourteen"], #player [data-id="why-fourteen"]').count() == 0
            assert page.locator('#article a[href$="egg-drop/verify_math.py"]').count() == 1
            assert page.locator('#bounds').count() == 1 and page.locator('[data-seek="bounds"]').count() == 0
            page.wait_for_function('document.querySelector("video").readyState >= 1')
            video = page.locator('video')
            info = video.evaluate('''v => {v.muted=true; v.textTracks[0].mode='hidden';
                return {duration:v.duration,controls:v.controls,width:v.videoWidth,height:v.videoHeight,poster:v.poster};}''')
            assert abs(info['duration'] - duration) < 0.1
            assert info['controls'] and (info['width'], info['height']) == (1920, 1080)
            page.wait_for_function('document.querySelector("track").readyState === 2')
            cues = video.evaluate('v => Array.from(v.textTracks[0].cues,c=>({text:c.text,start:c.startTime,end:c.endTime}))')
            assert len(cues) == len(facts['subtitles'])
            for cue, sub in zip(cues, facts['subtitles']):
                assert cue['text'] == sub['text']
                assert abs(cue['start'] - sub['from'] / fps) <= 0.00051
                assert abs(cue['end'] - sub['to'] / fps) <= 0.00051
            seek_checks = []
            for chapter in chapters:
                selector = '.chip' if width < 768 else '.ch'
                page.locator(f'{selector}[data-id="{chapter["id"]}"]').click()
                video.evaluate('v => v.pause()')
                page.wait_for_function('!document.querySelector("video").seeking')
                current = video.evaluate('v => v.currentTime')
                assert abs(current - chapter['start']) < 0.2, (width, chapter['id'], current)
                seek_checks.append({'id': chapter['id'], 'frame': chapter['frame'], 'expectedSeconds': chapter['start'], 'actualSeconds': current})
            for chapter in chapters:
                page.locator(f'[data-seek="{chapter["id"]}"]').click()
                video.evaluate('v => v.pause()')
                page.wait_for_function('!document.querySelector("video").seeking')
                assert abs(video.evaluate('v => v.currentTime') - chapter['start']) < 0.2
            video.evaluate('async v => {v.currentTime=0; await v.play();}')
            page.wait_for_timeout(400)
            playback = video.evaluate('v => ({time:v.currentTime,paused:v.paused,error:v.error?.code??null})')
            assert playback['time'] > 0.1 and not playback['paused'] and playback['error'] is None
            video.evaluate('v => v.pause()')
            page.wait_for_function('!document.querySelector(".vwrap").classList.contains("stuck")')
            sample = facts['subtitles'][0]
            video.evaluate('(v,t)=>{v.currentTime=t;v.textTracks[0].mode="showing";}', (sample['from'] + sample['to']) / (2 * fps))
            page.wait_for_function('!document.querySelector("video").seeking')
            page.wait_for_function('document.querySelector("video").textTracks[0].activeCues.length > 0')
            assert video.evaluate('v=>v.textTracks[0].activeCues[0].text') == sample['text']
            # Verify the accessible native track above, then return to the
            # default track mode for screenshots of the video's burnt-in text.
            video.evaluate('v=>{v.textTracks[0].mode="hidden";}')
            page.evaluate('scrollTo(0,0)')
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
            first_shot = output / f'episode-{width}.png'
            page.screenshot(path=str(first_shot))
            # Check motion and natural ending from the final shot, then capture
            # the actual last decoded video frame separately from the article.
            ending_from = facts['shots'][-1]['from'] / fps
            video.evaluate('async(v,t)=>{v.currentTime=t;await v.play();}', ending_from)
            page.wait_for_timeout(400)
            ending_playback = video.evaluate('v=>({time:v.currentTime,paused:v.paused,error:v.error?.code??null})')
            assert ending_playback['time'] > ending_from + 0.1 and not ending_playback['paused'] and ending_playback['error'] is None
            video.evaluate('(v,t)=>{v.pause();v.currentTime=t;}', (frames - 1) / fps)
            page.wait_for_function('!document.querySelector("video").seeking')
            last_shot = output / f'ending-last-{width}.png'
            video.screenshot(path=str(last_shot))
            video.evaluate('async(v,t)=>{v.currentTime=t;await v.play();}', max(0, info['duration'] - 0.4))
            page.wait_for_function('document.querySelector("video").ended')
            ended = video.evaluate('v=>({time:v.currentTime,ended:v.ended,error:v.error?.code??null})')
            assert ended['ended'] and ended['error'] is None
            page.wait_for_function('!document.querySelector(".vwrap").classList.contains("stuck")')
            page.locator('#why-fourteen').scroll_into_view_if_needed()
            page.locator('#why-fourteen').evaluate('e=>e.scrollIntoView({block:"start"})')
            proof_shot = output / f'article-proof-{width}.png'
            page.screenshot(path=str(proof_shot))
            budget_table = page.locator('#article>table').filter(has=page.locator('thead th', has_text='首枚次数'))
            assert budget_table.count() == 1
            math = json.loads((PRODUCTION / 'qa-math.json').read_text())
            def interval(pair):
                return str(pair[0]) if pair[0] == pair[1] else f'{pair[0]}…{pair[1]}'
            actual_budgets = budget_table.locator('tbody tr').evaluate_all('(rows)=>rows.map(r=>Array.from(r.cells,c=>c.textContent.trim()))')
            assert actual_budgets == [[str(r['firstEggDropNumber']), str(r['previousKnownSafeFloor']),
                str(r['firstBreakingFloor']), interval(r['candidateFIntervalAfterBreak']),
                str(r['maximumSecondEggDrops']), str(r['totalWorstDropsIfFirstBreakHere'])]
                for r in math['decreasingBreakBudgets']]
            example_table = page.locator('#article>table').filter(has=page.locator('thead th', has_text='此后候选F'))
            actual_example = example_table.locator('tbody tr').evaluate_all('(rows)=>rows.map(r=>Array.from(r.cells,c=>c.textContent.trim()))')
            assert actual_example == [[str(e['drop']), str(e['egg']), str(e['floor']), '碎' if e['broke'] else '不碎',
                str(e['remainingEggs']), interval(e['highestSafeFAfter'])] for e in math['exampleF31']['events']]
            bounds_table = page.locator('#article>table').filter(has=page.locator('thead th', has_text='阈值F'))
            actual_bounds = bounds_table.locator('tbody tr').evaluate_all('(rows)=>rows.map(r=>Array.from(r.cells,c=>c.textContent.trim()))')
            assert actual_bounds == [[str(f), str(math['decreasing']['dropCountByF'][f])] for f in (0,13,31,99,100)]
            budget_table.scroll_into_view_if_needed()
            certificate_shot = output / f'article-budget-table-{width}.png'
            page.screenshot(path=str(certificate_shot))
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
            footnotes = page.locator('.footnotes')
            assert footnotes.count() == 1
            footnote_geometry = footnotes.evaluate('e=>({width:e.getBoundingClientRect().width,scrollWidth:e.scrollWidth,overflowWrap:getComputedStyle(e.querySelector("p")).overflowWrap})')
            assert footnote_geometry['scrollWidth'] <= footnote_geometry['width'] + 1
            assert footnote_geometry['overflowWrap'] == 'anywhere'
            footnote_shot = output / f'footnotes-{width}.png'
            footnotes.screenshot(path=str(footnote_shot))
            page.goto(base, wait_until='networkidle')
            assert page.locator('a.track-puzzles').count() == 1
            assert page.locator('a.track-puzzles').get_attribute('href').endswith('/learn/#puzzles')
            assert page.locator(f'a.card[href="/video-studio/episodes/{SLUG}/"]').count() == 1
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
            page.goto(base + 'series/puzzles/', wait_until='networkidle')
            assert page.locator('.lesson-list a.lesson').evaluate_all('(ns)=>ns.map(a=>a.getAttribute("href"))') == expected_links
            page.goto(base + 'learn/#puzzles', wait_until='networkidle')
            assert page.locator('#puzzles .chapter-lessons a').evaluate_all('(ns)=>ns.map(a=>a.getAttribute("href"))') == expected_links
            page.goto(base + 'library/?track=puzzles', wait_until='networkidle')
            assert page.locator('select[name="track"]').input_value() == 'puzzles'
            visible = page.locator('#library-grid li:not([hidden]) a[data-series]')
            assert sorted(visible.evaluate_all('(ns)=>ns.map(a=>a.getAttribute("href"))')) == sorted(expected_links)
            assert not errors and not failed, (errors, failed)
            results.append({'viewport': [width, height], 'video': info, 'chapters': seek_checks,
                'allArticleChapterSeeksPassed': True, 'captions': len(cues), 'activeCaptionChecked': sample['text'],
                'playback': playback, 'endingPlayback': ending_playback, 'ended': ended,
                'horizontalOverflow': False, 'articleOnlyAppendixReadable': True, 'appendixVideoJump': False,
                'runtimeErrors': errors, 'failedResponses': failed, 'footnotes': footnote_geometry,
                'budgetTableRows': actual_budgets, 'exampleEventRows': actual_example, 'thresholdRows': actual_bounds,
                'screenshots': [str(p.relative_to(ROOT)) for p in (first_shot, last_shot, proof_shot, certificate_shot, footnote_shot)]})
            # Persist real measurements at each completed viewport so a later
            # viewport failure cannot erase an earlier result or invite backfill.
            (PRODUCTION / f'qa-site-viewport-{width}.json').write_text(json.dumps({
                'status': 'passed', 'checkedAtUTC': datetime.now(timezone.utc).isoformat(),
                'base': base, 'viewportResult': results[-1],
                'scope': 'This viewport only; full-run status is recorded separately in qa-site.json.'
            }, ensure_ascii=False, indent=2) + '\n')
            context.close()
        browser.close()
    report = {'status': 'passed', 'checkedAtUTC': datetime.now(timezone.utc).isoformat(),
              'base': base, 'candidateVersion': json.loads((ROOT / 'site/package.json').read_text())['version'],
              'builtHtmlPageCount': len(list(DIST.rglob('*.html'))), 'frames': frames, 'fps': fps,
              'subtitleCount': len(facts['subtitles']), 'shotCount': len(facts['shots']), 'chapters': chapters,
              'sourceUrl': source, 'puzzleDirectory': puzzle_slugs(),
              'deliveryFileCount': len(manifest['filesSHA256']), 'mediaSHA256': {n: manifest['filesSHA256'][n] for n in (meta['video'],meta['poster'])},
              'viewports': results,
              'scope': 'Actual Chromium UI and built delivery. Not a full audiovisual review or a measured learning-outcome experiment.'}
    (PRODUCTION / 'qa-site.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    (SITE / 'qa-site.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    (PRODUCTION / 'qa-site.md').write_text(f"P05 local site QA passed at 1440×1000 and 390×844.\n\n{frames} frames / {fps} fps; {len(facts['subtitles'])} captions; {len(chapters)} chapters. All chapter and article seeks, complete caption text/timing, start and ending playback, final frame, normal end, article-only lower bound and threshold checks, and puzzles navigation checked in Chromium. Screenshot paths and exact hashes are in qa-site.json.\n\nScope: delivery and browser behavior only; no claim of full human audiovisual review or measured understanding.\n")
    print(json.dumps({'status': 'passed', 'viewports': [[1440,1000],[390,844]], 'frames': frames,
                      'captions': len(facts['subtitles']), 'chapters': len(chapters), 'pages': report['builtHtmlPageCount']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
