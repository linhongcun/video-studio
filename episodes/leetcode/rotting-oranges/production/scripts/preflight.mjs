/** LC994 actual Remotion DOM COPYFIT, subtitle, opening title, stop-guard, and complete-code-card audit.
 * Does not drive the site or replace independent continuous-video review.
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import crypto from 'node:crypto';
import os from 'node:os';

const ep = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const remotion = path.join(ep, 'remotion');
const require = createRequire(path.join(remotion, 'package.json'));
const {bundle} = require('@remotion/bundler');
const {renderStill, selectComposition, openBrowser} = require('@remotion/renderer');
const webpack = require('webpack');

const sb = JSON.parse(fs.readFileSync(path.join(ep, 'storyboard.json'), 'utf8'));
const shots = sb.scenes.flatMap((s) => s.shots);
const card = sb.meta.unvoicedEndCard;
const code = JSON.parse(fs.readFileSync(path.join(ep, 'solution.json'), 'utf8')).lines;
const sha = (p) => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const out = path.join(ep, 'qa/preflight');
fs.mkdirSync(out, {recursive: true});

const frames = [
  ...new Set(
    shots
      .flatMap((s) => [
        s.from,
        s.from + Math.floor(s.durationInFrames * 0.25),
        s.from + Math.floor(s.durationInFrames * 0.5),
        s.from + Math.floor(s.durationInFrames * 0.78),
        s.from + s.durationInFrames - 1,
        ...(s.subtitles ?? []).map((c) => s.from + Math.floor((c.from + c.to) / 2)),
      ])
      .concat([card.from - 1, card.from, card.from + 75, card.from + 149]),
  ),
]
  .filter((f) => f >= 0 && f < sb.meta.durationInFrames)
  .sort((a, b) => a - b);

const report = {
  status: 'running',
  startedAt: new Date().toISOString(),
  storyboardSHA256: sha(path.join(ep, 'storyboard.json')),
  frames,
  audits: [],
  warnings: [],
  errors: [],
  fontFiles: [],
  limitation: 'Sampled final-frame DOM geometry and semantic checks; continuous action and audio reviewed separately.',
};

for (const candidate of [
  path.join(os.homedir(), 'Library/Fonts/NotoSansCJK-Regular.ttc'),
  path.join(os.homedir(), 'Library/Fonts/NotoSansCJK-Bold.ttc'),
  path.join(os.homedir(), 'Library/Fonts/NotoSansMono-Variable.ttf'),
  '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
  '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
]) {
  if (fs.existsSync(candidate)) {
    report.fontFiles.push({path: candidate, sha256: sha(candidate)});
  }
}

let browser;
let frame = null;
try {
  const serveUrl = await bundle({
    entryPoint: path.join(remotion, 'src/index.ts'),
    enableCaching: false,
    publicDir: path.join(remotion, 'public'),
    webpackOverride: (c) => ({
      ...c,
      resolve: {...c.resolve, alias: {...c.resolve?.alias, '@storyboard': path.join(ep, 'storyboard.json')}},
      plugins: [...(c.plugins ?? []), new webpack.DefinePlugin({__HAS_VOICE_AUDIO__: false})],
    }),
  });
  const defaultChrome = fs.existsSync('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    : '/usr/bin/chromium';
  const executable = process.env.CHROME_BIN ?? defaultChrome;
  browser = await openBrowser('chrome', {browserExecutable: executable, logLevel: 'error'});
  const newPage = browser.newPage.bind(browser);
  browser.newPage = async (options) => {
    const page = await newPage(options);
    const close = page.close.bind(page);
    page.close = async (closeOpts) => {
      if (Number.isInteger(frame) && !page.closed) {
        const audit = await page.evaluate(
          async ({frame, cardFrom, code}) => {
            await document.fonts.ready;
            const base = (document.querySelector('[data-leetcode-canvas]') ?? document.querySelector('svg')).getBoundingClientRect();
            const box = (r) => ({
              x: ((r.x - base.x) * 1920) / base.width,
              y: ((r.y - base.y) * 1080) / base.height,
              w: (r.width * 1920) / base.width,
              h: (r.height * 1080) / base.height,
            });
            const visible = (e) => {
              let a = 1;
              while (e) {
                const s = getComputedStyle(e);
                if (s.display === 'none' || s.visibility === 'hidden') return false;
                a *= Number(s.opacity);
                e = e.parentElement;
              }
              return a > 0.03;
            };
            const sub = document.querySelector('[data-subtitle]');
            const subtitle = sub && visible(sub) ? box(sub.getBoundingClientRect()) : null;
            const texts = [...document.querySelectorAll('svg text,[data-leetcode-header] div')]
              .filter((e) => e.textContent.trim() && visible(e) && (!e.children.length || e.tagName === 'text'))
              .map((e) => ({
                text: e.textContent,
                subtitle: !!e.closest('[data-subtitle]'),
                ...box(e.getBoundingClientRect()),
              }));
            const violations = [];
            for (const t of texts) {
              if (t.x < 30 || t.y < 18 || t.x + t.w > 1890 || t.y + t.h > 1060) {
                violations.push({type: 'COPYFIT', text: t});
              }
              if (
                !t.subtitle &&
                subtitle &&
                t.y + t.h > subtitle.y - 4 &&
                t.y < subtitle.y + subtitle.h &&
                t.x < subtitle.x + subtitle.w &&
                t.x + t.w > subtitle.x
              ) {
                violations.push({type: 'subtitle-overlap', text: t});
              }
            }
            const cardEl = document.querySelector('[data-code-card="complete-python-solution"]');
            const lines = cardEl ? [...cardEl.querySelectorAll('[data-code-line]')].map((e) => e.textContent) : [];
            if ((frame >= cardFrom) !== !!cardEl) violations.push({type: 'code-boundary'});
            if (cardEl && (subtitle || JSON.stringify(lines) !== JSON.stringify(code))) {
              violations.push({type: 'code-card-content-or-subtitle'});
            }
            return {frame, texts, subtitle, codeVisible: !!cardEl, codeLines: lines.length, violations};
          },
          {frame, cardFrom: card.from, code},
        );
        report.audits.push(audit);
      }
      await close(closeOpts);
    };
    return page;
  };

  const onBrowserLog = (log) => {
    if (['warn', 'warning'].includes(log.type)) report.warnings.push(log);
    if (['error', 'assert'].includes(log.type)) report.errors.push(log);
  };
  const composition = await selectComposition({
    serveUrl,
    id: 'Main',
    puppeteerInstance: browser,
    browserExecutable: executable,
    onBrowserLog,
    logLevel: 'error',
  });
  for (const f of frames) {
    frame = f;
    await renderStill({
      serveUrl,
      composition,
      frame: f,
      puppeteerInstance: browser,
      browserExecutable: executable,
      output: path.join(out, `frame-${String(f).padStart(6, '0')}.png`),
      scale: 0.65,
      onBrowserLog,
      logLevel: 'error',
    });
  }
  report.violations = report.audits.flatMap((a) => a.violations.map((v) => ({frame: a.frame, ...v})));
  if (!report.audits.find((a) => a.frame === 0)?.texts.some((t) => t.text.includes('腐烂的橘子'))) {
    report.violations.push({frame: 0, type: 'opening-problem-title-missing'});
  }
  if (!report.audits.some((a) => a.texts.some((t) => t.text.includes('越界跳过')))) {
    report.violations.push({type: 'oob-skip-caption-not-observed'});
  }
  if (!report.audits.some((a) => a.texts.some((t) => t.text.includes('已为 2 跳过')))) {
    report.violations.push({type: 'collision-skip-caption-not-observed'});
  }
  if (!report.audits.some((a) => a.texts.some((t) => t.text.includes('while queue and fresh > 0')))) {
    report.violations.push({type: 'stop-guard-caption-not-observed'});
  }
  report.status = report.errors.length || report.violations.length || report.audits.length !== frames.length ? 'failed' : 'passed';
} catch (e) {
  report.status = 'failed';
  report.failure = String(e);
  console.error(e);
} finally {
  if (browser) await browser.close({silent: true});
  report.completedAt = new Date().toISOString();
  fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify(report, null, 2) + '\n');
}
console.log(report.status, report.audits.length, 'frames', report.violations?.length ?? 0, 'layout violations');
if (report.status !== 'passed') process.exitCode = 1;
