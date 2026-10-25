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
const base = new URL(process.argv[2] ?? 'http://127.0.0.1:4321/video-studio/');
assert.ok(base.pathname.endsWith('/'), 'The base URL must end with /');
const evidenceDir = path.join(sourceDir, 'qa-site-evidence');
const reportFile = path.join(sourceDir, 'qa-site-browser.json');
const report = {
  checkedAt: new Date().toISOString(), base: base.href, slug, passed: false,
  scope: 'Built local site in real Chromium; muted playback, captions, all chapter seeks, article, directions and catalog at two viewports.',
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
  assert.equal(meta.draft, false, 'Final site QA requires the publishable frozen episode');
  assert.equal(meta.ep, 38);
  assert.equal(meta.series, 'engineering-algorithms');
  assert.ok(meta.createdAt && meta.updatedAt && meta.publishedAt);
  assert.equal(meta.sourcePath, 'episodes-codex/consistent-hashing/remotion');
  const storyboard = readJson(path.join(episodeDir, 'storyboard.json'));
  const fps = storyboard.meta?.fps ?? 30;
  const expectedDuration = (meta.finalVideoFrames ?? storyboard.meta.finalVideoFrames) / fps;
  assert.ok(Number.isFinite(expectedDuration) && expectedDuration > 0);
  const expectedCaptions = storyboard.scenes.flatMap((scene) => scene.shots.flatMap((shot) => (shot.subtitles ?? []).map((subtitle) => subtitle.text)));
  assert.ok(expectedCaptions.length, 'Frozen narration captions must exist');
  for (const file of ['meta.json', 'article.mdx', 'script.md', 'storyboard.json', meta.video, meta.poster, 'cover-4x3.jpg', 'cover-3x4.jpg']) {
    const published = path.join(episodeDir, file);
    const source = path.join(sourceDir, file);
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
    assert.ok(chapters.length > 0);
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
    const cueTexts = await page.locator('video').evaluate((video) => [...video.textTracks[0].cues].map((cue) => cue.text));
    assert.deepEqual(cueTexts, expectedCaptions, 'Native browser captions differ from frozen narration');
    result.captionCount = cueTexts.length;

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

    await page.locator('.reading-links a[href="#article"]').click();
    await page.waitForFunction(() => location.hash === '#article');
    assert.ok((await page.locator('#article').innerText()).length > 200);
    const imageFailures = await page.locator('#article img').evaluateAll((images) => images.filter((image) => !image.complete || !image.naturalWidth).map((image) => image.src));
    assert.deepEqual(imageFailures, []);
    const toc = page.locator('details.toc');
    if (!(await toc.getAttribute('open'))) {
      if (!(await toc.evaluate((element) => element.open))) await toc.locator('summary').click();
    }
    const firstToc = page.locator('[data-toc]').first();
    const targetId = await firstToc.getAttribute('data-toc');
    await firstToc.click();
    await page.waitForFunction((id) => location.hash === `#${id}`, targetId);
    result.articleTarget = targetId;
    result.screenshots.push(await screenshot(page, `article-${viewport.width}.png`));
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
    assert.equal(await page.locator(`a[href="/video-studio/episodes/${slug}/"]`).count(), 1);
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
