// Prepared for final delivery only. No report is produced by --help.
// node docs/number-of-islands-boundaries/qa-site.cjs --revision-tag vX.Y.Z --preservation-base SHA
// One build and one historical regression serve both real browser cases.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../..'), site = path.join(root, 'site'), dist = path.join(site, 'dist');
const output = path.join(__dirname, 'site-qa'), slug = 'number-of-islands';
const algorithmSlugs = ['container-most-water', 'longest-substring', 'binary-search', 'two-sum', 'reverse-linked-list', 'climbing-stairs', slug];
const readJson = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const sha = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');
const fileSha = (file) => sha(fs.readFileSync(file));
const epHref = (name) => `/video-studio/episodes/${name}/`;
const filesIn = (dir) => fs.readdirSync(dir, {withFileTypes: true}).flatMap((e) => e.isDirectory() ? filesIn(path.join(dir, e.name)) : [path.join(dir, e.name)]);
const git = (args, encoding = 'utf8') => cp.execFileSync('git', args, {cwd: root, encoding, maxBuffer: 128 * 1024 * 1024});
const gitBytes = (commit, relative) => git(['show', `${commit}:${relative}`], null);
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function parse(args) {
  const options = {revisionDate: '2026-10-25', port: 4227, reuseBuild: false};
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
    assert.ok(options.preservationBase, 'An explicit --preservation-base is required');
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
  if item.name.startswith('episodes/number-of-islands/') or item.isdir(): continue
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
  const extra = git(['ls-files', '--others', '--exclude-standard', '--', 'episodes', ':(exclude)episodes/number-of-islands']).trim();
  assert.equal(extra, '', 'Non-task canonical files were added');
  const tracked = git(['diff', '--no-ext-diff', '--name-only', commit, '--', 'episodes', ':(exclude)episodes/number-of-islands']).trim();
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
  const sixLeetCodeFullSHA256 = Object.fromEntries(Object.entries(files).filter(([name]) => algorithmSlugs.slice(0, -1).some((s) => name.startsWith(`episodes/${s}/`))));
  assert.ok(algorithmSlugs.slice(0, -1).every((s) => Object.hasOwn(sixLeetCodeFullSHA256, `episodes/${s}/meta.json`)));
  for (const current of ['monty-hall', 'agent-skills', 'adapter-pattern']) assert.ok(Object.hasOwn(files, `episodes/${current}/meta.json`), `Published ${current} must remain`);
  return {baselineCommit: commit, allCanonicalFilesSHA256: files, sixLeetCodeFullSHA256, canonicalEpisodes: metadata.map((relative) => readJson(path.join(root, relative))), retiredAgentsRemainAbsent: retired, retiredProductionRemainUntracked: retiredProduction};
}

function cuesFor(storyboard) {
  return storyboard.scenes.flatMap((scene) => scene.shots.flatMap((shot) => shot.subtitles.map((sub) => ({
    text: sub.text, start: (shot.from + sub.from) / storyboard.meta.fps, end: (shot.from + sub.to + 1) / storyboard.meta.fps,
  }))));
}
function chaptersFor(storyboard) {
  return storyboard.scenes.reduce((chapters, scene) => {
    if (chapters.at(-1)?.id !== scene.chapterId) chapters.push({id: scene.chapterId, start: scene.from / storyboard.meta.fps});
    return chapters;
  }, []);
}

