// Prepared for final delivery only. No report is produced by --help.
// node docs/climbing-stairs-scene/qa-site.cjs --revision-tag vX.Y.Z --preservation-base SHA
// One build and one historical regression serve both real browser cases.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../..'), site = path.join(root, 'site'), dist = path.join(site, 'dist');
const output = path.join(__dirname, 'site-qa'), slug = 'climbing-stairs';
const initialBase = 'bb9b4e9782ed4b7b2d12a8fac9fd478193febfb8';
const algorithmSlugs = ['container-most-water', 'longest-substring', 'binary-search', 'two-sum', 'reverse-linked-list', slug];
const readJson = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const sha = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');
const fileSha = (file) => sha(fs.readFileSync(file));
const epHref = (name) => `/video-studio/episodes/${name}/`;
const filesIn = (dir) => fs.readdirSync(dir, {withFileTypes: true}).flatMap((e) => e.isDirectory() ? filesIn(path.join(dir, e.name)) : [path.join(dir, e.name)]);
const git = (args, encoding = 'utf8') => cp.execFileSync('git', args, {cwd: root, encoding, maxBuffer: 128 * 1024 * 1024});
const gitBytes = (commit, relative) => git(['show', `${commit}:${relative}`], null);
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function parse(args) {
  const options = {preservationBase: initialBase, revisionDate: '2026-10-25', port: 4207, reuseBuild: false};
  const values = {'--revision-tag': 'revisionTag', '--preservation-base': 'preservationBase', '--revision-date': 'revisionDate', '--port': 'port', '--base': 'base'};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--help') {options.help = true; continue;}
    if (args[i] === '--reuse-build') {options.reuseBuild = true; continue;}
    const equal = args[i].indexOf('='), key = equal < 0 ? args[i] : args[i].slice(0, equal);
    const value = equal < 0 ? args[++i] : args[i].slice(equal + 1);
    assert.ok(values[key] && value, `Unknown or missing argument: ${key}`); options[values[key]] = value;
  }
  if (!options.help) {
    assert.match(options.revisionTag || '', /^v\d+\.\d+\.\d+$/, 'An explicit --revision-tag is required');
    assert.match(options.revisionDate, /^\d{4}-\d{2}-\d{2}$/);
    options.preservationBase = git(['rev-parse', `${options.preservationBase}^{commit}`]).trim();
    options.port = Number(options.port); assert.ok(Number.isInteger(options.port) && options.port > 0);
    options.externalPreview = !!options.base;
    options.base ||= `http://127.0.0.1:${options.port}/video-studio/`;
    const baseURL = new URL(options.base); assert.ok(['http:', 'https:'].includes(baseURL.protocol));
    assert.ok(baseURL.pathname.endsWith('/'), '--base must end with /');
  }
  return options;
}

