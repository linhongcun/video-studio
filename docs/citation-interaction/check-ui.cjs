// Independent browser QA. Build and start Astro preview separately before running.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const assert = require('node:assert/strict');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '../..');
const out = process.env.CITATION_QA_OUTPUT ? path.resolve(root, process.env.CITATION_QA_OUTPUT) : __dirname;
const base = process.env.CITATION_QA_BASE || 'http://127.0.0.1:4323/video-studio/';
const shots = path.join(out, 'screenshots');
const read = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const attr = (name, value) => `[${name}=${JSON.stringify(value)}]`;
const triggerFor = (page, id) => page.locator('button' + attr('data-source-trigger', id));
const panelFor = (page, id) => page.locator('aside[popover="auto"]' + attr('data-source-panel', id));
const url = (slug) => `${base}episodes/${slug}/`;
const openSelector = 'aside[data-source-panel]:popover-open';
const results = [], failures = [];
const caseFilter = process.env.CITATION_QA_CASE_FILTER ? new RegExp(process.env.CITATION_QA_CASE_FILTER) : null;
const reportName = process.env.CITATION_QA_REPORT || 'browser-review';
assert.ok(/^[a-zA-Z0-9-]+$/.test(reportName));
fs.mkdirSync(shots, {recursive: true});

async function runCase(name, action, page) {
  if (caseFilter && !caseFilter.test(name)) return;
  try {
    const detail = await action();
    results.push({name, ...detail});
    console.log(`PASS ${name}`);
  } catch (error) {
    failures.push({name, message: error.message, stack: error.stack?.split('\n').slice(0, 4)});
    console.error(`FAIL ${name}: ${error.message}`);
    if (page) await page.screenshot({path: path.join(shots, `failure-${name.replace(/[^a-zA-Z0-9-]/g, '-')}.png`)}).catch(() => {});
  }
}

async function ensureOpen(page, id) {
  await page.waitForFunction((id) => document.querySelector(`aside[data-source-panel="${id}"]`)?.matches(':popover-open'), id);
  assert.equal(await triggerFor(page, id).getAttribute('aria-expanded'), 'true');
  assert.equal(await page.locator(openSelector).count(), 1);
}

async function ensureClosed(page, id) {
  await page.waitForFunction((id) => !document.querySelector(`aside[data-source-panel="${id}"]`)?.matches(':popover-open')
    && document.querySelector(`button[data-source-trigger="${id}"]`)?.getAttribute('aria-expanded') === 'false', id);
  assert.equal(await triggerFor(page, id).getAttribute('aria-expanded'), 'false');
}

async function bounds(page, id) {
  const rect = await panelFor(page, id).boundingBox();
  const viewport = page.viewportSize();
  assert.ok(rect && rect.width > 200 && rect.height > 80);
  assert.ok(rect.x >= 3 && rect.y >= 3, `panel starts outside viewport: ${JSON.stringify(rect)}`);
  assert.ok(rect.x + rect.width <= viewport.width - 3, `panel right edge exceeds viewport: ${JSON.stringify(rect)}`);
  assert.ok(rect.y + rect.height <= viewport.height - 3, `panel bottom exceeds viewport: ${JSON.stringify(rect)}`);
  return rect;
}

async function flow(page) {
  return page.locator('#article > p, #article > h2, #article > h3, #article > figure:not([data-source-quote])').evaluateAll((nodes) => nodes.map((node) => {
    const rect = node.getBoundingClientRect();
    return {top: rect.top + scrollY, height: rect.height};
  }));
}

function noShift(before, after) {
  assert.equal(before.length, after.length);
  for (let i = 0; i < before.length; i++) {
    assert.ok(Math.abs(before[i].top - after[i].top) < 1, `article block ${i} shifted vertically`);
    assert.ok(Math.abs(before[i].height - after[i].height) < 1, `article block ${i} changed height`);
  }
}

async function positionTLS(page) {
  await page.locator('#tls').evaluate((node) => window.scrollTo(0, node.getBoundingClientRect().top + scrollY - 100));
}

async function closeButton(page, id) {
  const panel = panelFor(page, id);
  const button = panel.getByRole('button', {name: /关闭/}).first();
  assert.equal(await button.count(), 1, 'panel needs a labelled close button');
  return button;
}

async function verifyLinkHit(page, id) {
  const link = panelFor(page, id).locator('cite a').first();
  await link.scrollIntoViewIfNeeded();
  const box = await link.boundingBox();
  assert.ok(box);
  const point = {x: box.x + Math.min(box.width / 2, 80), y: box.y + box.height / 2};
  const hit = await page.evaluate(({x, y}) => document.elementFromPoint(x, y)?.closest('a')?.href, point);
  assert.equal(hit, await link.getAttribute('href'));
  return {href: hit, point};
}

