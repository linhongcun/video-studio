// Final local delivery QA for the five-episode approach revision. Run only after final
// canonical MP4/JPG/article/script/storyboard and real frame counts are ready:
//   node docs/leetcode-derivation-20261025/qa-site.cjs
// One actual build and one historical regression serve all ten browser cases.
// A browser-only retry may use --reuse-build if the recorded inputs still match.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const crypto = require('node:crypto');
const {chromium} = require('playwright');

const root = path.resolve(__dirname, '../..');
const site = path.join(root, 'site');
const dist = path.join(site, 'dist');
const output = path.join(__dirname, 'site-qa');
const port = Number(process.env.QA_SITE_PORT || 4197);
const base = process.env.QA_SITE_BASE || `http://127.0.0.1:${port}/video-studio/`;
assert.ok(base.endsWith('/'), 'QA_SITE_BASE must end with a slash');
const siteVersion = JSON.parse(fs.readFileSync(path.join(site, 'package.json'), 'utf8')).version;
const baselineCommit = 'e38fa9236fbc340f834581302320494d2a1c1ce7';
// Later upstream work was merged before delivery. Preserve its short P01 and
// every other episode, while retaining the original LC.70 baseline separately.
const upstreamCommit = 'fcbf3e162743b59d23334b0df0d691460ee4889d';
const revisionDate = '2026-10-25';
const specifications = [
  {slug: 'two-sum', ep: 25, problem: 1, sentences: 28},
  {slug: 'longest-substring', ep: 23, problem: 3, sentences: 40},
  {slug: 'binary-search', ep: 24, problem: 704, sentences: 30},
  {slug: 'reverse-linked-list', ep: 26, problem: 206, sentences: 30},
  {slug: 'container-most-water', ep: 22, problem: 11, sentences: 44},
];
const algorithmSlugs = ['container-most-water', 'longest-substring', 'binary-search', 'two-sum', 'reverse-linked-list', 'climbing-stairs'];
const readJson = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const sha = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');
const fileSha = (file) => sha(fs.readFileSync(file));
const parseTime = (stamp) => stamp.split(':').reduce((total, n) => total * 60 + Number(n), 0);
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const epHref = (slug) => `/video-studio/episodes/${slug}/`;
const listFiles = (dir) => fs.readdirSync(dir, {withFileTypes: true}).flatMap((entry) => entry.isDirectory()
  ? listFiles(path.join(dir, entry.name)) : [path.join(dir, entry.name)]);

