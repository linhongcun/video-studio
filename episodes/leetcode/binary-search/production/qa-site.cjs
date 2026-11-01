// Local delivery QA. Run from the repo root after the approved media is copied:
//   node episodes-codex/binary-search/qa-site.cjs
// Builds the actual site, runs the existing learning-path regression once, and
// opens the new page at desktop/mobile sizes. This is not narration listening.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const crypto = require('node:crypto');
const {chromium} = require('playwright');

const production = __dirname;
const root = path.resolve(production, '../..');
const canonical = path.join(root, 'episodes/binary-search');
const dist = path.join(root, 'site/dist');
const output = path.join(production, 'remotion/out/site-qa');
const base = process.env.QA_SITE_BASE || 'http://127.0.0.1:4186/video-studio/';
const meta = JSON.parse(fs.readFileSync(path.join(canonical, 'meta.json'), 'utf8'));
const siteVersion = JSON.parse(fs.readFileSync(path.join(root, 'site/package.json'), 'utf8')).version;
assert.equal(meta.firstRelease, `v${siteVersion}`, 'This new episode must debut in the site version being built');
const previousReportCommit = '5a41a16ebaadb8339e4bc592edf325a407e74295';
const storyboard = JSON.parse(fs.readFileSync(path.join(canonical, 'storyboard.json'), 'utf8'));
const fps = storyboard.meta.fps;
const frames = storyboard.meta.finalVideoFrames;
const card = storyboard.meta.unvoicedEndCard;
assert.equal(meta.draft, false, 'Only approved final media should enter the delivery QA');
assert.equal(meta.finalVideoFrames, frames);
assert.equal(card.durationInFrames, 150);
assert.equal(card.from + card.durationInFrames, frames);
const sha = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');
const videoSha = sha(fs.readFileSync(path.join(canonical, meta.video)));
const posterSha = sha(fs.readFileSync(path.join(canonical, meta.poster)));
const expectedIds = ['problem', 'halve', 'missing', 'code'];
const expectedStarts = storyboard.scenes.map((scene) => scene.from / fps);
const narration = storyboard.scenes.flatMap((s) => s.shots.flatMap((sh) => sh.subtitles.map((sub) => sub.text)));
const displayDuration = `${Math.floor(frames / fps / 60)}:${String(Math.floor(frames / fps % 60)).padStart(2, '0')}`;
const parseTime = (stamp) => stamp.split(':').reduce((total, n) => total * 60 + Number(n), 0);
const browserChecks = [];
const screenshots = [];
const expectedSource = `https://github.com/linhongcun/video-studio/tree/main/${meta.sourcePath}`;

function countFiles(dir, predicate) {
  return fs.readdirSync(dir, {withFileTypes: true}).reduce((n, entry) => n + (entry.isDirectory()
    ? countFiles(path.join(dir, entry.name), predicate) : Number(predicate(entry.name))), 0);
}
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

