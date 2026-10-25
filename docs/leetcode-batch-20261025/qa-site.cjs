// Final local delivery QA for the three-episode batch. Run only after final
// canonical MP4/JPG/article/script/storyboard and real frame counts are ready:
//   node docs/leetcode-batch-20261025/qa-site.cjs
// One actual build and one historical regression serve all six browser cases.
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
const port = Number(process.env.QA_SITE_PORT || 4187);
const base = process.env.QA_SITE_BASE || `http://127.0.0.1:${port}/video-studio/`;
assert.ok(base.endsWith('/'), 'QA_SITE_BASE must end with a slash');
const siteVersion = JSON.parse(fs.readFileSync(path.join(site, 'package.json'), 'utf8')).version;
const specifications = [
  {slug: 'two-sum', ep: 25, problem: 1, sentences: 24, chapters: ['problem', 'lookup', 'distinct', 'code']},
  {slug: 'reverse-linked-list', ep: 26, problem: 206, sentences: 28, chapters: ['problem', 'save', 'reverse', 'code']},
  {slug: 'climbing-stairs', ep: 27, problem: 70, sentences: 24, chapters: ['problem', 'last-step', 'rolling', 'code']},
];
const algorithmSlugs = ['container-most-water', 'longest-substring', 'binary-search', ...specifications.map((e) => e.slug)];
const readJson = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const sha = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');
const fileSha = (file) => sha(fs.readFileSync(file));
const parseTime = (stamp) => stamp.split(':').reduce((total, n) => total * 60 + Number(n), 0);
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const epHref = (slug) => `/video-studio/episodes/${slug}/`;
const listFiles = (dir) => fs.readdirSync(dir, {withFileTypes: true}).flatMap((entry) => entry.isDirectory()
  ? listFiles(path.join(dir, entry.name)) : [path.join(dir, entry.name)]);

function inputsFor(spec) {
  const canonical = path.join(root, 'episodes', spec.slug);
  const production = path.join(root, 'episodes-codex', spec.slug);
  const meta = readJson(path.join(canonical, 'meta.json'));
  assert.equal(meta.draft, false, `${spec.slug}: final media must be approved before delivery QA`);
  assert.equal(meta.firstRelease, `v${siteVersion}`, `${spec.slug}: confirm the actual debut version before building`);
  assert.equal(meta.slug, spec.slug); assert.equal(meta.ep, spec.ep); assert.equal(meta.problemNumber, spec.problem);
  assert.equal(meta.series, 'leetcode'); assert.deepEqual(meta.platforms, {});
  assert.equal(meta.publishedAt, '2026-10-25');
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
  assert.deepEqual(storyboard.scenes.map((s) => s.chapterId), spec.chapters);
  const expectedStarts = storyboard.scenes.map((s) => s.from / fps);
  const expectedCues = storyboard.scenes.flatMap((scene) => scene.shots.flatMap((shot) => shot.subtitles.map((sub) => ({
    text: sub.text, start: (shot.from + sub.from) / fps, end: (shot.from + sub.to + 1) / fps,
  }))));
  assert.equal(expectedCues.length, spec.sentences);
  assert.ok(expectedCues.every((cue) => cue.end <= card.from / fps));
  const videoSha = fileSha(path.join(canonical, meta.video));
  const posterSha = fileSha(path.join(canonical, meta.poster));
  assert.equal(videoSha, fileSha(path.join(production, meta.video)), `${spec.slug}: canonical MP4 differs from final production`);
  assert.equal(posterSha, fileSha(path.join(production, meta.poster)), `${spec.slug}: canonical poster differs from final production`);
  const covers = Object.fromEntries(['16x9', '4x3', '3x4'].map((ratio) => {
    const name = `cover-${ratio}.jpg`, digest = fileSha(path.join(canonical, name));
    assert.equal(digest, fileSha(path.join(production, name)), `${spec.slug}: stale canonical ${name}`);
    return [name, digest];
  }));
  return {...spec, canonical, production, meta, storyboard, fps, frames, card, expectedStarts, expectedCues, videoSha, posterSha,
    covers,
    displayDuration: `${Math.floor(frames / fps / 60)}:${String(Math.floor(frames / fps % 60)).padStart(2, '0')}`,
    expectedSource: `https://github.com/linhongcun/video-studio/tree/main/${meta.sourcePath}`};
}

const fingerprintFiles = (files) => sha([...files].sort().map((file) => `${path.relative(root, file)}\0${fileSha(file)}`).join('\n'));