// Hash actual Git archive bytes, including symlink identity when applicable.
// Ignored local caches in historical canonical directories are not site inputs.
function preservedCanonical(commit) {
  const script = String.raw`
import hashlib,json,os,pathlib,subprocess,sys,tarfile
root=pathlib.Path.cwd(); commit=sys.argv[1]; files={}
p=subprocess.Popen(['git','archive','--format=tar',commit,'episodes'],stdout=subprocess.PIPE)
with tarfile.open(fileobj=p.stdout,mode='r|') as archive:
 for item in archive:
  if item.name.startswith('episodes/climbing-stairs/') or item.isdir(): continue
  if item.issym():
   old=item.linkname.encode(); current=os.readlink(root/item.name).encode()
  else:
   assert item.isfile(),item.name
   old=archive.extractfile(item).read(); current=(root/item.name).read_bytes()
  expected=hashlib.sha256(old).hexdigest()
  assert hashlib.sha256(current).hexdigest()==expected,item.name
  files[item.name]=expected
assert p.wait()==0
print(json.dumps(files,sort_keys=True))
`;
  const files = JSON.parse(cp.execFileSync('python3', ['-c', script, commit], {cwd: root, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024}));
  const extra = git(['ls-files', '--others', '--exclude-standard', '--', 'episodes', ':(exclude)episodes/climbing-stairs']).trim();
  assert.equal(extra, '', 'Non-task canonical files were added');
  const tracked = git(['diff', '--no-ext-diff', '--name-only', commit, '--', 'episodes', ':(exclude)episodes/climbing-stairs']).trim();
  assert.equal(tracked, '', 'Non-task canonical content differs from the chosen main baseline');
  const metadata = Object.keys(files).filter((name) => /^episodes\/[^/]+\/meta\.json$/.test(name));
  const expectedSlugs = metadata.map((name) => name.split('/')[1]).sort();
  const actualSlugs = fs.readdirSync(path.join(root, 'episodes')).filter((name) => name !== slug && fs.existsSync(path.join(root, 'episodes', name, 'meta.json'))).sort();
  assert.deepEqual(actualSlugs, expectedSlugs);
  const retired = ['agent-intro', 'agent-tool-execution'];
  for (const name of retired) {
    assert.equal(fs.existsSync(path.join(root, 'episodes', name, 'meta.json')), false, `Retired ${name} must not be restored`);
    assert.equal(git(['ls-files', '--', `episodes/${name}`, `episodes-codex/${name}`]).trim(), '');
  }
  const retiredProduction = ['agent-intro', 'agent-intro-v2', 'agent-intro-v3', 'agent-tool-execution'];
  for (const name of retiredProduction) assert.equal(git(['ls-files', '--', `episodes-codex/${name}`]).trim(), '', `Retired production ${name} must not be restored`);
  const fiveLeetCodeFullSHA256 = Object.fromEntries(Object.entries(files).filter(([name]) => algorithmSlugs.slice(0, -1).some((s) => name.startsWith(`episodes/${s}/`))));
  assert.ok(algorithmSlugs.slice(0, -1).every((s) => Object.hasOwn(fiveLeetCodeFullSHA256, `episodes/${s}/meta.json`)));
  return {baselineCommit: commit, allCanonicalFilesSHA256: files, fiveLeetCodeFullSHA256, canonicalEpisodes: metadata.map((relative) => readJson(path.join(root, relative))), retiredAgentsRemainAbsent: retired, retiredProductionRemainUntracked: retiredProduction};
}

function cuesFor(storyboard) {
  return storyboard.scenes.flatMap((scene) => scene.shots.flatMap((shot) => shot.subtitles.map((sub) => ({
    text: sub.text, start: (shot.from + sub.from) / storyboard.meta.fps, end: (shot.from + sub.to + 1) / storyboard.meta.fps,
  }))));
}

