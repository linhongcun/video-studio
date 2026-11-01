import {bundle} from '@remotion/bundler';
import {openBrowser, renderStill, selectComposition} from '@remotion/renderer';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import webpack from 'webpack';

// This entry records actual DOM/SVG audits. Missing audit output is a failure;
// the six generated images still require separate visual review.
const remotion = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
process.chdir(remotion);
const root = path.resolve(remotion, '..');
const out = path.resolve('out/covers-audit');
fs.mkdirSync(out, {recursive: true});
const storyboard = fs.existsSync(path.join(root, 'storyboard.json'))
  ? path.join(root, 'storyboard.json') : path.resolve('src/placeholders/storyboard.json');
for (const input of [storyboard, path.join(root, 'covers.json')]) {
  if (!fs.existsSync(input)) throw new Error(`Missing episode input: ${input}`);
}
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const model = JSON.parse(fs.readFileSync(path.join(root, 'model.json')));
const sourceFiles = [storyboard, path.join(root, 'model.json'), path.join(root, 'covers.json'),
  ...['Cover.tsx', 'theme.ts', 'LayoutAudit.tsx', 'Root.tsx', 'Main.tsx', 'index.ts'].map(file => path.resolve('src', file)),
  path.resolve('package.json'), path.resolve('package-lock.json'), path.resolve('remotion.config.ts'), path.resolve('scripts/covers.mjs')];
const sourceSHA = Object.fromEntries(sourceFiles.map(file => [path.relative(root, file), hash(file)]));
const sourcesUnchanged = () => {for (const [file, expected] of Object.entries(sourceSHA)) if (hash(path.join(root, file)) !== expected) throw new Error('Cover source changed during actual render: ' + file);};
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
  const prefix = 'SKIPLIST_LAYOUT_AUDIT ';
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
      images.push({size, format, file: path.relative(root, file), sha256: hash(file)});
      sourcesUnchanged();
    }
  }
} finally { await browser.close({silent: true}); }
const latest = Object.fromEntries(audits.map(audit => [audit.kind, audit]));
const violations = Object.values(latest).flatMap(audit => audit.violations ?? []);
const auditCoverage = Object.values(latest).every(audit => Array.isArray(audit.violations));
const expectedPorts = model.before.levels.flatMap((ids, level) => [model.head, ...ids].map(id => ({id, level, value: String(model.before.nodes[id].value ?? ''), next: String(model.before.nodes[id].forward[level] ?? 'null')})));
const expectedEdges = expectedPorts.filter(p => p.next !== 'null').map(p => `${p.level}:${p.id}->${p.next}`).sort();
const semanticViolations = [];
for (const [kind, audit] of Object.entries(latest)) {
  const ports = audit.ports ?? [], edges = audit.edges ?? [], cursors = audit.cursors ?? [];
  if (ports.length !== expectedPorts.length) semanticViolations.push({kind, type: 'actual-port-count', actual: ports.length, expected: expectedPorts.length});
  for (const expected of expectedPorts) {
    const rows = ports.filter(p => p.node === expected.id && p.level === expected.level);
    if (rows.length !== 1) {semanticViolations.push({kind, type: 'actual-port-identity', expected, actual: rows}); continue;}
    const p = rows[0], text = expected.id === model.head ? '起点' : expected.value;
    if (p.value !== expected.value || p.next !== expected.next || JSON.stringify(p.actualTexts) !== JSON.stringify([text])) semanticViolations.push({kind, type: 'actual-port-text-or-successor', expected, actual: p});
  }
  const actualEdges = edges.map(e => `${e.level}:${e.from}->${e.to}`).sort();
  if (JSON.stringify(actualEdges) !== JSON.stringify(expectedEdges)) semanticViolations.push({kind, type: 'actual-rendered-edge-set', expected: expectedEdges, actual: actualEdges});
  if (cursors.length !== 1 || cursors[0].node !== model.search.predecessors[0] || cursors[0].level !== 0) semanticViolations.push({kind, type: 'actual-cursor-port', actual: cursors});
}
sourcesUnchanged();
const passed = Object.keys(latest).length === 3 && auditCoverage
  && violations.length === 0 && images.length === 6 && logErrors.length === 0 && semanticViolations.length === 0;
const report = {status: passed ? 'bounds-passed-awaiting-visual-review' : 'failed',
  checkedAtUTC: new Date().toISOString(), method: 'Actual Chromium SVG/DOM bounds after fonts load',
  auditLogPrefix: 'SKIPLIST_LAYOUT_AUDIT ', sourceSHA, audits: Object.values(latest), images, violations, semanticViolations, logErrors,
  semanticScope: 'Actual port values/text/successors, model-derived edge set and current lower predecessor; route geometry is separately inspected in actual images.',
  visualReview: {status: 'pending', scope: 'Each actual PNG and JPG must be opened before covers are final.'}};
fs.writeFileSync(path.join(out, 'covers-layout-audit.json'), JSON.stringify(report, null, 2) + '\n');
fs.writeFileSync(path.join(root, 'qa-covers.json'), JSON.stringify(report, null, 2) + '\n');
console.log(`covers: ${Object.keys(latest).length} sizes, ${violations.length} layout violations, ${semanticViolations.length} semantic violations, ${images.length} actual image files`);
if (!passed) process.exitCode = 1;
