import {bundle} from '@remotion/bundler';
import {openBrowser, renderStill, selectComposition} from '@remotion/renderer';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import webpack from 'webpack';

// This entry records actual DOM/SVG audits. Missing audit output is a failure;
// the six generated images still require separate visual review.
const root = path.resolve('..');
const out = path.resolve('out/covers-audit');
fs.mkdirSync(out, {recursive: true});
const storyboard = fs.existsSync(path.join(root, 'storyboard.json'))
  ? path.join(root, 'storyboard.json') : path.resolve('src/placeholders/storyboard.json');
for (const input of [storyboard, path.join(root, 'covers.json')]) {
  if (!fs.existsSync(input)) throw new Error(`Missing episode input: ${input}`);
}
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), enableCaching: false,
  webpackOverride: config => ({...config, resolve: {...config.resolve,
    alias: {...config.resolve?.alias, '@storyboard': storyboard, '@covers': path.join(root, 'covers.json')},
    modules: [path.resolve('node_modules'), 'node_modules']},
    plugins: [...(config.plugins ?? []), new webpack.DefinePlugin({__HAS_VOICE_AUDIO__: false})],
  }),
});
const browserExecutable = '/usr/bin/chromium';
const browser = await openBrowser('chrome', {browserExecutable});
const audits = [], images = [], logErrors = [];
const onBrowserLog = log => {
  const prefix = 'BLOOM_LAYOUT_AUDIT ';
  if (!log.text?.startsWith(prefix)) return;
  try { audits.push(JSON.parse(log.text.slice(prefix.length))); }
  catch (error) { logErrors.push(String(error)); }
};
try {
  for (const size of ['16x9', '4x3', '3x4']) {
    const inputProps = {size, auditLayout: true};
    const selected = await selectComposition({serveUrl, id: 'Cover' + size,
      browserExecutable, puppeteerInstance: browser, inputProps});
    const composition = {...selected, props: {...selected.props, ...inputProps}};
    for (const format of ['png', 'jpeg']) {
      const file = path.join(root, `cover-${size}.${format === 'png' ? 'png' : 'jpg'}`);
      await renderStill({composition, serveUrl, output: file, browserExecutable,
        puppeteerInstance: browser, inputProps, onBrowserLog, imageFormat: format,
        jpegQuality: format === 'jpeg' ? 94 : undefined});
      images.push({size, format, file: path.relative(root, file),
        sha256: crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')});
    }
  }
} finally { await browser.close({silent: true}); }
const latest = Object.fromEntries(audits.map(audit => [audit.kind, audit]));
const violations = Object.values(latest).flatMap(audit => audit.violations ?? []);
const auditCoverage = Object.values(latest).every(audit => Array.isArray(audit.violations));
const passed = Object.keys(latest).length === 3 && auditCoverage
  && violations.length === 0 && images.length === 6 && logErrors.length === 0;
const report = {status: passed ? 'bounds-passed-awaiting-visual-review' : 'failed',
  checkedAtUTC: new Date().toISOString(), method: 'Actual Chromium SVG/DOM bounds after fonts load',
  auditLogPrefix: 'BLOOM_LAYOUT_AUDIT ', audits: Object.values(latest), images, violations, logErrors,
  visualReview: {status: 'pending', scope: 'Each actual PNG and JPG must be opened before covers are final.'}};
fs.writeFileSync(path.join(out, 'covers-layout-audit.json'), JSON.stringify(report, null, 2) + '\n');
fs.writeFileSync(path.join(root, 'qa-covers.json'), JSON.stringify(report, null, 2) + '\n');
console.log(`covers: ${Object.keys(latest).length} sizes, ${violations.length} violations, ${images.length} actual image files`);
if (!passed) process.exitCode = 1;