function finalInputs(options) {
  const canonical = path.join(root, 'episodes', slug), production = path.join(root, 'episodes-codex', slug);
  const meta = readJson(path.join(canonical, 'meta.json')), sb = readJson(path.join(canonical, 'storyboard.json'));
  const original = JSON.parse(gitBytes(options.preservationBase, `episodes/${slug}/meta.json`));
  const originalSB = JSON.parse(gitBytes(options.preservationBase, `episodes/${slug}/storyboard.json`));
  for (const key of ['slug', 'ep', 'problemNumber', 'title', 'series', 'publishedAt', 'firstRelease', 'sourcePath', 'platforms']) assert.deepEqual(meta[key], original[key], `Historical ${key} changed`);
  assert.equal(meta.firstRelease, 'v0.57.0'); assert.equal(meta.publishedAt, '2026-10-25'); assert.equal(meta.updatedAt, options.revisionDate);
  assert.equal(meta.draft, false); assert.equal(meta.problemNumber, 70); assert.equal(meta.series, 'leetcode');
  assert.equal(meta.sourcePath, 'episodes-codex/climbing-stairs/remotion');
  assert.equal(`v${readJson(path.join(site, 'package.json')).version}`, options.revisionTag, 'Build the explicit revision, not another package version');
  assert.notEqual(meta.firstRelease, options.revisionTag);
  assert.equal(meta.finalVideoFrames, 4779); assert.equal(sb.meta.finalVideoFrames, 4779); assert.equal(sb.meta.fps, 30);
  const card = sb.meta.unvoicedEndCard; assert.equal(card.durationInFrames, 150); assert.equal(card.from + 150, 4779);
  const cues = cuesFor(sb); assert.equal(cues.length, 24); assert.deepEqual(cues, cuesFor(originalSB), 'The 24 original narration cues and their timing must be retained');
  assert.ok(cues.every((cue) => cue.end <= card.from / 30));
  const chapters = sb.scenes.map((scene) => ({id: scene.chapterId, start: scene.from / 30}));
  assert.equal(chapters.length, 4); assert.equal(new Set(chapters.map((c) => c.id)).size, 4);
  for (const chapter of chapters) assert.match(chapter.id, /^[a-z][a-z0-9-]*$/);
  for (const name of ['article.mdx', 'script.md', 'storyboard.json', meta.video, 'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg']) assert.equal(fileSha(path.join(canonical, name)), fileSha(path.join(production, name)), `Stale canonical ${name}`);
  for (const item of fs.readdirSync(canonical, {withFileTypes: true})) {
    assert.equal(item.isDirectory(), false, 'Production code must not be copied into canonical');
    assert.ok(!/\.(?:wav|png|tsx?|jsx?)$/i.test(item.name), `Production artifact in canonical: ${item.name}`);
  }
  const videoSha256 = fileSha(path.join(canonical, meta.video)), posterSha256 = fileSha(path.join(canonical, meta.poster));
  assert.notEqual(videoSha256, sha(gitBytes(options.preservationBase, `episodes/${slug}/${original.video}`)), 'The old video is not a final stair-scene revision');
  assert.notEqual(posterSha256, sha(gitBytes(options.preservationBase, `episodes/${slug}/${original.poster}`)), 'The final stair-scene poster has not been delivered');
  const rendered = readJson(path.join(production, 'render-result.json'));
  assert.equal(rendered.sha256, videoSha256); assert.equal(rendered.frames, 4779); assert.equal(rendered.bytes, fs.statSync(path.join(canonical, meta.video)).size);
  assert.ok(Math.abs(rendered.finalLUFS + 16) <= .3); assert.ok(rendered.truePeakDBTP <= -2);
  const frozen = readJson(path.join(production, 'source-sha256.json'));
  for (const [relative, expected] of Object.entries(frozen)) assert.equal(fileSha(path.resolve(production, relative)), expected, `Frozen input changed: ${relative}`);
  const retainedInputs = Object.fromEntries(['voice.wav', 'solution.py'].map((name) => {
    const digest = fileSha(path.join(production, name)); assert.equal(digest, sha(gitBytes(options.preservationBase, `episodes-codex/${slug}/${name}`))); return [name, digest];
  }));
  return {slug, canonical, production, meta, storyboard: sb, fps: 30, frames: 4779, card, cues, chapters, videoSha256, posterSha256, retainedInputs,
    displayDuration: '2:39', expectedSource: `https://github.com/linhongcun/video-studio/tree/main/${meta.sourcePath}`,
    covers: Object.fromEntries(['16x9', '4x3', '3x4'].map((ratio) => [`cover-${ratio}.jpg`, fileSha(path.join(canonical, `cover-${ratio}.jpg`))]))};
}