const baselineBytes = (relative, commit = baselineCommit) => cp.execFileSync('git', ['show', `${commit}:${relative}`], {cwd: root, maxBuffer: 64 * 1024 * 1024});
const baselineJson = (relative) => JSON.parse(baselineBytes(relative).toString('utf8'));
const upstreamJson = (relative) => JSON.parse(baselineBytes(relative, upstreamCommit).toString('utf8'));
const taskSharedPaths = ['episodes-codex/_shared/remix_approach.py', 'episodes-codex/_shared/test_remix_approach.py', 'episodes-codex/_template/README.md'];
const taskOwned = (name) => specifications.some(({slug}) => name.startsWith(`episodes/${slug}/`) || name.startsWith(`episodes-codex/${slug}/`)) || taskSharedPaths.includes(name);
function preservedUpstream() {
  const paths = ['episodes', 'episodes-codex',
    ...specifications.flatMap(({slug}) => [`:(exclude)episodes/${slug}`, `:(exclude)episodes-codex/${slug}`]),
    ...taskSharedPaths.map((name) => `:(exclude)${name}`)];
  const changed = cp.execFileSync('git', ['diff', '--no-ext-diff', '--name-only', upstreamCommit, '--', ...paths], {cwd: root, encoding: 'utf8'}).trim();
  assert.equal(changed, '', 'Upstream episode content changed outside the five revisions and their shared production helper');
  const extra = cp.execFileSync('git', ['ls-files', '--others', '--exclude-standard', '--', ...paths], {cwd: root, encoding: 'utf8'}).trim();
  assert.equal(extra, '', 'Unexpected non-task episode content was added');
  const names = cp.execFileSync('git', ['ls-tree', '-r', '--name-only', upstreamCommit, '--', 'episodes', 'episodes-codex'], {cwd: root, encoding: 'utf8'}).trim().split(/\r?\n/).filter((name) => name && !taskOwned(name));
  const metaPaths = names.filter((name) => /^episodes\/[^/]+\/meta\.json$/.test(name));
  const actualSlugs = fs.readdirSync(path.join(root, 'episodes')).filter((slug) => fs.existsSync(path.join(root, 'episodes', slug, 'meta.json')) && !specifications.some((spec) => spec.slug === slug)).sort();
  assert.deepEqual(actualSlugs, metaPaths.map((name) => name.split('/')[1]).sort());
  const canonicalEpisodes = metaPaths.map((relative) => {
    const slug = relative.split('/')[1], meta = upstreamJson(relative);
    const expectedFiles = names.filter((name) => name.startsWith(`episodes/${slug}/`)).sort();
    // git diff and ls-files above check tracked bytes and nonignored additions.
    // Historical canonical trees can contain ignored local node_modules caches;
    // installing those is neither a published content change nor a rollback.
    const metaSha256 = sha(baselineBytes(relative, upstreamCommit));
    assert.equal(fileSha(path.join(root, relative)), metaSha256);
    return {slug, title: meta.title, series: meta.series, frames: meta.finalVideoFrames, draft: !!meta.draft, archived: !!meta.archived, video: meta.video, poster: meta.poster, fileCount: expectedFiles.length, metaSha256};
  });
  return {baselineCommit: upstreamCommit, trackedCanonicalAndProductionFiles: names.length, exactTrackedBytesUnchanged: true,
    taskSharedFilesExcluded: taskSharedPaths, canonicalEpisodes};
}
function preservedCanonical(slug) {
  const prefix = `episodes/${slug}/`;
  const names = cp.execFileSync('git', ['ls-tree', '-r', '--name-only', baselineCommit, '--', prefix], {cwd: root, encoding: 'utf8'}).trim().split(/\r?\n/).filter(Boolean);
  const actual = listFiles(path.join(root, 'episodes', slug)).map((name) => path.relative(root, name)).sort();
  assert.deepEqual(actual, [...names].sort(), `${slug}: retained canonical file set changed`);
  return Object.fromEntries(names.map((name) => {
    const original = sha(baselineBytes(name));
    assert.equal(fileSha(path.join(root, name)), original, `${slug}: retained canonical bytes changed: ${name}`);
    return [name, original];
  }));
}
function retainedInputs() {
  const climb = preservedCanonical('climbing-stairs');
  const upstream = preservedUpstream();
  const puzzle = readJson(path.join(root, 'episodes/horse-racing/meta.json'));
  const upstreamPuzzle = upstreamJson('episodes/horse-racing/meta.json');
  assert.deepEqual(puzzle, upstreamPuzzle, 'Keep the actual latest-main P01 metadata');
  const puzzleVideo = fileSha(path.join(root, 'episodes/horse-racing', puzzle.video));
  assert.equal(puzzleVideo, sha(baselineBytes(`episodes/horse-racing/${puzzle.video}`, upstreamCommit)), 'Keep the actual latest-main P01 media');
  assert.equal(puzzleVideo, fileSha(path.join(root, 'episodes-codex/horse-racing', puzzle.video)));
  return {climbingStairs: {baselineCommit, allCanonicalFilesSHA256: climb}, upstream,
    P01: {baselineCommit: upstreamCommit, frames: puzzle.finalVideoFrames, metaSha256: fileSha(path.join(root, 'episodes/horse-racing/meta.json')), videoSha256: puzzleVideo}};
}

function expectedRecentHrefs() {
  return fs.readdirSync(path.join(root, 'episodes')).filter((slug) => fs.existsSync(path.join(root, 'episodes', slug, 'meta.json')))
    .map((slug) => readJson(path.join(root, 'episodes', slug, 'meta.json'))).filter((meta) => !meta.draft && !meta.archived)
    .sort((a, b) => String(b.publishedAt).localeCompare(String(a.publishedAt)) || b.ep - a.ep || (b.lessonOrder ?? 0) - (a.lessonOrder ?? 0))
    .slice(0, 6).map((meta) => epHref(meta.slug));
}

