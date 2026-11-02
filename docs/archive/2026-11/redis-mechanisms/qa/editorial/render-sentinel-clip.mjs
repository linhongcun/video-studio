// Directed bounded clips from the exact audited preview bundle, plus an exact PCM slice.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const get = key => process.argv.slice(2).find(value => value.startsWith(key + '='))?.slice(key.length + 1);
if (!process.env.REDIS_INDEPENDENT_RENDER_LOCK) {
  const result = spawnSync('flock', ['/tmp/video-studio-render.lock', process.execPath,
    fileURLToPath(import.meta.url), ...process.argv.slice(2)], {stdio: 'inherit',
    env: {...process.env, REDIS_INDEPENDENT_RENDER_LOCK: 'held'}});
  process.exit(result.status ?? 1);
}
if (!get('--preview-report') || !get('--out-dir')) throw Error('Require --preview-report=... --out-dir=... --first=N --last=N');
const previewFile = path.resolve(get('--preview-report')), preview = JSON.parse(fs.readFileSync(previewFile, 'utf8'));
const D = preview.production, OUT = path.resolve(get('--out-dir'));
if (!OUT.startsWith(HERE + path.sep) || fs.existsSync(OUT)) throw Error('Choose a new child of QA archive; preserve attempts');
const first = Number(get('--first')), last = Number(get('--last'));
if (!Number.isInteger(first) || !Number.isInteger(last) || first < 0 || last < first ||
  last - first + 1 > 450 || last >= preview.resolvedComposition.durationInFrames) throw Error('Require valid <=450-frame bounded range');
const sha = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
if (!Object.entries(preview.sourceSHA256).every(([file, value]) => sha(file) === value)) throw Error('Production changed; first make a new preview bundle');
for (const [file, value] of Object.entries(preview.bundleSHA256)) {
  if (sha(path.join(preview.bundle, file)) !== value) throw Error('Audited bundle changed');
}
fs.mkdirSync(OUT, {recursive: true});
const req = createRequire(path.join(D, 'remotion/package.json'));
const {openBrowser, selectComposition, renderMedia} = req('@remotion/renderer');
const REPORT = path.join(OUT, 'short-clip-review.json'), props = preview.props;
const report = {kind: 'independent-directed-source-motion-clip', production: D, first, last,
  frames: last - first + 1, previewReport: previewFile, previewReportSHA256: sha(previewFile),
  sourceSHA256: preview.sourceSHA256, props, reviewerScriptSHA256: sha(fileURLToPath(import.meta.url)), machinePass: false, visualReviewed: false,
  scope: 'Fresh source motion with an exact original voice PCM sample interval. Preview is not the formally color-converted final media; no semantic listening claim.'};
const save = () => fs.writeFileSync(REPORT, JSON.stringify(report, null, 2) + '\n');
save();
let browser;
try {
  browser = await openBrowser('chrome', {browserExecutable: '/usr/bin/chromium', logLevel: 'error'});
  const comp = await selectComposition({serveUrl: preview.bundle, id: 'Main', inputProps: props, puppeteerInstance: browser, logLevel: 'error'});
  comp.props = {...comp.props, ...props};
  report.resolvedComposition = {id: comp.id, width: comp.width, height: comp.height, fps: comp.fps, durationInFrames: comp.durationInFrames, props: comp.props};
  save();
  const silent = path.join(OUT, 'motion-silent.mp4');
  await renderMedia({serveUrl: preview.bundle, composition: comp, inputProps: props,
    puppeteerInstance: browser, codec: 'h264', scale: .5, crf: 19, concurrency: 2,
    frameRange: [first, last], outputLocation: silent, muted: true, logLevel: 'error'});
  const pcm = path.join(OUT, 'original-voice-interval.wav');
  const trim = ['ffmpeg', '-v', 'error', '-i', path.join(D, 'voice.wav'), '-af',
    `atrim=start_sample=${first * 1600}:end_sample=${(last + 1) * 1600},asetpts=PTS-STARTPTS`,
    '-c:a', 'pcm_s16le', pcm];
  const slice = spawnSync(trim[0], trim.slice(1), {encoding: 'utf8'});
  report.voiceSlice = {command: trim, exit: slice.status, stderr: slice.stderr};
  if (slice.status !== 0) throw Error('Exact original voice slice failed');
  const final = path.join(OUT, 'motion-with-original-voice.mp4');
  const mux = ['ffmpeg', '-v', 'error', '-i', silent, '-i', pcm, '-map', '0:v:0', '-map', '1:a:0',
    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-shortest', final];
  const mix = spawnSync(mux[0], mux.slice(1), {encoding: 'utf8'});
  report.mux = {command: mux, exit: mix.status, stderr: mix.stderr};
  if (mix.status !== 0) throw Error('Original voice preview mux failed');
  const decode = spawnSync('ffmpeg', ['-v', 'error', '-xerror', '-err_detect', 'explode', '-i', final, '-f', 'null', '-'], {encoding: 'utf8'});
  report.completeClipDecode = {exit: decode.status, stderr: decode.stderr};
  if (decode.status !== 0 || decode.stderr) throw Error('Complete short clip decode failed');
  report.files = Object.fromEntries([silent, pcm, final].map(file => [file, sha(file)]));
  report.machinePass = true;
} catch (error) {
  report.failure = {name: error.name, message: error.message, stack: error.stack};
} finally {
  if (browser) await browser.close({silent: true});
  report.sourceInputsUnchanged = Object.entries(report.sourceSHA256).every(([file, value]) => fs.existsSync(file) && sha(file) === value);
  if (!report.sourceInputsUnchanged) report.machinePass = false;
  save();
}
console.log(JSON.stringify({machinePass: report.machinePass, report: REPORT}));
process.exitCode = report.machinePass ? 0 : 1;
