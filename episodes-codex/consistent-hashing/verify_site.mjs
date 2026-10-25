// After the frozen episode is copied and the site is built/served:
// node episodes-codex/consistent-hashing/verify_site.mjs [http://127.0.0.1:4321/video-studio/]
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

const require = createRequire(import.meta.url);
const {chromium} = require('playwright');
const sourceDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(sourceDir, '../..');
const slug = 'consistent-hashing';
const episodeDir = path.join(root, 'episodes', slug);
const appendixOnly = process.argv.includes('--appendix-only');
const base = new URL(process.argv.slice(2).find((argument) => /^https?:\/\//.test(argument)) ?? 'http://127.0.0.1:4321/video-studio/');
assert.ok(base.pathname.endsWith('/'), 'The base URL must end with /');
const evidenceDir = path.join(sourceDir, appendixOnly ? 'qa-site-reference-evidence' : 'qa-site-evidence');
const reportFile = path.join(sourceDir, appendixOnly ? 'qa-site-reference-browser.json' : 'qa-site-browser.json');
const report = {
  checkedAt: new Date().toISOString(), base: base.href, slug, passed: false,
  scope: appendixOnly
    ? 'Reference-appendix regression in real Chromium at two viewports: final duration, all 28 caption boundaries, four original chapter seeks, first/middle/last reference-card pauses and both article source links. Unchanged reading/navigation retain their earlier full QA.'
    : 'Built local site in real Chromium; muted playback, captions, all chapter seeks, article, directions and catalog at two viewports.',
  limitations: ['Browser playback and screenshots do not establish full-film listening or teaching quality.'],
  files: {}, viewports: [], errors: [],
};
const hash = (file) => createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const readJson = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const url = (rel = '') => new URL(rel, base).href;
let browser;

async function noPageOverflow(page, label) {
  const dimensions = await page.evaluate(() => ({viewport: innerWidth, document: document.documentElement.scrollWidth}));
  assert.ok(dimensions.document <= dimensions.viewport + 1, `${label}: page-wide horizontal overflow ${JSON.stringify(dimensions)}`);
  return dimensions;
}

async function screenshot(page, name) {
  const output = path.join(evidenceDir, name);
  await page.screenshot({path: output, animations: 'disabled'});
  return path.relative(root, output);
}

async function go(page, rel) {
  const response = await page.goto(url(rel), {waitUntil: 'networkidle'});
  assert.equal(response?.status(), 200, `Cannot open ${rel}`);
}

try {
  fs.mkdirSync(evidenceDir, {recursive: true});
  const meta = readJson(path.join(episodeDir, 'meta.json'));
  const delivery = readJson(path.join(sourceDir, 'delivery-copy.json'));
  assert.equal(meta.draft, false, 'Final site QA requires the publishable frozen episode');
  assert.equal(meta.ep, 38);
  assert.equal(meta.series, 'engineering-algorithms');
  assert.ok(meta.createdAt && meta.updatedAt && meta.publishedAt);
  assert.equal(meta.sourcePath, 'episodes-codex/consistent-hashing/remotion');
  assert.equal(meta.createdAt, delivery.metadataPreserved.createdAt);
  assert.equal(meta.updatedAt, delivery.metadataPreserved.updatedAt);
  assert.deepEqual(meta, delivery.metadata);
  assert.equal(hash(path.join(episodeDir, 'meta.json')), delivery.files['meta.json'].sha256);
  report.files['meta.json'] = delivery.files['meta.json'];
  const storyboard = readJson(path.join(episodeDir, 'storyboard.json'));
  const fps = storyboard.meta?.fps ?? 30;
  const bodyFrames = storyboard.meta.finalVideoFrames;
  const appendix = meta.referenceAppendix;
  assert.equal(appendix.kind, 'references');
  assert.equal(appendix.from, bodyFrames);
  assert.equal(appendix.durationInFrames, 150);
  assert.equal(meta.finalVideoFrames, bodyFrames + appendix.durationInFrames);
  const references = readJson(path.join(episodeDir, appendix.sources));
  const receipt = readJson(path.join(episodeDir, appendix.manifest));
  assert.equal(references.sources.length, 2);
  assert.equal(receipt.finalVideoFrames, meta.finalVideoFrames);
  assert.equal(receipt.bodyFrames, bodyFrames);
  assert.equal(receipt.outputSHA256, hash(path.join(episodeDir, meta.video)));
  report.referenceSources = references.sources.map(({id, organization, title, url}) => ({id, organization, title, url}));
  report.bodyFrames = bodyFrames;
  report.finalFrames = meta.finalVideoFrames;
  const expectedDuration = (meta.finalVideoFrames ?? storyboard.meta.finalVideoFrames) / fps;
  assert.ok(Number.isFinite(expectedDuration) && expectedDuration > 0);
  const expectedCaptions = storyboard.scenes.flatMap((scene) => scene.shots.flatMap((shot) => (shot.subtitles ?? []).map((subtitle) => subtitle.text)));
  assert.equal(expectedCaptions.length, 28, 'All 28 frozen narration captions must exist');
  const expectedCues = storyboard.scenes.flatMap((scene) => scene.shots.flatMap((shot) => shot.subtitles.map((subtitle) => ({
    text: subtitle.text,
    start: Number(((shot.from + subtitle.from) / fps).toFixed(3)),
    end: shot.from + subtitle.to + 1 === appendix.from
      ? (Math.ceil(appendix.from / fps * 1000) - 1) / 1000
      : Number(((shot.from + subtitle.to + 1) / fps).toFixed(3)),
  }))));
  const expectedChapters = storyboard.scenes.map((scene) => ({id: scene.chapterId, start: scene.from / fps}));
  assert.equal(expectedChapters.length, 4);
  const articleSource = fs.readFileSync(path.join(sourceDir, 'article.mdx'), 'utf8');
  const expectedPython = articleSource.match(/```python\s*\n([\s\S]*?)```/)?.[1].trim();
  assert.ok(expectedPython, 'The article must retain its complete Python example');
  for (const [file, detail] of Object.entries(delivery.files).filter(([file]) => file !== 'meta.json')) {
    const published = path.join(episodeDir, file);
    const source = path.join(sourceDir, detail.source ?? file);
    assert.ok(fs.existsSync(published), `Missing published ${file}`);
    assert.ok(fs.existsSync(source), `Missing production ${file}`);
    assert.equal(hash(published), hash(source), `Production and published ${file} differ`);
    report.files[file] = {sha256: hash(published), bytes: fs.statSync(published).size};
  }
  browser = await chromium.launch({headless: true, executablePath: '/usr/bin/chromium', args: ['--no-sandbox', '--disable-dev-shm-usage']});
  report.browser = browser.version();

  for (const viewport of [{width: 1440, height: 1000}, {width: 390, height: 844}]) {
    const context = await browser.newContext({viewport, reducedMotion: 'reduce'});
    const page = await context.newPage();
    const pageErrors = [];
    page.on('pageerror', (error) => pageErrors.push(String(error)));
    const result = {viewport, chapterSeeks: [], screenshots: []};
    report.viewports.push(result);

    await go(page, `episodes/${slug}/`);
    assert.equal(await page.locator('h1').innerText(), meta.title);
    assert.ok((await page.locator('.meta').innerText()).includes('创建于'));
    assert.ok((await page.locator('.meta').innerText()).includes('修改于'));
    assert.equal(await page.locator('video[controls][playsinline]').count(), 1);
    assert.equal(await page.locator(`a[href="https://github.com/linhongcun/video-studio/tree/main/${meta.sourcePath}"]`).count(), 1);
    assert.equal(await page.locator('.pager').count(), 0, 'The first independent engineering lesson must not inherit unrelated previous/next lessons');
    const chapters = await page.locator('#player').evaluate((element) => JSON.parse(element.dataset.chapters));
    assert.deepEqual(chapters.map(({id, start}) => ({id, start})), expectedChapters);
    assert.equal(chapters[0].start, 0);
    for (let i = 0; i < chapters.length; i++) {
      assert.ok(chapters[i].start < expectedDuration);
      if (i) assert.ok(chapters[i].start > chapters[i - 1].start);
      assert.equal(await page.locator(`#${chapters[i].id}`).count(), 1, `Missing article heading ${chapters[i].id}`);
    }
    result.chapters = chapters;
    await page.locator('video').evaluate((video) => { video.muted = true; video.load(); });
    await page.waitForFunction(() => document.querySelector('video').readyState >= 2);
    const media = await page.locator('video').evaluate((video) => ({duration: video.duration, width: video.videoWidth, height: video.videoHeight, error: video.error?.message ?? null}));
    assert.equal(media.error, null);
    assert.ok(Math.abs(media.duration - expectedDuration) < 0.12, `Video duration ${media.duration} differs from ${expectedDuration}`);
    assert.ok(media.width > 0 && media.height > 0);
    result.media = media;
    await page.locator('video').evaluate((video) => { video.textTracks[0].mode = 'showing'; });
    await page.waitForFunction(() => document.querySelector('video').textTracks[0]?.cues?.length > 0);
    const browserCues = await page.locator('video').evaluate((video) => [...video.textTracks[0].cues].map((cue) => ({text: cue.text, start: cue.startTime, end: cue.endTime})));
    const cueTexts = browserCues.map((cue) => cue.text);
    assert.deepEqual(cueTexts, expectedCaptions, 'Native browser captions differ from frozen narration');
    assert.deepEqual(browserCues, expectedCues, 'Native caption times differ from the frozen 30fps subtitle boundaries');
    assert.ok(browserCues.every((cue) => cue.end < appendix.from / fps), 'Body captions must end before the first reference-card frame');
    result.captionCount = cueTexts.length;
    result.browserCues = browserCues;

    await page.locator('video').focus();
    await page.keyboard.press('k');
    await page.waitForFunction(() => document.querySelector('video').currentTime > 0.25 && !document.querySelector('video').paused);
    await page.keyboard.press('k');
    await page.waitForFunction(() => document.querySelector('video').paused);
    result.keyboardPlayback = await page.locator('video').evaluate((video) => ({time: video.currentTime, paused: video.paused}));
    const selector = viewport.width >= 768 ? '.ch' : '.chip';
    for (let i = 0; i < chapters.length; i++) {
      const button = page.locator(`#player ${selector}[data-index="${i}"]`);
      await button.click();
      await page.waitForFunction(({start}) => {
        const video = document.querySelector('video');
        return video.currentTime >= start && video.currentTime < start + 1 && !video.paused;
      }, {start: chapters[i].start});
      await page.locator('video').evaluate((video) => video.pause());
      assert.equal(await button.getAttribute('aria-current'), 'true');
      result.chapterSeeks.push({id: chapters[i].id, expected: chapters[i].start, actual: await page.locator('video').evaluate((video) => video.currentTime)});
    }
    result.referenceCardPauses = [];
    for (const offset of [0, Math.floor(appendix.durationInFrames / 2), appendix.durationInFrames - 1]) {
      const frame = appendix.from + offset;
      const pause = await page.locator('video').evaluate(async (video, time) => {
        video.pause();
        const presented = new Promise((resolve) => video.requestVideoFrameCallback((_, metadata) => resolve({mediaTime: metadata.mediaTime, presentedFrames: metadata.presentedFrames})));
        const seeked = new Promise((resolve) => video.addEventListener('seeked', resolve, {once: true}));
        video.currentTime = time;
        await seeked;
        return {time: video.currentTime, paused: video.paused, presented: await presented};
      }, frame / fps);
      await page.waitForFunction(() => !document.querySelector('video').textTracks[0].activeCues?.length);
      pause.activeCues = await page.locator('video').evaluate((video) => [...video.textTracks[0].activeCues].map((cue) => cue.text));
      assert.equal(pause.paused, true);
      assert.deepEqual(pause.activeCues, []);
      const output = path.join(evidenceDir, `references-${offset}-${viewport.width}.png`);
      await page.locator('video').screenshot({path: output, animations: 'disabled'});
      result.screenshots.push(path.relative(root, output));
      result.referenceCardPauses.push({frame, offset, expectedTime: frame / fps, ...pause, screenshot: path.relative(root, output)});
    }
    await page.locator('video').evaluate(async (video) => {
      const cue = video.textTracks[0].cues[0];
      video.currentTime = (cue.startTime + cue.endTime) / 2;
      await new Promise((resolve) => video.addEventListener('seeked', resolve, {once: true}));
    });
    await page.waitForFunction(() => document.querySelector('video').textTracks[0].activeCues?.length > 0);
    result.activeCaption = await page.locator('video').evaluate((video) => [...video.textTracks[0].activeCues].map((cue) => cue.text));
    assert.ok(result.activeCaption.includes(expectedCaptions[0]));
    await page.evaluate(() => scrollTo(0, 0));
    result.episodeDimensions = await noPageOverflow(page, 'episode');
    result.screenshots.push(await screenshot(page, `episode-${viewport.width}.png`));

    if (appendixOnly) {
      assert.ok((await page.locator('.meta').innerText()).includes('视频 3:21'));
      const articleLinks = await page.locator('#article a[href]').evaluateAll((links) => links.map((link) => link.href));
      result.referenceLinks = references.sources.map((reference) => ({id: reference.id, url: reference.url, present: articleLinks.includes(new URL(reference.url).href)}));
      assert.ok(result.referenceLinks.every((reference) => reference.present));
      assert.deepEqual(pageErrors, [], 'Unexpected browser JavaScript errors');
      result.pageErrors = pageErrors;
      result.passed = true;
      await context.close();
      continue;
    }

    await page.locator('.reading-links a[href="#article"]').click();
    await page.waitForFunction(() => location.hash === '#article');
    assert.ok((await page.locator('#article').innerText()).length > 200);
    assert.equal(await page.locator('#article figure svg').count(), 2);
    result.articleDiagrams = await page.locator('#article figure svg').evaluateAll((svgs) => svgs.map((svg) => ({
      title: svg.querySelector('title')?.textContent,
      description: svg.querySelector('desc')?.textContent,
      viewBox: svg.getAttribute('viewBox'),
      width: svg.getBoundingClientRect().width,
      height: svg.getBoundingClientRect().height,
    })));
    for (const diagram of result.articleDiagrams) assert.ok(diagram.title && diagram.description && diagram.width > 0 && diagram.height > 0);
    result.svgRendering = await page.locator('#article figure svg').evaluateAll((svgs) => {
      const title = svgs[0].querySelector('text');
      const arc = svgs[0].querySelector('path[stroke="#fbbf24"]');
      const token = svgs[1].querySelector('g[font-size="25"] text');
      return {
        firstLabelFont: getComputedStyle(title).fontSize,
        firstLabelAnchor: getComputedStyle(title).textAnchor,
        takeoverArcStroke: getComputedStyle(arc).strokeWidth,
        tokenLabelFont: token ? getComputedStyle(token).fontSize : null,
        tokenLabelAnchor: token ? getComputedStyle(token).textAnchor : null,
      };
    });
    assert.deepEqual(result.svgRendering, {firstLabelFont: '24px', firstLabelAnchor: 'middle', takeoverArcStroke: '14px', tokenLabelFont: '25px', tokenLabelAnchor: 'middle'});
    assert.equal((await page.locator('#article .cb pre code').innerText()).trim(), expectedPython);
    result.pythonMatchesFrozenArticle = true;
    const articleLinks = await page.locator('#article a[href]').evaluateAll((links) => links.map((link) => link.href));
    result.referenceLinks = references.sources.map((reference) => ({id: reference.id, url: reference.url, present: articleLinks.includes(new URL(reference.url).href)}));
    assert.ok(result.referenceLinks.every((reference) => reference.present), 'Both reference-card sources need full links in the article');
    const imageFailures = await page.locator('#article img').evaluateAll((images) => images.filter((image) => !image.complete || !image.naturalWidth).map((image) => image.src));
    assert.deepEqual(imageFailures, []);
    const toc = page.locator('details.toc');
    if (!(await toc.getAttribute('open'))) {
      if (!(await toc.evaluate((element) => element.open))) await toc.locator('summary').click();
    }
    const firstToc = page.locator('[data-toc]').first();
    assert.equal(await page.locator('[data-toc]').count(), 4);
    const targetId = await firstToc.getAttribute('data-toc');
    await firstToc.click();
    await page.waitForFunction((id) => location.hash === `#${id}`, targetId);
    result.articleTarget = targetId;
    result.screenshots.push(await screenshot(page, `article-${viewport.width}.png`));
    for (let i = 0; i < 2; i++) {
      const figure = page.locator('#article figure').nth(i);
      await figure.scrollIntoViewIfNeeded();
      const output = path.join(evidenceDir, `diagram-${i + 1}-${viewport.width}.png`);
      await figure.screenshot({path: output, animations: 'disabled'});
      result.screenshots.push(path.relative(root, output));
    }
    const code = page.locator('#article .cb');
    await code.scrollIntoViewIfNeeded();
    result.screenshots.push(await screenshot(page, `code-${viewport.width}.png`));
    await page.locator('[data-open-course]').click();
    assert.equal(await page.locator('#course-directory').evaluate((element) => element.open), true);
    const courseLinks = await page.locator('#course-directory nav a').evaluateAll((links) => links.map((link) => ({href: link.getAttribute('href'), current: link.getAttribute('aria-current')})));
    assert.deepEqual(courseLinks, [{href: `/video-studio/episodes/${slug}/`, current: 'page'}]);

    await go(page);
    const homeDirections = await page.locator('.track-links h2').allTextContents();
    assert.deepEqual(homeDirections, ['系统原理', 'Agent 开发', '算法可视化', '设计模式', '趣味推理', '工程算法']);
    assert.equal(await page.locator('a.track-engineering[href="/video-studio/learn/#engineering"]').count(), 1);
    result.homeDimensions = await noPageOverflow(page, 'home');
    result.screenshots.push(await screenshot(page, `home-${viewport.width}.png`));
    await go(page, 'learn/#engineering');
    assert.equal(await page.locator('#engineering h2').innerText(), '工程算法');
    assert.equal(await page.locator('#engineering .chapter-lessons a').count(), 1);
    assert.equal(await page.locator('#engineering .chapter-lessons a').getAttribute('href'), `/video-studio/episodes/${slug}/`);
    result.learnDimensions = await noPageOverflow(page, 'learn');
    result.screenshots.push(await screenshot(page, `learn-${viewport.width}.png`));
    await go(page, 'series/engineering-algorithms/');
    assert.equal(await page.locator('h1').innerText(), '工程算法');
    assert.equal(await page.locator(`.lesson-list .lesson[href="/video-studio/episodes/${slug}/"]`).count(), 1);
    result.seriesDimensions = await noPageOverflow(page, 'series');

    await go(page, 'library/?track=engineering');
    await page.waitForFunction(() => !document.querySelector('.catalog-controls').hidden);
    assert.equal(await page.locator('select[name="track"]').inputValue(), 'engineering');
    assert.equal(await page.locator('#library-grid > ul > li:not([hidden])').count(), 1);
    assert.equal(await page.locator('#library-grid > ul > li:not([hidden]) .card').getAttribute('data-series'), 'engineering-algorithms');
    await page.locator('select[name="series"]').selectOption('engineering-algorithms');
    assert.equal(await page.locator('#library-grid > ul > li:not([hidden])').count(), 1);
    result.libraryDimensions = await noPageOverflow(page, 'library');
    assert.deepEqual(pageErrors, [], 'Unexpected browser JavaScript errors');
    result.pageErrors = pageErrors;
    result.passed = true;
    await context.close();
  }
  const rssResponse = await fetch(url('rss.xml'));
  assert.equal(rssResponse.status, 200);
  const rss = await rssResponse.text();
  assert.ok(rss.includes(`/episodes/${slug}/`));
  report.rss = {status: rssResponse.status, includesEpisode: true};
  report.passed = true;
} catch (error) {
  report.errors.push(String(error.stack ?? error));
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  fs.writeFileSync(reportFile, `${JSON.stringify(report, null, 2)}\n`);
  console.log(JSON.stringify({report: reportFile, passed: report.passed, viewports: report.viewports.length, errors: report.errors}));
}