function inputsFor(spec) {
  const canonical = path.join(root, 'episodes', spec.slug);
  const production = path.join(root, 'episodes-codex', spec.slug);
  const meta = readJson(path.join(canonical, 'meta.json'));
  assert.equal(meta.draft, false, `${spec.slug}: final media must be approved before delivery QA`);
  const originalMeta = baselineJson(`episodes/${spec.slug}/meta.json`);
  assert.equal(meta.firstRelease, originalMeta.firstRelease, `${spec.slug}: a revision must preserve its real first release`);
  assert.notEqual(meta.firstRelease, `v${siteVersion}`, `${spec.slug}: a patch must not reuse its debut version`);
  assert.equal(meta.publishedAt, originalMeta.publishedAt);
  assert.equal(meta.updatedAt, revisionDate);
  assert.equal(meta.slug, spec.slug); assert.equal(meta.ep, spec.ep); assert.equal(meta.problemNumber, spec.problem);
  assert.equal(meta.series, 'leetcode'); assert.deepEqual(meta.platforms, originalMeta.platforms ?? {});
  assert.equal(meta.sourcePath, `episodes-codex/${spec.slug}/remotion`);
  assert.equal(meta.title, readJson(path.join(production, 'episode-config.json')).title);
  const storyboard = readJson(path.join(canonical, 'storyboard.json'));
  assert.equal(fileSha(path.join(canonical, 'storyboard.json')), fileSha(path.join(production, 'storyboard.json')));
  for (const name of ['script.md', 'article.mdx']) {
    assert.equal(fileSha(path.join(canonical, name)), fileSha(path.join(production, name)), `${spec.slug}: stale canonical ${name}`);
  }
  for (const entry of fs.readdirSync(canonical, {withFileTypes: true})) {
    assert.equal(entry.isDirectory(), false, `${spec.slug}: production directories must stay outside canonical content`);
    assert.ok(!/\.(?:wav|png|tsx?|jsx?)$/i.test(entry.name), `${spec.slug}: production artifact leaked into canonical content: ${entry.name}`);
  }
  const fps = storyboard.meta.fps;
  const frames = storyboard.meta.finalVideoFrames;
  const card = storyboard.meta.unvoicedEndCard;
  assert.equal(fps, 30);
  assert.ok(Number.isInteger(frames) && frames > 150, `${spec.slug}: real final frames are required`);
  assert.equal(meta.finalVideoFrames, frames);
  assert.equal(card.durationInFrames, 150); assert.equal(card.from + card.durationInFrames, frames);
  const chapters = storyboard.scenes.map((s) => s.chapterId);
  assert.equal(chapters.length, 4); assert.equal(new Set(chapters).size, 4);
  assert.ok(chapters.every((id) => typeof id === 'string' && /^[a-z][a-z0-9-]*$/.test(id)));
  assert.deepEqual(chapters, readJson(path.join(production, 'storyboard.json')).scenes.map((scene) => scene.chapterId));
  const expectedStarts = storyboard.scenes.map((s) => s.from / fps);
  const expectedCues = storyboard.scenes.flatMap((scene) => scene.shots.flatMap((shot) => shot.subtitles.map((sub) => ({
    text: sub.text, start: (shot.from + sub.from) / fps, end: (shot.from + sub.to + 1) / fps,
  }))));
  assert.equal(expectedCues.length, spec.sentences);
  assert.ok(expectedCues.every((cue) => cue.end <= card.from / fps));
  const videoSha = fileSha(path.join(canonical, meta.video));
  const posterSha = fileSha(path.join(canonical, meta.poster));
  const rendered = readJson(path.join(production, 'render-result.json'));
  assert.equal(rendered.sha256, videoSha, `${spec.slug}: encoded final QA must identify this exact MP4`);
  assert.equal(rendered.frames, frames);
  assert.ok(Math.abs(rendered.finalLUFS + 16) <= 0.3);
  assert.ok(rendered.truePeakDBTP <= -2);
  const frozen = readJson(path.join(production, 'source-sha256.json'));
  for (const [relative, expected] of Object.entries(frozen)) assert.equal(fileSha(path.resolve(production, relative)), expected, `${spec.slug}: frozen input changed: ${relative}`);
  const baseline = readJson(path.join(production, 'revisions/approach-first/baseline.json'));
  assert.notEqual(videoSha, baseline.sha256['video.mp4'], `${spec.slug}: final revision MP4 is still the baseline`);
  assert.equal(videoSha, fileSha(path.join(production, meta.video)), `${spec.slug}: canonical MP4 differs from final production`);
  assert.equal(posterSha, fileSha(path.join(production, meta.poster)), `${spec.slug}: canonical poster differs from final production`);
  const covers = Object.fromEntries(['16x9', '4x3', '3x4'].map((ratio) => {
    const name = `cover-${ratio}.jpg`, digest = fileSha(path.join(canonical, name));
    assert.equal(digest, fileSha(path.join(production, name)), `${spec.slug}: stale canonical ${name}`);
    return [name, digest];
  }));
  return {...spec, chapters, canonical, production, meta, originalMeta, storyboard, fps, frames, card, expectedStarts, expectedCues, videoSha, posterSha,
    covers,
    displayDuration: `${Math.floor(frames / fps / 60)}:${String(Math.floor(frames / fps % 60)).padStart(2, '0')}`,
    expectedSource: `https://github.com/linhongcun/video-studio/tree/main/${meta.sourcePath}`};
}

