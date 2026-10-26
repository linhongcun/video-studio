#!/usr/bin/env node
/* Targeted post-build article QA. This never runs the whole-site checker.
 * Usage: node docs/reference-endcards/batch-10/check-articles-browser.cjs
 *          --base-url http://127.0.0.1:4350/video-studio/
 * ARTICLE_QA_BASE may supply the same URL. Actual screenshots still need review.
 */
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const {execFileSync} = require('node:child_process');
const {pathToFileURL} = require('node:url');

const ROOT = path.resolve(__dirname, '../../..');
const OUT = __dirname;
const PRIOR_REPORT = path.join(OUT, 'qa-article-browser-before-sourcequote-interaction.json');
const TARGETS = ['container-most-water', 'longest-substring', 'number-of-islands', 'permutations', 'trapping-rain-water'];
const MODES = [
  {name: 'desktop-dark', width: 1440, height: 1000, theme: 'dark', screenshots: true, mobile: false},
  {name: 'mobile-dark', width: 390, height: 844, theme: 'dark', screenshots: true, mobile: true},
];
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const sha = file => digest(fs.readFileSync(file));
const relative = file => path.relative(ROOT, file);
const normalize = text => text.replace(/\s+/g, ' ').trim();

function argumentsForRun() {
  const argv = process.argv.slice(2);
  if (argv.includes('--help') || argv.includes('-h')) {
    console.log('Usage: node docs/reference-endcards/batch-10/check-articles-browser.cjs --base-url http://127.0.0.1:PORT/video-studio/\nChecks only five startup targets in desktop-dark and mobile-dark (10 cases): actual click/touch open and close, exact quotation/metadata, Figure load/seek, strict zero overflow. Saves 10 open-panel screenshots, preserves prior 40-case report and does not replay those cases.');
    return null;
  }
  let base = process.env.ARTICLE_QA_BASE;
  for (let i = 0; i < argv.length; i++) {
    assert.equal(argv[i], '--base-url', `Unknown argument: ${argv[i]}`);
    assert.ok(argv[i + 1], '--base-url needs a URL');
    base = argv[++i];
  }
  assert.ok(base, 'Pass the final-built preview URL using --base-url or ARTICLE_QA_BASE');
  const url = new URL(base.endsWith('/') ? base : base + '/');
  assert.ok(['http:', 'https:'].includes(url.protocol) && url.pathname === '/video-studio/' && !url.search && !url.hash,
    'Expected the plain /video-studio/ preview base URL');
  return url.href;
}

function attribute(node, name) {
  const item = node.attributes?.find(a => a.type === 'mdxJsxAttribute' && a.name === name);
  if (typeof item?.value === 'string') return item.value;
  const body = item?.value?.data?.estree?.body;
  if (body?.length === 1 && body[0].type === 'ExpressionStatement' && body[0].expression.type === 'Literal') return body[0].expression.value;
  return undefined;
}

function modules(tree) {
  const quotes = [], figures = [];
  const visit = node => {
    if (node.type === 'code' || node.type === 'inlineCode') return;
    if (/^mdxJsx(?:Flow|Text)Element$/.test(node.type)) {
      if (node.name === 'SourceQuote') quotes.push(Object.fromEntries(
        ['sourceId', 'supports', 'translation'].map(key => [key, attribute(node, key)])));
      if (node.name === 'Figure') figures.push(Object.fromEntries(
        ['src', 'alt', 'caption', 'seekTo', 'chapter', 'kind', 'n'].map(key => [key, attribute(node, key)])));
    }
    for (const child of node.children ?? []) visit(child);
  };
  visit(tree);
  return {quotes, figures};
}