const fingerprintFiles = (files) => sha([...new Set(files)].sort().map((file) => `${path.relative(root, file)}\0${fileSha(file)}`).join('\n'));
function inputFingerprint(e) {
  const canonical = git(['ls-files', '--cached', '--others', '--exclude-standard', '--', 'episodes']).trim().split(/\r?\n/).filter(Boolean).map((name) => path.join(root, name));
  // The QA harness is not a build input: a harness-only fix may reuse the same
  // unchanged output; actual site inputs and complete dist still must match.
  return fingerprintFiles([...filesIn(path.join(site, 'src')), ...filesIn(path.join(site, 'scripts')),
    ...fs.readdirSync(site, {withFileTypes: true}).filter((x) => x.isFile()).map((x) => path.join(site, x.name)),
    ...canonical, ...['solution.py', 'episode-config.json', 'render-result.json', 'source-sha256.json'].map((name) => path.join(e.production, name))]);
}
function runLogged(command, args, cwd, file) {
  const result = cp.spawnSync(command, args, {cwd, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024});
  fs.writeFileSync(file, `${result.stdout || ''}${result.stderr || ''}`);
  if (result.error) throw result.error; assert.equal(result.status, 0, `Failed ${command}; see ${file}`);
}
function parseVtt(bytes) {
  const blocks = bytes.toString('utf8').trim().split(/\r?\n\s*\r?\n/); assert.equal(blocks.shift(), 'WEBVTT');
  const seconds = (stamp) => stamp.split(':').reduce((total, n) => total * 60 + Number(n), 0);
  return blocks.map((block) => {const lines = block.split(/\r?\n/), match = /^(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)$/.exec(lines[0]); assert.ok(match); return {start: seconds(match[1]), end: seconds(match[2]), text: lines.slice(1).join('\n')};});
}
async function seek(page, seconds) {
  await page.locator('video').evaluate((v, time) => {v.pause(); v.currentTime = time;}, seconds);
  await page.waitForFunction((time) => {const v = document.querySelector('video'); return !v.seeking && v.readyState >= 2 && Math.abs(v.currentTime - time) < .1;}, seconds);
}
async function playTo(page, target) {
  return page.locator('video').evaluate(async (v, target) => {
    const beforeTime = v.currentTime; if (target - beforeTime < .5) throw Error('At least .5s of real playback required');
    v.muted = true; v.playbackRate = 1; const started = performance.now(); let playingEvent = false, callbacks = 0, timeUpdates = 0, callback, done = false;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => finish(Error('Playback timed out')), 25000);
      const playing = () => {playingEvent = true;}, timeupdate = () => {timeUpdates++;}, error = () => finish(Error(v.error?.message || 'Media error'));
      function finish(error) {
        if (done) return; done = true;
        clearTimeout(timer); v.pause(); if (callback && v.cancelVideoFrameCallback) v.cancelVideoFrameCallback(callback);
        v.removeEventListener('playing', playing); v.removeEventListener('timeupdate', timeupdate); v.removeEventListener('error', error);
        const result = {beforeTime, afterTime: v.currentTime, advancedSeconds: v.currentTime - beforeTime, wallMilliseconds: performance.now() - started, playingEvent, videoFrameCallbacks: callbacks, timeUpdates, paused: v.paused, muted: v.muted, mediaError: v.error?.message ?? null};
        if (error) reject(error); else resolve(result);
      }
      function tick() {if (done) return; if (v.requestVideoFrameCallback) callbacks++; if (playingEvent && !v.paused && v.currentTime >= target) finish(); else if (v.requestVideoFrameCallback) callback = v.requestVideoFrameCallback(tick); else requestAnimationFrame(tick);}
      v.addEventListener('playing', playing); v.addEventListener('timeupdate', timeupdate); v.addEventListener('error', error);
      if (v.requestVideoFrameCallback) callback = v.requestVideoFrameCallback(tick); else requestAnimationFrame(tick);
      v.play().catch(finish);
    });
  }, target);
}
async function capture(page, width, theme, name, screenshots) {
  await page.evaluate(() => scrollTo({top: 0, left: 0, behavior: 'instant'}));
  await page.waitForFunction(() => !document.querySelector('#player .vwrap').classList.contains('stuck'));
  const screenshot = path.join(output, `${slug}-${name}-${width}-${theme}.png`); await page.screenshot({path: screenshot}); screenshots.push(screenshot);
  const frame = path.join(output, `${slug}-${name}-decoded-${width}.png`);
  const bytes = await page.locator('video').evaluate((v) => {const c = document.createElement('canvas'); c.width = v.videoWidth; c.height = v.videoHeight; c.getContext('2d').drawImage(v, 0, 0); return c.toDataURL('image/png').split(',')[1];});
  fs.writeFileSync(frame, Buffer.from(bytes, 'base64')); screenshots.push(frame);
  return {screenshot: path.relative(root, screenshot), decodedFrame: path.relative(root, frame), actualCaptureTime: await page.locator('video').evaluate((v) => v.currentTime)};
}
async function checkPage(context, e, width, theme, options, screenshots) {
  const page = await context.newPage(), errors = []; page.on('pageerror', (error) => errors.push(error.message));
  const response = await page.goto(new URL(`episodes/${slug}/`, options.base).href, {waitUntil: 'networkidle'}); assert.equal(response.status(), 200);
  await page.evaluate(() => document.fonts.ready); assert.equal(await page.locator('h1').innerText(), e.meta.title);
  assert.ok((await page.locator('footer').innerText()).includes(options.revisionTag)); assert.ok((await page.locator('.eh .meta').innerText()).includes(e.displayDuration));
  assert.ok(await page.getByText('LC.70', {exact: false}).count() > 0); assert.equal(await page.locator('.pl').count(), 0);
  assert.ok(await page.locator(`a[href="${e.expectedSource}"]`).count() > 0);
  assert.ok((await page.locator('article pre').allTextContents()).some((code) => code.trim() === fs.readFileSync(path.join(e.production, 'solution.py'), 'utf8').trim()));
  assert.deepEqual(await page.locator('.pager a').evaluateAll((links) => links.map((a) => a.getAttribute('href'))), [epHref('reverse-linked-list')]);
  const video = page.locator('video'); await video.evaluate((v) => {v.muted = true;}); await page.waitForFunction(() => document.querySelector('video').readyState >= 1);
  const media = await video.evaluate((v) => ({duration: v.duration, controls: v.controls, width: v.videoWidth, height: v.videoHeight, defaultCaptionModes: [...v.textTracks].map((t) => t.mode)}));
  assert.ok(media.controls && Math.abs(media.duration - e.frames / e.fps) < .1); assert.deepEqual([media.width, media.height], [1920, 1080]);
  const chapters = await page.locator('#player').evaluate((el) => JSON.parse(el.dataset.chapters));
  assert.deepEqual(chapters.map(({id, start}) => ({id, start})), e.chapters);
  const seeks = [];
  for (const chapter of chapters) {
    assert.ok(await page.locator(`article #${chapter.id}`).count() > 0);
    const selector = `#player ${width < 768 ? '.chip' : '.ch'}[data-id="${chapter.id}"]`;
    await page.locator(selector).click(); await video.evaluate((v) => v.pause());
    await page.waitForFunction((time) => {const v = document.querySelector('video'); return !v.seeking && Math.abs(v.currentTime - time) < .7;}, chapter.start);
    assert.equal(await page.locator(selector).getAttribute('aria-current'), 'true'); seeks.push({id: chapter.id, expected: chapter.start, actual: await video.evaluate((v) => v.currentTime)});
  }
  const responseVtt = await context.request.get(new URL(`episodes/${slug}/captions.vtt`, options.base).href); assert.equal(responseVtt.status(), 200);
  const vtt = await responseVtt.body(), cues = parseVtt(vtt); assert.equal(cues.length, 24); assert.deepEqual(cues.map((c) => c.text), e.cues.map((c) => c.text));
  for (let i = 0; i < cues.length; i++) for (const key of ['start', 'end']) assert.ok(Math.abs(cues[i][key] - e.cues[i][key]) < .001);
  assert.equal(sha(vtt), fileSha(path.join(dist, 'episodes', slug, 'captions.vtt')));
  assert.ok(cues.every((c) => c.end <= e.card.from / 30));
  const httpMedia = [];
  if (width === 1440) for (const [name, expected] of [[e.meta.video, e.videoSha256], [e.meta.poster, e.posterSha256]]) {
    const asset = await context.request.get(new URL(`episodes/${slug}/${name}`, options.base).href); assert.equal(asset.status(), 200);
    const body = await asset.body(); assert.equal(sha(body), expected); httpMedia.push({name, status: 200, bytes: body.length, sha256: sha(body)});
  }
  await video.evaluate((v) => {v.textTracks[0].mode = 'showing';}); await seek(page, (cues[0].start + cues[0].end) / 2);
  await page.waitForFunction(() => {const v = document.querySelector('video'); return document.querySelector('track').readyState === 2 && v.textTracks[0].cues?.length === 24 && v.textTracks[0].activeCues?.length > 0;});
  const narratedCC = await video.evaluate((v) => ({time: v.currentTime, cues: v.textTracks[0].cues.length, activeCues: v.textTracks[0].activeCues.length}));
  await video.evaluate((v, modes) => { [...v.textTracks].forEach((t, i) => {t.mode = modes[i];}); }, media.defaultCaptionModes);
  await seek(page, 0); const openingPlayback = await playTo(page, 4); assert.ok(openingPlayback.playingEvent && openingPlayback.advancedSeconds >= .5 && openingPlayback.paused && !openingPlayback.mediaError);
  const opening = await capture(page, width, theme, 'staircase-opening', screenshots);
  await video.evaluate((v) => {v.textTracks[0].mode = 'showing';}); const silentSamples = [];
  for (const offset of [.1, 2.5, 4.8]) {await seek(page, e.card.from / 30 + offset); assert.equal(await video.evaluate((v) => v.textTracks[0].activeCues.length), 0); silentSamples.push({time: await video.evaluate((v) => v.currentTime), activeCues: 0});}
  await seek(page, e.card.from / 30 + 1); const cardPlayback = await playTo(page, e.card.from / 30 + 2);
  assert.ok(cardPlayback.playingEvent && cardPlayback.advancedSeconds >= .5 && cardPlayback.paused && !cardPlayback.mediaError); assert.equal(await video.evaluate((v) => v.textTracks[0].activeCues.length), 0);
  await video.evaluate((v, modes) => {[...v.textTracks].forEach((t, i) => {t.mode = modes[i];});}, media.defaultCaptionModes);
  const codeCard = await capture(page, width, theme, 'complete-python', screenshots);
  const overflow = await page.evaluate(() => ({scrollWidth: document.documentElement.scrollWidth, bodyScrollWidth: document.body.scrollWidth}));
  assert.ok(overflow.scrollWidth <= width && overflow.bodyScrollWidth <= width); assert.deepEqual(errors, []); await page.close();
  return {slug, width, theme, httpStatus: response.status(), media, chapters, seeks, httpMedia, captions: {count: 24, sha256: sha(vtt), exactTextAndFrameTiming: true, narratedCC, silentSamples}, openingPlayback, opening, cardPlayback, codeCard, overflow, errors};
}

