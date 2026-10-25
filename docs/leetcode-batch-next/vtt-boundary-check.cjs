'use strict';
const assert = require('node:assert/strict'), fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const {createRequire} = require('node:module');
const root = path.resolve(__dirname, '../..'), episodes = path.join(root, 'episodes'), output = path.join(__dirname, 'site-qa/vtt-boundary-before');
const sourcePath = path.join(root, 'site/src/lib/episodes.ts');
const {transformSync} = createRequire(path.join(root, 'site/package.json'))('esbuild');
const sha = (value) => crypto.createHash('sha256').update(value).digest('hex');
function runtime(source, io = fs, directory = episodes) {
  const selected = source.slice(source.indexOf('const readJson'), source.indexOf('/** 章节：')) + source.slice(source.indexOf('/** WebVTT'), source.indexOf('let cache:'));
  return new Function('fs', 'path', 'EP_DIR', transformSync(selected.replace(/^export /gm, ''), {loader: 'ts'}).code + ';return buildVtt;')(io, path, directory);
}
const slugs = () => fs.readdirSync(episodes).filter((slug) => fs.existsSync(path.join(episodes, slug, 'meta.json'))).sort();
function split(body) {return body.trim().split(/\n\s*\n/).slice(1).map((block) => {const [stamp, ...lines] = block.split('\n'); return {stamp, text: lines.join('\n')};});}
function seconds(stamp) {return stamp.split(':').reduce((total, n) => total * 60 + Number(n), 0);}
if (process.argv[2] === '--snapshot') {
  assert.ok(!fs.existsSync(output), 'Retain the original snapshot; do not overwrite it'); fs.mkdirSync(output, {recursive: true});
  const source = fs.readFileSync(sourcePath, 'utf8'), build = runtime(source), rows = [];
  fs.writeFileSync(path.join(output, 'episodes.ts'), source);
  for (const slug of slugs()) {
    const body = build(slug), built = path.join(root, 'site/dist/episodes', slug, 'captions.vtt');
    assert.equal(fs.readFileSync(built, 'utf8'), body, slug + ': old real generator must match second build');
    fs.writeFileSync(path.join(output, slug + '.vtt'), body); rows.push({slug, sha256: sha(body), bytes: Buffer.byteLength(body)});
  }
  fs.writeFileSync(path.join(output, 'manifest.json'), JSON.stringify({purpose: 'Actual second-build VTT bytes before the integer-millisecond code-card boundary correction',sourceSHA256: sha(source), rows}, null, 2) + '\n');
  console.log(JSON.stringify({snapshotted: rows.length}));
} else if (process.argv[2] === '--verify') {
  const source = fs.readFileSync(sourcePath, 'utf8'), oldSource = fs.readFileSync(path.join(output, 'episodes.ts'), 'utf8'), build = runtime(source), report = {scope: 'Shared VTT serialization only; canonical and production inputs are not modified', checkedAtUTC: new Date().toISOString(), rows: [], synthetic: []};
  for (const slug of slugs()) {
    const oldBody = fs.readFileSync(path.join(output, slug + '.vtt'), 'utf8'), next = build(slug), changes = [], before = split(oldBody), after = split(next);
    assert.equal(before.length, after.length);
    const file = path.join(episodes, slug, 'storyboard.json'), sb = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : {};
    for (let i = 0; i < before.length; i++) {
      assert.equal(before[i].text, after[i].text); const oldTimes = before[i].stamp.split(' --> '), newTimes = after[i].stamp.split(' --> '); assert.equal(oldTimes[0], newTimes[0]);
      if (oldTimes[1] !== newTimes[1]) {
        const card = sb.meta.unvoicedEndCard, boundary = card.from / (sb.meta.fps ?? 30), expected = (Math.ceil(boundary * 1000) - 1) / 1000;
        assert.ok(Number.isInteger(card.from) && card.durationInFrames > 0); assert.ok(Math.abs(boundary * 1000 - Math.round(boundary * 1000)) < 1e-7);
        assert.ok(Math.abs(seconds(oldTimes[1]) - boundary) < 1e-9); assert.ok(Math.abs(seconds(newTimes[1]) - expected) < 1e-9); assert.ok(Math.abs(seconds(oldTimes[1]) - seconds(newTimes[1]) - .001) < 1e-9);
        changes.push({cue: i + 1, previousEnd: oldTimes[1], correctedEnd: newTimes[1], cardFromFrame: card.from, exactBoundarySeconds: boundary});
      }
    }
    if (!changes.length) assert.equal(oldBody, next);
    if (process.argv.includes('--built')) assert.equal(fs.readFileSync(path.join(root, 'site/dist/episodes', slug, 'captions.vtt'), 'utf8'), next);
    report.rows.push({slug, previousSHA256: sha(oldBody), correctedSHA256: sha(next), changes});
  }
  for (const [label, card, endFrame, expectedEnd] of [
    ['integer-millisecond boundary', {from: 5463, durationInFrames: 150}, 5463, '00:03:02.099'],
    ['fractional-millisecond boundary at 30fps', {from: 5633, durationInFrames: 150}, 5633, '00:03:07.766'],
    ['ordinary cue before the card', {from: 5463, durationInFrames: 150}, 5000, '00:02:46.667'],
    ['no appendix', undefined, 5633, '00:03:07.767'],
    ['invalid appendix', {from: 5633, durationInFrames: 0}, 5633, '00:03:07.767'],
  ]) {
    const sb = {meta: {fps: 30, unvoicedEndCard: card}, scenes: [{id: 'chapter', chapterId: 'chapter', shots: [{id: 'shot', durationInFrames: endFrame, subtitles: [{text: 'Boundary fixture', from: 0, to: endFrame - 1}]}]}]};
    const mock = {existsSync: (file) => file.endsWith('storyboard.json'), readFileSync: () => JSON.stringify(sb)};
    const body = runtime(source, mock, '/fixture')('fixture'), oldBody = runtime(oldSource, mock, '/fixture')('fixture');
    assert.equal(split(body)[0].stamp.split(' --> ')[1], expectedEnd); assert.equal(split(body)[0].text, 'Boundary fixture');
    if (!['integer-millisecond boundary'].includes(label)) assert.equal(body, oldBody);
    report.synthetic.push({label, expectedEnd, actualEnd: split(body)[0].stamp.split(' --> ')[1]});
  }
  report.changed = report.rows.filter((row) => row.changes.length).map((row) => row.slug); report.unchangedCount = report.rows.length - report.changed.length; report.generatedBuiltVTTMatched = process.argv.includes('--built');
  fs.writeFileSync(path.join(__dirname, 'site-qa/vtt-boundary-audit.json'), JSON.stringify(report, null, 2) + '\n'); console.log(JSON.stringify({changed: report.changed, unchangedCount: report.unchangedCount, synthetic: report.synthetic.length, built: report.generatedBuiltVTTMatched}));
} else throw new Error('Use --snapshot once before correction, then --verify [--built].');