function inputFingerprint(episodes) {
  // Include historical canonical inputs and top-level Astro configuration: a
  // browser retry must not silently reuse a regression from another checkout.
  const canonicalRoot = path.join(root, 'episodes');
  const canonicalFiles = fs.readdirSync(canonicalRoot).filter((slug) => fs.existsSync(path.join(canonicalRoot, slug, 'meta.json')))
    .flatMap((slug) => listFiles(path.join(canonicalRoot, slug)));
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
  for (const e of specifications) assert.ok(await page.locator(`a.card[href="${epHref(e.slug)}"]`).count() > 0);
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
  return {width, seriesHrefs, libraryHrefs, visibleAlgorithms: 6, allThreeHomeCards: true, allThreeRSSItemsWithProblemNumbers: true, P01Preserved: true};
}

(async () => {
  // All readiness assertions run before the expensive build. Drafts and missing
  // or provisional frame counts therefore cannot produce a passing report.
  const episodes = specifications.map(inputsFor);
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
    const report = {status: 'passed', checkedAtUTC: new Date().toISOString(), executor: 'Codex batch_site agent',
      baseCommit: cp.execFileSync('git', ['rev-parse', 'HEAD'], {cwd: root, encoding: 'utf8'}).trim(), siteVersion, firstRelease: episodes[0].meta.firstRelease,
      inputFingerprint: fingerprint,
      build: {command: 'cd site && npm run build', passed: true, runs: 1, reusedForBrowserResume: reuseBuild, htmlFiles: listFiles(dist).filter((f) => f.endsWith('.html')).length, log: path.relative(root, path.join(output, 'build.log'))},
      historicalRegression: {command: 'node site/scripts/check-learning-path.mjs --complete --built', passed: true, runs: 1, log: path.relative(root, path.join(output, 'learning-path.log'))},
      media: episodes.map((e) => ({slug: e.slug, frames: e.frames, fps: e.fps, seconds: e.frames / e.fps, videoSha256: e.videoSha, posterSha256: e.posterSha, productionCanonicalCoverSha256: e.covers, productionCanonicalBuiltAndHTTPIdentical: true, codeCardFromFrame: e.card.from, codeCardFrames: e.card.durationInFrames})),
      browserChecks, siteEntries, screenshots: screenshots.map((f) => ({path: path.relative(root, f), sha256: fileSha(f)})),
      limits: ['Three new pages were checked at 1440px light and 390px dark; the existing historical regression ran once against the same build.',
        'Subtitle text and every serialized cue boundary were checked against the frozen storyboard within 0.001 seconds. Three samples per code card had zero active cues.',
        'Playback/pause checks used about one second of muted code-card playback per page and viewport. This is not full narration listening, ASR, algorithm proof or a beginner learning experiment.',
        'Screenshots and decoded browser frames were captured for review; capturing them alone is not a claim of human visual inspection.',
        'Actual Release/changelog selection and production HTTPS deployment checks remain the publishing task.']};
    fs.writeFileSync(path.join(__dirname, 'qa-site.json'), JSON.stringify(report, null, 2) + '\n');
    const rows = report.media.map((e) => `| ${e.slug} | ${e.frames} | ${e.seconds.toFixed(3)} | 4 | ${specifications.find((s) => s.slug === e.slug).sentences} | 5 |`).join('\n');
    fs.writeFileSync(path.join(__dirname, 'qa-site.md'), `# 三集网站集成检查\n\n执行者：${report.executor}；实际检查时间：${report.checkedAtUTC}。结果：通过，版本v${siteVersion}。\n\n同一份最终站点完成一次构建、一次历史学习路径回归，以及三页各1440/390两种视口的实际章节跳转、字幕加载、短暂静音播放与暂停。\n\n| 课程 | 帧数 | 秒数 | 章节 | 精确字幕句数 | 静态卡秒数 |\n| --- | ---: | ---: | ---: | ---: | ---: |\n${rows}\n\n六集算法顺序、三片首页/资料库/RSS入口、独立P01、源码链接、正文完整程序及原生播放器控件检查通过。三个完整视频及海报的制作源、canonical、构建产物和HTTP响应SHA一致；完整哈希、各章实际seek时间与截图索引见[机器报告](qa-site.json)。\n\n字幕逐句文字与起止时间对应冻结分镜，5秒代码卡内三个采样点均无活动cue。每页每视口只做约1秒静音代码卡播放检查，不代表全片听辨、ASR、算法证明、初学者实验或用户认可。截图已捕获，独立人工视觉复核须另记实际范围。正式Release与生产HTTPS部署核验由发布流程另记。\n`);
    console.log(JSON.stringify({status: report.status, report: path.relative(root, path.join(__dirname, 'qa-site.json')), browserCases: browserChecks.length, siteEntries, media: report.media}, null, 2));
  } finally {
    if (browser) await browser.close(); if (preview) preview.kill('SIGTERM');
  }
})().catch((error) => {console.error(error); process.exitCode = 1;});