async function checkEntries(context, options) {
  const page = await context.newPage(), expected = algorithmSlugs.map(epHref); await page.goto(options.base, {waitUntil: 'networkidle'});
  assert.ok(await page.locator('a.track-algorithms[href="/video-studio/learn/#algorithms"]').count() > 0);
  assert.ok(await page.locator(`a.start-link[href="${epHref('container-most-water')}"]`).count() > 0);
  await page.goto(new URL('learn/', options.base).href, {waitUntil: 'networkidle'}); assert.equal(await page.locator('#algorithms').count(), 1); assert.ok(await page.locator('a[href="/video-studio/series/leetcode/"]').count() > 0);
  await page.goto(new URL('series/leetcode/', options.base).href, {waitUntil: 'networkidle'});
  assert.deepEqual(await page.locator('.lesson-list a.lesson').evaluateAll((links) => links.map((a) => a.getAttribute('href'))), expected);
  assert.ok((await page.locator('.course-count').innerText()).includes('已发布 6 篇'));
  await page.goto(new URL('library/?series=leetcode&sort=learning', options.base).href, {waitUntil: 'networkidle'});
  await page.waitForFunction(() => [...document.querySelectorAll('#library-grid li')].filter((el) => getComputedStyle(el).display !== 'none').length === 6);
  assert.deepEqual(await page.locator('#library-grid li:visible a.card').evaluateAll((links) => links.map((a) => a.getAttribute('href'))), expected);
  const rss = await context.request.get(new URL('rss.xml', options.base).href); assert.equal(rss.status(), 200);
  assert.ok(((await rss.text()).match(/<item>[\s\S]*?<\/item>/g) || []).some((item) => item.includes('/episodes/climbing-stairs/') && item.includes('LC.70')));
  await page.close(); return {algorithmDirection: true, learningEntry: true, seriesHrefs: expected, libraryHrefs: expected, rssLC70: true};
}