const fingerprintFiles = (files) => sha([...files].sort().map((file) => `${path.relative(root, file)}\0${fileSha(file)}`).join('\n'));

function inputFingerprint(episodes) {
  // Include historical canonical inputs and top-level Astro configuration: a
  // browser retry must not silently reuse a regression from another checkout.
  const canonicalFiles = cp.execFileSync('git', ['ls-files', '--cached', '--others', '--exclude-standard', '--', 'episodes'], {cwd: root, encoding: 'utf8'})
    .trim().split(/\r?\n/).filter(Boolean).map((relative) => path.join(root, relative));
  const files = [
    ...listFiles(path.join(site, 'src')), ...listFiles(path.join(site, 'scripts')),
    ...fs.readdirSync(site, {withFileTypes: true}).filter((e) => e.isFile()).map((e) => path.join(site, e.name)),
    ...canonicalFiles, __filename,
    ...episodes.flatMap((e) => ['solution.py', 'episode-config.json'].map((name) => path.join(e.production, name))),
  ];
  return fingerprintFiles(files);
}

function parseVtt(bytes) {
  const blocks = bytes.toString('utf8').trim().split(/\r?\n\s*\r?\n/);
  assert.equal(blocks.shift(), 'WEBVTT');
  return blocks.map((block) => {
    const lines = block.split(/\r?\n/);
    const match = /^(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)$/.exec(lines[0]);
    assert.ok(match, `Unexpected VTT cue: ${lines[0]}`);
    return {start: parseTime(match[1]), end: parseTime(match[2]), text: lines.slice(1).join('\n')};
  });
}

function runLogged(command, args, cwd, file) {
  try {
    const result = cp.spawnSync(command, args, {cwd, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024});
    fs.writeFileSync(file, `${result.stdout || ''}${result.stderr || ''}`);
    if (result.error) throw result.error;
    assert.equal(result.status, 0, `${command} failed; see ${path.relative(root, file)}`);
  } catch (error) { throw error; }
}

