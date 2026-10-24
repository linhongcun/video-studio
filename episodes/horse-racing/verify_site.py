#!/usr/bin/env python3
"""Verify the built horse-racing page and its real browser controls.

Run after frozen assets have been copied and `npm run build` has passed.
Start Astro preview on port 4331, then run this file. This checks delivery and
navigation; it does not claim that a first-time viewer understands the lesson.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='http://127.0.0.1:4331/video-studio/')
    parser.add_argument('--tail-only', action='store_true',
                        help='Check the replaced ending and unchanged prefix; keep the original full-site QA report.')
    args = parser.parse_args()
    base = args.base.rstrip('/') + '/'
    episode = Path(__file__).resolve().parent
    repo = episode.parents[1]
    dist = repo / 'site/dist'
    out = episode / ('out/site-qa-ending' if args.tail_only else 'out/site-qa')
    out.mkdir(parents=True, exist_ok=True)
    meta = json.loads((episode / 'meta.json').read_text())
    storyboard = json.loads((episode / 'storyboard.json').read_text())
    assert meta['draft'] is False, 'Final site checks require the published candidate'
    fps = storyboard['meta']['fps']
    expected_chapters = []
    expected_subtitles = []
    current_shots = []
    frame = 0
    for scene in storyboard['scenes']:
        chapter_id = scene.get('chapterId', scene['id'])
        if not expected_chapters or expected_chapters[-1]['id'] != chapter_id:
            expected_chapters.append({'id': chapter_id, 'frame': frame, 'start': frame / fps})
        for shot in scene['shots']:
            current_shots.append({'shot': shot, 'from': frame})
            expected_subtitles.extend(sub['text'] for sub in shot['subtitles'])
            frame += shot['durationInFrames']
    assert frame == meta['finalVideoFrames']
    prefix = None
    tail_from = 0
    if args.tail_only:
        baseline = repo / 'episodes-codex/horse-racing/revisions/self-contained-ending/before/storyboard.json'
        old_storyboard = json.loads(baseline.read_text())
        old_shots, old_from = [], 0
        for scene in old_storyboard['scenes']:
            for shot in scene['shots']:
                old_shots.append({'shot': shot, 'from': old_from})
                old_from += shot['durationInFrames']
        old_prefix = [entry for entry in old_shots if int(entry['shot']['id']) <= 17]
        new_prefix = [entry for entry in current_shots if int(entry['shot']['id']) <= 17]
        def prefix_facts(entry):
            shot = entry['shot']
            return {'id': shot['id'], 'from': entry['from'],
                    'durationInFrames': shot['durationInFrames'], 'chapterId': shot['chapterId'],
                    'narration': shot['narration'], 'subtitles': shot['subtitles']}
        assert [prefix_facts(entry) for entry in new_prefix] == [prefix_facts(entry) for entry in old_prefix]
        assert len(old_prefix) == 17
        tail_from = sum(entry['shot']['durationInFrames'] for entry in old_prefix)
        tail_chapters = [chapter for chapter in expected_chapters if chapter['frame'] >= tail_from]
        assert tail_chapters and tail_chapters[0]['id'] == 'lower-bound'
        assert tail_chapters[0]['frame'] == tail_from
        prefix = {'shotCount': len(old_prefix), 'frames': tail_from,
                  'subtitleCount': sum(len(entry['shot']['subtitles']) for entry in old_prefix),
                  'timingAndTextUnchanged': True}
    built_episode = dist / 'episodes/horse-racing'
    vtt = (built_episode / 'captions.vtt').read_text()
    cue_texts = [block.split('\n', 1)[1] for block in vtt.strip().split('\n\n')[1:]]
    assert cue_texts == expected_subtitles
    hashes = {}
    for filename in (meta['video'], meta['poster']):
        original = digest(episode / filename)
        built = digest(built_episode / filename)
        assert original == built, f'Built {filename} differs from frozen delivery'
        hashes[filename] = original
    html = (built_episode / 'index.html').read_text()
    for chapter in expected_chapters:
        assert f'id="{chapter["id"]}"' in html, f'Missing article anchor: {chapter}'
    assert 'horse-racing' in (dist / 'rss.xml').read_text()
    assert '趣味推理' in (dist / 'series/puzzles/index.html').read_text()
    assert 'series/puzzles' in (dist / 'learn/index.html').read_text()
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path='/usr/bin/chromium', headless=True,
            args=['--no-sandbox', '--autoplay-policy=no-user-gesture-required'],
        )
        for width, height in ((1440, 1000), (390, 844)):
            context = browser.new_context(viewport={'width': width, 'height': height})
            page = context.new_page()
            page.set_default_timeout(20000)
            errors, bad_responses = [], []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('response', lambda response: bad_responses.append(
                {'url': response.url, 'status': response.status}) if response.status >= 400 else None)
            response = page.goto(base + 'episodes/horse-racing/', wait_until='networkidle')
            assert response.status == 200
            assert page.locator('h1').inner_text() == meta['title']
            assert page.locator('#course-directory li').count() == 1
            assert page.locator('#course-directory a').get_attribute('href').endswith('/episodes/horse-racing/')
            for chapter in expected_chapters:
                assert page.locator('#' + chapter['id']).count() == 1
            actual_chapters = page.locator('#player').evaluate('(el) => JSON.parse(el.dataset.chapters)')
            assert [chapter['id'] for chapter in actual_chapters] == [chapter['id'] for chapter in expected_chapters]
            assert [chapter['start'] for chapter in actual_chapters] == [chapter['start'] for chapter in expected_chapters]
            page.wait_for_function('document.querySelector("video").readyState >= 1')
            video_info = page.locator('video').evaluate('''video => {
                video.muted = true;
                video.textTracks[0].mode = 'hidden';
                return {duration: video.duration, controls: video.controls,
                    poster: video.poster, width: video.videoWidth, height: video.videoHeight};
            }''')
            assert abs(video_info['duration'] - frame / fps) < 0.1
            assert video_info['controls'] and video_info['width'] == 1920 and video_info['height'] == 1080
            page.wait_for_function('document.querySelector("track").readyState === 2')
            assert page.locator('video').evaluate('v => v.textTracks[0].cues.length') == len(expected_subtitles)
            seek_checks = []
            chapters_to_seek = tail_chapters if args.tail_only else expected_chapters
            for chapter in chapters_to_seek:
                selector = '.chip' if width < 768 else '.ch'
                page.locator(f'{selector}[data-id="{chapter["id"]}"]').click()
                page.locator('video').evaluate('video => video.pause()')
                page.wait_for_function('!document.querySelector("video").seeking')
                actual = page.locator('video').evaluate('video => video.currentTime')
                assert abs(actual - chapter['start']) < 0.2, (width, chapter, actual)
                seek_checks.append({'id': chapter['id'], 'expected': chapter['start'], 'actual': actual})
            # The article's native chapter action is a separate entry point.
            button = page.locator('[data-seek]').last
            target_id = button.get_attribute('data-seek')
            button.click()
            page.locator('video').evaluate('video => video.pause()')
            page.wait_for_function('!document.querySelector("video").seeking')
            article_seek = page.locator('video').evaluate('video => video.currentTime')
            target_start = next(chapter['start'] for chapter in expected_chapters if chapter['id'] == target_id)
            assert abs(article_seek - target_start) < 0.2
            playback_from = tail_from / fps if args.tail_only else 0
            page.locator('video').evaluate('async (video, start) => {video.currentTime = start; await video.play();}', playback_from)
            page.wait_for_timeout(350)
            playback = page.locator('video').evaluate('video => ({time: video.currentTime, paused: video.paused, error: video.error?.code ?? null})')
            assert playback['time'] > playback_from + 0.1 and not playback['paused'] and playback['error'] is None
            page.locator('video').evaluate('video => video.pause()')
            # The existing mobile player releases its sticky state three seconds
            # after pause. Capture the normal page only after that transition.
            page.wait_for_function('!document.querySelector(".vwrap").classList.contains("stuck")')
            if args.tail_only:
                page.locator('video').evaluate('(video, time) => {video.currentTime = time;}', min(playback_from + 3, frame / fps - 1))
                page.wait_for_function('!document.querySelector("video").seeking')
            overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
            assert not overflow, f'Horizontal overflow at {width}'
            page.evaluate('scrollTo(0,0)')
            screenshot = out / f'episode-{width}.png'
            page.screenshot(path=str(screenshot), full_page=False)
            home_overflow = None
            if not args.tail_only:
                page.goto(base, wait_until='networkidle')
                assert page.locator('a.track-puzzles').count() == 1
                assert page.locator('a.track-puzzles').get_attribute('href').endswith('/learn/#puzzles')
                home_overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
                assert not home_overflow
                page.screenshot(path=str(out / f'home-{width}.png'), full_page=False)
                page.goto(base + 'learn/#puzzles', wait_until='networkidle')
                assert page.locator('#puzzles .chapter-lessons a').count() == 1
                assert page.locator('#puzzles .chapter-lessons a').get_attribute('href').endswith('/episodes/horse-racing/')
                page.goto(base + 'library/?track=puzzles', wait_until='networkidle')
                assert page.locator('select[name="track"]').input_value() == 'puzzles'
                visible = page.locator('#library-grid li:not([hidden]) a[data-series]')
                assert visible.count() == 1
                assert visible.get_attribute('href').endswith('/episodes/horse-racing/')
            assert not errors, errors
            assert not bad_responses, bad_responses
            results.append({'viewport': [width, height], 'video': video_info,
                            'seekChecks': seek_checks, 'articleSeek': {'id': target_id, 'time': article_seek},
                            'playback': playback, 'playbackFrom': playback_from,
                            'captionCount': len(expected_subtitles),
                            'chapterCount': len(expected_chapters), 'horizontalOverflow': overflow,
                            'homeHorizontalOverflow': home_overflow, 'runtimeErrors': errors,
                            'failedResponses': bad_responses, 'screenshot': str(screenshot.relative_to(repo))})
            context.close()
        browser.close()
    report = {'checkedAtUtc': datetime.now(timezone.utc).isoformat(), 'base': base,
              'scope': 'Changed ending and unchanged prefix with actual Chromium controls; original full-site navigation QA retained separately.' if args.tail_only else 'Built files and actual Chromium UI, not a learning-outcome experiment or full audiovisual review.',
              'mediaSHA256': hashes, 'frames': frame, 'fps': fps,
              'subtitleCount': len(expected_subtitles), 'chapters': expected_chapters,
              'unchangedPrefix': prefix, 'tailOnly': args.tail_only,
              'viewports': results, 'status': 'passed'}
    report_path = episode / ('qa-site-ending.json' if args.tail_only else 'qa-site.json')
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': 'passed', 'viewports': [r['viewport'] for r in results],
                      'frames': frame, 'captions': len(expected_subtitles), 'chapters': len(expected_chapters)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
