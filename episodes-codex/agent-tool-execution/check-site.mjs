/** Run only after the canonical media is approved, draft=false and root's build.
 * node episodes-codex/agent-tool-execution/check-site.mjs --base-url http://127.0.0.1:4173/video-studio/
 * Checks actual Chromium playback, native CC cues and eight chapter/heading
 * controls per viewport. Does not build, publish or mutate production inputs.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import crypto from 'node:crypto';

const require = createRequire(import.meta.url);
const {chromium} = require('playwright');
const directory = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(directory, '../..');
const slug = 'agent-tool-execution';
const canonical = path.join(root, 'episodes', slug);
const getArg = (name, fallback) => process.argv.includes(name) ? process.argv[process.argv.indexOf(name) + 1] : fallback;
const baseUrl = getArg('--base-url', 'http://127.0.0.1:4173/video-studio/');
assert.match(baseUrl, /^http:\/\/(?:127\.0\.0\.1|localhost|\[::1\])(?::\d+)?\/video-studio\/$/, 'Use the actual locally built preview server');
const json = (name) => JSON.parse(fs.readFileSync(name, 'utf8'));
const digest = (name) => crypto.createHash('sha256').update(fs.readFileSync(name)).digest('hex');
const meta = json(path.join(canonical, 'meta.json'));
const sb = json(path.join(canonical, 'storyboard.json'));
const freezePath = path.join(directory, 'source-sha256.json');
const freezeBefore = digest(freezePath);
assert.equal(meta.draft, false, 'Canonical media must be approved before browser validation');
assert.equal(meta.finalVideoFrames, 3305);
assert.equal(sb.meta.fps, 30);
assert.equal(sb.meta.finalVideoFrames, 3305);
assert.equal(meta.ep, 28);
assert.equal(meta.series, 'agent');
assert.equal(meta.sourcePath, 'episodes-codex/agent-tool-execution/remotion');
const chapters = sb.scenes.map((scene) => ({id: scene.chapterId, title: scene.title, frame: scene.from, start: scene.from / 30}));
assert.deepEqual(chapters.map((chapter) => chapter.id), ['hook', 'execute', 'deny', 'recap']);
assert.deepEqual(chapters.map((chapter) => chapter.frame), [0, 241, 2031, 2899]);
const expectedCues = sb.scenes.flatMap((scene) => scene.shots.flatMap((shot) => shot.subtitles.map((sub) => ({
  text: sub.text, start: (shot.from + sub.from) / 30, end: (shot.from + sub.to + 1) / 30,
}))));
assert.equal(expectedCues.length, 22);
const output = path.join(directory, 'remotion/out/qa-site');
fs.mkdirSync(output, {recursive: true});
const browser = await chromium.launch({executablePath: '/usr/bin/chromium', headless: true, args: ['--no-sandbox']});
const viewports = [];
try {
  for (const viewport of [{width: 1440, height: 1000}, {width: 390, height: 844}]) {
    const context = await browser.newContext({viewport, colorScheme: 'dark', reducedMotion: 'reduce'});
    const page = await context.newPage();
    const pageErrors = [], failedResponses = [];
    page.on('pageerror', (error) => pageErrors.push(error.message));
    page.on('response', (response) => {if (response.status() >= 400) failedResponses.push({status: response.status(), url: response.url()});});
    await page.goto(new URL(`episodes/${slug}/`, baseUrl).href, {waitUntil: 'domcontentloaded'});
    await page.locator('video').waitFor();
    await page.evaluate(() => {
      const video = document.querySelector('video');
      video.muted = true;
      video.preload = 'auto';
      if (video.textTracks[0]) video.textTracks[0].mode = 'hidden';
    });
    await page.waitForFunction(() => {
      const video = document.querySelector('video');
      return video.readyState >= 2 && video.videoWidth > 0 && video.textTracks[0]?.cues?.length === 22;
    }, {timeout: 20000});
    assert.equal(await page.locator('h1').textContent(), meta.title);
    const media = await page.evaluate(() => {
      const video = document.querySelector('video');
      return {duration: video.duration, width: video.videoWidth, height: video.videoHeight, controls: video.controls,
        source: video.currentSrc, poster: video.poster, trackMode: video.textTracks[0].mode,
        cues: Array.from(video.textTracks[0].cues).map((cue) => ({text: cue.text, start: cue.startTime, end: cue.endTime}))};
    });
    assert.ok(Math.abs(media.duration - 3305 / 30) < 1 / 30);
    assert.equal(media.width, 1920);
    assert.equal(media.height, 1080);
    assert.equal(media.controls, true);
    assert.equal(media.source, new URL(`episodes/${slug}/video.mp4`, baseUrl).href);
    assert.equal(media.poster, new URL(`episodes/${slug}/cover-16x9.jpg`, baseUrl).href);
    media.cues.forEach((cue, index) => {
      assert.equal(cue.text, expectedCues[index].text);
      assert.ok(Math.abs(cue.start - expectedCues[index].start) < 0.001);
      assert.ok(Math.abs(cue.end - expectedCues[index].end) < 0.001);
    });
    await page.evaluate(async () => {
      const video = document.querySelector('video');
      await video.play();
    });
    await page.waitForFunction(() => document.querySelector('video').currentTime >= 0.5);
    const initialPlayback = await page.evaluate(() => {
      const video = document.querySelector('video');
      const record = {currentTime: video.currentTime, pausedBeforeCheck: video.paused, decodedFrames: video.getVideoPlaybackQuality().totalVideoFrames};
      video.pause();
      return record;
    });
    assert.equal(initialPlayback.pausedBeforeCheck, false);
    assert.ok(initialPlayback.decodedFrames > 0);
    await page.evaluate(async () => {
      const image = new Image();
      image.src = document.querySelector('video').poster;
      await image.decode();
      if (!image.naturalWidth || !image.naturalHeight) throw new Error('Poster failed to decode');
    });
    const pageChapters = await page.locator('#player').evaluate((element) => JSON.parse(element.dataset.chapters));
    assert.deepEqual(pageChapters, chapters.map(({id, title, start}) => ({id, title, start})));
    assert.equal(await page.locator(`a[href="https://github.com/linhongcun/video-studio/tree/main/${meta.sourcePath}"]`).count(), 1);
    for (const chapter of chapters) assert.equal(await page.locator(`article h2#${chapter.id}`).count(), 1);
    await page.evaluate(() => {
      window.__siteQaSeeking = [];
      document.querySelector('video').addEventListener('seeking', () => window.__siteQaSeeking.push(document.querySelector('video').currentTime));
    });
    const seekRecords = [];
    for (const kind of ['player-chapter', 'article-heading']) {
      for (const chapter of chapters) {
        await page.evaluate(() => {document.querySelector('video').pause(); window.__siteQaSeeking = [];});
        const selector = kind === 'article-heading' ? `a[data-seek="${chapter.id}"]`
          : `${viewport.width < 768 ? '.chip' : '.ch'}[data-id="${chapter.id}"]`;
        await page.locator(selector).click();
        await page.waitForFunction(() => window.__siteQaSeeking.length > 0 && !document.querySelector('video').seeking);
        const record = await page.evaluate(() => {
          const video = document.querySelector('video');
          const record = {seekingTime: window.__siteQaSeeking[0], settledTime: video.currentTime, hash: location.hash,
            activeChapter: document.querySelector('.ch[aria-current]')?.dataset.id, playbackStarted: !video.paused};
          video.pause();
          return record;
        });
        assert.ok(Math.abs(record.seekingTime - chapter.start) <= 1 / 30 + 0.001, JSON.stringify({kind, chapter, record}));
        assert.equal(record.hash, `#t=${chapter.start}`);
        assert.equal(record.activeChapter, chapter.id);
        assert.equal(record.playbackStarted, true);
        seekRecords.push({kind, id: chapter.id, frame: chapter.frame, expectedSeconds: chapter.start, ...record, errorSeconds: Math.abs(record.seekingTime - chapter.start)});
      }
    }
    await page.locator('[data-open-course]').click();
    assert.equal(await page.locator('#course-directory').getAttribute('open') !== null, true);
    const courseLinks = await page.locator('#course-directory nav a').evaluateAll((links) => links.map((link) => link.getAttribute('href')));
    assert.deepEqual(courseLinks, ['/video-studio/episodes/agent-intro/', '/video-studio/episodes/agent-tool-execution/']);
    const pagerLinks = await page.locator('nav[aria-label="上一课 / 下一课"] a').evaluateAll((links) => links.map((link) => link.getAttribute('href')));
    assert.deepEqual(pagerLinks, ['/video-studio/episodes/agent-intro/']);
    const overflow = await page.evaluate(() => ({scrollWidth: document.documentElement.scrollWidth, viewportWidth: innerWidth}));
    assert.ok(overflow.scrollWidth <= overflow.viewportWidth + 1);
    await page.locator('#player').scrollIntoViewIfNeeded();
    const playerScreenshot = path.join(output, `${viewport.width}-player.png`);
    await page.screenshot({path: playerScreenshot, fullPage: false});
    await page.locator('#article').scrollIntoViewIfNeeded();
    const articleScreenshot = path.join(output, `${viewport.width}-article.png`);
    await page.screenshot({path: articleScreenshot, fullPage: false});
    await page.locator('nav[aria-label="上一课 / 下一课"] a').click();
    await page.waitForURL(new URL('episodes/agent-intro/', baseUrl).href);
    const previousPager = await page.locator('nav[aria-label="上一课 / 下一课"] a').evaluateAll((links) => links.map((link) => link.getAttribute('href')));
    assert.deepEqual(previousPager, ['/video-studio/episodes/agent-tool-execution/']);
    await page.locator('nav[aria-label="上一课 / 下一课"] a').click();
    await page.waitForURL(new URL(`episodes/${slug}/`, baseUrl).href);
    await page.goto(new URL('series/agent/', baseUrl).href, {waitUntil: 'domcontentloaded'});
    const seriesLinks = await page.locator('.lesson-list a.lesson').evaluateAll((links) => links.map((link) => link.getAttribute('href')));
    assert.deepEqual(seriesLinks, ['/video-studio/episodes/agent-intro/', '/video-studio/episodes/agent-tool-execution/']);
    assert.deepEqual(pageErrors, []);
    assert.deepEqual(failedResponses, []);
    viewports.push({viewport, media, initialPlayback, chapters: pageChapters, seeks: seekRecords, courseLinks, pagerLinks,
      previousPager, seriesLinks, courseDirectoryOpened: true, posterDecoded: true, sourceLinkCorrect: true, fourArticleAnchors: true,
      overflow, pageErrors, failedResponses, screenshots: [playerScreenshot, articleScreenshot].map((file) => ({file: path.relative(directory, file), sha256: digest(file)}))});
    await context.close();
  }
} finally {
  await browser.close();
}
assert.equal(digest(freezePath), freezeBefore);
const report = {status: 'passed', checkedAt: new Date().toISOString(), executor: 'Codex a02_site agent', baseUrl,
  slug, version: 'v' + json(path.join(root, 'site/package.json')).version,
  sourceManifestSha256: freezeBefore, sourceManifestUnchanged: true,
  method: 'Actual headless system Chromium at 1440/390: native video playback and decoded frames, 22 loaded text-track cues, four precise player chapter clicks and four article heading play controls per viewport, course directory and A01/A02 navigation, poster decode, screenshots and horizontal overflow.',
  totalSeekControls: viewports.reduce((sum, viewport) => sum + viewport.seeks.length, 0),
  maxSeekErrorSeconds: Math.max(...viewports.flatMap((viewport) => viewport.seeks.map((seek) => seek.errorSeconds))),
  viewports, limits: ['This is local built-page browser verification; publication and complete online asset identity are checked separately.', 'Screenshots require visual review before claiming layout approval. No human listening, word ASR, live model or production order access, platform publishing or measured learning outcomes is claimed.']};
fs.writeFileSync(path.join(directory, 'site-qa.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({status: report.status, viewports: viewports.map((entry) => entry.viewport.width),
  captionsPerViewport: 22, seeks: report.totalSeekControls, maxSeekErrorSeconds: report.maxSeekErrorSeconds,
  report: path.join(directory, 'site-qa.json')}, null, 2));