async function checkPage(context, e, width, theme, screenshots) {
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  const response = await page.goto(new URL(`episodes/${e.slug}/`, base).href, {waitUntil: 'networkidle'});
  assert.equal(response.status(), 200);
  await page.evaluate(() => document.fonts.ready);
  assert.equal(await page.locator('h1').innerText(), e.meta.title);
  assert.ok((await page.locator('footer').innerText()).includes(`v${siteVersion}`));
  assert.ok((await page.locator('.eh .meta').innerText()).includes(e.displayDuration));
  assert.ok(await page.getByText(`LC.${e.problem}`, {exact: false}).count() > 0);
  assert.equal(await page.locator('.pl').count(), 0);
  assert.ok(await page.locator(`a[href="${e.expectedSource}"]`).count() > 0);
  assert.ok((await page.locator('article pre').allTextContents()).some((code) => code.trim() === fs.readFileSync(path.join(e.production, 'solution.py'), 'utf8').trim()));
  const index = algorithmSlugs.indexOf(e.slug);
  const neighbors = [algorithmSlugs[index - 1], algorithmSlugs[index + 1]].filter(Boolean).map(epHref);
  assert.deepEqual(await page.locator('.pager a').evaluateAll((links) => links.map((a) => a.getAttribute('href'))), neighbors);
  const video = page.locator('video');
  await video.evaluate((v) => {v.muted = true;});
  await page.waitForFunction(() => document.querySelector('video').readyState >= 1);
  const media = await video.evaluate((v) => ({duration: v.duration, controls: v.controls, width: v.videoWidth, height: v.videoHeight}));
  assert.equal(media.controls, true); assert.ok(Math.abs(media.duration - e.frames / e.fps) < 0.1);
  assert.deepEqual([media.width, media.height], [1920, 1080]);
  const chapters = await page.locator('#player').evaluate((el) => JSON.parse(el.dataset.chapters));
  assert.deepEqual(chapters.map((c) => c.id), e.chapters);
  assert.deepEqual(chapters.map((c) => c.start), e.expectedStarts);
  const seeks = [];
  for (const chapter of chapters) {
    assert.ok(await page.locator(`article #${chapter.id}`).count() > 0);
    const selector = `#player ${width < 768 ? '.chip' : '.ch'}[data-id="${chapter.id}"]`;
    await page.locator(selector).click(); await video.evaluate((v) => v.pause());
    await page.waitForFunction((expected) => {const v = document.querySelector('video'); return !v.seeking && Math.abs(v.currentTime - expected) < 0.7;}, chapter.start);
    assert.equal(await page.locator(selector).getAttribute('aria-current'), 'true');
    seeks.push({id: chapter.id, expected: chapter.start, actual: await video.evaluate((v) => v.currentTime)});
  }
  const vttResponse = await context.request.get(new URL(`episodes/${e.slug}/captions.vtt`, base).href);
  assert.equal(vttResponse.status(), 200);
  const vtt = await vttResponse.body(), cues = parseVtt(vtt);
  assert.equal(cues.length, e.sentences); assert.deepEqual(cues.map((c) => c.text), e.expectedCues.map((c) => c.text));
  for (let i = 0; i < cues.length; i++) {
    for (const boundary of ['start', 'end']) assert.ok(Math.abs(cues[i][boundary] - e.expectedCues[i][boundary]) < 0.001, `${e.slug}: cue ${i} ${boundary}`);
  }
  const cardStart = e.card.from / e.fps;
  const finalCueEnd = Math.max(...cues.map((c) => c.end));
  assert.ok(Math.abs(finalCueEnd - cardStart) < 0.001);
  assert.ok(cues.every((c) => c.end <= cardStart + 0.001), 'No cue may overlap the silent code card');
  assert.equal(sha(vtt), fileSha(path.join(dist, 'episodes', e.slug, 'captions.vtt')));
  if (width === 1440) {
    for (const [name, expected] of [[e.meta.video, e.videoSha], [e.meta.poster, e.posterSha]]) {
      const asset = await context.request.get(new URL(`episodes/${e.slug}/${name}`, base).href);
      assert.equal(asset.status(), 200); assert.equal(sha(await asset.body()), expected);
    }
  }
  await video.evaluate((v, t) => {v.textTracks[0].mode = 'showing'; v.currentTime = t;}, (cues[0].start + cues[0].end) / 2);
  await page.waitForFunction((n) => {const v = document.querySelector('video'); return document.querySelector('track').readyState === 2 && v.textTracks[0].cues?.length === n && v.textTracks[0].activeCues?.length > 0 && !v.seeking;}, e.sentences);
  const narratedCC = await video.evaluate((v) => ({time: v.currentTime, loadedCues: v.textTracks[0].cues.length, activeCues: v.textTracks[0].activeCues.length}));
  const silentSamples = [];
  for (const offset of [0.1, 2.5, 4.8]) {
    await video.evaluate((v, t) => {v.pause(); v.currentTime = t;}, cardStart + offset);
    await page.waitForFunction(() => {const v = document.querySelector('video'); return !v.seeking && v.readyState >= 2 && v.textTracks[0].activeCues.length === 0;});
    silentSamples.push(await video.evaluate((v) => ({time: v.currentTime, activeCues: v.textTracks[0].activeCues.length, paused: v.paused})));
  }
  const cardTime = cardStart + 1;
  await video.evaluate((v, t) => {v.currentTime = t;}, cardTime);
  await page.waitForFunction(() => !document.querySelector('video').seeking);
  await video.evaluate((v) => v.play());
  await page.waitForFunction((t) => {const v = document.querySelector('video'); return !v.paused && v.currentTime >= t + 1 && v.readyState >= 2;}, cardTime);
  const playing = await video.evaluate((v) => ({time: v.currentTime, paused: v.paused, muted: v.muted, activeCues: v.textTracks[0].activeCues.length, error: v.error?.message ?? null}));
  await video.evaluate((v) => v.pause());
  const paused = await video.evaluate((v) => ({time: v.currentTime, paused: v.paused, activeCues: v.textTracks[0].activeCues.length, seeking: v.seeking}));
  assert.equal(paused.paused, true); assert.equal(paused.activeCues, 0); assert.equal(paused.seeking, false); assert.equal(playing.error, null);
  const raw = await video.evaluate((v) => {const canvas = document.createElement('canvas'); canvas.width = v.videoWidth; canvas.height = v.videoHeight; canvas.getContext('2d').drawImage(v, 0, 0); return canvas.toDataURL('image/png').split(',')[1];});
  const framePath = path.join(output, `${e.slug}-complete-python-${width}.png`);
  fs.writeFileSync(framePath, Buffer.from(raw, 'base64')); screenshots.push(framePath);
  const overflow = await page.evaluate(() => ({scrollWidth: document.documentElement.scrollWidth,
    count: [...document.body.querySelectorAll('*')].filter((el) => {const b = el.getBoundingClientRect(); return b.width && b.height && getComputedStyle(el).visibility !== 'hidden' && !el.closest('.sr-only,.chips') && !(el.closest('pre') && el.tagName !== 'PRE') && !(el.closest('table') && el.tagName !== 'TABLE') && (b.left < -1 || b.right > innerWidth + 1);}).length}));
  assert.equal(overflow.count, 0); assert.equal(overflow.scrollWidth, width); assert.deepEqual(errors, []);
  await page.mouse.move(10, 10); await page.evaluate(() => scrollTo({top: 0, left: 0, behavior: 'instant'}));
  await page.waitForFunction(() => !document.querySelector('#player .vwrap').classList.contains('stuck'));
  assert.equal(await page.locator('#player .vwrap').evaluate((el) => el.classList.contains('stuck')), false);
  const screenshot = path.join(output, `${e.slug}-player-${width}-${theme}.png`); await page.screenshot({path: screenshot}); screenshots.push(screenshot);
  await page.close();
  return {slug: e.slug, width, theme, httpStatus: response.status(), title: e.meta.title, label: `LC.${e.problem}`, displayDuration: e.displayDuration,
    expectedSource: e.expectedSource, pagerHrefs: neighbors, media, chapters, seeks, captions: {count: cues.length, sha256: sha(vtt), exactNarrationAndTiming: true, finalCueEnd, cardStart, narratedCC, silentSamples},
    playbackSmoke: {playing, paused, scope: 'About one second of muted code-card playback; no narration listening claim.'}, codeCardFrame: path.relative(root, framePath), overflow, errors};
}

