// Fresh independent integer-frame source review. Production inputs are read-only.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const get = key => process.argv.slice(2).find(value => value.startsWith(key + '='))?.slice(key.length + 1);
if (!process.env.REDIS_INDEPENDENT_RENDER_LOCK) {
  const result = spawnSync('flock', ['/tmp/video-studio-render.lock', process.execPath,
    fileURLToPath(import.meta.url), ...process.argv.slice(2)], {
    stdio: 'inherit', env: {...process.env, REDIS_INDEPENDENT_RENDER_LOCK: 'held'},
  });
  process.exit(result.status ?? 1);
}
if (!get('--dir') || !get('--spec') || !get('--out-dir')) {
  throw Error('Usage: node render-preview.mjs --dir=/actual/production --spec=/samples.json --out-dir=/new/qa/attempt [--subtitles=on]');
}
const D = path.resolve(get('--dir')), OUT = path.resolve(get('--out-dir'));
if (!OUT.startsWith(HERE + path.sep) || fs.existsSync(OUT)) throw Error('Preserve attempts; select a new output child of this QA archive');
fs.mkdirSync(OUT, {recursive: true});
const specFile = path.resolve(get('--spec')), SPEC = JSON.parse(fs.readFileSync(specFile, 'utf8'));
const REM = path.join(D, 'remotion'), req = createRequire(path.join(REM, 'package.json'));
let ROOT = D;
while (!fs.existsSync(path.join(ROOT, 'AGENTS.md'))) {
  const parent = path.dirname(ROOT);
  if (parent === ROOT) throw Error('Missing repository root');
  ROOT = parent;
}
const {episodeDirectory} = await import(pathToFileURL(path.join(ROOT, 'site/scripts/episode-paths.mjs')).href);
const slug = JSON.parse(fs.readFileSync(path.join(D, 'episode-config.json'), 'utf8')).slug;
const canonical = episodeDirectory(slug, {repoRoot: ROOT, kind: 'production'});
if (D !== canonical && !D.startsWith(canonical + path.sep)) throw Error('Choose an actual production root/revision');
const {bundle} = req('@remotion/bundler');
const {openBrowser, selectComposition, renderStill} = req('@remotion/renderer');
const webpack = req('webpack');
const sha = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const walk = directory => fs.readdirSync(directory, {withFileTypes: true}).flatMap(entry => {
  const file = path.join(directory, entry.name);
  return entry.isDirectory() ? walk(file) : /\.(tsx?|json|mjs|js|css|svg|png|jpe?g|wav)$/.test(entry.name) ? [file] : [];
});
const inputPaths = ['model.json', 'storyboard.json', 'script.md', 'voice.wav', 'episode-config.json',
  'covers.json', 'article-figure-plan.json', 'remotion/package.json', 'remotion/package-lock.json']
  .map(name => path.join(D, name)).filter(file => fs.existsSync(file));
inputPaths.push(...walk(path.join(REM, 'src')), specFile);
// Include shared visual dependencies and any imports declared by the reviewer.
inputPaths.push(...walk(path.join(ROOT, 'episodes/_shared/redis-video')),
  ...walk(path.join(ROOT, 'episodes/_shared/middleware-identity')));
for (const name of SPEC.extraInputs ?? []) inputPaths.push(path.resolve(ROOT, name));
const hashes = Object.fromEntries([...new Set(inputPaths)].map(file => [file, sha(file)]));
const subtitles = get('--subtitles') === 'on';
const props = {showSubtitles: subtitles, hideSubtitles: !subtitles, hideCaptions: !subtitles};
const REPORT = path.join(OUT, 'source-preview-review.json');
const report = {kind: 'independent-fresh-source-integer-frame-review', production: D,
  createdAtUTC: new Date().toISOString(), reviewerScriptSHA256: sha(fileURLToPath(import.meta.url)),
  specFile, specSHA256: sha(specFile), sourceSHA256: hashes, props, samples: [], console: [],
  consoleRaw: [], machinePass: false, visualReviewed: false,
  scope: 'Actual source DOM/PNG observations. Geometry checks do not establish meaning, motion clarity or learner understanding.'};