(async () => {
  fs.mkdirSync(output, {recursive: true});
  const reuseBuild = process.argv.includes('--reuse-build');
  if (reuseBuild) {
    assert.ok(fs.existsSync(path.join(output, 'build.log')) && fs.existsSync(path.join(output, 'learning-path.log')), 'Reuse requires the real successful build/regression logs');
    assert.equal(videoSha, sha(fs.readFileSync(path.join(dist, 'episodes/binary-search/video.mp4'))));
    assert.equal(posterSha, sha(fs.readFileSync(path.join(dist, 'episodes/binary-search/cover-16x9.jpg'))));
  } else {
    const buildLog = cp.execFileSync('npm', ['run', 'build'], {cwd: path.join(root, 'site'), encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe']});
    fs.writeFileSync(path.join(output, 'build.log'), buildLog);
    const regressionLog = cp.execFileSync('node', ['site/scripts/check-learning-path.mjs', '--complete', '--built'], {cwd: root, encoding: 'utf8'});
    fs.writeFileSync(path.join(output, 'learning-path.log'), regressionLog);
  }
  const preview = process.env.QA_SITE_BASE ? null : cp.spawn(process.execPath, [path.join(root, 'site/node_modules/astro/astro.js'), 'preview', '--host', '127.0.0.1', '--port', '4186'], {cwd: path.join(root, 'site'), stdio: 'ignore'});
  let browser;
  let siteEntries;
  try {
    for (let i = 0; i < 100; i++) {
      try {if ((await fetch(base)).ok) break;} catch {}
      assert.ok(i < 99, 'Local preview failed to start');
      await sleep(200);
    }
    browser = await chromium.launch({executablePath: '/usr/bin/chromium', args: ['--no-sandbox']});
    for (const [width, theme] of [[1440, 'light'], [390, 'dark']]) {
      const context = await browser.newContext({viewport: {width, height: 900}, colorScheme: theme});
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', (error) => errors.push(error.message));
      const response = await page.goto(new URL('episodes/binary-search/', base).href, {waitUntil: 'networkidle'});
      assert.equal(response.status(), 200);
      await page.evaluate(() => document.fonts.ready);
      assert.equal(await page.locator('h1').innerText(), meta.title);
      assert.ok((await page.locator('footer').innerText()).includes(`v${siteVersion}`), 'Rendered footer must use the new release version');
      assert.ok((await page.locator('.eh .meta').innerText()).includes(displayDuration));
      assert.ok(await page.getByText('LC.704', {exact: false}).count() > 0);
      assert.equal(await page.locator('.pl').count(), 0);
      assert.ok(await page.locator(`a[href="${expectedSource}"]`).count() > 0);
      const articleCode = await page.locator('article pre').allTextContents();
      assert.ok(articleCode.some((text) => text.trim() === fs.readFileSync(path.join(production, 'solution.py'), 'utf8').trim()), 'Article must show the same complete solution');
      assert.equal(await page.locator('.pager a').count(), 1);
      assert.equal(await page.locator('.pager a').getAttribute('href'), '/video-studio/episodes/longest-substring/');
      assert.ok((await page.locator('.pager').innerText()).includes('无重复字符的最长子串'));

      const video = page.locator('video');
      await page.waitForFunction(() => document.querySelector('video').readyState >= 1);
      const media = await video.evaluate((v) => ({duration: v.duration, controls: v.controls, width: v.videoWidth, height: v.videoHeight}));
      assert.equal(media.controls, true);
      assert.ok(Math.abs(media.duration - frames / fps) < 0.1);
      assert.deepEqual([media.width, media.height], [1920, 1080]);
      const chapters = await page.locator('#player').evaluate((el) => JSON.parse(el.dataset.chapters));
      assert.deepEqual(chapters.map((c) => c.id), expectedIds);
      assert.deepEqual(chapters.map((c) => c.start), expectedStarts);
      const seeks = [];
      for (const chapter of chapters) {
        assert.ok(await page.locator(`article #${chapter.id}`).count() > 0);
        const selector = `#player ${width < 768 ? '.chip' : '.ch'}[data-id="${chapter.id}"]`;
        await page.locator(selector).click();
        await video.evaluate((v) => v.pause());
        await page.waitForFunction((expected) => {const v = document.querySelector('video'); return !v.seeking && Math.abs(v.currentTime - expected) < 0.7;}, chapter.start);
        assert.equal(await page.locator(selector).getAttribute('aria-current'), 'true');
        seeks.push({id: chapter.id, expected: chapter.start, actual: await video.evaluate((v) => v.currentTime)});
      }

      const vttResponse = await context.request.get(new URL('episodes/binary-search/captions.vtt', base).href);
      assert.equal(vttResponse.status(), 200);
      const vtt = await vttResponse.body();
      const cues = vtt.toString('utf8').trim().split(/\r?\n\s*\r?\n/).slice(1).map((block) => {
        const lines = block.split(/\r?\n/);
        const match = /^(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)$/.exec(lines[0]);
        assert.ok(match);
        return {start: parseTime(match[1]), end: parseTime(match[2]), text: lines.slice(1).join('\n')};
      });
      assert.equal(cues.length, 28);
      assert.deepEqual(cues.map((c) => c.text), narration);
      const finalCueEnd = Math.max(...cues.map((c) => c.end));
      assert.ok(Math.abs(finalCueEnd - card.from / fps) < 0.001);
      assert.equal(sha(vtt), sha(fs.readFileSync(path.join(dist, 'episodes/binary-search/captions.vtt'))));
      if (width === 1440) {
        for (const [name, expected] of [[meta.video, videoSha], [meta.poster, posterSha]]) {
          const asset = await context.request.get(new URL(`episodes/binary-search/${name}`, base).href);
          assert.equal(asset.status(), 200);
          assert.equal(sha(await asset.body()), expected);
        }
      }

      const narratedTime = (cues[0].start + cues[0].end) / 2;
      await video.evaluate((v, t) => {v.textTracks[0].mode = 'showing'; v.muted = true; v.currentTime = t;}, narratedTime);
      await page.waitForFunction(() => {const v = document.querySelector('video'); return document.querySelector('track').readyState === 2 && v.textTracks[0].cues?.length === 28 && v.textTracks[0].activeCues?.length > 0 && !v.seeking;});
      const narratedCC = await video.evaluate((v) => ({currentTime: v.currentTime, mode: v.textTracks[0].mode, loadedCues: v.textTracks[0].cues.length, activeCues: v.textTracks[0].activeCues.length}));
      const cardTime = card.from / fps + 1;
      await video.evaluate((v, t) => {v.pause(); v.currentTime = t;}, cardTime);
      await page.waitForFunction(() => {const v = document.querySelector('video'); return !v.seeking && v.readyState >= 2 && v.textTracks[0].activeCues.length === 0;});
      const cardCC = await video.evaluate((v) => ({currentTime: v.currentTime, mode: v.textTracks[0].mode, activeCues: v.textTracks[0].activeCues.length, paused: v.paused}));
      await video.evaluate((v) => v.play());
      await page.waitForFunction((t) => {const v = document.querySelector('video'); return !v.paused && v.currentTime >= t + 1 && v.readyState >= 2;}, cardTime);
      const playing = await video.evaluate((v) => ({currentTime: v.currentTime, paused: v.paused, muted: v.muted, readyState: v.readyState, activeCues: v.textTracks[0].activeCues.length, error: v.error?.message ?? null}));
      await video.evaluate((v) => v.pause());
      const paused = await video.evaluate((v) => ({currentTime: v.currentTime, paused: v.paused, readyState: v.readyState, activeCues: v.textTracks[0].activeCues.length, seeking: v.seeking}));
      assert.equal(paused.paused, true); assert.equal(paused.activeCues, 0); assert.equal(paused.seeking, false); assert.equal(playing.error, null);
      const raw = await video.evaluate((v) => {const canvas = document.createElement('canvas'); canvas.width = v.videoWidth; canvas.height = v.videoHeight; canvas.getContext('2d').drawImage(v, 0, 0); return canvas.toDataURL('image/png').split(',')[1];});
      const rawPath = path.join(output, `complete-python-frame-${width}.png`); fs.writeFileSync(rawPath, Buffer.from(raw, 'base64')); screenshots.push(rawPath);

      const overflow = await page.evaluate(() => ({scrollWidth: document.documentElement.scrollWidth,
        count: [...document.body.querySelectorAll('*')].filter((el) => {const b = el.getBoundingClientRect(); return b.width && b.height && getComputedStyle(el).visibility !== 'hidden' && !el.closest('.sr-only,.chips') && !(el.closest('pre') && el.tagName !== 'PRE') && !(el.closest('table') && el.tagName !== 'TABLE') && (b.left < -1 || b.right > innerWidth + 1);}).length}));
      assert.equal(overflow.count, 0); assert.equal(overflow.scrollWidth, width); assert.deepEqual(errors, []);
      await page.mouse.move(10, 10); await page.evaluate(() => scrollTo({top: 0, left: 0, behavior: 'instant'}));
      const screenshot = path.join(output, `lc704-player-${width}-${theme}.png`); await page.screenshot({path: screenshot}); screenshots.push(screenshot);
      browserChecks.push({width, theme, httpStatus: response.status(), title: meta.title, displayLabel: 'LC.704', displayDuration, sourceEntry: expectedSource, media, chapters, seeks,
        captions: {count: cues.length, sha256: sha(vtt), exactNarrationMatch: true, finalCueEndSeconds: finalCueEnd, unvoicedCardStartSeconds: card.from / fps, narratedCC, cardCC},
        playbackSmoke: {from: cardTime, playing, paused, scope: 'Approximately one second of muted code-card playback; no narration listening claim.'}, codeCardFrame: rawPath, overflow, errors});

      if (width === 1440) {
        await page.goto(new URL('series/leetcode/', base).href, {waitUntil: 'networkidle'});
        const hrefs = await page.locator('.lesson-list a.lesson').evaluateAll((cards) => cards.map((a) => a.getAttribute('href')));
        const expectedHrefs = ['container-most-water', 'longest-substring', 'binary-search'].map((slug) => `/video-studio/episodes/${slug}/`);
        assert.deepEqual(hrefs, expectedHrefs);
        assert.ok((await page.locator('.course-count').innerText()).includes('已发布 3 篇'));
        await page.goto(base, {waitUntil: 'networkidle'});
        assert.ok(await page.locator('a.card[href="/video-studio/episodes/binary-search/"]').count() > 0);
        await page.goto(new URL('library/?series=leetcode&sort=learning', base).href, {waitUntil: 'networkidle'});
        assert.equal(await page.locator('#library-grid li:visible').count(), 3);
        assert.ok((await page.locator('#library-grid').innerText()).includes('LC.704'));
        const libraryHrefs = await page.locator('#library-grid li:visible a.card').evaluateAll((cards) => cards.map((a) => a.getAttribute('href')));
        assert.deepEqual(libraryHrefs, expectedHrefs);
        const rss = await context.request.get(new URL('rss.xml', base).href); assert.equal(rss.status(), 200);
        const rssItem = (await rss.text()).match(/<item>[\s\S]*?<\/item>/g)?.find((item) => item.includes('/episodes/binary-search/'));
        assert.ok(rssItem && rssItem.includes('LC.704'));
        const parallelLesson = await context.request.get(new URL('episodes/horse-racing/', base).href);
        assert.equal(parallelLesson.status(), 200, 'The parallel P01 lesson must remain published');
        const parallelMeta = JSON.parse(fs.readFileSync(path.join(root, 'episodes/horse-racing/meta.json'), 'utf8'));
        assert.ok((await parallelLesson.text()).includes(parallelMeta.title));
        siteEntries = {leetcodeSeriesLessons: hrefs, homeContainsNewEpisode: true, libraryLeetcodeVisibleCount: 3, libraryLearningOrder: libraryHrefs, rssItemPresentWithProblemNumber: true, sourceEntryVerified: expectedSource, parallelP01LessonPreserved: true};
      }
      await context.close();
    }
    assert.equal(videoSha, sha(fs.readFileSync(path.join(dist, 'episodes/binary-search/video.mp4'))));
    assert.equal(posterSha, sha(fs.readFileSync(path.join(dist, 'episodes/binary-search/cover-16x9.jpg'))));
    const report = {status: 'passed', checkedAtUTC: new Date().toISOString(), executor: 'Codex binary_site agent',
      baseCommit: cp.execFileSync('git', ['rev-parse', 'HEAD'], {cwd: root, encoding: 'utf8'}).trim(),
      siteVersion, slug: meta.slug, firstRelease: meta.firstRelease,
      supersedes: {commit: previousReportCommit, jsonPath: 'episodes-codex/binary-search/qa-site.json', markdownPath: 'episodes-codex/binary-search/qa-site.md', reason: 'The parallel P01 release already owns v0.55.0. The binary-search episode is unchanged; its actual first release and the current site version are v0.56.0.'},
      build: {command: 'cd site && npm run build', passed: true, runs: 1, reusedForBrowserResume: reuseBuild, htmlFiles: countFiles(dist, (name) => name.endsWith('.html')), indexedPages: fs.readdirSync(path.join(dist, 'pagefind/fragment')).filter((name) => name.endsWith('.pf_fragment')).length, log: path.join(output, 'build.log')},
      historicalRegression: {command: 'node site/scripts/check-learning-path.mjs --complete --built', passed: true, runs: 1, log: path.join(output, 'learning-path.log')},
      media: {frames, videoFrameDuration: frames / fps, videoSha256: videoSha, posterSha256: posterSha, sourceBuiltAndHTTPIdentical: true, codeCardFromFrame: card.from, codeCardFrames: card.durationInFrames, codeCardSeconds: card.durationInFrames / fps},
      browserChecks, siteEntries, screenshots: screenshots.map((p) => ({path: p, sha256: sha(fs.readFileSync(p))})),
      limits: ['Only the new page was checked at 1440px light and 390px dark; old full responsive matrices were not repeated.',
        'VTT timestamps serialize frame times to milliseconds; caption end was checked within 0.001 seconds of the silent card boundary.',
        'Pause and brief muted code-card playback were checked; this is not full-film listening, ASR or algorithm proof.',
        'Actual Release/changelog and production HTTPS media verification remain the publishing task.',
        'The prior v0.55.0 QA and its stale-pager-assertion repair remain traceable at Git commit 5a41a16. This report is a new build and browser check for the corrected v0.56.0 release identity on the main branch that includes P01.']};
    fs.writeFileSync(path.join(production, 'qa-site.json'), JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({status: report.status, report: path.join(production, 'qa-site.json'), media: report.media, siteEntries, screenshots}, null, 2));
  } finally {
    if (browser) await browser.close();
    if (preview) preview.kill('SIGTERM');
  }
})().catch((error) => {console.error(error); process.exitCode = 1;});