async function checkEntries(context, width) {
  const page = await context.newPage(), expectedHrefs = algorithmSlugs.map(epHref);
  await page.goto(new URL('series/leetcode/', base).href, {waitUntil: 'networkidle'});
  const seriesHrefs = await page.locator('.lesson-list a.lesson').evaluateAll((cards) => cards.map((a) => a.getAttribute('href')));
  assert.deepEqual(seriesHrefs, expectedHrefs); assert.ok((await page.locator('.course-count').innerText()).includes('已发布 6 篇'));
  await page.goto(base, {waitUntil: 'networkidle'});
  assert.ok(await page.locator('a.track-algorithms[href="/video-studio/learn/#algorithms"]').count() > 0);
  assert.ok(await page.locator(`a.start-link[href="${epHref('container-most-water')}"]`).count() > 0);
  const recentHrefs = await page.locator('.recent a.card').evaluateAll((links) => links.map((link) => link.getAttribute('href')));
  assert.deepEqual(recentHrefs, expectedRecentHrefs(), 'Keep the current published-date order, including new upstream lessons');
  await page.goto(new URL('learn/', base).href, {waitUntil: 'networkidle'});
  assert.equal(await page.locator('#algorithms').count(), 1);
  assert.ok(await page.locator('a[href="/video-studio/series/leetcode/"]').count() > 0);
  await page.goto(new URL('library/?series=leetcode&sort=learning', base).href, {waitUntil: 'networkidle'});
  await page.waitForFunction(() => [...document.querySelectorAll('#library-grid li')].filter((el) => getComputedStyle(el).display !== 'none').length === 6);
  const libraryHrefs = await page.locator('#library-grid li:visible a.card').evaluateAll((cards) => cards.map((a) => a.getAttribute('href')));
  assert.deepEqual(libraryHrefs, expectedHrefs);
  const rss = await context.request.get(new URL('rss.xml', base).href); assert.equal(rss.status(), 200);
  const items = (await rss.text()).match(/<item>[\s\S]*?<\/item>/g) || [];
  for (const e of specifications) assert.ok(items.some((item) => item.includes(`/episodes/${e.slug}/`) && item.includes(`LC.${e.problem}`)), `${e.slug}: missing RSS entry`);
  const p01 = await page.goto(new URL('episodes/horse-racing/', base).href, {waitUntil: 'networkidle'});
  assert.equal(p01.status(), 200); assert.equal(await page.locator('h1').innerText(), readJson(path.join(root, 'episodes/horse-racing/meta.json')).title);
  assert.equal(await page.locator('.pager a').count(), 0, 'P01 must remain an independent direction');
  await page.close();
  return {width, seriesHrefs, libraryHrefs, visibleAlgorithms: 6, homeAlgorithmDirectionAndStart: true, recentHrefs, allFiveReachableThroughDirectionAndLibrary: true, allFiveRSSItemsWithProblemNumbers: true, P01Preserved: true};
}

