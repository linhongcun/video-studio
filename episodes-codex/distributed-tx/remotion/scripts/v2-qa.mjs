import {bundle} from '@remotion/bundler';
import {openBrowser, renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import webpack from 'webpack';

const root = path.resolve('..');
const args = process.argv.slice(2);
const out = path.resolve(args.find(a => !a.startsWith('--')) ?? '/tmp/ep21-overview-qa');
const wanted = args.find(a => a.startsWith('--shots='))?.slice(8).split(',');
const detailed = (args.find(a => a.startsWith('--detail='))?.slice(9) ?? '05,06,10,11,12,15,16,17,18,20,21,22,25,27,29,30').split(',');
const edges = args.includes('--edges');
const data = JSON.parse(fs.readFileSync(root + '/storyboard.json', 'utf8'));
const shots = data.scenes.flatMap(s => s.shots);
fs.mkdirSync(out, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), enableCaching: false,
  webpackOverride: c => ({...c, resolve: {...c.resolve, alias: {...c.resolve?.alias,
    '@storyboard': root + '/storyboard.json', '@covers': root + '/covers.json'},
    modules: [path.resolve('node_modules'), 'node_modules']}, plugins: [...(c.plugins ?? []),
    new webpack.DefinePlugin({__HAS_VOICE_AUDIO__: false})]})});
const browser = await openBrowser('chrome', {browserExecutable: '/usr/bin/chromium', logLevel: 'error'});
const samples = [];
// Capture the adjacent frames around semantic state changes for manual review.
// Main uses rounded sentence ratios; business scenes use their precise ratio.
const point = (shot, sentence, ratio, business = false) => {
  const starts = shot.cueFrames.sentences;
  const a = starts[sentence], b = starts[sentence + 1] ?? shot.durationInFrames - 15;
  const raw = a + (b - a) * ratio;
  return business ? Math.ceil(raw) : Math.round(raw);
};
const stateChanges = shot => {
  const p = (sentence, ratio) => point(shot, sentence, ratio);
  const b = (sentence, ratio) => point(shot, sentence, ratio, true);
  return ({
    'xa-commit': [['durable-decision', p(0, .62)], ['order-committed', p(1, .34)], ['stock-committed', p(1, .7)]],
    'at-success': [['local-committed', p(0, .27)], ['global-complete', p(1, .6)]],
    'at-failure': [['validated', p(1, .28)], ['restored-stock', p(1, .62)]],
    'at-isolation': [['ordinary-read-returned', p(0, .61)]],
    'tcc-try': [['reserved-atomically', b(0, .65)], ['try-local-committed', b(1, .3)]],
    'tcc-confirm': [['reservation-confirmed', b(1, .6)]],
    'tcc-cancel': [['reservation-released', b(0, .7)]],
    'tcc-limit': [['switch-to-cancelled-branch', b(0, .48)], ['late-try-arrived', b(0, .8)]],
    'saga-intro': [['payment-local-commit', b(0, .65)], ['stock-local-commit', b(1, .6)]],
    'saga-failure': [['payment-deducted', b(1, .25)], ['out-of-stock-failed', b(1, .7)]],
    'saga-compensate': [['new-refund-committed', b(0, .7)]],
    'saga-risk': [['intermediate-state-visible', b(1, .7)]],
    'outbox-record': [['order-and-event-committed', p(1, .6)]],
    'outbox-consume': [['stock-and-marker-committed', p(0, .6)]],
    'tx-message-intro': [['half-message-saved', p(0, .4)], ['producer-local-commit', p(1, .67)]],
    'tx-message-check': [['local-result-returned', p(1, .68)]],
    'tx-message-limit': [['consumer-local-committed', p(1, .55)]],
  })[shot.visualType] ?? [];
};
try {
  const composition = await selectComposition({serveUrl, id: 'Main', puppeteerInstance: browser,
    inputProps: {hideSubtitles: false}, logLevel: 'error'});
  for (const shot of shots.filter(s => !wanted || wanted.includes(s.id))) {
    const phases = detailed.includes(shot.id) ? [0, .18, .38, .58, .78, .97] : [.65];
    for (const [index, phase] of phases.entries()) {
      const local = Math.min(shot.durationInFrames - 1, Math.round(shot.durationInFrames * phase));
      const file = path.join(out, `${shot.id}-${index}.png`);
      await renderStill({composition, serveUrl, frame: shot.from + local,
        output: file, puppeteerInstance: browser, inputProps: {hideSubtitles: false},
        scale: .5, imageFormat: 'png', logLevel: 'error'});
      samples.push({shot: shot.id, visualType: shot.visualType, phase, local,
        frame: shot.from + local, file});
    }
    if (edges) for (const [event, local] of stateChanges(shot)) {
      for (const delta of [-1, 0]) {
        const frame = shot.from + local + delta;
        const file = path.join(out, `${shot.id}-${event}-${delta < 0 ? 'before' : 'after'}.png`);
        await renderStill({composition, serveUrl, frame, output: file,
          puppeteerInstance: browser, inputProps: {hideSubtitles: false},
          scale: .5, imageFormat: 'png', logLevel: 'error'});
        samples.push({shot: shot.id, visualType: shot.visualType, event,
          state: delta < 0 ? 'before' : 'after', local: local + delta, frame, file});
      }
    }
    console.log(`QA ${shot.id} ${shot.visualType}: ${phases.length} phases`);
  }
  fs.writeFileSync(path.join(out, 'frames.json'), JSON.stringify(samples, null, 2) + '\n');
} finally {
  await browser.close({silent: true});
}
