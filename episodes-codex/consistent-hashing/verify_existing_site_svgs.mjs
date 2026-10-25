// Regression for the two existing articles with inline native SVG figures.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const require = createRequire(import.meta.url);
const {chromium} = require('playwright');
const dir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(dir, '../..');
const sha = (buffer) => createHash('sha256').update(buffer).digest('hex');
const report = {status: 'in-progress', checkedAt: new Date().toISOString(), baseline: '46395cfb', rows: [], errors: [],
  scope: 'Actual local Chromium. Compare article/source identities to the same paths upstream, and figure positions with the new margin rule disabled. Existing production/publication files are not presumed identical.'};
let browser;
try {
  browser = await chromium.launch({headless: true, executablePath: '/usr/bin/chromium', args: ['--no-sandbox']});
  for (const viewport of [{width: 1440, height: 1000}, {width: 390, height: 844}]) {
    const page = await browser.newPage({viewport, reducedMotion: 'reduce'});
    for (const slug of ['strategy-pattern', 'adapter-pattern']) {
      const response = await page.goto(`http://127.0.0.1:4321/video-studio/episodes/${slug}/`, {waitUntil: 'networkidle'});
      assert.equal(response.status(), 200);
      const readFigures = () => page.locator('#article figure').evaluateAll((figures) => figures.map((figure) => {
        const rect = figure.getBoundingClientRect(), style = getComputedStyle(figure);
        return {x: rect.x, width: rect.width, height: rect.height, marginLeft: style.marginLeft, marginRight: style.marginRight,
          inlineStyle: figure.getAttribute('style'), svgCount: figure.querySelectorAll('svg').length,
          text: figure.querySelector('svg')?.textContent?.trim().slice(0, 100)};
      }));
      const figures = await readFigures();
      assert.ok(figures.length && figures.every((figure) => figure.svgCount > 0));
      await page.evaluate(() => {
        for (const sheet of document.styleSheets) {
          try {
            for (const rule of sheet.cssRules)
              if (rule.selectorText?.replace(/\s/g, '') === '.prose>figure') rule.style.removeProperty('margin-inline');
          } catch { /* Cross-origin stylesheets cannot affect this same-origin rule. */ }
        }
      });
      const simulatedPreviousCSS = await readFigures();
      assert.deepEqual(figures, simulatedPreviousCSS, `${slug}: figure geometry changed`);
      const dimensions = await page.evaluate(() => ({viewport: innerWidth, document: document.documentElement.scrollWidth}));
      assert.ok(dimensions.document <= dimensions.viewport + 1);
      const identities = {};
      for (const file of [`episodes/${slug}/article.mdx`, `episodes-codex/${slug}/article.mdx`]) {
        const current = fs.readFileSync(path.join(root, file));
        const baseline = execFileSync('git', ['show', `46395cfb:${file}`], {cwd: root});
        assert.equal(sha(current), sha(baseline), `${file} changed from upstream`);
        identities[file] = {currentSHA256: sha(current), upstreamSHA256: sha(baseline)};
      }
      await page.locator('#article figure').first().scrollIntoViewIfNeeded();
      const screenshot = path.join(dir, `qa-site-evidence/existing-${slug}-${viewport.width}.png`);
      await page.screenshot({path: screenshot});
      report.rows.push({slug, viewport, figures, simulatedPreviousCSS, figureLayoutUnchanged: true,
        identities, dimensions, screenshot: path.relative(root, screenshot)});
    }
    await page.close();
  }
  report.status = 'passed';
} catch (error) {
  report.status = 'failed'; report.errors.push(String(error.stack ?? error)); process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  fs.writeFileSync(path.join(dir, 'qa-site-existing-svg.json'), `${JSON.stringify(report, null, 2)}\n`);
  console.log(JSON.stringify({status: report.status, checks: report.rows.length, errors: report.errors}));
}
