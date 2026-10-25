// Final batch QA only. --help never builds or writes a report.
'use strict';
const assert = require('node:assert/strict'), fs = require('node:fs'), path = require('node:path');
const cp = require('node:child_process'), crypto = require('node:crypto'), {createRequire} = require('node:module');
const root = path.resolve(__dirname, '../..'), site = path.join(root, 'site'), dist = path.join(site, 'dist'), out = path.join(__dirname, 'site-qa');
const read = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const sha = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex'), fileSha = (file) => sha(fs.readFileSync(file));
const git = (...args) => cp.execFileSync('git', args, {cwd: root, encoding: 'utf8', maxBuffer: 128 * 1024 * 1024});
const gitRead = (commit, relative) => JSON.parse(git('show', `${commit}:${relative}`));
const filesIn = (dir) => fs.readdirSync(dir, {withFileTypes: true}).flatMap((entry) => entry.isDirectory() ? filesIn(path.join(dir, entry.name)) : [path.join(dir, entry.name)]);
const epHref = (slug) => `/video-studio/episodes/${slug}/`;
const compare = (a, b) => a.ep - b.ep || (a.lessonOrder ?? 0) - (b.lessonOrder ?? 0);
const fingerprint = (files) => sha([...new Set(files)].sort().map((file) => `${path.relative(root, file)}\0${fileSha(file)}`).join('\n'));
function parse(args) {
  const opts = {port: 4237, reuseBuild: false};
  const values = {'--slugs': 'slugs', '--revision-tag': 'revisionTag', '--preservation-base': 'preservationBase', '--base': 'base', '--port': 'port', '--sample-frames': 'sampleFrames'};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--help') {opts.help = true; continue;}
    if (args[i] === '--reuse-build') {opts.reuseBuild = true; continue;}
    const split = args[i].indexOf('='), key = split < 0 ? args[i] : args[i].slice(0, split), value = split < 0 ? args[++i] : args[i].slice(split + 1);
    assert.ok(values[key] && value, `Unknown/missing option ${key}`); opts[values[key]] = value;
  }
  if (!opts.help) {
    assert.match(opts.revisionTag || '', /^v\d+\.\d+\.\d+$/); assert.ok(opts.preservationBase && opts.slugs, '--slugs, --revision-tag and --preservation-base are required');
    opts.slugs = opts.slugs.split(','); assert.equal(new Set(opts.slugs).size, 3); assert.equal(opts.slugs.length, 3);
    for (const slug of opts.slugs) assert.match(slug, /^[a-z][a-z0-9-]*$/);
    opts.preservationBase = git('rev-parse', `${opts.preservationBase}^{commit}`).trim();
    opts.sampleFrames = Object.fromEntries((opts.sampleFrames || '').split(',').filter(Boolean).map((item) => {const [slug, frame] = item.split(':'); assert.ok(opts.slugs.includes(slug) && Number.isInteger(Number(frame)) && Number(frame) > 0); return [slug, Number(frame)];}));
    opts.port = Number(opts.port); assert.ok(Number.isInteger(opts.port) && opts.port > 0); opts.externalPreview = !!opts.base;
    opts.base ||= `http://127.0.0.1:${opts.port}/video-studio/`; assert.ok(opts.base.endsWith('/'));
  }
  return opts;
}
function dateRuntime() {
  const source = fs.readFileSync(path.join(site, 'src/lib/episodes.ts'), 'utf8');
  const selected = source.slice(source.indexOf('/** 历史日期'), source.indexOf('/** NEW 根据')).replace(/^export /gm, '');
  const {transformSync} = createRequire(path.join(site, 'package.json'))('esbuild');
  return new Function(transformSync(selected, {loader: 'ts'}).code + '; return {dateIso, fmtVersion, fmtDate};')();
}
function fullISO(value, dates) {
  assert.ok(typeof value === 'string' && value.includes('T') && /(?:Z|[+-]\d{2}:\d{2})$/.test(value), 'New content dates require full ISO timestamps with timezone');
  dates.dateIso(value); return Date.parse(value);
}
function preserve(opts) {
  const code = String.raw`
import hashlib,json,os,pathlib,subprocess,sys,tarfile
root=pathlib.Path.cwd();commit=sys.argv[1];exclude=json.loads(sys.argv[2]);hashes={}
p=subprocess.Popen(['git','archive','--format=tar',commit,'episodes'],stdout=subprocess.PIPE)
with tarfile.open(fileobj=p.stdout,mode='r|') as archive:
 for item in archive:
  if item.isdir() or any(item.name.startswith('episodes/'+s+'/') for s in exclude):continue
  if item.issym():old=item.linkname.encode();actual=os.readlink(root/item.name).encode()
  else:old=archive.extractfile(item).read();actual=(root/item.name).read_bytes()
  digest=hashlib.sha256(old).hexdigest();assert hashlib.sha256(actual).hexdigest()==digest,item.name
  hashes[item.name]=digest
assert p.wait()==0
print(json.dumps(hashes,sort_keys=True))
`;
  const hashes = JSON.parse(cp.execFileSync('python3', ['-c', code, opts.preservationBase, JSON.stringify(opts.slugs)], {cwd: root, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024}));
  const paths = ['episodes', ...opts.slugs.map((slug) => `:(exclude)episodes/${slug}`)];
  assert.equal(git('diff', '--no-ext-diff', '--name-only', opts.preservationBase, '--', ...paths).trim(), '');
  assert.equal(git('ls-files', '--others', '--exclude-standard', '--', ...paths).trim(), '');
  const metaFiles = Object.keys(hashes).filter((file) => /^episodes\/[^/]+\/meta\.json$/.test(file));
  const actualSlugs = fs.readdirSync(path.join(root, 'episodes')).filter((slug) => !opts.slugs.includes(slug) && fs.existsSync(path.join(root, 'episodes', slug, 'meta.json'))).sort();
  assert.deepEqual(actualSlugs, metaFiles.map((file) => file.split('/')[1]).sort());
  return {baselineCommit: opts.preservationBase, allCanonicalSHA256: hashes, metadata: metaFiles.map((file) => read(path.join(root, file)))};
}
function cuePlan(sb) {return sb.scenes.flatMap((scene) => scene.shots.flatMap((shot) => shot.subtitles.map((sub) => ({text: sub.text, start: (shot.from + sub.from) / sb.meta.fps, end: (shot.from + sub.to + 1) / sb.meta.fps}))));}
function chapterPlan(sb) {return sb.scenes.reduce((result, scene) => {if (result.at(-1)?.id !== scene.chapterId) result.push({id: scene.chapterId, start: scene.from / sb.meta.fps}); return result;}, []);}
function inputs(slug, opts, dates) {
  const canonical = path.join(root, 'episodes', slug), production = path.join(root, 'episodes-codex', slug);
  const meta = read(path.join(canonical, 'meta.json')), config = read(path.join(production, 'episode-config.json')), sb = read(path.join(canonical, 'storyboard.json'));
  const reservationFiles = git('ls-tree', '-r', '--name-only', opts.preservationBase, '--', `episodes/${slug}`).trim().split(/\r?\n/).filter(Boolean);
  assert.deepEqual(reservationFiles, [`episodes/${slug}/meta.json`], 'Final preservation base must include the original metadata-only reservation');
  const reserved = gitRead(opts.preservationBase, reservationFiles[0]); assert.equal(reserved.draft, true); assert.equal(reserved.publishedAt, undefined);
  for (const key of ['slug', 'ep', 'problemNumber', 'firstRelease', 'createdAt', 'sourcePath']) assert.deepEqual(meta[key], reserved[key], `${slug}: reserved ${key} changed`);
  assert.equal(meta.slug, slug); assert.equal(meta.title, config.title); assert.equal(meta.draft, false); assert.equal(meta.series, 'leetcode');
  assert.equal(meta.sourcePath, `episodes-codex/${slug}/remotion`); assert.match(meta.firstRelease, /^v\d+\.\d+\.\d+$/);
  const created = fullISO(meta.createdAt, dates), modified = fullISO(meta.updatedAt, dates), published = fullISO(meta.publishedAt, dates);
  assert.ok(modified >= created && modified >= fullISO(reserved.updatedAt, dates) && published >= created);
  const fps = sb.meta.fps, frames = sb.meta.finalVideoFrames, card = sb.meta.unvoicedEndCard;
  assert.equal(fps, 30); assert.ok(Number.isInteger(frames) && frames > 150); assert.equal(meta.finalVideoFrames, frames);
  assert.equal(card.durationInFrames, 150); assert.equal(card.from + 150, frames);
  const cues = cuePlan(sb), chapters = chapterPlan(sb); assert.ok(cues.length > 0 && cues.every((cue) => cue.start >= 0 && cue.end > cue.start && cue.end <= card.from / fps));
  assert.equal(chapters.length, 4); assert.equal(new Set(chapters.map((chapter) => chapter.id)).size, 4);
  for (const chapter of chapters) assert.match(chapter.id, /^[a-z][a-z0-9-]*$/);
  const articleDerivation = require('./derived-articles/derive.cjs').verifyArticle(slug, path.join(canonical, 'article.mdx'));
  for (const name of ['script.md', 'storyboard.json', meta.video, 'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg']) assert.equal(fileSha(path.join(canonical, name)), fileSha(path.join(production, name)), `${slug}: stale canonical ${name}`);
  for (const entry of fs.readdirSync(canonical, {withFileTypes: true})) {assert.ok(!entry.isDirectory()); assert.ok(!/\.(?:wav|png|tsx?|jsx?)$/i.test(entry.name), `${slug}: production artifact in canonical`);}
  const videoSha256 = fileSha(path.join(canonical, meta.video)), posterSha256 = fileSha(path.join(canonical, meta.poster)), rendered = read(path.join(production, 'render-result.json'));
  assert.equal(rendered.sha256, videoSha256); assert.equal(rendered.frames, frames); assert.equal(rendered.bytes, fs.statSync(path.join(canonical, meta.video)).size);
  assert.ok(Math.abs(rendered.finalLUFS + 16) <= .3 && rendered.truePeakDBTP <= -2);
  for (const [relative, expected] of Object.entries(read(path.join(production, 'source-sha256.json')))) assert.equal(fileSha(path.resolve(production, relative)), expected, `${slug}: frozen ${relative} changed`);
  const solution = fs.readFileSync(path.join(production, 'solution.py'), 'utf8').trim(); assert.equal(read(path.join(production, 'solution.json')).lines.join('\n').trim(), solution);
  const sampleShots = sb.scenes.filter((scene) => scene.chapterId === chapters[2].id).flatMap((scene) => scene.shots), shot = sampleShots[Math.min(1, sampleShots.length - 1)];
  assert.ok(shot); const sampleFrame = opts.sampleFrames[slug] ?? Math.floor(shot.from + shot.durationInFrames / 2); assert.ok(sampleFrame > 15 && sampleFrame < card.from);
  return {slug, canonical, production, meta, sb, fps, frames, card, cues, chapters, solution, videoSha256, posterSha256, sampleFrame, articleDerivation,
    displayDuration: `${Math.floor(frames / fps / 60)}:${String(Math.floor(frames / fps % 60)).padStart(2, '0')}`, expectedSource: `https://github.com/linhongcun/video-studio/tree/main/${meta.sourcePath}`};
}
function parseVtt(bytes) {
  const blocks = bytes.toString().trim().split(/\r?\n\s*\r?\n/); assert.equal(blocks.shift(), 'WEBVTT');
  const seconds = (stamp) => stamp.split(':').reduce((sum, value) => sum * 60 + Number(value), 0);
  return blocks.map((block) => {const lines = block.split(/\r?\n/), [start, end] = lines[0].split(' --> '); assert.ok(end); return {start: seconds(start), end: seconds(end), text: lines.slice(1).join('\n')};});
}
async function seek(page, time) {await page.locator('video').evaluate((v, t) => {v.pause(); v.currentTime = t;}, time); await page.waitForFunction((t) => {const v = document.querySelector('video'); return !v.seeking && v.readyState >= 2 && Math.abs(v.currentTime - t) < .01;}, time);}
async function play(page, target) {
  const before = await page.locator('video').evaluate((v) => {v.muted = true; v.playbackRate = 1; window.__batchPlaying = false; v.addEventListener('playing', () => {window.__batchPlaying = true;}, {once: true}); return v.currentTime;});
  assert.ok(target - before >= .5); await page.locator('video').evaluate((v) => v.play());
  await page.waitForFunction((time) => {const v = document.querySelector('video'); return window.__batchPlaying && !v.paused && v.currentTime >= time && v.readyState >= 2;}, target);
  return page.locator('video').evaluate((v, before) => {v.pause(); return {beforeTime: before, afterTime: v.currentTime, advancedSeconds: v.currentTime - before, playingEvent: window.__batchPlaying, paused: v.paused, muted: v.muted, mediaError: v.error?.message ?? null};}, before);
}
async function pageCheck(context, e, opts, width, theme, series, dates, screenshots) {
  const page = await context.newPage(), errors = []; page.on('pageerror', (error) => errors.push(error.message));
  const response = await page.goto(new URL(`episodes/${e.slug}/`, opts.base).href, {waitUntil: 'networkidle'}); assert.equal(response.status(), 200); await page.evaluate(() => document.fonts.ready);
  assert.equal(await page.locator('.eh h1').innerText(), e.meta.title); assert.ok((await page.locator('footer').innerText()).includes(opts.revisionTag));
  assert.equal(await page.locator('.episode-version time').getAttribute('datetime'), e.meta.updatedAt); assert.ok((await page.locator('.episode-version').innerText()).includes(dates.fmtVersion(e.meta.updatedAt)));
  assert.deepEqual(await page.locator('.eh .meta time').evaluateAll((times) => times.map((time) => time.getAttribute('datetime'))), [e.meta.createdAt, e.meta.updatedAt]);
  const structured = JSON.parse(await page.locator('script[type="application/ld+json"]').innerText());
  assert.equal(structured.dateCreated, e.meta.createdAt); assert.equal(structured.dateModified, e.meta.updatedAt); assert.equal(structured.uploadDate, e.meta.publishedAt);
  assert.ok((await page.locator('.eh .meta').innerText()).includes(e.displayDuration)); assert.ok(await page.getByText(`LC.${e.meta.problemNumber}`, {exact: false}).count() > 0);
  assert.ok(await page.locator(`a[href="${e.expectedSource}"]`).count() > 0); assert.ok((await page.locator('article pre').allTextContents()).some((text) => text.trim() === e.solution));
  const index = series.indexOf(e.slug), neighbors = [series[index - 1], series[index + 1]].filter(Boolean).map(epHref);
  assert.deepEqual(await page.locator('.pager a').evaluateAll((links) => links.map((link) => link.getAttribute('href'))), neighbors);
  const video = page.locator('video'); await video.evaluate((v) => {v.muted = true;}); await page.waitForFunction(() => document.querySelector('video').readyState >= 1);
  const media = await video.evaluate((v) => ({duration: v.duration, controls: v.controls, width: v.videoWidth, height: v.videoHeight, defaultModes: [...v.textTracks].map((track) => track.mode)}));
  assert.ok(media.controls && Math.abs(media.duration - e.frames / e.fps) < .1); assert.deepEqual([media.width, media.height], [1920, 1080]);
  const chapters = await page.locator('#player').evaluate((el) => JSON.parse(el.dataset.chapters)); assert.deepEqual(chapters.map(({id, start}) => ({id, start})), e.chapters);
  const seeks = [];
  for (const chapter of chapters) {assert.ok(await page.locator(`article #${chapter.id}`).count() > 0); const selector = `#player ${width < 768 ? '.chip' : '.ch'}[data-id="${chapter.id}"]`; await page.locator(selector).click(); await video.evaluate((v) => v.pause()); await page.waitForFunction((time) => {const v = document.querySelector('video'); return !v.seeking && Math.abs(v.currentTime - time) < .7;}, chapter.start); assert.equal(await page.locator(selector).getAttribute('aria-current'), 'true'); seeks.push({id: chapter.id, expected: chapter.start, actual: await video.evaluate((v) => v.currentTime)});}
  const vttResponse = await context.request.get(new URL(`episodes/${e.slug}/captions.vtt`, opts.base).href); assert.equal(vttResponse.status(), 200); const vtt = await vttResponse.body(), cues = parseVtt(vtt);
  assert.equal(cues.length, e.cues.length); for (let i = 0; i < cues.length; i++) {assert.equal(cues[i].text, e.cues[i].text); for (const key of ['start', 'end']) assert.ok(Math.abs(cues[i][key] - e.cues[i][key]) < .001);}
  assert.ok(cues.every((cue) => cue.end <= e.card.from / e.fps)); assert.equal(sha(vtt), fileSha(path.join(dist, 'episodes', e.slug, 'captions.vtt')));
  const httpMedia = []; if (width === 1440) for (const [name, expected] of [[e.meta.video, e.videoSha256], [e.meta.poster, e.posterSha256]]) {const asset = await context.request.get(new URL(`episodes/${e.slug}/${name}`, opts.base).href); assert.equal(asset.status(), 200); const bytes = await asset.body(); assert.equal(sha(bytes), expected); httpMedia.push({name, bytes: bytes.length, sha256: sha(bytes)});}
  await video.evaluate((v) => {v.textTracks[0].mode = 'showing';}); await seek(page, (cues[0].start + cues[0].end) / 2); await page.waitForFunction((count) => {const v = document.querySelector('video'); return document.querySelector('track').readyState === 2 && v.textTracks[0].cues?.length === count && v.textTracks[0].activeCues?.length > 0;}, cues.length);
  const nativeCC = await video.evaluate((v) => ({loadedCues: v.textTracks[0].cues.length, activeCues: v.textTracks[0].activeCues.length})); await video.evaluate((v, modes) => {[...v.textTracks].forEach((track, i) => {track.mode = modes[i];});}, media.defaultModes);
  await seek(page, Math.max(0, e.sampleFrame / e.fps - 1)); const keyPlayback = await play(page, e.sampleFrame / e.fps); assert.ok(keyPlayback.paused && !keyPlayback.mediaError);
  await page.evaluate(() => scrollTo({top: 0, left: 0, behavior: 'instant'})); await page.waitForFunction(() => !document.querySelector('#player .vwrap').classList.contains('stuck'));
  const keyImage = path.join(out, `${e.slug}-key-${width}-${theme}.png`); await page.screenshot({path: keyImage}); screenshots.push(keyImage);
  await video.evaluate((v) => {v.textTracks[0].mode = 'showing';}); const cardSamples = [];
  for (const offset of [0, .0001, .1, 2.5, 4.8]) {const requested = e.card.from / e.fps + offset; await seek(page, requested); await page.evaluate(() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))); const sample = await video.evaluate((v, requested) => ({requested, currentTime: v.currentTime, activeCues: [...v.textTracks[0].activeCues].map((cue) => ({text: cue.text, start: cue.startTime, end: cue.endTime}))}), requested); cardSamples.push(sample); assert.equal(sample.activeCues.length, 0, JSON.stringify(sample));}
  await seek(page, e.card.from / e.fps + 1); const cardPlayback = await play(page, e.card.from / e.fps + 2); assert.ok(cardPlayback.paused && !cardPlayback.mediaError); await video.evaluate((v, modes) => {[...v.textTracks].forEach((track, i) => {track.mode = modes[i];});}, media.defaultModes);
  const cardImage = path.join(out, `${e.slug}-python-decoded-${width}.png`); const encoded = await video.evaluate((v) => {const canvas = document.createElement('canvas'); canvas.width = v.videoWidth; canvas.height = v.videoHeight; canvas.getContext('2d').drawImage(v, 0, 0); return canvas.toDataURL('image/png').split(',')[1];}); fs.writeFileSync(cardImage, Buffer.from(encoded, 'base64')); screenshots.push(cardImage);
  const overflow = await page.evaluate(() => ({document: document.documentElement.scrollWidth, body: document.body.scrollWidth})); assert.ok(overflow.document <= width && overflow.body <= width); assert.deepEqual(errors, []); await page.close();
  return {slug: e.slug, width, theme, media, seeks, chapters, httpMedia, captions: {count: cues.length, sha256: sha(vtt), exactTextAndFrameTiming: true, nativeCC, cardSamples}, keyPlayback, requestedSampleFrame: e.sampleFrame, cardPlayback, keyScreenshot: path.relative(root, keyImage), decodedCard: path.relative(root, cardImage), dates: {createdAt: e.meta.createdAt, updatedAt: e.meta.updatedAt, publishedAt: e.meta.publishedAt}, overflow, errors};
}
async function entries(context, opts, series) {
  const page = await context.newPage(); await page.goto(opts.base, {waitUntil: 'networkidle'}); assert.ok(await page.locator('a.track-algorithms[href="/video-studio/learn/#algorithms"]').count() > 0);
  const recent = await page.locator('.recent a.card').evaluateAll((links) => links.map((a) => a.getAttribute('href'))); for (const slug of opts.slugs) assert.ok(recent.includes(epHref(slug)));
  await page.goto(new URL('learn/', opts.base).href, {waitUntil: 'networkidle'}); assert.equal(await page.locator('#algorithms').count(), 1); assert.ok(await page.locator('a[href="/video-studio/series/leetcode/"]').count() > 0);
  await page.goto(new URL('series/leetcode/', opts.base).href, {waitUntil: 'networkidle'}); assert.deepEqual(await page.locator('.lesson-list a.lesson').evaluateAll((links) => links.map((a) => a.getAttribute('href'))), series.map(epHref));
  await page.goto(new URL('library/?series=leetcode&sort=learning', opts.base).href, {waitUntil: 'networkidle'}); await page.waitForFunction((count) => [...document.querySelectorAll('#library-grid li')].filter((el) => getComputedStyle(el).display !== 'none').length === count, series.length); assert.deepEqual(await page.locator('#library-grid li:visible a.card').evaluateAll((links) => links.map((a) => a.getAttribute('href'))), series.map(epHref));
  const rss = await context.request.get(new URL('rss.xml', opts.base).href); assert.equal(rss.status(), 200); for (const slug of opts.slugs) assert.ok((await rss.text()).includes(`/episodes/${slug}/`)); await page.close(); return {recent, series, algorithmLearningEntry: true, library: true, rss: true};
}
function logged(command, args, cwd, file) {const result = cp.spawnSync(command, args, {cwd, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024}); fs.writeFileSync(file, `${result.stdout || ''}${result.stderr || ''}`); if (result.error) throw result.error; assert.equal(result.status, 0, `See ${file}`);}
async function run(opts) {
  opts.stage = 'final media and ISO identity'; const dates = dateRuntime(), episodes = opts.slugs.map((slug) => inputs(slug, opts, dates)); assert.equal(`v${read(path.join(site, 'package.json')).version}`, opts.revisionTag);
  opts.stage = 'all non-batch canonical preservation'; const retained = preserve(opts), metadata = [...retained.metadata, ...episodes.map((e) => e.meta)];
  const series = metadata.filter((meta) => meta.series === 'leetcode' && !meta.draft && !meta.archived).sort(compare).map((meta) => meta.slug); const older = retained.metadata.filter((meta) => meta.series === 'leetcode' && !meta.draft && !meta.archived).sort(compare).map((meta) => meta.slug); assert.equal(series.length, older.length + episodes.length); assert.deepEqual(series.filter((slug) => !opts.slugs.includes(slug)), older);
  const canonical = git('ls-files', '--cached', '--others', '--exclude-standard', '--', 'episodes').trim().split(/\r?\n/).filter(Boolean).map((file) => path.join(root, file));
  const inputFingerprint = fingerprint([...filesIn(path.join(site, 'src')), ...filesIn(path.join(site, 'scripts')), ...fs.readdirSync(site, {withFileTypes: true}).filter((entry) => entry.isFile()).map((entry) => path.join(site, entry.name)), ...canonical, ...episodes.flatMap((e) => ['solution.py', 'solution.json', 'episode-config.json', 'render-result.json', 'source-sha256.json'].map((file) => path.join(e.production, file)))]);
  fs.mkdirSync(out, {recursive: true}); const receiptFile = path.join(out, 'build-receipt.json');
  if (opts.reuseBuild) {const receipt = read(receiptFile); assert.equal(receipt.inputFingerprint, inputFingerprint); assert.equal(receipt.distFingerprint, fingerprint(filesIn(dist))); assert.ok(receipt.buildPassed && receipt.datesPassed && receipt.regressionPassed);}
  else {opts.stage = 'one batch build'; logged('npm', ['run', 'build'], site, path.join(out, 'build.log')); opts.stage = 'built dates'; logged('npm', ['run', 'check:dates', '--', '--built'], site, path.join(out, 'dates-built.log')); opts.stage = 'historical learning regression'; logged('node', ['site/scripts/check-learning-path.mjs', '--complete', '--built'], root, path.join(out, 'learning-path.log')); fs.writeFileSync(receiptFile, JSON.stringify({revisionTag: opts.revisionTag, preservationBaseline: opts.preservationBase, inputFingerprint, distFingerprint: fingerprint(filesIn(dist)), checkedAtUTC: new Date().toISOString(), buildPassed: true, datesPassed: true, regressionPassed: true}, null, 2) + '\n');}
  for (const e of episodes) for (const [file, expected] of [[e.meta.video, e.videoSha256], [e.meta.poster, e.posterSha256]]) assert.equal(fileSha(path.join(dist, 'episodes', e.slug, file)), expected);
  retained.builtMedia = retained.metadata.filter((meta) => !meta.draft).map((meta) => ({slug: meta.slug, files: [meta.video, meta.poster].filter(Boolean).map((file) => {const relative = `episodes/${meta.slug}/${file}`, expected = retained.allCanonicalSHA256[relative]; assert.equal(fileSha(path.join(dist, relative)), expected); return {file, sha256: expected};})}));
  const preview = opts.externalPreview ? null : cp.spawn(process.execPath, [path.join(site, 'node_modules/astro/astro.js'), 'preview', '--host', '127.0.0.1', '--port', String(opts.port)], {cwd: site, stdio: 'ignore'}); let browser; const browserChecks = [], entryChecks = [], screenshots = [];
  try {for (let n = 0; n < 100; n++) {try {if ((await fetch(opts.base)).ok) break;} catch {} assert.ok(n < 99); await new Promise((resolve) => setTimeout(resolve, 200));}
    const {chromium} = require('playwright'); browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium', args: ['--no-sandbox', '--disable-dev-shm-usage']});
    for (const [width, theme] of [[1440, 'light'], [390, 'dark']]) {const context = await browser.newContext({viewport: {width, height: 900}, colorScheme: theme}); for (const e of episodes) {opts.stage = `${e.slug} browser ${width}`; browserChecks.push(await pageCheck(context, e, opts, width, theme, series, dates, screenshots));} entryChecks.push({width, ...await entries(context, opts, series)}); await context.close();}
    const report = {status: 'passed', checkedAtUTC: new Date().toISOString(), executor: 'Codex derive_site batch QA', revisionTag: opts.revisionTag, preservationBaseline: opts.preservationBase, slugs: opts.slugs, inputFingerprint,
      build: {runs: 1, passed: true, reused: opts.reuseBuild}, datesCheck: {builtRuns: 1, passed: true}, historicalRegression: {runs: 1, passed: true},
      media: episodes.map((e) => ({slug: e.slug, problemNumber: e.meta.problemNumber, frames: e.frames, fps: e.fps, cues: e.cues.length, cardFrom: e.card.from, cardFrames: 150, videoSha256: e.videoSha256, posterSha256: e.posterSha256, dates: {createdAt: e.meta.createdAt, updatedAt: e.meta.updatedAt, publishedAt: e.meta.publishedAt}, firstRelease: e.meta.firstRelease, articleDerivation: e.articleDerivation})),
      retained, algorithmSeries: {before: older, after: series}, browserChecks, entryChecks, screenshots: screenshots.map((file) => ({path: path.relative(root, file), sha256: fileSha(file)})), actualScreenshotReviewPending: true,
      localReleaseFetch: {warnings: fs.readFileSync(path.join(out, 'build.log'), 'utf8').split(/\r?\n/).filter((line) => line.includes('[changelog]')), batchReleaseChangelogRequiresProductionVerification: true},
      limits: ['Three finalized films share one real build, one built-date check and one learning regression. Playback is short and muted; native CC is enabled for measurement then restored.', 'Each page/viewport captures one real key-scene page screenshot and one browser-decoded full Python card; capture alone does not mean actual visual inspection.', 'All non-batch canonical bytes are preserved; unchanged old media are checked in the built local tree, not repeatedly downloaded online.', 'ISO creation timestamps and reserved firstRelease are retained. Last material modification and first publication timestamps are explicit metadata, never inferred from build time. No full listening, ASR or measured learning outcomes are claimed.']};
    fs.writeFileSync(path.join(__dirname, 'qa-site.json'), JSON.stringify(report, null, 2) + '\n'); fs.writeFileSync(path.join(__dirname, 'qa-site.md'), `# 三片批量网站QA\n\n实际检查${report.checkedAtUTC}，显式版本${opts.revisionTag}，机械检查通过。一次build、一次check:dates --built、一次历史回归；三片两视口共${browserChecks.length}组、${browserChecks.reduce((sum, row) => sum + row.seeks.length, 0)}次章seek。字幕和时长取真实SB，精确首卡/+.0001及中末卡无cue，完整Python/source和完整媒体HTTP SHA正确。\n\n新片createdAt/firstRelease固定，updatedAt/publishedAt均为有时区ISO且创建/修改/公开语义分别核对；页面时间、日期版本和结构化数据对应真实meta。其他canonical与${opts.preservationBase}完整SHA保持，算法系列${older.length}→${series.length}，入库/主页/学习入口/RSS可达。\n\n实际截图范围待逐份打开后另记；当前不把截图生成当成视觉检查通过。本次Release自身关联及生产HTTPS需发布后单独核验。详见qa-site.json和逐次attempt；不声称全片听辨、ASR或学习效果。\n`); return report;
  } finally {if (browser) await browser.close(); if (preview) preview.kill('SIGTERM');}
}
async function recorded(opts) {const file = path.join(__dirname, 'qa-site-attempts.json'), history = fs.existsSync(file) ? read(file) : {attempts: []}, attempt = {attempt: history.attempts.length + 1, status: 'running', startedAtUTC: new Date().toISOString(), revisionTag: opts.revisionTag, preservationBaseline: opts.preservationBase, slugs: opts.slugs, reuseBuild: opts.reuseBuild}; history.attempts.push(attempt); fs.writeFileSync(file, JSON.stringify(history, null, 2) + '\n'); try {const result = await run(opts); attempt.status = 'passed'; console.log(JSON.stringify({status: result.status, slugs: opts.slugs, browserCases: result.browserChecks.length, visualReviewPending: true}));} catch (error) {attempt.status = 'failed'; attempt.stage = opts.stage; attempt.exception = error.name; attempt.message = error.message; attempt.passReportWrittenByThisAttempt = false; throw error;} finally {attempt.finishedAtUTC = new Date().toISOString(); history.status = `${attempt.status}_on_attempt_${attempt.attempt}`; fs.writeFileSync(file, JSON.stringify(history, null, 2) + '\n');}}
module.exports = {parse, preserve, inputs, run};
if (require.main === module) {const opts = parse(process.argv.slice(2)); if (opts.help) console.log('After final media approval only: node qa-site.cjs --slugs daily-temperatures,permutations,trapping-rain-water --revision-tag vX.Y.Z --preservation-base SHA [--sample-frames slug:FRAME,...] [--reuse-build] [--port 4237 | --base URL]. No npm ci.'); else recorded(opts).catch((error) => {console.error(error); process.exitCode = 1;});}