async function expectations(parseArticle, readArticleSources, articleImageFile) {
  const startup = read(path.join(OUT, 'startup.json'));
  assert.deepEqual(startup.selection, TARGETS, 'Unexpected batch-10 article scope');
  return TARGETS.map(slug => {
    const dir = path.join(ROOT, 'episodes', slug);
    const articleFile = path.join(dir, 'article.mdx');
    // parseArticle handles both YAML-frontmatter MDX and Islands' original
    // Markdown title. There is deliberately no one-H1 or frontmatter gate.
    const props = modules(parseArticle(fs.readFileSync(articleFile, 'utf8')));
    assert.ok(props.quotes.length && props.figures.length, `${slug}: missing real article modules`);
    const sources = readArticleSources(slug, {repoRoot: ROOT});
    for (const quote of props.quotes) {
      const source = sources.get(quote.sourceId);
      assert.ok(source?.quotation?.text && source.quotation.locator, `${slug}: missing quote metadata ${quote.sourceId}`);
    }
    for (const figure of props.figures) {
      figure.file = articleImageFile(slug, figure.src, {repoRoot: ROOT});
      figure.sha256 = sha(figure.file);
      const asset = figure.src.slice('/video-studio/'.length);
      for (const tree of ['site/public', 'site/dist']) {
        assert.equal(sha(path.join(ROOT, tree, asset)), figure.sha256, `${slug}: ${tree} figure differs`);
      }
    }
    const files = ['meta.json', 'article.mdx', 'references.json', 'article-sources.json']
      .filter(name => fs.existsSync(path.join(dir, name)))
      .map(name => ({path: relative(path.join(dir, name)), sha256: sha(path.join(dir, name))}));
    const html = path.join(ROOT, 'site/dist/episodes', slug, 'index.html');
    return {slug, dir, ...props, sources, meta: read(path.join(dir, 'meta.json')),
      storyboard: read(path.join(dir, 'storyboard.json')), inputFiles: files,
      html: {path: relative(html), sha256: sha(html)}};
  });
}

async function screenshot(locator, filename, kind, result, directory) {
  const file = path.join(directory, filename);
  await locator.screenshot({path: file});
  result.screenshots.push({path: relative(file), kind, sha256: sha(file), actuallyViewed: false});
}

