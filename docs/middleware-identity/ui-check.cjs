/* Preparation only. Run only after root confirms production rendering and the new site build/port.
 * Four middleware pages; real muted playback before every pause/screenshot. No source/CSS changes.
 */
'use strict';
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const {createRequire} = require('module');
const {execFileSync} = require('child_process');
const SCRATCH = '/workspace/.video-studio-middleware-icon';
const SELECTED = {'server-cache':58, 'cache-consistency':25, 'message-queue':22, 'tx-outbox':50};
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
function parse(args) {
  const opts = {repo: '/workspace/video-studio', out: path.join(SCRATCH, 'ui-check.json'), screenshots: path.join(SCRATCH, 'screenshots')};
  const names = {'--base': 'base', '--expected-version': 'version', '--repo': 'repo', '--out': 'out', '--screenshots': 'screenshots'};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--help') {opts.help = true; continue;}
    const eq = args[i].indexOf('='), key = eq < 0 ? args[i] : args[i].slice(0, eq), value = eq < 0 ? args[++i] : args[i].slice(eq + 1);
    if (!names[key] || !value) throw Error('Unknown/missing CLI option: ' + key);
    opts[names[key]] = value;
  }
  if (!opts.help) {
    if (!opts.base || !opts.version) throw Error('Both --base and --expected-version are mandatory CLI arguments; no port/version or environment default exists.');
    const u = new URL(opts.base); if (!['http:', 'https:'].includes(u.protocol)) throw Error('HTTP(S) preview base required');
    if (!u.pathname.endsWith('/')) u.pathname += '/'; opts.base = u.toString();
  }
  return opts;
}
async function captionsLoadedWithOriginalMode(page) {
  const original = await page.evaluate(() => {
    const v = document.querySelector('video'), modes = [...v.textTracks].map(t => t.mode);
    v.pause(); v.muted = true;
    if (!v.textTracks.length) throw Error('Caption track missing');
    v.textTracks[0].mode = 'hidden'; return modes;
  });
  await page.waitForFunction(() => {
    const v = document.querySelector('video'), t = v.querySelector('track');
    return t?.readyState === 2 && v.textTracks[0].cues?.length > 0;
  }, null, {timeout: 25000});
  return await page.evaluate(modes => {
    const v = document.querySelector('video'), cueCountWhileLoaded = v.textTracks[0].cues.length; [...v.textTracks].forEach((t, i) => {t.mode = modes[i];});
    return {originalModes: modes, restoredModes: [...v.textTracks].map(t => t.mode), readyState: v.querySelector('track').readyState, cueCount: cueCountWhileLoaded, cueCountMeasuredInHiddenMode: true, label: v.textTracks[0].label};
  }, original);
}
async function setupSeek(page, seconds) {
  await page.evaluate(seconds => {
    const v = document.querySelector('video'); window.__pilotSetupSeeked = false; v.pause();
    v.addEventListener('seeked', () => {window.__pilotSetupSeeked = true;}, {once: true}); v.currentTime = seconds;
  }, seconds);
  await page.waitForFunction(() => window.__pilotSetupSeeked && !document.querySelector('video').seeking && document.querySelector('video').readyState >= 2, null, {timeout: 25000});
}
async function realPlayThenPause(page, target) {
  return await page.evaluate(async target => {
    const v = document.querySelector('video'); v.muted = true; v.playbackRate = 1;
    if (target >= v.duration) throw Error('Requested product-scene target exceeds current media duration');
    const result = {beforeTime: v.currentTime, requestedPauseTarget: target, wallStarted: performance.now(), playingEvent: false, timeupdateEvents: 0, videoFrameCallbacks: 0, lastPresentedMediaTime: null, evidence: 'Real video.play(), observed playback/time progression, then pause; any earlier seek is separate setup only'};
    if (target - result.beforeTime < .5) throw Error('Need at least half a second of real playback before capture');
    return await new Promise((resolve, reject) => {
      let done = false, callbackId;
      const timer = setTimeout(() => finish(Error('Timed out waiting for real media playback')), 25000);
      const onPlaying = () => {result.playingEvent = true;};
      const onTime = () => {result.timeupdateEvents++;};
      const onError = () => finish(Error('Media error during playback: ' + v.error?.message));
      const onEnded = () => finish(Error('Media ended before capture target'));
      function finish(error) {
        if (done) return; done = true; clearTimeout(timer); v.pause();
        v.removeEventListener('playing', onPlaying); v.removeEventListener('timeupdate', onTime); v.removeEventListener('error', onError); v.removeEventListener('ended', onEnded);
        if (callbackId && v.cancelVideoFrameCallback) v.cancelVideoFrameCallback(callbackId);
        result.afterTime = v.currentTime; result.advancedSeconds = result.afterTime - result.beforeTime; result.wallElapsedMs = performance.now() - result.wallStarted;
        result.paused = v.paused; result.readyState = v.readyState;
        if (error) reject(error); else resolve(result);
      }
      function tick(now, metadata) {
        if (done) return;
        if (metadata) {result.videoFrameCallbacks++; result.lastPresentedMediaTime = metadata.mediaTime;}
        if (!v.paused && v.currentTime >= target && result.playingEvent) return finish();
        if (v.requestVideoFrameCallback) callbackId = v.requestVideoFrameCallback(tick); else requestAnimationFrame(tick);
      }
      v.addEventListener('playing', onPlaying); v.addEventListener('timeupdate', onTime); v.addEventListener('error', onError); v.addEventListener('ended', onEnded);
      if (v.requestVideoFrameCallback) callbackId = v.requestVideoFrameCallback(tick); else requestAnimationFrame(tick);
      v.play().catch(error => finish(error));
    });
  }, target);
}
async function screenshotAfterRealPlayback(page, shot, viewport, fps, opts, report, slug) {
  if (shot.preroll !== null) await setupSeek(page, shot.preroll);
  const playback = await realPlayThenPause(page, shot.seconds);
  await page.waitForFunction(() => {const v = document.querySelector('video'); return v.paused && !v.seeking && v.readyState >= 2 && !v.error;}, null, {timeout: 25000});
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  await page.evaluate(() => document.querySelector('.vp').scrollIntoView({block: 'start'}));
  await page.locator('video').hover();
  await page.waitForFunction(() => !document.querySelector('.vp .vwrap').classList.contains('stuck'), null, {timeout: 5000});
  const state = await page.evaluate(() => {
    const v = document.querySelector('video'), r = v.getBoundingClientRect();
    return {captureTime: v.currentTime, paused: v.paused, muted: v.muted, controls: v.controls, controlsAttribute: v.hasAttribute('controls'), readyState: v.readyState, seeking: v.seeking,
      mediaError: v.error ? {code: v.error.code, message: v.error.message} : null, errorNoticeVisible: !document.querySelector('.vp .err').hidden,
      documentScrollWidth: document.documentElement.scrollWidth, bodyScrollWidth: document.body.scrollWidth, videoRect: {x: r.x, y: r.y, width: r.width, height: r.height, right: r.right}, captionModesAtCapture: [...v.textTracks].map(t => t.mode)};
  });
  const file = path.join(opts.screenshots, slug + '-' + viewport.width + '-' + shot.name + '.png');
  await page.screenshot({path: file, fullPage: false});
  const row = {slug, scene: shot.name, requestedSeconds: shot.seconds, setupSeekSeconds: shot.preroll, viewport, playback, ...state, approxFrame: Math.round(state.captureTime * fps), fps, screenshot: file, screenshotSha256: sha(file), actualVisualReviewPending: true};
  row.mechanicalPassed = playback.playingEvent && playback.advancedSeconds >= .5 && (playback.videoFrameCallbacks > 0 || playback.timeupdateEvents > 0) && state.paused && state.muted && state.controls && state.controlsAttribute && state.readyState >= 2 && !state.seeking && !state.mediaError && !state.errorNoticeVisible && state.documentScrollWidth <= viewport.width + 1 && state.bodyScrollWidth <= viewport.width + 1 && state.videoRect.right <= viewport.width + 1;
  report.captures.push(row);
  console.log(JSON.stringify({phase: 'capture', scene: shot.name, viewport, actualCaptureTime: row.captureTime, approxFrame: row.approxFrame, realPlayAdvance: playback.advancedSeconds, mechanicalPassed: row.mechanicalPassed, screenshot: file}));
}
async function run(opts) {
  const req = createRequire(path.join(opts.repo, 'episodes-codex/load-balancing/remotion/package.json'));
  let dependency; try {dependency = req.resolve('playwright');} catch {dependency = '/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.js';}
  const {chromium} = req(dependency);
  const report = {issue:271, scope:'Four middleware identity movies, two viewports, eight real-play/pause captures; exact media and chapter/VTT checks are separate', base:opts.base, expectedVersion:opts.version, helper:__filename, helperSha256:sha(__filename), browserDependency:dependency, startedAtUtc:new Date().toISOString(), pages:[],captures:[],errors:[],actualScreenshotReviewPending:true, limits:['Each capture follows an explicit setup seek and at least0.5seconds actual muted playback; not continuous/full-movie listening.','Actual captureTime and presentedMediaTime measured; not assumed equal to setup seek.','Caption cues measured while hidden, then original mode restored before capture. No native controls or spinner CSS hidden.']};
  try {report.gitHeadAtRun = execFileSync('git', ['rev-parse', 'HEAD'], {cwd: opts.repo, encoding: 'utf8'}).trim();} catch {}
  fs.mkdirSync(opts.screenshots, {recursive: true}); let browser;
  try {
    browser = await chromium.launch({headless: true, executablePath: '/usr/bin/chromium', args: ['--no-sandbox', '--disable-dev-shm-usage']}); report.browserVersion = await browser.version();
    for (const viewport of [{width: 1440, height: 1000}, {width: 390, height: 844}]) {
      for (const [slug, seconds] of Object.entries(SELECTED)) {
      const meta=read(path.join(opts.repo,'episodes',slug,'meta.json')), sb=read(path.resolve(opts.repo,meta.sourcePath,'../storyboard.json')), fps=sb.meta.fps;
      const page = await browser.newPage({viewport}); page.on('pageerror', e => report.errors.push({viewport, pageError: e.message}));
      try {
        await page.goto(opts.base + 'episodes/' + slug + '/', {waitUntil: 'domcontentloaded', timeout: 30000});
        await page.waitForFunction(() => {const v = document.querySelector('video'); return v && (v.readyState >= 1 || v.error);}, null, {timeout: 25000});
        await page.evaluate(() => document.fonts.ready);
        const p = await page.evaluate(() => {const v = document.querySelector('video'); return {h1: document.querySelector('h1')?.textContent.trim(), footerVersion: document.querySelector('footer')?.textContent.match(/\bv(\d+\.\d+\.\d+)\b/)?.[1], duration: v.duration, controls: v.controls, readyState: v.readyState, currentSrc: v.currentSrc, mediaError: v.error ? {code: v.error.code, message: v.error.message} : null};});
        p.slug = slug; p.viewport = viewport; p.expectedTitle = meta.title; p.passed = p.h1 === meta.title && p.footerVersion === opts.version && p.controls && !p.mediaError;
        p.captions = await captionsLoadedWithOriginalMode(page); report.pages.push(p);
        for (const target of [{name:'identity',seconds,preroll:seconds-1}]) await screenshotAfterRealPlayback(page, target, viewport, fps, opts, report, slug);
      } catch (e) {report.errors.push({viewport, error: String(e)}); console.log(JSON.stringify({phase: 'error', viewport, error: String(e)}));}
      finally {await page.close();}
      }
    }
  } catch (e) {report.errors.push({fatal: String(e)});}
  finally {if (browser) await browser.close();}
  report.completedAtUtc = new Date().toISOString(); report.mechanicalPassed = report.errors.length === 0 && report.pages.length === 8 && report.pages.every(x => x.passed) && report.captures.length === 8 && report.captures.every(x => x.mechanicalPassed);
  fs.mkdirSync(path.dirname(opts.out), {recursive: true}); fs.writeFileSync(opts.out, JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({done: true, mechanicalPassed: report.mechanicalPassed, captures: report.captures.length, actualScreenshotReviewPending: true, report: opts.out}));
  if (!report.mechanicalPassed) process.exitCode = 1; return report;
}
module.exports = {parse, SELECTED, run};
if (require.main === module) {const opts = parse(process.argv.slice(2)); if (opts.help) console.log('After render/build-ready: TMPDIR=/workspace/.video-studio-tmp flock /tmp/video-studio-render.lock node ui-check.cjs --base=http://127.0.0.1:NEW_PORT/video-studio/ --expected-version=X.Y.Z'); else run(opts).catch(e => {console.error(e); process.exitCode = 1;});}
