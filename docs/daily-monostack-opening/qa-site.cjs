// Final single-film problem-fit opening revision QA. --help never builds or writes.
'use strict';
const assert = require('node:assert/strict'), fs = require('node:fs'), path = require('node:path');
const cp = require('node:child_process'), crypto = require('node:crypto'), {createRequire} = require('node:module');
const root = path.resolve(__dirname, '../..'), site = path.join(root, 'site'), dist = path.join(site, 'dist'), out = path.join(__dirname, 'site-qa');
const read = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const sha = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex'), fileSha = (file) => sha(fs.readFileSync(file));
const git = (...args) => cp.execFileSync('git', args, {cwd: root, encoding: 'utf8', maxBuffer: 128 * 1024 * 1024});
const gitRead = (commit, relative) => JSON.parse(git('show', `${commit}:${relative}`));
const filesIn = (dir) => fs.readdirSync(dir, {withFileTypes: true}).flatMap((entry) => entry.isDirectory() ? filesIn(path.join(dir, entry.name)) : [path.join(dir, entry.name)]);
const SLUG = 'daily-temperatures';
const epHref = (slug) => `/video-studio/episodes/${slug}/`;
const compare = (a, b) => a.ep - b.ep || (a.lessonOrder ?? 0) - (b.lessonOrder ?? 0);
const fingerprint = (files) => sha([...new Set(files)].sort().map((file) => `${path.relative(root, file)}\0${fileSha(file)}`).join('\n'));
function parse(args) {
  const opts = {port: 4247, reuseBuild: false, slugs: [SLUG]};
  const values = {'--revision-tag': 'revisionTag', '--preservation-base': 'preservationBase', '--base': 'base', '--port': 'port', '--sample-frame': 'sampleFrame'};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--help') {opts.help = true; continue;}
    if (args[i] === '--reuse-build') {opts.reuseBuild = true; continue;}
    const split = args[i].indexOf('='), key = split < 0 ? args[i] : args[i].slice(0, split), value = split < 0 ? args[++i] : args[i].slice(split + 1);
    assert.ok(values[key] && value, `Unknown/missing option ${key}`); opts[values[key]] = value;
  }
  if (!opts.help) {
    assert.match(opts.revisionTag || '', /^v\d+\.\d+\.\d+$/); assert.ok(opts.preservationBase, '--revision-tag and --preservation-base are required');
    opts.preservationBase = git('rev-parse', `${opts.preservationBase}^{commit}`).trim();
    if (opts.sampleFrame !== undefined) {opts.sampleFrame = Number(opts.sampleFrame); assert.ok(Number.isInteger(opts.sampleFrame) && opts.sampleFrame > 15);}
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
function titleAuthorContract(references, receipt) {
  assert.equal(references.presentation, 'title-author'); assert.equal(receipt.presentation, 'title-author');
  assert.equal(receipt.layout.kind, 'title-author-single-column'); assert.equal(receipt.layout.maxItemsPerPage, 4);
  assert.deepEqual(receipt.layout.renderedFields, ['title', 'credit']); assert.equal(receipt.layout.quotesRendered, false);
  assert.equal(receipt.inputs.secondsPerPage, 5);
  const bibliography = references.sources.map((source) => ({id: source.id, title: source.title, credit: source.author ?? source.organization}));
  for (const item of bibliography) for (const value of Object.values(item)) assert.ok(typeof value === 'string' && value.trim());
  assert.deepEqual(receipt.bibliography, bibliography); return bibliography;
}
function inputs(slug, opts, dates) {
  const canonical = path.join(root, 'episodes', slug), production = path.join(root, 'episodes-codex', slug);
  const meta = read(path.join(canonical, 'meta.json')), config = read(path.join(production, 'episode-config.json')), sb = read(path.join(canonical, 'storyboard.json'));
  const original = gitRead(opts.preservationBase, `episodes/${slug}/meta.json`);
  assert.equal(original.draft, false, 'Use the already-published revision baseline');
  for (const key of ['slug', 'title', 'ep', 'problemNumber', 'firstRelease', 'createdAt', 'publishedAt', 'sourcePath']) assert.deepEqual(meta[key], original[key], `${slug}: published ${key} changed`);
  assert.equal(meta.slug, SLUG); assert.equal(meta.ep, 35); assert.equal(meta.problemNumber, 739); assert.equal(meta.firstRelease, 'v0.69.0'); assert.notEqual(meta.firstRelease, opts.revisionTag);
  assert.equal(meta.createdAt, '2026-10-25T11:43:59.215+00:00'); assert.equal(meta.publishedAt, '2026-10-25T13:12:39+00:00');
  assert.equal(meta.title, config.title); assert.equal(meta.draft, false); assert.equal(meta.series, 'leetcode'); assert.equal(meta.sourcePath, `episodes-codex/${slug}/remotion`);
  assert.ok(fullISO(meta.updatedAt, dates) > fullISO(original.updatedAt, dates)); fullISO(meta.createdAt, dates); fullISO(meta.publishedAt, dates);
  const rendered = read(path.join(production, 'render-result.json')), publication = rendered.publicationMetadata;
  const fps = sb.meta.fps, frames = meta.finalVideoFrames ?? publication?.finalVideoFrames, bodyFrames = sb.meta.finalVideoFrames, card = sb.meta.unvoicedEndCard, appendix = meta.referenceAppendix;
  assert.equal(fps, 30); assert.ok(Number.isInteger(frames) && frames > bodyFrames); assert.equal(meta.finalVideoFrames, frames);
  assert.equal(card.durationInFrames, 150); assert.equal(card.from + 150, bodyFrames);
  assert.deepEqual(publication, {finalVideoFrames: frames, referenceAppendix: appendix});
  assert.equal(appendix.kind, 'references'); assert.equal(appendix.from, bodyFrames); assert.equal(appendix.durationInFrames, 150); assert.equal(appendix.from + appendix.durationInFrames, frames);
  const references = read(path.join(canonical, appendix.sources)), receipt = read(path.join(canonical, appendix.manifest)), referenceMedia = read(path.join(canonical, 'reference-appendix-media-check.json'));
  for (const name of [appendix.sources, appendix.manifest, 'reference-appendix-media-check.json']) assert.equal(fileSha(path.join(canonical, name)), fileSha(path.join(production, name)), `Reference publication file differs: ${name}`);
  assert.equal(receipt.bodyFrames, bodyFrames); assert.equal(receipt.finalVideoFrames, frames); assert.equal(receipt.appendix.pages.length, 1); assert.equal(receipt.appendix.framesPerPage, 150);
  assert.equal(receipt.inputs.referencesSHA256, fileSha(path.join(canonical, appendix.sources)));
  assert.equal(receipt.inputs.bodySHA256, fileSha(path.join(production, 'remotion/out/body.mp4')));
  const bibliography = titleAuthorContract(references, receipt);
  assert.equal(referenceMedia.passed, true); assert.equal(referenceMedia.bodySHA256, receipt.inputs.bodySHA256); assert.equal(referenceMedia.outputSHA256, receipt.outputSHA256);
  for (const field of ['bodyDecodedFramesAndTimestampsEqual', 'outputVideoTimelineContinuous', 'audioPacketsAndTimingEqual']) assert.equal(referenceMedia[field], true);
  const referenceEvidence = [...new Set(references.sources.flatMap((source) => [source.verification.evidence, source.titleEvidence.evidence, source.quotation?.evidence].filter(Boolean)))].sort().map((relative) => ({path: relative, sha256: fileSha(path.join(root, relative))}));
  const cues = cuePlan(sb), chapters = chapterPlan(sb); assert.ok(cues.length > 0 && cues.every((cue) => cue.start >= 0 && cue.end > cue.start && cue.end <= card.from / fps));
  const scriptSentences = [...fs.readFileSync(path.join(production, 'script.md'), 'utf8').matchAll(/^旁白：(.+)$/gm)].flatMap((m) => m[1].match(/[^。！？]+[。！？]?/gu) || []);
  assert.ok(scriptSentences.length > 0); assert.equal(cues.length, scriptSentences.length); assert.equal(cues.map((c) => c.text).join('').replace(/\s/g, ''), scriptSentences.join('').replace(/\s/g, ''));
  assert.equal(chapters.length, 4); assert.equal(new Set(chapters.map((chapter) => chapter.id)).size, 4);
  for (const chapter of chapters) assert.match(chapter.id, /^[a-z][a-z0-9-]*$/);
  for (const name of ['article.mdx', 'script.md', 'storyboard.json', meta.video, 'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg']) assert.equal(fileSha(path.join(canonical, name)), fileSha(path.join(production, name)), `${slug}: stale canonical ${name}`);
  for (const entry of fs.readdirSync(canonical, {withFileTypes: true})) {assert.ok(!entry.isDirectory()); assert.ok(!/\.(?:wav|png|tsx?|jsx?)$/i.test(entry.name), `${slug}: production artifact in canonical`);}
  for (const name of ['cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg']) assert.equal(fileSha(path.join(canonical, name)), sha(cp.execFileSync('git', ['show', `${opts.preservationBase}:episodes/${slug}/${name}`], {cwd: root, maxBuffer: 32 * 1024 * 1024})));
  for (const name of ['solution.py', 'solution.json', config.algorithmTrace]) assert.equal(fileSha(path.join(production, name)), sha(cp.execFileSync('git', ['show', `${opts.preservationBase}:episodes-codex/${slug}/${name}`], {cwd: root, maxBuffer: 32 * 1024 * 1024})), `Preserved program/trace changed: ${name}`);
  const videoSha256 = fileSha(path.join(canonical, meta.video)), posterSha256 = fileSha(path.join(canonical, meta.poster));
  assert.notEqual(videoSha256, sha(cp.execFileSync('git', ['show', `${opts.preservationBase}:episodes/${slug}/${meta.video}`], {cwd: root, maxBuffer: 32 * 1024 * 1024})), 'Revised movie has not been delivered');
  assert.equal(rendered.sha256, videoSha256); assert.equal(rendered.frames, frames); assert.equal(rendered.bytes, fs.statSync(path.join(canonical, meta.video)).size);
  assert.equal(receipt.outputSHA256, videoSha256);
  assert.ok(Math.abs(rendered.finalLUFS + 16) <= .3 && rendered.truePeakDBTP <= -2);
  for (const [relative, expected] of Object.entries(read(path.join(production, 'source-sha256.json')))) assert.equal(fileSha(path.resolve(production, relative)), expected, `${slug}: frozen ${relative} changed`);
  const solution = fs.readFileSync(path.join(production, 'solution.py'), 'utf8').trim(); assert.equal(read(path.join(production, 'solution.json')).lines.join('\n').trim(), solution);
  const shots = sb.scenes.flatMap((scene) => scene.shots), opening = shots.find((shot) => shot.visualType === 'problem'), basic = shots.find((shot) => shot.visualType === 'stack-basics');
  assert.equal(shots.length, 14); assert.equal(config.shotCount, 14); assert.equal(cues.length, 28);
  assert.ok(opening && basic && opening.from === 0 && opening.voice.length === 2 && basic.voice.length === 2);
  assert.ok(opening.subtitles[1].text.includes('单调栈') && opening.subtitles[1].text.includes('日子'));
  assert.ok(Number.isInteger(opening.cueFrames.labels['单调栈']));
  const methodFrame = Math.floor(opening.from + (opening.voice[1].localStart + opening.voice[1].localEnd) / 2);
  assert.ok(methodFrame >= opening.from + opening.cueFrames.labels['单调栈'] && methodFrame < opening.from + opening.durationInFrames);
  const sampleFrame = opts.sampleFrame ?? Math.floor(basic.from + (basic.voice[1].localStart + basic.voice[1].localEnd) / 2); assert.ok(sampleFrame > 15 && sampleFrame < card.from);
  return {slug, canonical, production, meta, sb, fps, frames, bodyFrames, card, appendix, references, referenceEvidence, receipt, bibliography, cues, chapters, solution, videoSha256, posterSha256, sampleFrame, methodFrame, original,
    displayDuration: `${Math.floor(frames / fps / 60)}:${String(Math.floor(frames / fps % 60)).padStart(2, '0')}`, expectedSource: `https://github.com/linhongcun/video-studio/tree/main/${meta.sourcePath}`};
}
function parseVtt(bytes) {
  const blocks = bytes.toString().trim().split(/\r?\n\s*\r?\n/); assert.equal(blocks.shift(), 'WEBVTT');
  const seconds = (stamp) => stamp.split(':').reduce((sum, value) => sum * 60 + Number(value), 0);
  return blocks.map((block) => {const lines = block.split(/\r?\n/), [start, end] = lines[0].split(' --> '); assert.ok(end); return {start: seconds(start), end: seconds(end), text: lines.slice(1).join('\n')};});
}
async function seek(page, time) {await page.locator('video').evaluate((v, t) => {v.pause(); v.currentTime = t;}, time); await page.waitForFunction((t) => {const v = document.querySelector('video'); return !v.seeking && v.readyState >= 2 && Math.abs(v.currentTime - t) < .01;}, time);}
async function play(page, target) {
  const before = await page.locator('video').evaluate((v) => {v.muted = true; v.playbackRate = 1; window.__dailyPlaying = false; v.addEventListener('playing', () => {window.__dailyPlaying = true;}, {once: true}); return v.currentTime;});
  assert.ok(target - before >= .5); await page.locator('video').evaluate((v) => v.play());
  await page.waitForFunction((time) => {const v = document.querySelector('video'); return window.__dailyPlaying && !v.paused && v.currentTime >= time && v.readyState >= 2;}, target);
  return page.locator('video').evaluate((v, before) => {v.pause(); return {beforeTime: before, afterTime: v.currentTime, advancedSeconds: v.currentTime - before, playingEvent: window.__dailyPlaying, paused: v.paused, muted: v.muted, mediaError: v.error?.message ?? null};}, before);
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
  const referenceLinks = [...new Set(e.references.sources.flatMap((source) => [source.url, source.verification.sourceUrl].filter(Boolean)))];
  for (const url of referenceLinks) assert.ok(await page.locator('article a').evaluateAll((links, href) => links.some((a) => a.href === href), url), `Full reference URL missing from article: ${url}`);
  const articleText = await page.locator('article').innerText(); for (const reference of e.references.sources) {
    for (const label of ['organization', 'title']) assert.ok(articleText.includes(reference[label]), `Reference ${reference.id} lacks full ${label}`);
    for (const fragment of reference.version.split('·').map((part) => part.trim())) assert.ok(articleText.replace(/访问于/g, '访问').includes(fragment.replace(/访问于/g, '访问')), `Reference ${reference.id} lacks version fact ${fragment}`);
  }
  const index = series.indexOf(e.slug), neighbors = [series[index - 1], series[index + 1]].filter(Boolean).map(epHref);
  assert.deepEqual(await page.locator('.pager a').evaluateAll((links) => links.map((link) => link.getAttribute('href'))), neighbors);
  const video = page.locator('video'); await video.evaluate((v) => {v.muted = true;}); await page.waitForFunction(() => document.querySelector('video').readyState >= 1);
  const media = await video.evaluate((v) => ({duration: v.duration, controls: v.controls, width: v.videoWidth, height: v.videoHeight, defaultModes: [...v.textTracks].map((track) => track.mode)}));
  assert.ok(media.controls && Math.abs(media.duration - e.frames / e.fps) < .1); assert.deepEqual([media.width, media.height], [1920, 1080]);
  const chapters = await page.locator('#player').evaluate((el) => JSON.parse(el.dataset.chapters)); assert.deepEqual(chapters.map(({id, start}) => ({id, start})), e.chapters);
  const seeks = [];
  for (const chapter of chapters) {assert.ok(await page.locator(`article #${chapter.id}`).count() > 0); const selector = `#player ${width < 768 ? '.chip' : '.ch'}[data-id="${chapter.id}"]`; await page.locator(selector).click(); await video.evaluate((v) => v.pause()); await page.waitForFunction((time) => {const v = document.querySelector('video'); return !v.seeking && Math.abs(v.currentTime - time) < .7;}, chapter.start); assert.equal(await page.locator(selector).getAttribute('aria-current'), 'true'); seeks.push({id: chapter.id, expected: chapter.start, actual: await video.evaluate((v) => v.currentTime)});}
  const vttResponse = await context.request.get(new URL(`episodes/${e.slug}/captions.vtt`, opts.base).href); assert.equal(vttResponse.status(), 200); const vtt = await vttResponse.body(), cues = parseVtt(vtt);
  assert.equal(cues.length, e.cues.length); for (let i = 0; i < cues.length; i++) {assert.equal(cues[i].text, e.cues[i].text); for (const key of ['start', 'end']) {if (key === 'end' && e.cues[i].end === e.card.from / e.fps) assert.ok(Math.abs(cues[i].end - (Math.ceil(e.card.from / e.fps * 1000) - 1) / 1000) < 1e-9); else assert.ok(Math.abs(cues[i][key] - e.cues[i][key]) < .001);}}
  assert.ok(cues.every((cue) => cue.end <= e.card.from / e.fps)); assert.equal(sha(vtt), fileSha(path.join(dist, 'episodes', e.slug, 'captions.vtt')));
  const httpMedia = []; if (width === 1440) for (const [name, expected] of [[e.meta.video, e.videoSha256], [e.meta.poster, e.posterSha256]]) {const asset = await context.request.get(new URL(`episodes/${e.slug}/${name}`, opts.base).href); assert.equal(asset.status(), 200); const bytes = await asset.body(); assert.equal(sha(bytes), expected); httpMedia.push({name, bytes: bytes.length, sha256: sha(bytes)});}
  await video.evaluate((v) => {v.textTracks[0].mode = 'showing';}); await seek(page, (cues[0].start + cues[0].end) / 2); await page.waitForFunction((count) => {const v = document.querySelector('video'); return document.querySelector('track').readyState === 2 && v.textTracks[0].cues?.length === count && v.textTracks[0].activeCues?.length > 0;}, cues.length);
  const nativeCC = await video.evaluate((v) => ({loadedCues: v.textTracks[0].cues.length, activeCues: v.textTracks[0].activeCues.length})); await video.evaluate((v, modes) => {[...v.textTracks].forEach((track, i) => {track.mode = modes[i];});}, media.defaultModes);
  await seek(page, Math.max(0, e.methodFrame / e.fps - 1)); const methodPreviewPlayback = await play(page, e.methodFrame / e.fps); assert.ok(methodPreviewPlayback.paused && !methodPreviewPlayback.mediaError);
  await seek(page, Math.max(0, e.sampleFrame / e.fps - 1)); const keyPlayback = await play(page, e.sampleFrame / e.fps); assert.ok(keyPlayback.paused && !keyPlayback.mediaError);
  await page.evaluate(() => scrollTo({top: 0, left: 0, behavior: 'instant'})); await page.waitForFunction(() => !document.querySelector('#player .vwrap').classList.contains('stuck'));
  const keyImage = path.join(out, `${e.slug}-key-${width}-${theme}.png`); await page.screenshot({path: keyImage}); screenshots.push(keyImage);
  await video.evaluate((v) => {v.textTracks[0].mode = 'showing';}); const cardSamples = [];
  for (const offset of [0, .0001, .1, 2.5, 4.8]) {const requested = e.card.from / e.fps + offset; await seek(page, requested); await page.evaluate(() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))); const sample = await video.evaluate((v, requested) => ({requested, currentTime: v.currentTime, activeCues: [...v.textTracks[0].activeCues].map((cue) => ({text: cue.text, start: cue.startTime, end: cue.endTime}))}), requested); cardSamples.push(sample); assert.equal(sample.activeCues.length, 0, JSON.stringify(sample));}
  await seek(page, e.card.from / e.fps + 1); const cardPlayback = await play(page, e.card.from / e.fps + 2); assert.ok(cardPlayback.paused && !cardPlayback.mediaError); await video.evaluate((v, modes) => {[...v.textTracks].forEach((track, i) => {track.mode = modes[i];});}, media.defaultModes);
  const cardImage = path.join(out, `${e.slug}-python-decoded-${width}.png`); const encoded = await video.evaluate((v) => {const canvas = document.createElement('canvas'); canvas.width = v.videoWidth; canvas.height = v.videoHeight; canvas.getContext('2d').drawImage(v, 0, 0); return canvas.toDataURL('image/png').split(',')[1];}); fs.writeFileSync(cardImage, Buffer.from(encoded, 'base64')); screenshots.push(cardImage);
  await video.evaluate((v) => {v.textTracks[0].mode = 'showing';}); const referenceSamples = [];
  for (const frame of [e.appendix.from, e.appendix.from + 75, e.frames - 1]) {
    const requested = frame / e.fps; await seek(page, requested); await page.evaluate(() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    const sample = await video.evaluate((v, requested) => ({requested, currentTime: v.currentTime, paused: v.paused, activeCues: [...v.textTracks[0].activeCues].map((cue) => cue.text)}), requested);
    assert.ok(sample.paused); assert.deepEqual(sample.activeCues, []); referenceSamples.push(sample);
  }
  await seek(page, (e.appendix.from + 75) / e.fps); await video.evaluate((v) => v.requestFullscreen()); await page.waitForFunction(() => document.fullscreenElement === document.querySelector('video'));
  const fullscreen = await video.evaluate((v) => ({active: document.fullscreenElement === v, time: v.currentTime, paused: v.paused, activeCues: v.textTracks[0].activeCues.length})); assert.ok(fullscreen.active && fullscreen.paused && !fullscreen.activeCues);
  const referenceImage = path.join(out, `${e.slug}-references-fullscreen-${width}.png`); await page.screenshot({path: referenceImage}); screenshots.push(referenceImage);
  const decodedReferences = path.join(out, `${e.slug}-references-decoded-${width}.png`), referenceEncoded = await video.evaluate((v) => {const canvas = document.createElement('canvas'); canvas.width = v.videoWidth; canvas.height = v.videoHeight; canvas.getContext('2d').drawImage(v, 0, 0); return canvas.toDataURL('image/png').split(',')[1];}); fs.writeFileSync(decodedReferences, Buffer.from(referenceEncoded, 'base64')); screenshots.push(decodedReferences);
  await page.evaluate(() => document.exitFullscreen()); await video.evaluate((v, modes) => {[...v.textTracks].forEach((track, i) => {track.mode = modes[i];});}, media.defaultModes);
  const overflow = await page.evaluate(() => ({document: document.documentElement.scrollWidth, body: document.body.scrollWidth})); assert.ok(overflow.document <= width && overflow.body <= width); assert.deepEqual(errors, []); await page.close();
  return {slug: e.slug, width, theme, media, seeks, chapters, httpMedia, captions: {count: cues.length, sha256: sha(vtt), exactTextAndFrameTiming: true, nativeCC, cardSamples}, methodPreviewPlayback, methodPreviewFrame: e.methodFrame, keyPlayback, requestedSampleFrame: e.sampleFrame, cardPlayback, keyScreenshot: path.relative(root, keyImage), decodedCard: path.relative(root, cardImage), references: {referenceLinks, referenceSamples, fullscreen, fullscreenImage: path.relative(root, referenceImage), decodedImage: path.relative(root, decodedReferences), presentation: e.references.presentation, bibliography: e.bibliography}, dates: {createdAt: e.meta.createdAt, updatedAt: e.meta.updatedAt, publishedAt: e.meta.publishedAt}, overflow, errors};
}
async function entries(context, opts, series) {
  const page = await context.newPage(); await page.goto(opts.base, {waitUntil: 'networkidle'}); assert.ok(await page.locator('a.track-algorithms[href="/video-studio/learn/#algorithms"]').count() > 0);
  const recent = await page.locator('.recent a.card').evaluateAll((links) => links.map((a) => a.getAttribute('href'))); // A revised existing lesson need not enter the recent-debut cards.
  await page.goto(new URL('learn/', opts.base).href, {waitUntil: 'networkidle'}); assert.equal(await page.locator('#algorithms').count(), 1); assert.ok(await page.locator('a[href="/video-studio/series/leetcode/"]').count() > 0);
  await page.goto(new URL('series/leetcode/', opts.base).href, {waitUntil: 'networkidle'}); assert.deepEqual(await page.locator('.lesson-list a.lesson').evaluateAll((links) => links.map((a) => a.getAttribute('href'))), series.map(epHref));
  await page.goto(new URL('library/?series=leetcode&sort=learning', opts.base).href, {waitUntil: 'networkidle'}); await page.waitForFunction((count) => [...document.querySelectorAll('#library-grid li')].filter((el) => getComputedStyle(el).display !== 'none').length === count, series.length); assert.deepEqual(await page.locator('#library-grid li:visible a.card').evaluateAll((links) => links.map((a) => a.getAttribute('href'))), series.map(epHref));
  const rss = await context.request.get(new URL('rss.xml', opts.base).href); assert.equal(rss.status(), 200); for (const slug of opts.slugs) assert.ok((await rss.text()).includes(`/episodes/${slug}/`)); await page.close(); return {recent, series, algorithmLearningEntry: true, library: true, rss: true};
}
function logged(command, args, cwd, file) {const result = cp.spawnSync(command, args, {cwd, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024}); fs.writeFileSync(file, `${result.stdout || ''}${result.stderr || ''}`); if (result.error) throw result.error; assert.equal(result.status, 0, `See ${file}`);}
function runCounts(opts) {
  const file = path.join(__dirname, 'qa-site-attempts.json'), previous = fs.existsSync(file) ? read(file).attempts : [];
  return {build: previous.filter((a) => a.buildInvoked || (!a.reuseBuild && a.stage === 'single website build')).length + Number(!!opts.buildInvoked), dates: previous.filter((a) => a.datesInvoked).length + Number(!!opts.datesInvoked), regression: previous.filter((a) => a.regressionInvoked).length + Number(!!opts.regressionInvoked)};
}
async function run(opts) {
  opts.stage = 'final media and ISO identity'; const dates = dateRuntime(), episodes = opts.slugs.map((slug) => inputs(slug, opts, dates)); assert.equal(`v${read(path.join(site, 'package.json')).version}`, opts.revisionTag);
  opts.stage = 'shared reference sources and actual delivery contract'; const referenceChecker = await import(path.join(site, 'scripts/check-references.mjs')); referenceChecker.checkSources(episodes[0].production); referenceChecker.checkEpisode(episodes[0].canonical); assert.ok(read(path.join(site, 'package.json')).scripts.build.includes('check:references'));
  opts.stage = 'actual article MDX syntax'; const {compile} = await import(path.join(site, 'node_modules/@mdx-js/mdx/index.js')); await compile(fs.readFileSync(path.join(episodes[0].canonical, 'article.mdx'), 'utf8').replace(/^---[\s\S]*?\n---\n/, '').replace(/^(#{1,6} .*?)\s*\{#([\w-]+)\}[ \t]*$/gm, '$1 \\{#$2\\}'));
  opts.stage = 'all non-task canonical preservation'; const retained = preserve(opts), metadata = [...retained.metadata, ...episodes.map((e) => e.meta)];
  const series = metadata.filter((meta) => meta.series === 'leetcode' && !meta.draft && !meta.archived).sort(compare).map((meta) => meta.slug); const older = [...retained.metadata, episodes[0].original].filter((meta) => meta.series === 'leetcode' && !meta.draft && !meta.archived).sort(compare).map((meta) => meta.slug); assert.deepEqual(series, older, 'A revision preserves the complete algorithm lesson order');
  const canonical = git('ls-files', '--cached', '--others', '--exclude-standard', '--', 'episodes').trim().split(/\r?\n/).filter(Boolean).map((file) => path.join(root, file));
  const inputFingerprint = fingerprint([...filesIn(path.join(site, 'src')), ...filesIn(path.join(site, 'scripts')), ...fs.readdirSync(site, {withFileTypes: true}).filter((entry) => entry.isFile()).map((entry) => path.join(site, entry.name)), ...canonical, ...episodes.flatMap((e) => ['solution.py', 'solution.json', 'episode-config.json', 'render-result.json', 'source-sha256.json'].map((file) => path.join(e.production, file)))]);
  fs.mkdirSync(out, {recursive: true}); const receiptFile = path.join(out, 'build-receipt.json');
  if (opts.reuseBuild) {const receipt = read(receiptFile); assert.equal(receipt.inputFingerprint, inputFingerprint); assert.equal(receipt.distFingerprint, fingerprint(filesIn(dist))); assert.ok(receipt.buildPassed && receipt.datesPassed && receipt.regressionPassed);}
  else {opts.stage = 'single website build'; opts.buildInvoked = true; logged('npm', ['run', 'build'], site, path.join(out, 'build.log')); opts.stage = 'built dates'; opts.datesInvoked = true; logged('npm', ['run', 'check:dates', '--', '--built'], site, path.join(out, 'dates-built.log')); opts.stage = 'historical learning regression'; opts.regressionInvoked = true; logged('node', ['site/scripts/check-learning-path.mjs', '--complete', '--built'], root, path.join(out, 'learning-path.log')); fs.writeFileSync(receiptFile, JSON.stringify({revisionTag: opts.revisionTag, preservationBaseline: opts.preservationBase, inputFingerprint, distFingerprint: fingerprint(filesIn(dist)), checkedAtUTC: new Date().toISOString(), actualInvocations: runCounts(opts), buildPassed: true, datesPassed: true, regressionPassed: true}, null, 2) + '\n');}
  for (const e of episodes) for (const [file, expected] of [[e.meta.video, e.videoSha256], [e.meta.poster, e.posterSha256]]) assert.equal(fileSha(path.join(dist, 'episodes', e.slug, file)), expected);
  retained.builtMedia = retained.metadata.filter((meta) => !meta.draft).map((meta) => ({slug: meta.slug, files: [meta.video, meta.poster].filter(Boolean).map((file) => {const relative = `episodes/${meta.slug}/${file}`, expected = retained.allCanonicalSHA256[relative]; assert.equal(fileSha(path.join(dist, relative)), expected); return {file, sha256: expected};})}));
  const preview = opts.externalPreview ? null : cp.spawn(process.execPath, [path.join(site, 'node_modules/astro/astro.js'), 'preview', '--host', '127.0.0.1', '--port', String(opts.port)], {cwd: site, stdio: 'ignore'}); let browser; const browserChecks = [], entryChecks = [], screenshots = [];
  try {for (let n = 0; n < 100; n++) {try {if ((await fetch(opts.base)).ok) break;} catch {} assert.ok(n < 99); await new Promise((resolve) => setTimeout(resolve, 200));}
    const {chromium} = require('playwright'); browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium', args: ['--no-sandbox', '--disable-dev-shm-usage']});
    for (const [width, theme] of [[1440, 'light'], [390, 'dark']]) {const context = await browser.newContext({viewport: {width, height: 900}, colorScheme: theme}); for (const e of episodes) {opts.stage = `${e.slug} browser ${width}`; browserChecks.push(await pageCheck(context, e, opts, width, theme, series, dates, screenshots));} entryChecks.push({width, ...await entries(context, opts, series)}); await context.close();}
    const counts = read(receiptFile).actualInvocations;
    const report = {status: 'passed', checkedAtUTC: new Date().toISOString(), executor: 'Codex opening_site single revision QA', revisionTag: opts.revisionTag, preservationBaseline: opts.preservationBase, slugs: opts.slugs, inputFingerprint,
      build: {runs: counts.build, passed: true, reused: opts.reuseBuild}, datesCheck: {builtRuns: counts.dates, passed: true}, historicalRegression: {runs: counts.regression, passed: true},
      media: episodes.map((e) => ({slug: e.slug, problemNumber: e.meta.problemNumber, frames: e.frames, bodyFrames: e.bodyFrames, fps: e.fps, cues: e.cues.length, cardFrom: e.card.from, cardFrames: 150, referenceAppendix: e.appendix, referenceEvidence: e.referenceEvidence, sourceIds: e.references.sources.map((source) => source.id), videoSha256: e.videoSha256, posterSha256: e.posterSha256, dates: {createdAt: e.meta.createdAt, updatedAt: e.meta.updatedAt, publishedAt: e.meta.publishedAt}, firstRelease: e.meta.firstRelease})),
      retained, algorithmSeries: {before: older, after: series}, browserChecks, entryChecks, screenshots: screenshots.map((file) => ({path: path.relative(root, file), sha256: fileSha(file)})), actualScreenshotReviewPending: true,
      localReleaseFetch: {warnings: fs.readFileSync(path.join(out, 'build.log'), 'utf8').split(/\r?\n/).filter((line) => line.includes('[changelog]')), revisionChangelogRequiresProductionVerification: true},
      limits: ['Only this revised film has actual local muted playback/CC/seek and media HTTP checks. All other canonical bytes and built media are retained without old online media downloads.', 'Each viewport plays the early-method opening and integrated basics; captures the basics page, Python card, reference-card fullscreen and full decoded reference card; actual visual review must follow before final acceptance. References first/middle/last are paused with native CC empty.', 'Title, original creation/publication timestamps and firstRelease remain fixed. Only actual updatedAt and explicit release identity change. No full listening, ASR or learning outcome is claimed.']};
    fs.writeFileSync(path.join(__dirname, 'qa-site.json'), JSON.stringify(report, null, 2) + '\n');
    fs.writeFileSync(path.join(__dirname, 'qa-site.md'), `# 每日温度：单调栈贴题开场修订网站检查\n\n机械检查通过；显式${opts.revisionTag}，保留基线${opts.preservationBase}。实际${counts.build}次build、${counts.dates}次built日期检查、${counts.regression}次历史回归；两视口4章共8seek，开头早预告与同日期基础过程分别实际播放，字幕按真实SB句时，精确卡首/+0.0001与中末卡无native cue。完整Python/source/日期与MP4/海报HTTP SHA对应最终制作输入。最终时长按meta/publicationMetadata含资料附录；Python卡保留正文末150帧，随后单页150帧资料卡首中末暂停及真实全屏检查，title-author资料仅含原题/署名，来源与原题/摘录证据、回执及完整图文链接对应新共享检查器。\n\n原标题、ep35/LC739、createdAt、publishedAt及firstRelease v0.69.0保持，仅实质updatedAt更新。其他canonical完整SHA与算法链保持，主页算法方向/学习入口/系列/库/RSS可达。截图生成不代表视觉通过，须实际打开后记录。本次修订Release自身只关联Daily及生产HTTPS在发布后核验；本地Release fetch实况见JSON，不预记线上成功。\n`); return report;
  } finally {if (browser) await browser.close(); if (preview) preview.kill('SIGTERM');}
}
async function recorded(opts) {const file = path.join(__dirname, 'qa-site-attempts.json'), history = fs.existsSync(file) ? read(file) : {attempts: []}, attempt = {attempt: history.attempts.length + 1, status: 'running', startedAtUTC: new Date().toISOString(), revisionTag: opts.revisionTag, preservationBaseline: opts.preservationBase, slugs: opts.slugs, reuseBuild: opts.reuseBuild}; history.attempts.push(attempt); fs.writeFileSync(file, JSON.stringify(history, null, 2) + '\n'); try {const result = await run(opts); attempt.status = 'passed'; console.log(JSON.stringify({status: result.status, slugs: opts.slugs, browserCases: result.browserChecks.length, visualReviewPending: true}));} catch (error) {attempt.status = 'failed'; attempt.stage = opts.stage; attempt.exception = error.name; attempt.message = error.message; attempt.passReportWrittenByThisAttempt = false; throw error;} finally {attempt.buildInvoked = !!opts.buildInvoked; attempt.datesInvoked = !!opts.datesInvoked; attempt.regressionInvoked = !!opts.regressionInvoked; attempt.finishedAtUTC = new Date().toISOString(); history.status = `${attempt.status}_on_attempt_${attempt.attempt}`; fs.writeFileSync(file, JSON.stringify(history, null, 2) + '\n');}}
module.exports = {parse, preserve, inputs, run, titleAuthorContract};
if (require.main === module) {const opts = parse(process.argv.slice(2)); if (opts.help) console.log('After final media approval only: node qa-site.cjs --revision-tag vX.Y.Z --preservation-base SHA [--sample-frame FRAME] [--reuse-build] [--port 4247 | --base URL]. No npm ci; only Daily is revised. Requires the actual reference appendix/receipts; video total comes from publication metadata.'); else recorded(opts).catch((error) => {console.error(error); process.exitCode = 1;});}