const save = () => fs.writeFileSync(REPORT, JSON.stringify(report, null, 2) + '\n');
save();
let browser;
try {
  const bundleDir = path.join(OUT, 'bundle');
  const serveUrl = await bundle({entryPoint: path.join(REM, 'src/index.ts'), publicDir: path.join(REM, 'public'),
    outDir: bundleDir, enableCaching: false, webpackOverride: config => ({...config,
      resolve: {...config.resolve, alias: {...config.resolve?.alias,
        '@storyboard': path.join(D, 'storyboard.json'), '@covers': path.join(D, 'covers.json')},
        modules: [path.join(REM, 'node_modules'), 'node_modules']},
      plugins: [...(config.plugins ?? []), new webpack.DefinePlugin({__HAS_VOICE_AUDIO__: false})]})});
  report.bundle = serveUrl;
  report.bundleSHA256 = Object.fromEntries(walk(bundleDir).map(file => [path.relative(bundleDir, file), sha(file)]));
  browser = await openBrowser('chrome', {browserExecutable: '/usr/bin/chromium', logLevel: 'error'});
  let active = null, metrics = null;
  const newPage = browser.newPage.bind(browser);
  browser.newPage = async options => {
    const page = await newPage(options), close = page.close.bind(page);
    page.close = async options => {
      if (active) metrics = await page.evaluate(() => {
        const visible = element => {
          let alpha = 1;
          for (let node = element; node; node = node.parentElement) {
            const style = getComputedStyle(node);
            if (style.display === 'none' || style.visibility === 'hidden') return false;
            alpha *= Number(style.opacity);
          }
          const rect = element.getBoundingClientRect();
          return alpha > .1 && rect.width > 0 && rect.height > 0;
        };
        const all = [...document.querySelectorAll('text,[data-text],[data-subtitle]')].filter(visible);
        const nodes = all.filter(element => !all.some(other => other !== element && element.contains(other)));
        const texts = nodes.map(element => {
          const range = document.createRange(); range.selectNodeContents(element);
          const box = range.getBoundingClientRect(), style = getComputedStyle(element);
          return {text: element.textContent, x: box.x, y: box.y, w: box.width, h: box.height,
            clientWidth: element.clientWidth, scrollWidth: element.scrollWidth,
            color: style.color, fontFamily: style.fontFamily, fontSize: style.fontSize,
            subtitle: Boolean(element.closest('[data-subtitle]'))};
        });
        const movers = [...document.querySelectorAll('[data-travel-record],[data-moving-dot],[data-moving-body]')].filter(visible);
        const collisions = [];
        for (const mover of movers) {
          const a = mover.getBoundingClientRect();
          for (let index = 0; index < nodes.length; index++) {
            if (mover.contains(nodes[index]) || nodes[index].contains(mover)) continue;
            const b = texts[index], w = Math.min(a.right, b.x + b.w) - Math.max(a.left, b.x),
              h = Math.min(a.bottom, b.y + b.h) - Math.max(a.top, b.y);
            if (w > 1 && h > 1) collisions.push({body: mover.getAttribute('data-moving-body') ??
              mover.getAttribute('data-travel-record') ?? 'dot', text: b.text, w, h});
          }
        }
        const data = [...document.querySelectorAll('*')]
          .filter(element => [...element.attributes].some(attribute => attribute.name.startsWith('data-')))
          .map(element => ({tag: element.tagName, visible: visible(element), attrs: Object.fromEntries(
            [...element.attributes].filter(attribute => attribute.name.startsWith('data-')).map(attribute => [attribute.name, attribute.value]))}));
        return {texts, collisions, data,
          modelState: document.querySelector('[data-model-state]')?.getAttribute('data-model-state') ?? null,
          visibleSubtitles: [...document.querySelectorAll('[data-subtitle]')].filter(visible).length};
      });
      return close(options);
    };
    return page;
  };
  const comp = await selectComposition({serveUrl, id: 'Main', inputProps: props, puppeteerInstance: browser, logLevel: 'error'});
  comp.props = {...comp.props, ...props};
  report.resolvedComposition = {id: comp.id, width: comp.width, height: comp.height,
    durationInFrames: comp.durationInFrames, fps: comp.fps, props: comp.props};
  const seen = new Set();
  for (const sample of SPEC.samples) {
    if (!Number.isInteger(sample.frame) || sample.frame < 0 || sample.frame >= comp.durationInFrames || seen.has(sample.frame)) {
      throw Error('Unique exact valid integer frames required');
    }
    seen.add(sample.frame); active = sample; metrics = null;
    const png = path.join(OUT, `frame-${String(sample.frame).padStart(5, '0')}.png`);
    await renderStill({serveUrl, composition: comp, frame: sample.frame, output: png,
      imageFormat: 'png', inputProps: props, puppeteerInstance: browser, logLevel: 'error',
      onBrowserLog: log => {report.consoleRaw.push({frame: sample.frame, ...log});
        if (/COPYFIT|error/i.test(log.text)) report.console.push({frame: sample.frame, text: log.text});}});
    if (!metrics || !metrics.texts.length) throw Error('Missing actual text DOM observation');
    const violations = metrics.texts.filter(text => text.x < -.5 || text.y < -.5 ||
      text.x + text.w > comp.width + .5 || text.y + text.h > (text.subtitle ? comp.height : (SPEC.bodyTextBottom ?? 925)) ||
      (text.clientWidth > 0 && text.scrollWidth > text.clientWidth + 2));
    const mismatches = [];
    if (sample.expectedState && sample.expectedState !== metrics.modelState) mismatches.push({expected: sample.expectedState, actual: metrics.modelState});
    for (const wanted of sample.expectedText ?? []) {
      if (!metrics.texts.some(text => text.text.includes(wanted))) mismatches.push({missingVisibleText: wanted});
    }
    if (!subtitles && metrics.visibleSubtitles) mismatches.push({unexpectedVisibleSubtitles: metrics.visibleSubtitles});
    report.samples.push({...sample, file: png, sha256: sha(png), metrics, violations, mismatches});
    save();
    if (get('--stop-on-fail') !== 'false' && (violations.length || mismatches.length)) break;
  }
  report.sourceInputsUnchanged = Object.entries(hashes).every(([file, value]) => sha(file) === value);
  report.machinePass = report.sourceInputsUnchanged && report.samples.length === SPEC.samples.length &&
    !report.console.length && report.samples.every(sample => !sample.violations.length && !sample.mismatches.length);
  report.collisionCandidatesRequireVisualReview = report.samples.flatMap(sample =>
    sample.metrics.collisions.map(collision => ({frame: sample.frame, ...collision})));
  report.status = report.machinePass ? 'machine-screening-passed-await-actual-image-review' : 'machine-screening-failed';
} catch (error) {
  report.status = 'failed-preserved-raw-attempt';
  report.failure = {name: error.name, message: error.message, stack: error.stack};
} finally {
  if (browser) await browser.close({silent: true});
  report.sourceInputsUnchanged = Object.entries(hashes).every(([file, value]) => fs.existsSync(file) && sha(file) === value);
  if (!report.sourceInputsUnchanged) report.machinePass = false;
  save();
}
console.log(JSON.stringify({machinePass: report.machinePass, samples: report.samples.length, report: REPORT}));
process.exitCode = report.machinePass ? 0 : 1;