async function runCase(browser, base, expected, mode, directory) {
  const {slug} = expected;
  const result = {slug, mode: mode.name, viewport: {width: mode.width, height: mode.height},
    theme: mode.theme, screenshotMode: mode.screenshots, quotes: [], figures: [], screenshots: [], errors: [], passed: false};
  const context = await browser.newContext({viewport: result.viewport, colorScheme: mode.theme,
    reducedMotion: 'reduce', deviceScaleFactor: 1, isMobile: mode.mobile, hasTouch: mode.mobile});
  await context.addInitScript(theme => localStorage.setItem('vs:theme', theme), mode.theme);
  const page = await context.newPage();
  page.setDefaultTimeout(15000);
  page.on('pageerror', error => result.errors.push(error.message));
  const imageResponses = new Map();
  const imagePaths = new Set(expected.figures.map(figure => figure.src));
  page.on('response', response => {
    const pathname = new URL(response.url()).pathname;
    if (!imagePaths.has(pathname)) return;
    imageResponses.set(pathname, response.body().then(bytes => ({status: response.status(), bytes: bytes.length,
      sha256: digest(bytes), url: response.url()})).catch(error => ({error: error.message})));
  });
  try {
    const url = `${base}episodes/${slug}/`;
    const response = await page.goto(url, {waitUntil: 'load'});
    assert.equal(response.status(), 200);
    assert.equal(digest(await response.body()), expected.html.sha256, `${slug}: served HTML differs from final dist`);
    await page.evaluate(() => document.fonts.ready);
    const theme = await page.evaluate(() => ({active: document.documentElement.dataset.theme, preference: localStorage.getItem('vs:theme')}));
    assert.equal(theme.active, mode.theme);
    assert.equal(theme.preference, mode.theme);
    result.actualTheme = theme;
    const quotes = page.locator('#article .source-quote');
    assert.equal(await quotes.count(), expected.quotes.length);
    await page.waitForFunction(() => [...document.querySelectorAll('[data-source-quote]')].every(node => node.dataset.sourceReady === 'true'));
    assert.equal(await page.locator('aside[data-source-panel]:popover-open').count(), 0);
    for (let i = 0; i < expected.quotes.length; i++) {
      const props = expected.quotes[i], source = expected.sources.get(props.sourceId);
      const trigger = page.locator(`button[data-source-trigger="${props.sourceId}"]`);
      const node = page.locator(`aside[data-source-panel="${props.sourceId}"]`);
      assert.equal(await trigger.count(), 1);
      assert.equal(await node.count(), 1);
      assert.equal(await trigger.getAttribute('aria-label'), `查看原文与出处：${source.title}`);
      assert.equal(await trigger.getAttribute('aria-controls'), await node.getAttribute('id'));
      assert.equal(await trigger.getAttribute('popovertarget'), await node.getAttribute('id'));
      await trigger.scrollIntoViewIfNeeded();
      assert.ok(await trigger.isVisible());
      assert.equal(await trigger.getAttribute('aria-expanded'), 'false');
      assert.equal(await node.isVisible(), false);
      assert.equal(await node.locator('blockquote').isVisible(), false);
      const collapsed = await trigger.evaluate(button => ({inParagraph: !!button.closest('p'),
        rootHeight: [...document.querySelectorAll('[data-source-quote]')].find(root => root.dataset.sourceQuote === button.dataset.sourceTrigger).getBoundingClientRect().height}));
      assert.ok(collapsed.inParagraph && collapsed.rootHeight <= 48, `${slug}: citation is not a compact paragraph entry`);
      const flow = () => page.locator('#article > p, #article > h2, #article > h3, #article > figure').evaluateAll(nodes => nodes.map(node => {
        const rect = node.getBoundingClientRect(); return {top: rect.top + scrollY, height: rect.height};
      }));
      const before = await flow();
      if (mode.mobile) await trigger.tap(); else await trigger.click();
      await page.waitForFunction(id => document.querySelector(`aside[data-source-panel="${id}"]`)?.matches(':popover-open')
        && document.querySelector(`button[data-source-trigger="${id}"]`)?.getAttribute('aria-expanded') === 'true', props.sourceId);
      assert.ok(await node.isVisible());
      assert.equal(await node.getAttribute('data-source-state'), 'pinned');
      assert.equal(await page.locator('aside[data-source-panel]:popover-open').count(), 1);
      const box = await node.boundingBox();
      assert.ok(box && box.x >= 0 && box.y >= 0 && box.x + box.width <= mode.width && box.y + box.height <= mode.height,
        `${slug}: citation panel exceeds viewport`);
      const openMetrics = await page.evaluate(() => ({documentWidth: document.documentElement.scrollWidth, viewportWidth: innerWidth}));
      assert.ok(openMetrics.documentWidth <= openMetrics.viewportWidth);
      const actual = await node.evaluate(element => {
        const text = selector => element.querySelector(selector)?.textContent;
        const style = getComputedStyle(element.querySelector('blockquote'));
        return {id: element.dataset.sourcePanel, text: text('blockquote'), title: text('cite a'),
          url: element.querySelector('cite a')?.href, cite: element.querySelector('blockquote')?.getAttribute('cite'),
          identity: text('.source-identity'), locator: text('.source-location'),
          checkedAt: element.querySelector('.source-access time')?.dateTime,
          support: text('.source-support'), translation: text('.source-translation'),
          links: [...element.querySelectorAll('a')].map(a => a.href), width: element.getBoundingClientRect().width,
          quoteFontPixels: parseFloat(style.fontSize), lineHeightPixels: parseFloat(style.lineHeight),
          horizontalOverflow: element.scrollWidth - element.clientWidth,
          scrollHeight: element.scrollHeight, clientHeight: element.clientHeight};
      });
      assert.equal(actual.id, props.sourceId);
      assert.equal(actual.text, source.quotation.text, `${slug}: original quote changed`);
      assert.equal(actual.title, source.title);
      assert.equal(actual.url, new URL(source.url).href);
      assert.equal(actual.cite, source.verification.sourceUrl ?? source.url);
      assert.equal(normalize(actual.identity), `${source.author ?? source.organization} · ${source.version}`);
      assert.equal(actual.locator, `原文位置：${source.quotation.locator}`);
      assert.equal(actual.checkedAt, source.verification.checkedAt);
      assert.equal(normalize(actual.support), normalize(`编者说明 ${props.supports}`));
      if (props.translation) assert.equal(normalize(actual.translation), normalize(`译文 ${props.translation}`));
      else assert.equal(actual.translation, undefined);
      for (const link of new Set([source.url, source.verification.sourceUrl].filter(Boolean))) {
        assert.ok(actual.links.includes(new URL(link).href), `${slug}: source/fixed link missing`);
      }
      assert.ok(actual.width > 250 && actual.width <= mode.width && actual.horizontalOverflow <= 1);
      assert.ok(actual.quoteFontPixels >= 14 && actual.lineHeightPixels >= actual.quoteFontPixels * 1.3);
      const sourceLink = node.locator('cite a');
      await sourceLink.scrollIntoViewIfNeeded();
      const sourceLinkHit = await sourceLink.evaluate(link => {
        const rect = link.getClientRects()[0], x = rect.x + Math.min(rect.width / 2, 80), y = rect.y + rect.height / 2;
        return {expected: link.href, actual: document.elementFromPoint(x, y)?.closest('a')?.href};
      });
      assert.equal(sourceLinkHit.actual, sourceLinkHit.expected);
      await node.evaluate(panel => { panel.scrollTop = 0; });
      if (mode.screenshots) await screenshot(node, `${slug}-${mode.name}-quote-${i + 1}.png`, 'quote', result, directory);
      const close = node.getByRole('button', {name: '关闭原文与出处'});
      if (mode.mobile) await close.tap(); else await close.click();
      await page.waitForFunction(id => !document.querySelector(`aside[data-source-panel="${id}"]`)?.matches(':popover-open')
        && document.querySelector(`button[data-source-trigger="${id}"]`)?.getAttribute('aria-expanded') === 'false', props.sourceId);
      assert.equal(await node.isVisible(), false);
      const after = await flow();
      assert.equal(after.length, before.length);
      for (let j = 0; j < before.length; j++) {
        assert.ok(Math.abs(after[j].top - before[j].top) < 1 && Math.abs(after[j].height - before[j].height) < 1,
          `${slug}: source panel changed article layout`);
      }
      result.quotes.push({...actual, metadataSourceId: source.id, exactOriginalTextAndMetadataMatch: true,
        interaction: {collapsed, control: mode.mobile ? 'actual touchscreen tap' : 'actual mouse click',
          openedPinned: true, closedWithLabelledButton: true, layoutShift: false, panelBounds: box,
          openDocumentMetrics: openMetrics, sourceLinkHit, externalSourceNavigationPerformed: false}});
    }
    assert.equal(await page.locator('#article figure.fig').count(), expected.figures.length);
    const fps = expected.storyboard.meta.fps ?? 30;
    const bodyEnd = expected.meta.referenceAppendix?.from
      ?? expected.storyboard.meta.unvoicedEndCard?.from ?? expected.meta.finalVideoFrames;
    for (let i = 0; i < expected.figures.length; i++) {
      const props = expected.figures[i];
      let figure = page.locator('#article figure.fig').nth(i);
      let image = figure.locator('img');
      await image.scrollIntoViewIfNeeded();
      await image.evaluate(node => node.decode());
      const actual = await image.evaluate(node => ({src: new URL(node.currentSrc).pathname,
        naturalWidth: node.naturalWidth, naturalHeight: node.naturalHeight, alt: node.alt,
        width: node.getBoundingClientRect().width, height: node.getBoundingClientRect().height,
        complete: node.complete, imageHref: node.parentElement.getAttribute('href'),
        openLabel: node.parentElement.getAttribute('aria-label')}));
      assert.equal(actual.src, props.src);
      assert.equal(actual.imageHref, props.src);
      assert.equal(actual.alt, props.alt);
      assert.equal(actual.openLabel, `打开原图：${props.alt}`);
      assert.ok(actual.complete && actual.naturalWidth >= 640 && actual.naturalHeight > 0);
      assert.ok(actual.width >= 250 && actual.width <= mode.width && actual.height > 0);
      assert.ok(Math.abs(actual.width / actual.height - actual.naturalWidth / actual.naturalHeight) < .02);
      const served = await imageResponses.get(props.src);
      assert.ok(served && !served.error, `${slug}: loaded-image response unavailable: ${JSON.stringify(served)}`);
      assert.equal(served.status, 200);
      assert.equal(served.sha256, props.sha256, `${slug}: actual loaded image differs from local original`);
      const caption = figure.locator('figcaption');
      assert.ok(await caption.isVisible());
      const text = normalize(await caption.innerText());
      assert.ok(text.includes(normalize(props.caption)), `${slug}: figure caption changed`);
      assert.equal(await caption.locator('a').filter({hasText: '查看大图'}).getAttribute('href'), props.src);
      const captionStyle = await caption.evaluate(node => ({font: parseFloat(getComputedStyle(node).fontSize),
        overflow: node.scrollWidth - node.clientWidth}));
      assert.ok(captionStyle.font >= 12 && captionStyle.overflow <= 1);
      const record = {...actual, caption: text, actualLoadedImage: served,
        originalImageNavigationRetested: false, priorOriginalImageAndVisualEvidence: relative(PRIOR_REPORT),
        kind: props.kind ?? 'video'};
      if (record.kind === 'video') {
        assert.ok(Number.isFinite(props.seekTo) && props.seekTo >= 0 && props.seekTo < bodyEnd / fps,
          `${slug}: Figure timestamp is outside the actual lecture body`);
        const seek = figure.locator('[data-seek-time]');
        assert.equal(Number(await seek.getAttribute('data-seek-time')), props.seekTo);
        const chapters = await page.locator('#player').evaluate(node => JSON.parse(node.dataset.chapters));
        let chapter = chapters[0];
        for (const item of chapters) if (item.start <= props.seekTo + .05) chapter = item;
        if (props.chapter) assert.equal(chapter.id, props.chapter, `${slug}: Figure chapter and timestamp disagree`);
        await page.locator('#player video').evaluate(video => {
          video.muted = true;
          video.pause();
          video.addEventListener('seeked', () => video.pause(), {once: true});
        });
        await seek.click();
        await page.waitForFunction(time => {
          const v = document.querySelector('#player video');
          return v && !v.seeking && v.paused && v.readyState >= 2 && Math.abs(v.currentTime - time) < .1;
        }, props.seekTo);
        const state = await page.locator('#player video').evaluate(video => ({time: video.currentTime,
          paused: video.paused, error: video.error?.message ?? null,
          activeChapter: document.querySelector('#player .ch[aria-current="true"]')?.dataset.id}));
        assert.ok(!state.error && state.paused && Math.abs(state.time - props.seekTo) <= 1 / fps + .05);
        assert.equal(state.activeChapter, chapter.id);
        assert.equal(Number(new URL(page.url()).hash.slice(3)), props.seekTo);
        record.seek = {expectedSeconds: props.seekTo, expectedChapter: chapter.id, ...state,
          continuousPlaybackTestPerformed: false};
      }
      result.figures.push(record);
    }
    result.documentMetrics = await page.evaluate(() => ({documentWidth: document.documentElement.scrollWidth,
      viewportWidth: innerWidth}));
    result.horizontalOverflow = result.documentMetrics.documentWidth - result.documentMetrics.viewportWidth;
    assert.ok(result.documentMetrics.documentWidth <= result.documentMetrics.viewportWidth,
      `${slug}: page overflows horizontally`);
    assert.deepEqual(result.errors, []);
    result.passed = true;
  } catch (error) {
    result.failure = {message: error.message, stack: error.stack};
  } finally {
    await context.close();
  }
  return result;
}

