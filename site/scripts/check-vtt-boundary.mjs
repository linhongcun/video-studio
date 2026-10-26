// Run the real buildVtt (and its real shotPlan) without Astro's unrelated glob.
// Capture before a change, then compare all current episode VTTs on frozen inputs:
//   node site/scripts/check-vtt-boundary.mjs --capture /tmp/vtt-before.json
//   node site/scripts/check-vtt-boundary.mjs --before /tmp/vtt-before.json --report REPORT.json
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {transformSync} from 'esbuild';

const ROOT = path.resolve(import.meta.dirname, '../..');
const EP_DIR = path.join(ROOT, 'episodes');
const SOURCE = path.join(ROOT, 'site/src/lib/episodes.ts');
const hash = (value) => crypto.createHash('sha256').update(value).digest('hex');
const args = process.argv.slice(2);
const option = (name) => args.includes(name) ? args[args.indexOf(name) + 1] : undefined;

function realBuildVtt(text, io = fs) {
  const start = text.indexOf('const readJson =');
  const end = text.indexOf('\nlet cache:', start);
  assert.ok(start >= 0 && end > start, 'Actual buildVtt source block not found');
  const extracted = text.slice(start, end).replace(/^export /gm, '');
  const {code} = transformSync(extracted, {loader: 'ts'});
  return vm.compileFunction(`${code}\nreturn buildVtt;`, ['fs', 'path', 'EP_DIR'])(io, path, EP_DIR);
}

function frozenIO(files) {
  return {
    existsSync(file) { return Object.hasOwn(files, path.relative(EP_DIR, file)); },
    readFileSync(file, encoding) {
      const relative = path.relative(EP_DIR, file);
      assert.ok(Object.hasOwn(files, relative), `Unexpected input: ${relative}`);
      return encoding ? files[relative] : Buffer.from(files[relative]);
    },
  };
}

function capture() {
  const slugs = fs.readdirSync(EP_DIR).filter((slug) => fs.existsSync(path.join(EP_DIR, slug, 'meta.json'))).sort();
  const files = {};
  for (const slug of slugs) for (const name of ['meta.json', 'storyboard.json', 'remotion/src/timing.json']) {
    const file = path.join(EP_DIR, slug, name);
    if (fs.existsSync(file)) files[path.join(slug, name)] = fs.readFileSync(file, 'utf8');
  }
  const source = fs.readFileSync(SOURCE, 'utf8');
  const build = realBuildVtt(source, frozenIO(files));
  return {capturedAtUTC: new Date().toISOString(), source, sourceSHA256: hash(source), files,
          inputSHA256: Object.fromEntries(Object.entries(files).map(([name, body]) => [name, hash(body)])),
          slugs, vtts: Object.fromEntries(slugs.map((slug) => [slug, build(slug)]))};
}

function cues(vtt) {
  assert.ok(vtt.startsWith('WEBVTT\n'));
  return vtt.trimEnd().split('\n\n').slice(1).map((block) => {
    const [range, ...text] = block.split('\n');
    const match = /^(\d+:\d{2}:\d{2}\.\d{3}) --> (\d+:\d{2}:\d{2}\.\d{3})$/.exec(range);
    assert.ok(match, `Invalid cue range: ${range}`);
    return {start: match[1], end: match[2], text: text.join('\n')};
  });
}

function milliseconds(stamp) {
  const [h, m, s] = stamp.split(':');
  const [whole, part] = s.split('.');
  return BigInt(h) * 3600000n + BigInt(m) * 60000n + BigInt(whole) * 1000n + BigInt(part);
}

function fixture(frame, {kind = 'reference', cueEnd = frame, duration = 150} = {}) {
  const sb = {meta: {fps: 30}, scenes: [{id: 'one', chapterId: 'one', shots: [{id: 'one',
    durationInFrames: frame, subtitles: [{from: 0, to: 29, text: '前面的字幕保持原样'},
                                       {from: 30, to: cueEnd - 1, text: '末句'}]}]}]};
  const meta = {};
  const card = {from: frame, durationInFrames: duration};
  if (kind === 'python') sb.meta.unvoicedEndCard = card;
  else if (kind === 'java') sb.meta.javaEndCard = card;
  else if (kind === 'reference') meta.referenceAppendix = card;
  // Code cards take precedence over a later bibliography in the actual code.
  if (kind === 'python' || kind === 'java') meta.referenceAppendix = {from: frame + 150, durationInFrames: 150};
  return {'fixture/storyboard.json': JSON.stringify(sb), 'fixture/meta.json': JSON.stringify(meta)};
}

function regressions(text) {
  const cases = [
    {name: 'real-counterexample-3924/30-reference', frame: 3924, expected: '00:02:10.799'},
    {name: 'noninteger-millisecond-reference', frame: 5633, expected: '00:03:07.766'},
    {name: 'python-card-precedes-later-reference', frame: 5633, kind: 'python', expected: '00:03:07.766'},
    {name: 'java-card-precedes-later-reference', frame: 3924, kind: 'java', expected: '00:02:10.799'},
    {name: 'end-away-from-card-unchanged', frame: 3924, cueEnd: 3921, expected: '00:02:10.700'},
    {name: 'invalid-zero-duration-card-unchanged', frame: 3924, duration: 0, expected: '00:02:10.800'},
    {name: 'no-card-normal-rounding-unchanged', frame: 3924, kind: 'none', expected: '00:02:10.800'},
  ];
  return cases.map((item) => {
    const result = cues(realBuildVtt(text, frozenIO(fixture(item.frame, item)))('fixture'));
    assert.equal(result[1].end, item.expected, item.name);
    assert.deepEqual(result[0], {start: '00:00:00.000', end: '00:00:01.000', text: '前面的字幕保持原样'}, item.name);
    assert.equal(result[1].start, '00:00:01.000', item.name);
    assert.equal(result[1].text, '末句', item.name);
    console.log(`PASS ${item.name}: ${result[1].end}`);
    return {name: item.name, expectedEnd: item.expected, actualEnd: result[1].end, passed: true};
  });
}

