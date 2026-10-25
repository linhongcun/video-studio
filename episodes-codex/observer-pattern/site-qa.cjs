// D02 final publishing QA. Run after approved copies and the final version:
//   node episodes-codex/observer-pattern/site-qa.cjs
// --reuse-build resumes browser checks only when recorded build inputs still match.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const crypto = require('node:crypto');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '../..'), site = path.join(root, 'site'), dist = path.join(site, 'dist');
const output = path.join(__dirname, 'site-qa'), canonical = path.join(root, 'episodes/observer-pattern');
const slug = 'observer-pattern', seriesSlugs = ['strategy-pattern', slug];
const json = (f) => JSON.parse(fs.readFileSync(f, 'utf8'));
const hash = (b) => crypto.createHash('sha256').update(b).digest('hex');
const fileHash = (f) => hash(fs.readFileSync(f));
const files = (dir) => fs.readdirSync(dir, {withFileTypes: true}).flatMap((e) => e.isDirectory() ? files(path.join(dir, e.name)) : [path.join(dir, e.name)]);
const fingerprint = (paths) => hash([...paths].sort().map((p) => `${path.relative(root, p)}\0${fileHash(p)}`).join('\n'));
const meta = json(path.join(canonical, 'meta.json')), sb = json(path.join(canonical, 'storyboard.json'));
const version = json(path.join(site, 'package.json')).version;
const fps = sb.meta.fps, frames = meta.finalVideoFrames;
const href = (s) => `/video-studio/episodes/${s}/`;
const port = Number(process.env.QA_SITE_PORT || 4198);
const base = process.env.QA_SITE_BASE || `http://127.0.0.1:${port}/video-studio/`;
assert.ok(base.endsWith('/'));
assert.equal(meta.draft, false); assert.equal(meta.firstRelease, 'v' + version);
assert.equal(meta.slug, slug); assert.equal(meta.ep, 28); assert.equal(meta.lessonOrder, 2);
assert.equal(meta.episodePart, '设计模式 D02'); assert.equal(meta.series, 'design-patterns');
assert.equal(meta.sourcePath, `episodes-codex/${slug}/remotion`); assert.deepEqual(meta.platforms, {});
assert.equal(fps, 30); assert.equal(frames, sb.meta.finalVideoFrames || sb.meta.durationInFrames);
assert.equal(meta.title, json(path.join(__dirname, 'episode-config.json')).title);
const manifest = json(path.join(__dirname, 'site-copy-manifest.json'));
for (const f of manifest.files) {
  assert.equal(fileHash(path.join(canonical, f.file)), f.sha256);
  assert.equal(fileHash(path.join(__dirname, f.file)), f.sha256);
}
for (const e of fs.readdirSync(canonical, {withFileTypes: true})) {
  assert.equal(e.isDirectory(), false); assert.ok(!/\.(wav|png|tsx?|jsx?)$/i.test(e.name));
}
const chapters = [], expectedCues = []; let offset = 0;
for (const scene of sb.scenes) {
  if (chapters.at(-1)?.id !== scene.chapterId) chapters.push({id: scene.chapterId, title: scene.title, frame: offset, start: offset / fps});
  for (const shot of scene.shots) {
    for (const sub of shot.subtitles) expectedCues.push({text: sub.text, start: (offset + sub.from) / fps, end: (offset + sub.to + 1) / fps});
    offset += shot.durationInFrames;
  }
}
assert.equal(offset, frames); assert.equal(expectedCues.length, sb.scenes.flatMap((s) => s.shots).length * 2);
const videoSha = fileHash(path.join(canonical, meta.video)), posterSha = fileHash(path.join(canonical, meta.poster));
const source = `https://github.com/linhongcun/video-studio/tree/main/${meta.sourcePath}`;
const parseTime = (s) => s.split(':').reduce((a, b) => a * 60 + Number(b), 0);
const parseVtt = (s) => s.trim().split(/\r?\n\s*\r?\n/).slice(1).map((block) => {
  const lines = block.split(/\r?\n/), times = lines.shift().split(' --> ');
  return {start: parseTime(times[0]), end: parseTime(times[1]), text: lines.join('\n')};
});
function logged(cmd, args, cwd, name) {
  const r = cp.spawnSync(cmd, args, {cwd, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024});
  fs.writeFileSync(path.join(output, name), `${r.stdout || ''}${r.stderr || ''}`);
  if (r.error) throw r.error; assert.equal(r.status, 0, `${cmd} failed; see site-qa/${name}`);
}
function buildFingerprint() {
  const canonicalInputs = fs.readdirSync(path.join(root, 'episodes')).filter((s) => fs.existsSync(path.join(root, 'episodes', s, 'meta.json')))
    .flatMap((s) => ['meta.json', 'article.mdx', 'storyboard.json'].map((n) => path.join(root, 'episodes', s, n)).filter(fs.existsSync));
  return fingerprint([...files(path.join(site, 'src')), ...files(path.join(site, 'scripts')),
    path.join(site, 'package.json'), path.join(site, 'package-lock.json'), path.join(site, 'astro.config.mjs'),
    ...canonicalInputs, path.join(canonical, meta.video), path.join(canonical, meta.poster)]);
}
async function checkPage(context, width, theme) {
  const page = await context.newPage(), errors = []; page.on('pageerror', (e) => errors.push(e.message));
  const response = await page.goto(new URL(`episodes/${slug}/`, base).href, {waitUntil: 'networkidle'});
  assert.equal(response.status(), 200); await page.evaluate(() => document.fonts.ready);
  assert.equal(await page.locator('h1').innerText(), meta.title);
  assert.ok((await page.locator('footer').innerText()).includes(`v${version}`));
  assert.ok((await page.locator('.eh .meta').innerText()).includes(`${Math.floor(frames / fps / 60)}:${String(Math.floor(frames / fps % 60)).padStart(2, '0')}`));
  assert.ok(await page.locator(`a[href="${source}"]`).count() > 0);
  assert.equal(await page.locator('.pl').count(), 0);
  assert.deepEqual(await page.locator('.pager a').evaluateAll((a) => a.map((el) => el.getAttribute('href'))), [href('strategy-pattern')]);
  const dir = page.locator('#course-directory nav');
  assert.deepEqual(await dir.locator('a').evaluateAll((a) => a.map((el) => el.getAttribute('href'))), seriesSlugs.map(href));
  assert.equal(await dir.locator('[aria-current="page"]').getAttribute('href'), href(slug));
  const video = page.locator('video'); await video.evaluate((v) => {v.muted = true; v.load();});
  await page.waitForFunction(() => document.querySelector('video').readyState >= 2);
  const media = await video.evaluate((v) => ({duration: v.duration, controls: v.controls, width: v.videoWidth, height: v.videoHeight}));
  assert.equal(media.controls, true); assert.deepEqual([media.width, media.height], [1920, 1080]);
  assert.ok(Math.abs(media.duration - frames / fps) < 0.1);
  const actualChapters = await page.locator('#player').evaluate((el) => JSON.parse(el.dataset.chapters));
  assert.deepEqual(actualChapters.map((c) => [c.id, c.start]), chapters.map((c) => [c.id, c.start]));
  const seeks = [];
  for (const c of chapters) {
    assert.ok(await page.locator(`article #${c.id}`).count() > 0);
    const target = page.locator(`#player .${width < 768 ? 'chip' : 'ch'}[data-id="${c.id}"]`);
    // Pause on the real seek event to measure the click target before playback advances.
    await video.evaluate((v) => v.addEventListener('seeking', () => v.pause(), {once: true}));
    await target.click(); await video.evaluate((v) => v.pause());
    await page.waitForFunction((t) => {const v = document.querySelector('video'); return !v.seeking && Math.abs(v.currentTime - t) < 0.01;}, c.start);
    const actual = await video.evaluate((v) => v.currentTime); assert.equal(await target.getAttribute('aria-current'), 'true');
    await video.evaluate((v) => v.play());
    await page.waitForFunction((t) => {const v = document.querySelector('video'); return v.currentTime > t + 0.25 && !v.paused && v.readyState >= 2;}, actual);
    const playing = await video.evaluate((v) => ({time: v.currentTime, paused: v.paused, error: v.error?.message ?? null, decodedFrames: v.getVideoPlaybackQuality().totalVideoFrames}));
    await video.evaluate((v) => v.pause()); assert.equal(playing.error, null);
    seeks.push({id: c.id, expected: c.start, actual, error: Math.abs(actual - c.start), playing});
  }
  const responseVtt = await context.request.get(new URL(`episodes/${slug}/captions.vtt`, base).href);
  assert.equal(responseVtt.status(), 200); const vtt = await responseVtt.body(), cues = parseVtt(vtt.toString());
  assert.equal(cues.length, expectedCues.length); assert.deepEqual(cues.map((c) => c.text), expectedCues.map((c) => c.text));
  let maxTimestampError = 0;
  cues.forEach((c, i) => {for (const k of ['start', 'end']) {const error = Math.abs(c[k] - expectedCues[i][k]); assert.ok(error < 0.001); maxTimestampError = Math.max(maxTimestampError, error);}});
  await video.evaluate((v, t) => {v.textTracks[0].mode = 'showing'; v.currentTime = t;}, (cues[0].start + cues[0].end) / 2);
  await page.waitForFunction((count) => {const v = document.querySelector('video'); return !v.seeking && document.querySelector('track').readyState === 2 && v.textTracks[0].cues?.length === count && v.textTracks[0].activeCues?.length > 0;}, cues.length);
  const captionTrack = await video.evaluate((v) => ({language: v.textTracks[0].language, label: v.textTracks[0].label, cueCount: v.textTracks[0].cues.length, activeCues: v.textTracks[0].activeCues.length}));
  if (width === 1440) for (const [name, expected] of [[meta.video, videoSha], [meta.poster, posterSha]]) {
    const asset = await context.request.get(new URL(`episodes/${slug}/${name}`, base).href); assert.equal(asset.status(), 200); assert.equal(hash(await asset.body()), expected);
  }
  const overflow = await page.evaluate(() => ({viewport: innerWidth, documentWidth: document.documentElement.scrollWidth,
    elements: [...document.body.querySelectorAll('*')].filter((el) => {const r = el.getBoundingClientRect(); return r.width && r.height && getComputedStyle(el).visibility !== 'hidden' && !el.closest('.sr-only,.chips') && !(el.closest('pre') && el.tagName !== 'PRE') && !(el.closest('table') && el.tagName !== 'TABLE') && (r.left < -1 || r.right > innerWidth + 1);}).map((el) => ({tag: el.tagName, class: el.className})).slice(0, 20)}));
  assert.ok(overflow.documentWidth <= width); assert.deepEqual(overflow.elements, []); assert.deepEqual(errors, []);
  await page.mouse.move(10, 10); await page.evaluate(() => scrollTo({top: 0, left: 0, behavior: 'instant'}));
  const screenshot = path.join(output, `observer-player-${width}-${theme}.png`); await page.screenshot({path: screenshot});
  await page.locator('article').scrollIntoViewIfNeeded();
  const articleScreenshot = path.join(output, `observer-article-${width}-${theme}.png`); await page.screenshot({path: articleScreenshot});
  await page.close(); return {width, theme, media, seeks, captions: {sha256: hash(vtt), cueCount: cues.length, maxTimestampError, captionTrack},
    pagerHrefs: [href('strategy-pattern')], directoryHrefs: seriesSlugs.map(href), source, overflow, errors,
    screenshots: [screenshot, articleScreenshot].map((f) => ({path: path.relative(root, f), sha256: fileHash(f)}))};
}
(async () => {
  fs.mkdirSync(output, {recursive: true}); const inputFingerprint = buildFingerprint(), receipt = path.join(output, 'build-receipt.json');
  const reuseBuild = process.argv.includes('--reuse-build');
  if (reuseBuild) {
    const old = json(receipt); assert.equal(old.inputFingerprint, inputFingerprint); assert.equal(old.distFingerprint, fingerprint(files(dist)));
  } else {
    logged('npm', ['run', 'build'], site, 'build.log');
    logged('node', ['site/scripts/check-learning-path.mjs', '--complete', '--built'], root, 'learning-path.log');
    fs.writeFileSync(receipt, JSON.stringify({inputFingerprint, distFingerprint: fingerprint(files(dist)), checkedAtUTC: new Date().toISOString(), buildPassed: true}, null, 2) + '\n');
  }
  const pages = fs.readdirSync(path.join(root, 'episodes')).filter((s) => fs.existsSync(path.join(root, 'episodes', s, 'meta.json')) && !json(path.join(root, 'episodes', s, 'meta.json')).draft);
  pages.forEach((s) => assert.ok(fs.existsSync(path.join(dist, 'episodes', s, 'index.html'))));
  for (const [name, expected] of [[meta.video, videoSha], [meta.poster, posterSha]]) assert.equal(fileHash(path.join(dist, 'episodes', slug, name)), expected);
  const preview = process.env.QA_SITE_BASE ? null : cp.spawn(process.execPath, [path.join(site, 'node_modules/astro/astro.js'), 'preview', '--host', '127.0.0.1', '--port', String(port)], {cwd: site, stdio: 'ignore'});
  let browser; const browserChecks = [], entries = [];
  try {
    for (let i = 0; i < 100; i++) {try {if ((await fetch(base)).ok) break;} catch {} assert.ok(i < 99, 'Preview did not start'); await new Promise((r) => setTimeout(r, 200));}
    browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium', args: ['--no-sandbox']});
    for (const [width, theme] of [[1440, 'light'], [390, 'dark']]) {
      const context = await browser.newContext({viewport: {width, height: 900}, colorScheme: theme});
      browserChecks.push(await checkPage(context, width, theme));
      const page = await context.newPage(); await page.goto(new URL('series/design-patterns/', base).href, {waitUntil: 'networkidle'});
      const seriesHrefs = await page.locator('.lesson-list a.lesson').evaluateAll((a) => a.map((el) => el.getAttribute('href'))); assert.deepEqual(seriesHrefs, seriesSlugs.map(href));
      await page.goto(base, {waitUntil: 'networkidle'}); assert.ok(await page.locator(`a.card[href="${href(slug)}"]`).count() > 0);
      await page.goto(new URL('library/?series=design-patterns&sort=learning', base).href, {waitUntil: 'networkidle'});
      await page.waitForFunction(() => [...document.querySelectorAll('#library-grid li')].filter((el) => getComputedStyle(el).display !== 'none').length === 2);
      const libraryHrefs = await page.locator('#library-grid li:visible a.card').evaluateAll((a) => a.map((el) => el.getAttribute('href'))); assert.deepEqual(libraryHrefs, seriesSlugs.map(href));
      await page.goto(new URL('episodes/strategy-pattern/', base).href, {waitUntil: 'networkidle'});
      assert.deepEqual(await page.locator('.pager a').evaluateAll((a) => a.map((el) => el.getAttribute('href'))), [href(slug)]);
      const rss = await context.request.get(new URL('rss.xml', base).href); assert.equal(rss.status(), 200); assert.ok((await rss.text()).includes(`episodes/${slug}/`));
      entries.push({width, seriesHrefs, libraryHrefs, D01NextD02: true, homeCard: true, rssItem: true});
      await context.close();
    }
    const report = {status: 'passed', checkedAtUTC: new Date().toISOString(), executedBy: 'Codex observer_site agent',
      baseline: cp.execFileSync('git', ['rev-parse', 'HEAD'], {cwd: root, encoding: 'utf8'}).trim(), siteVersion: version,
      release: meta.firstRelease, inputFingerprint, build: {passed: true, command: 'cd site && npm run build', reusedForBrowserResume: reuseBuild, pagesPreserved: pages},
      historicalRegression: {passed: true, command: 'node site/scripts/check-learning-path.mjs --complete --built'},
      media: {frames, fps, seconds: frames / fps, videoSha256: videoSha, posterSha256: posterSha, productionCanonicalBuiltAndHTTPIdentical: true}, chapters, browserChecks, entries,
      limits: ['Two viewports: 1440px light and 390px dark. All chapter buttons were actually clicked and followed by short muted playback.',
        'Every serialized subtitle text and start/end boundary was compared with the frozen storyboard; the browser loaded the complete cue track.',
        'Screenshots were captured; capture alone does not claim visual inspection. This check is not full narration listening, ASR, a beginner experiment, or user approval.',
        'Production HTTPS and actual Release entry verification is a separate post-deployment step.']};
    fs.writeFileSync(path.join(__dirname, 'site-browser-check.json'), JSON.stringify(report, null, 2) + '\n');
    fs.writeFileSync(path.join(__dirname, 'site-static-check.json'), JSON.stringify({status: 'passed', checkedAtUTC: report.checkedAtUTC, release: meta.firstRelease,
      videoSha256: videoSha, posterSha256: posterSha, vttSha256: browserChecks[0].captions.sha256,
      cueCount: expectedCues.length, chapters, finalVideoFrames: frames, source, pagesPreserved: pages, buildPassed: true, historicalRegressionPassed: true}, null, 2) + '\n');
    console.log(JSON.stringify({status: 'passed', report: 'episodes-codex/observer-pattern/site-browser-check.json', viewports: browserChecks.length, chapters: chapters.length, cueCount: expectedCues.length, pagesPreserved: pages.length}));
  } finally {if (browser) await browser.close(); if (preview) preview.kill('SIGTERM');}
})().catch((e) => {console.error(e); process.exitCode = 1;});
