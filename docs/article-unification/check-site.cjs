// Run after the normal site build, with Astro preview listening on port 4323.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '../..');
const sha = (file) => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const read = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const episodes = fs.readdirSync(path.join(root, 'episodes')).filter((slug) => {
  const file = path.join(root, 'episodes', slug, 'meta.json');
  return fs.existsSync(file) && !read(file).draft && !read(file).archived;
});
const base = process.env.ARTICLE_QA_BASE || 'http://127.0.0.1:4323/video-studio/';
const shots = path.join(__dirname, 'screenshots');
fs.mkdirSync(shots, {recursive: true});

(async () => {
  const browser = await chromium.launch({executablePath: '/usr/bin/chromium', args: ['--no-sandbox', '--disable-dev-shm-usage']});
  const results = [];
  const failures = [];
  try {
    for (const mode of [{width: 1440, height: 1000, theme: 'light'}, {width: 390, height: 844, theme: 'dark'}]) {
      const context = await browser.newContext({viewport: {width: mode.width, height: mode.height}, colorScheme: mode.theme, reducedMotion: 'reduce'});
      await context.addInitScript((theme) => localStorage.setItem('vs:theme', theme), mode.theme);
      const page = await context.newPage();
      for (const slug of episodes) {
        try {
          const errors = [];
          const listener = (error) => errors.push(error.message);
          page.on('pageerror', listener);
          const response = await page.goto(`${base}episodes/${slug}/`, {waitUntil: 'load'});
          assert.equal(response.status(), 200);
          const sources = new Map();
          for (const file of ['references.json', 'article-sources.json']) {
            const full = path.join(root, 'episodes', slug, file);
            if (fs.existsSync(full)) for (const source of read(full).sources) sources.set(source.id, source);
          }
          const quotes = await page.locator('#article .source-quote').evaluateAll((nodes) => nodes.map((node) => ({
            id: node.dataset.sourceQuote,
            text: node.querySelector('blockquote').textContent,
            locator: node.querySelector('.source-location').textContent,
            title: node.querySelector('cite a').textContent,
            url: node.querySelector('cite a').href,
            width: node.getBoundingClientRect().width,
          })));
          assert.ok(quotes.length > 0);
          for (const quote of quotes) {
            const source = sources.get(quote.id);
            assert.equal(quote.text, source.quotation.text);
            assert.equal(quote.title, source.title);
            assert.equal(quote.url, source.url);
            assert.ok(quote.locator.includes(source.quotation.locator));
            assert.ok(quote.width > 250 && quote.width <= mode.width);
          }
          const images = page.locator('#article figure.fig img');
          const pictures = [];
          for (let i = 0; i < await images.count(); i++) {
            const image = images.nth(i);
            await image.scrollIntoViewIfNeeded();
            await image.evaluate((node) => node.decode());
            const info = await image.evaluate((node) => ({src: new URL(node.src).pathname, width: node.naturalWidth, display: node.getBoundingClientRect().width, alt: node.alt}));
            assert.ok(info.width >= 640 && info.alt && info.display <= mode.width);
            assert.equal(await image.locator('..').getAttribute('href'), info.src);
            const relative = info.src.slice('/video-studio/'.length);
            assert.equal(sha(path.join(root, 'site/public', relative)), sha(path.join(root, relative)));
            pictures.push(info);
          }
          const svgCount = await page.locator('#article > figure:not(.source-quote) svg').count();
          assert.ok(pictures.length + svgCount > 0);
          const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
          assert.ok(overflow <= 1, `${slug}: horizontal overflow ${overflow}`);
          let seek;
          if (['http-request', 'db-lock', 'two-sum'].includes(slug) && pictures.length) {
            const link = page.locator('#article [data-seek-time]').first();
            const target = Number(await link.getAttribute('data-seek-time'));
            await link.click();
            await page.waitForFunction((seconds) => {
              const video = document.querySelector('video');
              return video.readyState >= 1 && Math.abs(video.currentTime - seconds) < 2;
            }, target);
            seek = await page.locator('video').evaluate((video) => { video.pause(); return video.currentTime; });
            assert.ok(Math.abs(seek - target) < 2);
          }
          if (['http-request', 'db-lock', 'two-sum', 'strategy-pattern'].includes(slug)) {
            const quote = page.locator('#article .source-quote').first();
            await quote.screenshot({path: path.join(shots, `${slug}-quote-${mode.width}-${mode.theme}.png`)});
            if (pictures.length) await page.locator('#article figure.fig').first().screenshot({path: path.join(shots, `${slug}-figure-${mode.width}-${mode.theme}.png`)});
            else await page.locator('#article > figure:not(.source-quote)').first().screenshot({path: path.join(shots, `${slug}-figure-${mode.width}-${mode.theme}.png`)});
          }
          if (slug === 'two-sum') {
            const original = page.locator('#article .fig-image-link').first();
            const href = await original.getAttribute('href');
            await original.click();
            await page.waitForURL((url) => url.pathname === href);
            assert.ok(await page.locator('img').evaluate((image) => image.naturalWidth >= 640));
            await page.goBack({waitUntil: 'load'});
          }
          assert.deepEqual(errors, []);
          page.off('pageerror', listener);
          results.push({slug, ...mode, quotes: quotes.length, pictures, svgCount, overflow, ...(seek === undefined ? {} : {seek})});
        } catch (error) {
          failures.push({slug, ...mode, message: error.message});
        }
      }
      await context.close();
    }
  } finally {
    await browser.close();
    fs.writeFileSync(path.join(__dirname, 'browser-review.json'), JSON.stringify({base, checkedAt: new Date().toISOString(), results, failures, limitations: 'Chromium simulated desktop/mobile; no physical-device or user-reading study.'}, null, 2) + '\n');
  }
  console.log(JSON.stringify({pages: results.length, failures}));
  if (failures.length) process.exitCode = 1;
})();