function finalInputs(options) {
  const canonical = path.join(root, 'episodes', slug), production = path.join(root, 'episodes-codex', slug);
  const meta = readJson(path.join(canonical, 'meta.json')), sb = readJson(path.join(canonical, 'storyboard.json'));
  const config = readJson(path.join(production, 'episode-config.json')); assert.equal(meta.title, config.title);
  const original = JSON.parse(gitBytes(options.preservationBase, `episodes/${slug}/meta.json`));
  assert.equal(original.draft, false, 'This revision requires the already-published LC.200 baseline');
  for (const key of ['slug', 'ep', 'problemNumber', 'firstRelease', 'publishedAt', 'sourcePath']) assert.deepEqual(meta[key], original[key], `Published identity changed: ${key}`);
  assert.equal(meta.ep, 34); assert.equal(meta.problemNumber, 200); assert.equal(meta.firstRelease, 'v0.66.0');
  assert.notEqual(meta.firstRelease, options.revisionTag); assert.equal(meta.updatedAt, options.revisionDate);
  assert.equal(meta.draft, false); assert.equal(meta.problemNumber, 200); assert.equal(meta.series, 'leetcode');
  assert.equal(meta.sourcePath, 'episodes-codex/number-of-islands/remotion');
  assert.equal(`v${readJson(path.join(site, 'package.json')).version}`, options.revisionTag, 'Build the explicit revision identity');
  const fps = sb.meta.fps, frames = sb.meta.finalVideoFrames;
  assert.equal(fps, 30); assert.ok(Number.isInteger(frames) && frames > 150, 'Real finalized frame count is required'); assert.equal(meta.finalVideoFrames, frames);
  const card = sb.meta.unvoicedEndCard; assert.equal(card.durationInFrames, 150); assert.equal(card.from + 150, frames);
  const cues = cuesFor(sb); assert.ok(cues.length > 0 && cues.every((cue) => cue.end > cue.start && cue.end <= card.from / fps));
  const narrationLines = [...fs.readFileSync(path.join(production, 'script.md'), 'utf8').matchAll(/^旁白：(.+)$/gm)].map((match) => match[1].trim());
  const scriptSentences = narrationLines.flatMap((line) => line.match(/[^。！？]+[。！？]?/gu) || []);
  assert.ok(scriptSentences.length > 0); assert.equal(cues.length, scriptSentences.length, 'VTT must contain every scripted narration sentence');
  assert.equal(cues.map((cue) => cue.text).join('').replace(/\s/g, ''), scriptSentences.join('').replace(/\s/g, ''), 'Storyboard must retain all scripted narration');
  const chapters = chaptersFor(sb);
  assert.equal(chapters.length, 4); assert.equal(new Set(chapters.map((c) => c.id)).size, 4);
  for (const chapter of chapters) assert.match(chapter.id, /^[a-z][a-z0-9-]*$/);
  for (const name of ['article.mdx', 'script.md', 'storyboard.json', meta.video, 'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg']) assert.equal(fileSha(path.join(canonical, name)), fileSha(path.join(production, name)), `Stale canonical ${name}`);
  for (const item of fs.readdirSync(canonical, {withFileTypes: true})) {
    assert.equal(item.isDirectory(), false, 'Production code must not be copied into canonical');
    assert.ok(!/\.(?:wav|png|tsx?|jsx?)$/i.test(item.name), `Production artifact in canonical: ${item.name}`);
  }
  const videoSha256 = fileSha(path.join(canonical, meta.video)), posterSha256 = fileSha(path.join(canonical, meta.poster));
  assert.notEqual(videoSha256, sha(gitBytes(options.preservationBase, `episodes/${slug}/${meta.video}`)), 'The revised final movie has not been delivered');
  for (const name of ['cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg']) assert.equal(fileSha(path.join(canonical, name)), sha(gitBytes(options.preservationBase, `episodes/${slug}/${name}`)), `Unchanged cover was modified: ${name}`);
  for (const name of ['solution.py', 'solution.json', 'research/demo-trace.json']) assert.equal(fileSha(path.join(production, name)), sha(gitBytes(options.preservationBase, `episodes-codex/${slug}/${name}`)), `Preserved program/trace changed: ${name}`);
  const rendered = readJson(path.join(production, 'render-result.json'));
  assert.equal(rendered.sha256, videoSha256); assert.equal(rendered.frames, frames); assert.equal(rendered.bytes, fs.statSync(path.join(canonical, meta.video)).size);
  assert.ok(Math.abs(rendered.finalLUFS + 16) <= .3); assert.ok(rendered.truePeakDBTP <= -2);
  const frozen = readJson(path.join(production, 'source-sha256.json'));
  for (const [relative, expected] of Object.entries(frozen)) assert.equal(fileSha(path.resolve(production, relative)), expected, `Frozen input changed: ${relative}`);
  const solution = fs.readFileSync(path.join(production, 'solution.py'), 'utf8').trim();
  assert.equal(readJson(path.join(production, 'solution.json')).lines.join('\n').trim(), solution, 'Displayed full card and executed Python must agree');
  const productionInputs = Object.fromEntries(['voice.wav', 'solution.py', 'solution.json'].map((name) => [name, fileSha(path.join(production, name))]));
  const revisedShot = sb.scenes.flatMap((scene) => scene.shots).find((shot) => /^06(?:-|$)/.test(String(shot.id)));
  assert.ok(revisedShot?.subtitles?.[1], 'Shot06 second sentence must be present');
  const boundaryCue = {start: (revisedShot.from + revisedShot.subtitles[1].from) / fps, end: (revisedShot.from + revisedShot.subtitles[1].to + 1) / fps};
  return {slug, canonical, production, meta, storyboard: sb, fps, frames, card, cues, chapters, videoSha256, posterSha256, productionInputs, boundaryCue,
    productionInternalEp: config.episode, publishedInternalEp: meta.ep,
    displayDuration: `${Math.floor(frames / fps / 60)}:${String(Math.floor(frames / fps % 60)).padStart(2, '0')}`,
    expectedSource: `https://github.com/linhongcun/video-studio/tree/main/${meta.sourcePath}`,
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
  await page.evaluate(() => document.fonts.ready); assert.equal(await page.locator('.eh h1').innerText(), e.meta.title);
  assert.ok((await page.locator('footer').innerText()).includes(options.revisionTag)); assert.ok((await page.locator('.eh .meta').innerText()).includes(e.displayDuration));
  assert.ok(await page.getByText('LC.200', {exact: false}).count() > 0); assert.equal(await page.locator('.pl').count(), 0);
  assert.ok(await page.locator(`a[href="${e.expectedSource}"]`).count() > 0);
  assert.ok((await page.locator('article pre').allTextContents()).some((code) => code.trim() === fs.readFileSync(path.join(e.production, 'solution.py'), 'utf8').trim()));
  assert.deepEqual(await page.locator('.pager a').evaluateAll((links) => links.map((a) => a.getAttribute('href'))), [epHref('climbing-stairs')]);
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
  const vtt = await responseVtt.body(), cues = parseVtt(vtt); assert.equal(cues.length, e.cues.length); assert.deepEqual(cues.map((c) => c.text), e.cues.map((c) => c.text));
  for (let i = 0; i < cues.length; i++) for (const key of ['start', 'end']) assert.ok(Math.abs(cues[i][key] - e.cues[i][key]) < .001);
  assert.equal(sha(vtt), fileSha(path.join(dist, 'episodes', slug, 'captions.vtt')));
  assert.ok(cues.every((c) => c.end <= e.card.from / e.fps), 'Serialized cues must not extend into the code card');
  const httpMedia = [];
  if (width === 1440) for (const [name, expected] of [[e.meta.video, e.videoSha256], [e.meta.poster, e.posterSha256]]) {
    const asset = await context.request.get(new URL(`episodes/${slug}/${name}`, options.base).href); assert.equal(asset.status(), 200);
    const body = await asset.body(); assert.equal(sha(body), expected); httpMedia.push({name, status: 200, bytes: body.length, sha256: sha(body)});
  }
  await video.evaluate((v) => {v.textTracks[0].mode = 'showing';}); await seek(page, (cues[0].start + cues[0].end) / 2);
  await page.waitForFunction((count) => {const v = document.querySelector('video'); return document.querySelector('track').readyState === 2 && v.textTracks[0].cues?.length === count && v.textTracks[0].activeCues?.length > 0;}, e.cues.length);
  const narratedCC = await video.evaluate((v) => ({time: v.currentTime, cues: v.textTracks[0].cues.length, activeCues: v.textTracks[0].activeCues.length}));
  await video.evaluate((v, modes) => { [...v.textTracks].forEach((t, i) => {t.mode = modes[i];}); }, media.defaultCaptionModes);
  const boundaryPlayback = [], boundaryScene = [];
  // Exact samples supplied from this frozen MP4: left event2418..2465,
  // upper event2466..2513. Pause after real playback inside both windows.
  for (const [name, frame] of [['left', 2441], ['upper', 2489]]) {
    const target = frame / e.fps; assert.ok(target > e.boundaryCue.start && target < e.boundaryCue.end);
    await seek(page, Math.max(e.boundaryCue.start, target - 1)); const playback = await playTo(page, target);
    assert.ok(playback.playingEvent && playback.advancedSeconds >= .5 && playback.paused && !playback.mediaError);
    boundaryPlayback.push({name, requestedFrame: frame, ...playback});
    boundaryScene.push({name, requestedFrame: frame, ...await capture(page, width, theme, `boundaries-shot06-${name}`, screenshots)});
  }
  await video.evaluate((v) => {v.textTracks[0].mode = 'showing';}); const silentSamples = [];
  for (const offset of [0, .0001, .1, 2.5, 4.8]) {
    const requested = e.card.from / e.fps + offset; await seek(page, requested);
    await page.evaluate(() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    const sample = await video.evaluate((v, requested) => ({requested, currentTime: v.currentTime, activeCues: v.textTracks[0].activeCues.length,
      cues: [...v.textTracks[0].activeCues].map((cue) => ({text: cue.text, start: cue.startTime, end: cue.endTime}))}), requested);
    silentSamples.push(sample);
    fs.writeFileSync(path.join(output, `native-card-boundary-${width}.json`), JSON.stringify({width, exactCardStart: e.card.from / e.fps, samples: silentSamples}, null, 2) + '\n');
    assert.equal(sample.activeCues, 0, `Native CC remains active at ${requested}`);
  }
  await seek(page, e.card.from / e.fps + 1); const cardPlayback = await playTo(page, e.card.from / e.fps + 2);
  assert.ok(cardPlayback.playingEvent && cardPlayback.advancedSeconds >= .5 && cardPlayback.paused && !cardPlayback.mediaError); assert.equal(await video.evaluate((v) => v.textTracks[0].activeCues.length), 0);
  await video.evaluate((v, modes) => {[...v.textTracks].forEach((t, i) => {t.mode = modes[i];});}, media.defaultCaptionModes);
  const codeCard = await capture(page, width, theme, 'complete-python', screenshots);
  const overflow = await page.evaluate(() => ({scrollWidth: document.documentElement.scrollWidth, bodyScrollWidth: document.body.scrollWidth}));
  assert.ok(overflow.scrollWidth <= width && overflow.bodyScrollWidth <= width); assert.deepEqual(errors, []); await page.close();
  return {slug, width, theme, httpStatus: response.status(), media, chapters, seeks, httpMedia, captions: {count: cues.length, sha256: sha(vtt), exactTextAndFrameTiming: true, narratedCC, silentSamples}, boundaryPlayback, boundaryScene, cardPlayback, codeCard, overflow, errors};
}

async function checkEntries(context, options) {
  const page = await context.newPage(), expected = algorithmSlugs.map(epHref); await page.goto(options.base, {waitUntil: 'networkidle'});
  assert.ok(await page.locator('a.track-algorithms[href="/video-studio/learn/#algorithms"]').count() > 0);
  assert.ok(await page.locator(`a.start-link[href="${epHref('container-most-water')}"]`).count() > 0);
  const recentHrefs = await page.locator('.recent a.card').evaluateAll((links) => links.map((a) => a.getAttribute('href')));
  await page.goto(new URL('learn/', options.base).href, {waitUntil: 'networkidle'}); assert.equal(await page.locator('#algorithms').count(), 1); assert.ok(await page.locator('a[href="/video-studio/series/leetcode/"]').count() > 0);
  await page.goto(new URL('series/leetcode/', options.base).href, {waitUntil: 'networkidle'});
  assert.deepEqual(await page.locator('.lesson-list a.lesson').evaluateAll((links) => links.map((a) => a.getAttribute('href'))), expected);
  assert.ok((await page.locator('.course-count').innerText()).includes(`已发布 ${algorithmSlugs.length} 篇`));
  await page.goto(new URL('library/?series=leetcode&sort=learning', options.base).href, {waitUntil: 'networkidle'});
  await page.waitForFunction((count) => [...document.querySelectorAll('#library-grid li')].filter((el) => getComputedStyle(el).display !== 'none').length === count, algorithmSlugs.length);
  assert.deepEqual(await page.locator('#library-grid li:visible a.card').evaluateAll((links) => links.map((a) => a.getAttribute('href'))), expected);
  const rss = await context.request.get(new URL('rss.xml', options.base).href); assert.equal(rss.status(), 200);
  assert.ok(((await rss.text()).match(/<item>[\s\S]*?<\/item>/g) || []).some((item) => item.includes('/episodes/number-of-islands/') && item.includes('LC.200')));
  await page.close(); return {algorithmDirection: true, learningEntry: true, recentHrefs, seriesHrefs: expected, libraryHrefs: expected, rssLC200: true};
}

async function run(options) {
  options.stage = 'final media readiness'; const e = finalInputs(options); options.stage = 'canonical preservation'; const retained = preservedCanonical(options.preservationBase); fs.mkdirSync(output, {recursive: true});
  const input = inputFingerprint(e), receiptPath = path.join(output, 'build-receipt.json');
  if (options.reuseBuild) {
    const receipt = readJson(receiptPath); assert.equal(receipt.inputFingerprint, input); assert.equal(receipt.distFingerprint, fingerprintFiles(filesIn(dist))); assert.ok(receipt.buildPassed && receipt.regressionPassed);
  } else {
    options.stage = 'single website build'; runLogged('npm', ['run', 'build'], site, path.join(output, 'build.log'));
    options.stage = 'historical learning regression'; runLogged('node', ['site/scripts/check-learning-path.mjs', '--complete', '--built'], root, path.join(output, 'learning-path.log'));
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
      options.stage = `browser ${width} ${theme}`; const context = await browser.newContext({viewport: {width, height: 900}, colorScheme: theme}); browserChecks.push(await checkPage(context, e, width, theme, options, screenshots)); siteEntries.push({width, ...await checkEntries(context, options)}); await context.close();
    }
    const releaseWarnings = fs.readFileSync(path.join(output, 'build.log'), 'utf8').split(/\r?\n/).filter((line) => line.includes('[changelog]'));
    const report = {status: 'passed', checkedAtUTC: new Date().toISOString(), executor: 'Codex derive_site agent', revisionTag: options.revisionTag, preservationBaseline: options.preservationBase, revisionDate: options.revisionDate,
      checkoutHeadAtRun: git(['rev-parse', 'HEAD']).trim(), helperSha256: fileSha(__filename), inputFingerprint: input,
      build: {passed: true, runs: 1, reusedForBrowserResume: options.reuseBuild, log: 'docs/number-of-islands-boundaries/site-qa/build.log'}, historicalRegression: {passed: true, runs: 1, log: 'docs/number-of-islands-boundaries/site-qa/learning-path.log'},
      media: [{slug, frames: e.frames, fps: e.fps, narrationCues: e.cues.length, videoSha256: e.videoSha256, posterSha256: e.posterSha256, coverSha256: e.covers, cardFrames: 150, cardFrom: e.card.from, productionInputs: e.productionInputs, publishedInternalEp: e.publishedInternalEp, productionInternalEp: e.productionInternalEp}], retained, browserChecks, siteEntries,
      screenshots: screenshots.map((file) => ({path: path.relative(root, file), sha256: fileSha(file)})), actualScreenshotReviewPending: true,
      localReleaseFetch: {warnings: releaseWarnings, newReleaseChangelogRequiresPostReleaseVerification: true},
      limits: [`Two actual browser viewports, eight chapter clicks/seeks, ${e.cues.length} exact VTT cues, native CC activation, real muted playback around shot06 second sentence and about 1s card playback per viewport. This is not full-video listening or ASR.`, 'Screenshots and actual browser-decoded frames were captured; model visual inspection must be recorded separately after viewing.', 'Other canonical tracked files and all six previously published LeetCode file SHA identities are preserved; no assumption is made about their untracked production MP4s.', 'Published LC200 identity and firstRelease/publishedAt are retained; updatedAt and the explicit current tag identify this revision. Release-specific changelog and real production delivery are checked only after publishing with explicit revision/deployment identity.']};
    fs.writeFileSync(path.join(__dirname, 'qa-site.json'), JSON.stringify(report, null, 2) + '\n');
    fs.writeFileSync(path.join(__dirname, 'qa-site.md'), `# LC.200 边界说明修订：网站检查\n\n实际检查：${report.checkedAtUTC}；修订${options.revisionTag}，结果通过。一次构建和一次历史回归；1440亮色/390暗色两组，四章共8次实际点击/seek。${e.cues.length}句VTT逐字与新SB帧时一致，正式片${e.frames}帧/${(e.frames / e.fps).toFixed(3)}秒。实际播放06第二句边界画面约1秒后暂停，以及完整程序卡约1秒；原生CC测完恢复默认，精确首卡、+0.0001秒与中末卡采样activeCues全0。完整Python/source/文章及MP4/海报HTTP SHA匹配。\n\n本片ep34/LC200/首发v0.66.0/原publishedAt保留，仅当前补丁tag与updatedAt表示此次修订。三封面、程序/trace及所有其他canonical与${options.preservationBase}保持，七片算法series顺序不变，P05当前已发表状态保留。首页算法方向、学习入口、系列/库/RSS可达，不要求旧片挤进首页近期卡。\n\n截图与实际浏览器解码帧已捕获，模型须实际打开后另记范围。构建Release提示：${releaseWarnings.length ? releaseWarnings.join('；') : '未记录失败提示'}；该补丁自身changelog与生产HTTPS在发布后按显式身份核验，不预记通过。不声称全片听辨、ASR或观众学习效果。详见[机器报告](qa-site.json)。\n`);

    console.log(JSON.stringify({status: report.status, revisionTag: options.revisionTag, browserCases: browserChecks.length, seeks: browserChecks.reduce((n, row) => n + row.seeks.length, 0), report: 'docs/number-of-islands-boundaries/qa-site.json'}, null, 2));
    return report;
  } finally {if (browser) await browser.close(); if (preview) preview.kill('SIGTERM');}
}

async function runRecorded(options) {
  const attemptsPath = path.join(__dirname, 'qa-site-attempts.json');
  const history = fs.existsSync(attemptsPath) ? readJson(attemptsPath) : {attempts: []};
  const attempt = {attempt: history.attempts.length + 1, status: 'running', startedAtUTC: new Date().toISOString(), revisionTag: options.revisionTag, preservationBaseline: options.preservationBase, reuseBuild: options.reuseBuild};
  history.attempts.push(attempt); fs.writeFileSync(attemptsPath, JSON.stringify(history, null, 2) + '\n');
  try {const result = await run(options); attempt.status = 'passed'; attempt.passReport = 'qa-site.json'; return result;}
  catch (error) {attempt.status = 'failed'; attempt.exception = error.name; attempt.message = error.message; attempt.stage = options.stage; attempt.passReportWrittenByThisAttempt = false; throw error;}
  finally {attempt.finishedAtUTC = new Date().toISOString(); history.status = `${attempt.status}_on_attempt_${attempt.attempt}`; fs.writeFileSync(attemptsPath, JSON.stringify(history, null, 2) + '\n');}
}

module.exports = {parse, preservedCanonical, finalInputs, run, runRecorded};
if (require.main === module) {
  const options = parse(process.argv.slice(2));
  if (options.help) console.log('Only after final-media approval: node qa-site.cjs --revision-tag vX.Y.Z --preservation-base SHA [--revision-date YYYY-MM-DD] [--port 4227 | --base URL] [--reuse-build]. No npm ci. A harness-only fix may reuse a matching build receipt.');
  else runRecorded(options).catch((error) => {console.error(error); process.exitCode = 1;});
}