(async () => {
  const {readArticleSources} = await import(pathToFileURL(path.join(root, 'site/scripts/article-sources.mjs')).href);
  const {parseArticle} = await import(pathToFileURL(path.join(root, 'site/scripts/check-articles.mjs')).href);
  const episodes = fs.readdirSync(path.join(root, 'episodes')).filter((slug) => {
    const file = path.join(root, 'episodes', slug, 'meta.json');
    return fs.existsSync(file) && !read(file).draft && !read(file).archived;
  }).sort();
  const requestedSlugs = (process.env.CITATION_QA_SLUGS || '').split(',').map((slug) => slug.trim()).filter(Boolean);
  assert.ok(requestedSlugs.every((slug) => episodes.includes(slug)), 'CITATION_QA_SLUGS must name current published episodes');
  const pageEpisodes = requestedSlugs.length ? episodes.filter((slug) => requestedSlugs.includes(slug)) : episodes;
  const expected = new Map(episodes.map((slug) => {
    const tree = parseArticle(fs.readFileSync(path.join(root, 'episodes', slug, 'article.mdx'), 'utf8'));
    const ids = [];
    const walk = (node) => {
      if (node.type === 'code' || node.type === 'inlineCode') return;
      if (node.name === 'SourceQuote') ids.push(node.attributes.find((item) => item.name === 'sourceId').value);
      for (const child of node.children ?? []) walk(child);
    };
    walk(tree);
    return [slug, {ids, sources: readArticleSources(slug)}];
  }));
  const browser = await chromium.launch({executablePath: '/usr/bin/chromium', args: ['--no-sandbox', '--disable-dev-shm-usage']});
  try {
    // Read all rendered pages in two representative modes. No hover is needed to
    // inspect saved text: popover contents must remain in the original HTML.
    for (const mode of [{width: 1440, height: 1000, theme: 'light', mobile: false}, {width: 390, height: 844, theme: 'dark', mobile: true}]) {
      const context = await browser.newContext({viewport: {width: mode.width, height: mode.height}, colorScheme: mode.theme, reducedMotion: 'reduce', isMobile: mode.mobile, hasTouch: mode.mobile});
      await context.addInitScript((theme) => localStorage.setItem('vs:theme', theme), mode.theme);
      const page = await context.newPage();
      page.setDefaultTimeout(7000);
      page.setDefaultNavigationTimeout(20000);
      for (const slug of pageEpisodes) await runCase(`all-${slug}-${mode.width}`, async () => {
        const errors = [];
        const listener = (error) => errors.push(error.message);
        page.on('pageerror', listener);
        try {
          await page.mouse.move(0, 0);
          assert.equal((await page.goto(url(slug), {waitUntil: 'load'})).status(), 200);
          const ids = expected.get(slug).ids;
          assert.equal(await page.locator('[data-source-quote]').count(), ids.length);
          assert.equal(await page.locator(openSelector).count(), 0);
          const positions = [];
          for (const id of ids) {
            const trigger = triggerFor(page, id), panel = panelFor(page, id);
            assert.equal(await trigger.count(), 1);
            assert.equal(await panel.count(), 1);
            assert.equal(await trigger.getAttribute('aria-expanded'), 'false');
            assert.equal(await trigger.getAttribute('aria-controls'), await panel.getAttribute('id'));
            assert.equal(await trigger.getAttribute('popovertarget'), await panel.getAttribute('id'));
            assert.equal(await panel.isVisible(), false);
            const source = expected.get(slug).sources.get(id);
            assert.equal((await panel.locator('blockquote').textContent()).trim(), source.quotation.text.trim());
            assert.equal(await panel.locator('cite a').textContent(), source.title);
            assert.equal(await panel.locator('cite a').getAttribute('href'), source.url);
            const text = await panel.textContent();
            assert.ok(text.includes(source.quotation.locator));
            assert.ok(text.includes(source.verification.checkedAt));
            const position = await trigger.evaluate((node) => {
              const sourceId = node.dataset.sourceTrigger;
              const sourceRoot = [...document.querySelectorAll('[data-source-quote]')].find((item) => item.dataset.sourceQuote === sourceId);
              const paragraph = node.closest('p');
              return {rootHeight: sourceRoot.getBoundingClientRect().height, inParagraph: !!paragraph};
            });
            assert.ok(position.rootHeight <= 48, `${slug}/${id}: collapsed citation takes card height ${position.rootHeight}`);
            if (slug !== 'strategy-pattern') assert.ok(position.inParagraph, `${slug}/${id}: trigger is not beside its paragraph`);
            positions.push(position);
          }
          const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
          assert.ok(overflow <= 1, `horizontal overflow ${overflow}`);
          assert.deepEqual(errors, []);
          return {slug, ...mode, excerpts: ids.length, positions, overflow};
        } finally { page.off('pageerror', listener); }
      }, page);
      await context.close();
    }

    for (const theme of ['light', 'dark']) {
      const context = await browser.newContext({viewport: {width: 1440, height: 1000}, colorScheme: theme, reducedMotion: 'reduce'});
      await context.addInitScript((value) => localStorage.setItem('vs:theme', value), theme);
      const page = await context.newPage();
      page.setDefaultTimeout(7000);
      page.setDefaultNavigationTimeout(20000);
      await page.goto(url('http-request'), {waitUntil: 'load'});
      const id = 'R4';
      await positionTLS(page);
      await page.screenshot({path: path.join(shots, `tls-collapsed-1440-${theme}.png`)});
      await runCase(`desktop-hover-pin-${theme}`, async () => {
        const before = await flow(page);
        const trigger = triggerFor(page, id), panel = panelFor(page, id);
        await trigger.hover();
        await ensureOpen(page, id);
        const box = await bounds(page, id);
        await page.mouse.move(box.x + box.width / 2, box.y + Math.min(70, box.height / 2));
        await page.waitForTimeout(450);
        await ensureOpen(page, id);
        const link = await verifyLinkHit(page, id);
        await trigger.click();
        await page.mouse.move(4, 150);
        await page.waitForTimeout(450);
        await ensureOpen(page, id);
        noShift(before, await flow(page));
        await page.screenshot({path: path.join(shots, `tls-open-1440-${theme}.png`)});
        await trigger.click();
        await ensureClosed(page, id);
        return {box, link, layoutShift: false};
      }, page);
      if (theme === 'light') {
        await runCase('desktop-close-focus-keyboard-switch', async () => {
          const trigger = triggerFor(page, id);
          await page.mouse.move(4, 150);
          await trigger.focus();
          await page.keyboard.press('Enter');
          await ensureOpen(page, id);
          const visited = [];
          let focusedSource = false;
          for (let i = 0; i < 8; i++) {
            const focus = await page.evaluate(() => ({tag: document.activeElement.tagName, href: document.activeElement.getAttribute('href'), inside: !!document.activeElement.closest('aside[data-source-panel]')}));
            visited.push(focus);
            if (focus.inside && focus.href) { focusedSource = true; break; }
            await page.keyboard.press('Tab');
          }
          assert.ok(focusedSource, 'Tab cannot reach source links from the open citation');
          await page.keyboard.press('Escape');
          await ensureClosed(page, id);
          assert.ok(await trigger.evaluate((node) => document.activeElement === node), 'Escape did not return focus to citation trigger');
          await trigger.click();
          await ensureOpen(page, id);
          await (await closeButton(page, id)).click();
          await ensureClosed(page, id);
          await trigger.click();
          await ensureOpen(page, id);
          await page.mouse.click(5, 150);
          await ensureClosed(page, id);
          await trigger.click();
          await ensureOpen(page, id);
          await triggerFor(page, 'R2').click();
          await ensureOpen(page, 'R2');
          assert.equal(await panelFor(page, id).isVisible(), false);
          await page.keyboard.press('Escape');
          await ensureClosed(page, 'R2');
          return {visited, switchKeptOneOpen: true, closeButton: true, escape: true, outsideClick: true};
        }, page);
      }
      await context.close();
    }

    for (const theme of ['dark', 'light']) {
      const context = await browser.newContext({viewport: {width: 390, height: 844}, colorScheme: theme, reducedMotion: 'reduce', isMobile: true, hasTouch: true});
      await context.addInitScript((value) => localStorage.setItem('vs:theme', value), theme);
      const page = await context.newPage();
      page.setDefaultTimeout(7000);
      page.setDefaultNavigationTimeout(20000);
      await page.goto(url('http-request'), {waitUntil: 'load'});
      await positionTLS(page);
      await page.screenshot({path: path.join(shots, `tls-collapsed-390-${theme}.png`)});
      await runCase(`mobile-touch-${theme}`, async () => {
        const before = await flow(page);
        const trigger = triggerFor(page, 'R4');
        await trigger.tap();
        await ensureOpen(page, 'R4');
        const box = await bounds(page, 'R4');
        noShift(before, await flow(page));
        await page.screenshot({path: path.join(shots, `tls-open-390-${theme}.png`)});
        await trigger.tap();
        await ensureClosed(page, 'R4');
        await trigger.tap();
        await ensureOpen(page, 'R4');
        await (await closeButton(page, 'R4')).tap();
        await ensureClosed(page, 'R4');
        return {box, layoutShift: false, touchToggle: true};
      }, page);
      if (theme === 'dark') await runCase('mobile-small-height-edge-resize-scroll', async () => {
        await page.setViewportSize({width: 390, height: 430});
        const trigger = triggerFor(page, 'R4');
        await trigger.scrollIntoViewIfNeeded();
        await trigger.tap();
        await ensureOpen(page, 'R4');
        const small = await bounds(page, 'R4');
        const panel = panelFor(page, 'R4');
        const scrollBefore = await panel.evaluate((node) => ({client: node.clientHeight, scroll: node.scrollHeight}));
        assert.ok(scrollBefore.scroll > scrollBefore.client, 'small-height panel did not constrain long source content');
        const pageY = await page.evaluate(() => scrollY);
        const gesture = await context.newCDPSession(page);
        const touchX = small.x + small.width / 2, touchY = small.y + small.height - 65;
        await gesture.send('Input.dispatchTouchEvent', {type: 'touchStart', touchPoints: [{x: touchX, y: touchY}]});
        for (let step = 1; step <= 8; step++) {
          await gesture.send('Input.dispatchTouchEvent', {type: 'touchMove', touchPoints: [{x: touchX, y: touchY - step * 17}]});
          await page.waitForTimeout(25);
        }
        await gesture.send('Input.dispatchTouchEvent', {type: 'touchEnd', touchPoints: []});
        await page.waitForTimeout(250);
        await gesture.detach();
        assert.ok(await panel.evaluate((node) => node.scrollTop > 0), 'native touch gesture did not scroll the source panel');
        assert.equal(await page.evaluate(() => scrollY), pageY, 'scrolling the panel moved the article');
        const resizeStartedAt = Date.now();
        await page.setViewportSize({width: 320, height: 568});
        // Positioning intentionally runs in requestAnimationFrame after resize.
        await page.waitForFunction(() => {
          const panel = document.querySelector('aside[data-source-panel="R4"]');
          if (!panel?.matches(':popover-open')) return false;
          const rect = panel.getBoundingClientRect();
          return rect.left >= 3 && rect.top >= 3 && rect.right <= innerWidth - 3 && rect.bottom <= innerHeight - 3;
        });
        const resizeSettledMs = Date.now() - resizeStartedAt;
        const resized = await bounds(page, 'R4');
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.waitForTimeout(350);
        await ensureClosed(page, 'R4');
        return {small, scrollBefore, resized, resizeSettledMs, panelScrollKeptArticlePosition: true, offscreenAnchorClosed: true};
      }, page);
      await context.close();
    }

    const noJSContext = await browser.newContext({viewport: {width: 390, height: 844}, javaScriptEnabled: false, colorScheme: 'dark', isMobile: true, hasTouch: true});
    const noJS = await noJSContext.newPage();
    noJS.setDefaultTimeout(7000);
    noJS.setDefaultNavigationTimeout(20000);
    await runCase('no-javascript-native-popover', async () => {
      await noJS.goto(url('http-request'), {waitUntil: 'load'});
      const trigger = triggerFor(noJS, 'R4'), panel = panelFor(noJS, 'R4');
      assert.equal(await panel.isVisible(), false);
      await trigger.tap();
      await noJS.waitForFunction(() => document.querySelector('aside[data-source-panel="R4"]').matches(':popover-open'));
      assert.equal((await panel.locator('blockquote').textContent()).trim(), expected.get('http-request').sources.get('R4').quotation.text.trim());
      const box = await bounds(noJS, 'R4');
      await (await closeButton(noJS, 'R4')).tap();
      assert.equal(await panel.isVisible(), false);
      return {box, originalTextRetained: true, nativeOpenClose: true};
    }, noJS);
    await noJSContext.close();
  } finally {
    await browser.close();
    fs.writeFileSync(path.join(out, `${reportName}.json`), JSON.stringify({base, checkedAt: new Date().toISOString(), results, failures,
      limitations: 'Chromium simulated viewports and touch. Source-link targets/hit-testing/focus checked without navigating external source sites; no physical-device or reading study.'}, null, 2) + '\n');
  }
  console.log(JSON.stringify({passed: results.length, failures}));
  if (failures.length) process.exitCode = 1;
})().catch((error) => {
  fs.writeFileSync(path.join(out, 'browser-fatal.json'), JSON.stringify({checkedAt: new Date().toISOString(), message: error.message, stack: error.stack, results, failures}, null, 2));
  console.error(error);
  process.exitCode = 1;
});