async function main() {
  const base = argumentsForRun();
  if (!base) return;
  const report = {task: 'reference-batch10-article-browser', checkedAtUTC: new Date().toISOString(), base,
    targets: TARGETS, expectedCaseCount: TARGETS.length * MODES.length, cases: [], failures: [],
    screenshotModes: MODES.filter(m => m.screenshots).map(m => m.name),
    assertionOnlyModes: MODES.filter(m => !m.screenshots).map(m => m.name),
    scope: 'Five published batch-10 articles in desktop-dark/mobile-dark only: collapsed SourceQuote entry, actual mouse/touch open/close and exact original text/identity, Figure image/caption/timestamp, strict zero overflow. Prior 40 browser cases and figure visuals remain historical evidence; they are not replayed.',
    status: 'running', automatedAssertionsPassed: false, passed: false,
    visualReview: 'Pending actual view_image inspection of 10 newly saved open SourceQuote panel screenshots.',
    limitations: ['Chromium viewport/theme emulation, not a physical-device or reader comprehension study.',
      'This incremental run uses dark themes only. Prior light-theme and figure screenshots remain tied to their historical candidates.',
      'Citation URLs and their hit targets are checked against metadata without external navigation. Original-image navigation was checked in the preserved prior report and is not repeated.',
      'The shared citation interaction suite targets hover/keyboard/Escape/outside click/multiple-source/no-JS/fallback behavior. This batch repeats only actual desktop click/mobile tap open, source data and labelled-button close; it does not claim to rerun the complete shared suite.',
      'Native figure links seek and pause as soon as seeking completes. No continuous/tail playback, old media QA replay or explicit full MP4 GET is performed.',
      'CSS font/width checks do not replace actual screenshot review.'],
  };
  let browser;
  const stamp = report.checkedAtUTC.replace(/[:.]/g, '-');
  const directory = path.join(OUT, 'article-browser', stamp);
  fs.mkdirSync(directory, {recursive: true});
  try {
    const {parseArticle} = await import(pathToFileURL(path.join(ROOT, 'site/scripts/check-articles.mjs')).href);
    const {readArticleSources, articleImageFile} = await import(pathToFileURL(path.join(ROOT, 'site/scripts/article-sources.mjs')).href);
    const expected = await expectations(parseArticle, readArticleSources, articleImageFile);
    report.version = read(path.join(ROOT, 'site/package.json')).version;
    assert.equal(report.version, '0.76.1', 'Run only after the final 0.76.1 build');
    report.commit = execFileSync('git', ['rev-parse', 'HEAD'], {cwd: ROOT, encoding: 'utf8'}).trim();
    const previous = read(PRIOR_REPORT);
    assert.ok(previous.passed && previous.totalActualBrowserCasesExecuted === 40, 'Missing preserved 40-case evidence');
    report.historicalEvidence = {report: relative(PRIOR_REPORT), sha256: sha(PRIOR_REPORT),
      version: previous.version, commit: previous.commit, actualBrowserCasesExecuted: 40,
      executionHistory: previous.executionHistory, notReexecutedThisRun: true};
    report.upstreamInteractionQA = ['docs/citation-interaction/check-ui.cjs', 'docs/citation-interaction/browser-review.json']
      .filter(file => fs.existsSync(path.join(ROOT, file))).map(file => ({path: file, sha256: sha(path.join(ROOT, file)), rerunByThisScript: false}));
    report.startupBaseCommit = read(path.join(OUT, 'startup.json')).baseCommit;
    report.inputs = expected.map(({slug, inputFiles, html}) => ({slug, inputFiles, html}));
    report.moduleInputs = ['site/src/components/SourceQuote.astro', 'site/src/scripts/source-quotes.ts', 'site/src/components/Figure.astro', 'docs/article-style.md']
      .map(file => ({path: file, sha256: sha(path.join(ROOT, file))}));
    report.expectedScreenshotCount = expected.reduce((n, item) => n + item.quotes.length, 0) * MODES.length;
    const {chromium} = require('playwright');
    browser = await chromium.launch({executablePath: '/usr/bin/chromium', headless: true,
      args: ['--no-sandbox', '--disable-dev-shm-usage']});
    report.browserVersion = browser.version();
    for (const mode of MODES) for (const item of expected) {
      const result = await runCase(browser, base, item, mode, directory);
      report.cases.push(result);
      if (!result.passed) report.failures.push({slug: result.slug, mode: result.mode, ...result.failure});
      console.log(JSON.stringify({slug: result.slug, mode: result.mode, passed: result.passed,
        screenshots: result.screenshots.length, ...(result.failure ? {error: result.failure.message} : {})}));
    }
    report.screenshots = report.cases.flatMap(c => c.screenshots);
    report.currentRunActualBrowserCasesExecuted = report.cases.length;
    report.totalActualBrowserCasesExecuted = 40 + report.cases.length;
    report.automatedAssertionsPassed = report.cases.length === report.expectedCaseCount && !report.failures.length
      && report.screenshots.length === report.expectedScreenshotCount;
    report.status = report.automatedAssertionsPassed ? 'automated-passed-visual-pending' : 'failed';
  } catch (error) {
    report.failures.push({message: error.message, stack: error.stack});
    report.status = 'failed';
  } finally {
    if (browser) await browser.close();
    report.finishedAtUTC = new Date().toISOString();
    fs.writeFileSync(path.join(OUT, 'qa-article-browser.json'), JSON.stringify(report, null, 2) + '\n');
  }
  console.log(JSON.stringify({status: report.status, cases: report.cases.length,
    screenshots: report.screenshots?.length ?? 0, report: relative(path.join(OUT, 'qa-article-browser.json'))}));
  if (!report.automatedAssertionsPassed) process.exitCode = 1;
}

if (require.main === module) main().catch(error => { console.error(error); process.exitCode = 1; });