async function run(options) {
  const e = finalInputs(options), retained = preservedCanonical(options.preservationBase); fs.mkdirSync(output, {recursive: true});
  const input = inputFingerprint(e), receiptPath = path.join(output, 'build-receipt.json');
  if (options.reuseBuild) {
    const receipt = readJson(receiptPath); assert.equal(receipt.inputFingerprint, input); assert.equal(receipt.distFingerprint, fingerprintFiles(filesIn(dist))); assert.ok(receipt.buildPassed && receipt.regressionPassed);
  } else {
    runLogged('npm', ['run', 'build'], site, path.join(output, 'build.log'));
    runLogged('node', ['site/scripts/check-learning-path.mjs', '--complete', '--built'], root, path.join(output, 'learning-path.log'));
    fs.writeFileSync(receiptPath, JSON.stringify({revisionTag: options.revisionTag, preservationBaseline: options.preservationBase, inputFingerprint: input, distFingerprint: fingerprintFiles(filesIn(dist)), checkedAtUTC: new Date().toISOString(), buildPassed: true, regressionPassed: true}, null, 2) + '\n');
  }
  for (const [name, expected] of [[e.meta.video, e.videoSha256], [e.meta.poster, e.posterSha256]]) assert.equal(fileSha(path.join(dist, 'episodes', slug, name)), expected);
  retained.builtMedia = retained.canonicalEpisodes.filter((meta) => !meta.draft).map((meta) => ({slug: meta.slug, files: [meta.video, meta.poster].filter(Boolean).map((name) => {
    const relative = `episodes/${meta.slug}/${name}`, expected = retained.allCanonicalFilesSHA256[relative]; assert.equal(fileSha(path.join(dist, relative)), expected); return {name, sha256: expected};
  })}));
  const preview = options.externalPreview ? null : cp.spawn(process.execPath, [path.join(site, 'node_modules/astro/astro.js'), 'preview', '--host', '127.0.0.1', '--port', String(options.port)], {cwd: site, stdio: 'ignore'});
  let browser; const browserChecks = [], siteEntries = [], screenshots = [];
  try {
    for (let i = 0; i < 100; i++) {try {if ((await fetch(options.base)).ok) break;} catch {} assert.ok(i < 99, 'Preview did not start'); await sleep(200);}
    const {chromium} = require('playwright'); browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium', args: ['--no-sandbox', '--disable-dev-shm-usage']});
    for (const [width, theme] of [[1440, 'light'], [390, 'dark']]) {
      const context = await browser.newContext({viewport: {width, height: 900}, colorScheme: theme}); browserChecks.push(await checkPage(context, e, width, theme, options, screenshots)); siteEntries.push({width, ...await checkEntries(context, options)}); await context.close();
    }
    const releaseWarnings = fs.readFileSync(path.join(output, 'build.log'), 'utf8').split(/\r?\n/).filter((line) => line.includes('[changelog]'));
    const report = {status: 'passed', checkedAtUTC: new Date().toISOString(), executor: 'Codex derive_site agent', revisionTag: options.revisionTag, preservationBaseline: options.preservationBase, revisionDate: options.revisionDate,
      checkoutHeadAtRun: git(['rev-parse', 'HEAD']).trim(), helperSha256: fileSha(__filename), inputFingerprint: input,
      build: {passed: true, runs: 1, reusedForBrowserResume: options.reuseBuild, log: 'docs/climbing-stairs-scene/site-qa/build.log'}, historicalRegression: {passed: true, runs: 1, log: 'docs/climbing-stairs-scene/site-qa/learning-path.log'},
      media: [{slug, frames: 4779, fps: 30, videoSha256: e.videoSha256, posterSha256: e.posterSha256, coverSha256: e.covers, cardFrames: 150, cardFrom: e.card.from, retainedInputs: e.retainedInputs}], retained, browserChecks, siteEntries,
      screenshots: screenshots.map((file) => ({path: path.relative(root, file), sha256: fileSha(file)})), actualScreenshotReviewPending: true,
      localReleaseFetch: {warnings: releaseWarnings, newPatchChangelogRequiresPostReleaseVerification: true},
      limits: ['Two actual browser viewports, eight chapter clicks/seeks, 24 exact VTT cues, native CC activation, real muted opening playback to about 4s and about 1s card playback per viewport. This is not full-video listening or ASR.', 'Screenshots and actual browser-decoded frames were captured; model visual inspection must be recorded separately after viewing.', 'Other canonical tracked files and all five other LeetCode file SHA identities are preserved; no assumption is made about their untracked production MP4s.', 'Historical firstRelease/publishedAt are retained. Release-specific changelog and real production delivery are checked only after publishing with explicit revision/deployment identity.']};
    fs.writeFileSync(path.join(__dirname, 'qa-site.json'), JSON.stringify(report, null, 2) + '\n');
    fs.writeFileSync(path.join(__dirname, 'qa-site.md'), `# LC.70 楼梯场景：网站检查\n\n实际检查：${report.checkedAtUTC}；版本${options.revisionTag}，结果通过。一次构建和一次历史回归；1440亮色/390暗色两组，四章共8次真实点击/seek。24句VTT逐字与帧时一致，原生CC实际激活后恢复默认状态；每视口实际播放开头约4秒、程序卡约1秒再暂停。150帧/5秒程序卡三个位置无cue，源码和完整Python正文正确，完整MP4/海报HTTP SHA一致，三尺寸封面canonical与production一致。\n\n其他5条LeetCode全部canonical文件SHA与${options.preservationBase}保持，其他当前canonical与同一基线相同；已发布媒体在同次构建中逐字节复制，撤下的两条Agent未恢复。首页算法方向、学习页、六片系列、资料库与RSS可达。首发v0.57.0和发布日期保留。\n\n截图/浏览器解码帧已捕获，实际模型视觉复核尚待另记。构建Release提示：${releaseWarnings.length ? releaseWarnings.join('；') : '未记录失败提示'}。本地不预记新补丁线上changelog通过，不声称全片听辨、ASR或观众学习效果。详情见[机器记录](qa-site.json)。\n`);
    console.log(JSON.stringify({status: report.status, revisionTag: options.revisionTag, browserCases: browserChecks.length, seeks: browserChecks.reduce((n, row) => n + row.seeks.length, 0), report: 'docs/climbing-stairs-scene/qa-site.json'}, null, 2));
    return report;
  } finally {if (browser) await browser.close(); if (preview) preview.kill('SIGTERM');}
}

module.exports = {parse, preservedCanonical, finalInputs, run};
if (require.main === module) {
  const options = parse(process.argv.slice(2));
  if (options.help) console.log('Only after final-media approval: node qa-site.cjs --revision-tag vX.Y.Z [--preservation-base SHA] [--revision-date YYYY-MM-DD] [--port 4207 | --base URL] [--reuse-build]. No npm ci. A harness-only fix may reuse a matching build receipt.');
  else run(options).catch((error) => {console.error(error); process.exitCode = 1;});
}