(async () => {
  // All readiness assertions run before the expensive build. Drafts and missing
  // or provisional frame counts therefore cannot produce a passing report.
  const episodes = specifications.map(inputsFor);
  assert.equal(episodes.reduce((count, e) => count + e.expectedCues.length, 0), 172);
  const retained = retainedInputs();
  fs.mkdirSync(output, {recursive: true});
  const fingerprint = inputFingerprint(episodes), receiptPath = path.join(output, 'build-receipt.json');
  const reuseBuild = process.argv.includes('--reuse-build');
  if (reuseBuild) {
    const receipt = readJson(receiptPath);
    assert.equal(receipt.inputFingerprint, fingerprint, 'Build inputs changed; the previous build cannot be reused');
    assert.equal(receipt.distFingerprint, fingerprintFiles(listFiles(dist)), 'Built output changed; the previous regression cannot be reused');
    assert.equal(receipt.buildPassed, true); assert.equal(receipt.regressionPassed, true);
    for (const name of ['build.log', 'learning-path.log']) assert.ok(fs.existsSync(path.join(output, name)));
  } else {
    runLogged('npm', ['run', 'build'], site, path.join(output, 'build.log'));
    runLogged('node', ['site/scripts/check-learning-path.mjs', '--complete', '--built'], root, path.join(output, 'learning-path.log'));
    fs.writeFileSync(receiptPath, JSON.stringify({inputFingerprint: fingerprint, distFingerprint: fingerprintFiles(listFiles(dist)), checkedAtUTC: new Date().toISOString(), buildPassed: true, regressionPassed: true}, null, 2) + '\n');
  }
  for (const e of episodes) {
    assert.equal(fileSha(path.join(dist, 'episodes', e.slug, e.meta.video)), e.videoSha);
    assert.equal(fileSha(path.join(dist, 'episodes', e.slug, e.meta.poster)), e.posterSha);
  }
  const climbMeta = readJson(path.join(root, 'episodes/climbing-stairs/meta.json'));
  for (const name of [climbMeta.video, climbMeta.poster]) assert.equal(fileSha(path.join(dist, 'episodes/climbing-stairs', name)), fileSha(path.join(root, 'episodes/climbing-stairs', name)));
  const oldClimbQA = readJson(path.join(root, 'docs/leetcode-batch-20261025/qa-site.json')).browserChecks.find((check) => check.slug === 'climbing-stairs' && check.width === 1440);
  retained.climbingStairs.builtVTTSha256 = fileSha(path.join(dist, 'episodes/climbing-stairs/captions.vtt'));
  assert.equal(retained.climbingStairs.builtVTTSha256, oldClimbQA.captions.sha256);
  assert.equal(fileSha(path.join(dist, 'episodes/horse-racing/video.mp4')), retained.P01.videoSha256);
  retained.upstream.builtMedia = retained.upstream.canonicalEpisodes.filter((episode) => !episode.draft).map((episode) => {
    const files = [episode.video, episode.poster].filter(Boolean).map((name) => {
      const digest = fileSha(path.join(root, 'episodes', episode.slug, name));
      assert.equal(fileSha(path.join(dist, 'episodes', episode.slug, name)), digest, `${episode.slug}: upstream media changed during build`);
      return {name, sha256: digest};
    });
    assert.ok(fs.existsSync(path.join(dist, 'episodes', episode.slug, 'index.html')));
    return {slug: episode.slug, files};
  });
  const preview = process.env.QA_SITE_BASE ? null : cp.spawn(process.execPath, [path.join(site, 'node_modules/astro/astro.js'), 'preview', '--host', '127.0.0.1', '--port', String(port)], {cwd: site, stdio: 'ignore'});
  let browser;
  const browserChecks = [], siteEntries = [], screenshots = [];
  try {
    for (let i = 0; i < 100; i++) {
      try {if ((await fetch(base)).ok) break;} catch {}
      assert.ok(i < 99, 'Local preview failed to start'); await sleep(200);
    }
    browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium', args: ['--no-sandbox']});
    for (const [width, theme] of [[1440, 'light'], [390, 'dark']]) {
      const context = await browser.newContext({viewport: {width, height: 900}, colorScheme: theme});
      for (const e of episodes) browserChecks.push(await checkPage(context, e, width, theme, screenshots));
      siteEntries.push(await checkEntries(context, width)); await context.close();
    }
    const report = {status: 'passed', checkedAtUTC: new Date().toISOString(), executor: 'Codex derive_site agent',
      baseCommit: cp.execFileSync('git', ['rev-parse', 'HEAD'], {cwd: root, encoding: 'utf8'}).trim(), siteVersion, revisionTag: `v${siteVersion}`, originalFirstReleases: Object.fromEntries(episodes.map((e) => [e.slug, e.meta.firstRelease])), retained,
      inputFingerprint: fingerprint,
      build: {command: 'cd site && npm run build', passed: true, runs: 1, reusedForBrowserResume: reuseBuild, htmlFiles: listFiles(dist).filter((f) => f.endsWith('.html')).length, log: path.relative(root, path.join(output, 'build.log'))},
      historicalRegression: {command: 'node site/scripts/check-learning-path.mjs --complete --built', passed: true, runs: 1, log: path.relative(root, path.join(output, 'learning-path.log'))},
      media: episodes.map((e) => ({slug: e.slug, frames: e.frames, fps: e.fps, seconds: e.frames / e.fps, videoSha256: e.videoSha, posterSha256: e.posterSha, productionCanonicalCoverSha256: e.covers, productionCanonicalBuiltAndHTTPIdentical: true, codeCardFromFrame: e.card.from, codeCardFrames: e.card.durationInFrames})),
      browserChecks, siteEntries, screenshots: screenshots.map((f) => ({path: path.relative(root, f), sha256: fileSha(f)})),
      limits: ['Five revised pages were checked at 1440px light and 390px dark; the existing historical regression ran once against the same build. Historical firstRelease and publishedAt values are preserved.',
        'Subtitle text and every serialized cue boundary were checked against the frozen storyboard within 0.001 seconds. Three samples per code card had zero active cues.',
        'Playback/pause checks used about one second of muted code-card playback per page and viewport. This is not full narration listening, ASR, algorithm proof or a beginner learning experiment.',
        'Screenshots and decoded browser frames were captured for review; capturing them alone is not a claim of human visual inspection.',
        'The homepage keeps its six-recent-items rule and original publication dates. All five are reachable through the algorithm direction/library; LC.11 is the algorithm entry lesson. Actual patch Release/changelog and production HTTPS delivery remain the publishing task.']};
    const rows = report.media.map((e) => `| ${e.slug} | ${e.frames} | ${e.seconds.toFixed(3)} | 4 | ${specifications.find((s) => s.slug === e.slug).sentences} | 5 |`).join('\n');
    const releaseWarning = fs.readFileSync(path.join(output, 'build.log'), 'utf8').split(/\r?\n/).filter((line) => line.includes('[changelog]'));
    report.localReleaseFetch = {warnings: releaseWarning, newPatchReleaseNotPublishedDuringLocalQA: true};
    fs.writeFileSync(path.join(__dirname, 'qa-site.json'), JSON.stringify(report, null, 2) + '\n');
    fs.writeFileSync(path.join(__dirname, 'qa-site.md'), `# 五片思路推导修订：网站检查\n\n执行者：${report.executor}；实际检查时间：${report.checkedAtUTC}。结果：通过，修订版本v${siteVersion}。\n\n同一最终站点完成一次构建、一次历史学习路径回归，五页各1440/390两视口共10组实际章节跳转、字幕加载、短暂静音播放与暂停；原首发版本和发布日期保留，updatedAt为${revisionDate}。\n\n| 课程 | 帧数 | 秒数 | 章节 | 精确字幕句数 | 程序卡秒数 |\n| --- | ---: | ---: | ---: | ---: | ---: |\n${rows}\n\n20章共40次实际seek、172句VTT逐句与起止时间、代码卡三个采样零cue、完整程序、源码和媒体完整HTTP SHA均通过。六集算法顺序及五片资料库/系列/RSS入口正确。首页保留原首发日期和最近6条规则；算法方向与入门链接可达，不能声称五片均是首页近期卡。\n\nLC.70全部9个canonical文件逐字节对Git基线${baselineCommit}保持，构建媒体和VTT相同；P01按最新上游基线${upstreamCommit}保留${retained.P01.frames}帧短版及其完整媒体；其余${retained.upstream.canonicalEpisodes.length}个非本任务canonical目录与上游输入保持，已发布媒体在同次构建中逐字节复制。详情见[机器记录](qa-site.json)。\n\n每页每视口仅约1秒静音程序卡播放检查，不声称全片听辨、ASR、算法证明、新手实验或用户认可。截图已捕获，模型实际视觉复核另记范围。构建中的Release抓取提示：${releaseWarning.length ? releaseWarning.join('；') : '未记录失败提示'}。本地不预记新补丁Release/生产更新日志通过；实际Release后HTTPS核验另行完成。\n`);
    console.log(JSON.stringify({status: report.status, report: path.relative(root, path.join(__dirname, 'qa-site.json')), browserCases: browserChecks.length, siteEntries, media: report.media}, null, 2));
  } finally {
    if (browser) await browser.close(); if (preview) preview.kill('SIGTERM');
  }
})().catch((error) => {console.error(error); process.exitCode = 1;});