if (option('--capture')) {
  const snapshot = capture();
  fs.writeFileSync(option('--capture'), JSON.stringify(snapshot, null, 2) + '\n');
  console.log(`Captured ${snapshot.slugs.length} actual VTTs and ${Object.keys(snapshot.files).length} real JSON inputs before the fix.`);
} else {
  const current = fs.readFileSync(SOURCE, 'utf8');
  const tests = regressions(current);
  const report = {checkedAtUTC: new Date().toISOString(), scope: 'Execute the actual buildVtt and shotPlan functions, not a copied serializer. Only the exact valid-card cue end is adjusted.',
                  passed: true, regressionTests: tests, afterSourceSHA256: hash(current)};
  if (option('--before')) {
    const before = JSON.parse(fs.readFileSync(option('--before'), 'utf8'));
    assert.equal(hash(before.source), before.sourceSHA256);
    assert.equal(cues(realBuildVtt(before.source, frozenIO(fixture(3924)))('fixture'))[1].end,
                 '00:02:10.800', 'Captured real old function must reproduce the counterexample');
    const oldBuild = realBuildVtt(before.source, frozenIO(before.files));
    const newBuild = realBuildVtt(current, frozenIO(before.files));
    const changed = [], unchanged = [];
    for (const slug of before.slugs) {
      const oldVtt = oldBuild(slug), newVtt = newBuild(slug);
      assert.equal(oldVtt, before.vtts[slug], `${slug}: captured before output differs`);
      const entry = {slug, beforeSHA256: hash(oldVtt), afterSHA256: hash(newVtt)};
      if (oldVtt === newVtt) { unchanged.push(entry); continue; }
      const previous = cues(oldVtt), next = cues(newVtt);
      assert.equal(previous.length, next.length, `${slug}: cue count changed`);
      const sb = JSON.parse(before.files[path.join(slug, 'storyboard.json')]);
      const meta = JSON.parse(before.files[path.join(slug, 'meta.json')]);
      const card = sb.meta?.unvoicedEndCard ?? sb.meta?.javaEndCard ?? meta.referenceAppendix;
      const fps = sb.meta?.fps ?? 30;
      assert.ok(Number.isSafeInteger(fps) && fps > 0 && Number.isSafeInteger(card?.from));
      let expectedVtt = oldVtt;
      const differences = [];
      previous.forEach((oldCue, index) => {
        const newCue = next[index];
        assert.equal(oldCue.start, newCue.start, `${slug}: cue start changed`);
        assert.equal(oldCue.text, newCue.text, `${slug}: cue text changed`);
        if (oldCue.end === newCue.end) return;
        assert.equal(index, previous.length - 1, `${slug}: a non-final cue changed`);
        assert.equal(milliseconds(oldCue.end) - milliseconds(newCue.end), 1n, `${slug}: change is not exactly -1ms`);
        const endMs = milliseconds(newCue.end), numerator = BigInt(card.from) * 1000n, denominator = BigInt(fps);
        assert.ok(endMs * denominator < numerator && (endMs + 1n) * denominator >= numerator,
                  `${slug}: new end is not the greatest integral millisecond strictly before the exact rational card start`);
        expectedVtt = expectedVtt.replace(`${oldCue.start} --> ${oldCue.end}\n`, `${newCue.start} --> ${newCue.end}\n`);
        differences.push({cueIndex: index, beforeEnd: oldCue.end, afterEnd: newCue.end,
                          deltaMilliseconds: -1, exactCardStart: `${card.from}/${fps} seconds`,
                          rationalStrictBoundaryProofPassed: true});
      });
      assert.equal(expectedVtt, newVtt, `${slug}: bytes outside the targeted end timestamp changed`);
      assert.ok(differences.length);
      changed.push({...entry, changes: differences, allOtherBytesIdentical: true});
    }
    const actualNow = capture();
    assert.deepEqual(actualNow.slugs, before.slugs, 'Actual episode selection changed during comparison');
    for (const slug of before.slugs)
      assert.equal(actualNow.vtts[slug], newBuild(slug), `${slug}: current real inputs now generate different VTT bytes`);
    report.beforeSourceSHA256 = before.sourceSHA256;
    report.beforeCaptureAtUTC = before.capturedAtUTC;
    report.beforeSnapshotSHA256 = hash(fs.readFileSync(option('--before')));
    report.comparedFiles = before.slugs.length;
    report.beforeInputSHA256 = before.inputSHA256;
    report.currentInputSHA256 = actualNow.inputSHA256;
    report.changed = changed;
    report.unchanged = unchanged;
    report.currentRealWorkspaceOutputsMatchComparison = true;
    console.log(`Compared ${before.slugs.length} actual VTTs: ${changed.length} changed, ${unchanged.length} byte-identical.`);
    for (const item of changed) console.log(`${item.slug}: ${item.changes.map((c) => `${c.beforeEnd} -> ${c.afterEnd}`).join(', ')}`);
  }
  if (option('--report')) fs.writeFileSync(option('--report'), JSON.stringify(report, null, 2) + '\n');
  console.log('Real buildVtt boundary regressions passed.');
}
