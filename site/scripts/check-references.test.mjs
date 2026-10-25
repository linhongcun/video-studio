import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {test} from 'node:test';
import {checkEpisode, checkPublished, checkSources, shaFile} from './check-references.mjs';

const digest = '1'.repeat(64);
const originalQuotation = 'This is the exact "quoted" sentence in the synthetic original.';
const write = (file, value) => fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n');

function fixture(t, slug = 'new-video') {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'reference-policy-'));
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  fs.mkdirSync(path.join(root, 'docs'));
  fs.writeFileSync(path.join(root, 'docs/evidence.md'),
    'Synthetic test evidence; no published citation.\nReference fixture\n' + originalQuotation + '\n');
  const episode = path.join(root, 'episodes', slug);
  fs.mkdirSync(episode, {recursive: true});
  const refs = {schemaVersion: 1, presentation: 'original-title-quote', episode: slug, checkedAt: '2026-10-25', sources: [{
    id: 'R1', organization: 'Synthetic fixture', title: 'Reference fixture', version: '2026',
    titleEvidence: {locator: 'Synthetic document title', evidence: 'docs/evidence.md'},
    url: 'https://example.com/reference', supports: ['A synthetic supported claim'], sections: '§1',
    verification: {status: 'verified', checkedAt: '2026-10-25', evidence: 'docs/evidence.md',
      sourceUrl: 'https://example.com/fixed-source'},
  }]};
  write(path.join(episode, 'references.json'), refs);
  fs.writeFileSync(path.join(episode, 'article.mdx'), '# Reference fixture\nhttps://example.com/reference\nhttps://example.com/fixed-source\n');
  fs.writeFileSync(path.join(episode, 'video.mp4'), 'Synthetic media identity fixture, not a playable MP4.');
  const videoSHA = shaFile(path.join(episode, 'video.mp4'));
  // The body includes a previously completed code card after 1000 narrative
  // frames; the reference appendix follows the complete 1200-frame body.
  const meta = {slug, draft: false, video: 'video.mp4', finalVideoFrames: 1350,
    referenceAppendix: {kind: 'references', from: 1200, durationInFrames: 150,
      sources: 'references.json', manifest: 'reference-appendix.json'}};
  const receipt = {schemaVersion: 1, presentation: 'original-title-quote', episode: slug, bodyFrames: 1200, finalVideoFrames: 1350,
    sourceTitles: [{id: 'R1', title: 'Reference fixture'}], quotations: [],
    outputSHA256: videoSHA, inputs: {bodySHA256: digest, generatorSHA256: digest,
      referencesSHA256: shaFile(path.join(episode, 'references.json'))},
    appendix: {kind: 'references', from: 1200, durationInFrames: 150,
      sourceIds: ['R1'], framesPerPage: 150, pages: [{file: 'references-01.png', sha256: digest}]}};
  const media = {passed: true, bodySHA256: digest, outputSHA256: videoSHA,
    bodyFrames: 1200, appendedFrames: 150, finalFrames: 1350,
    bodyDecodedFramesAndTimestampsEqual: true, outputVideoTimelineContinuous: true,
    audioPacketsAndTimingEqual: true, bodyFrameMD5RowsSHA256: digest,
    audioPacketPayloadAndTimingSHA256: digest, decodedAudioPCM: 'SHA256=' + digest};
  write(path.join(episode, 'meta.json'), meta);
  write(path.join(episode, 'storyboard.json'), {meta: {durationInFrames: 1000}});
  write(path.join(episode, 'reference-appendix.json'), receipt);
  write(path.join(episode, 'reference-appendix-media-check.json'), media);
  return {root, episode, refs, meta, receipt, media, save(name, value) { write(path.join(episode, name), value); }};
}

test('new video with a complete appendix passes, including a prior code card', (t) => {
  const f = fixture(t);
  assert.deepEqual(checkEpisode(f.episode, {repoRoot: f.root}), {slug: 'new-video', sourceCount: 1});
  assert.equal(checkPublished({repoRoot: f.root, legacySlugs: new Set()}).validated.length, 1);
});

test('new public video without appendix is rejected; historical video remains deferred', (t) => {
  const f = fixture(t);
  delete f.meta.referenceAppendix;
  f.save('meta.json', f.meta);
  for (const name of ['references.json', 'reference-appendix.json', 'reference-appendix-media-check.json'])
    fs.unlinkSync(path.join(f.episode, name));
  assert.throws(() => checkPublished({repoRoot: f.root, legacySlugs: new Set()}), /new public video requires/);
  const legacyVideoSHA256 = {'new-video': shaFile(path.join(f.episode, 'video.mp4'))};
  assert.deepEqual(checkPublished({repoRoot: f.root, legacySlugs: new Set(['new-video']), legacyVideoSHA256}).legacyDeferred, ['new-video']);
  fs.appendFileSync(path.join(f.episode, 'video.mp4'), ' remade');
  assert.throws(() => checkPublished({repoRoot: f.root, legacySlugs: new Set(['new-video']), legacyVideoSHA256}), /remade public video requires/);
});

test('legacy episode cannot bypass a broken or partially declared appendix', (t) => {
  const f = fixture(t, 'legacy-video');
  f.meta.referenceAppendix = {};
  f.save('meta.json', f.meta);
  assert.throws(() => checkPublished({repoRoot: f.root, legacySlugs: new Set(['legacy-video'])}), /missing referenceAppendix/);
});

test('appendix path declarations cannot silently fall back from empty metadata', (t) => {
  const f = fixture(t);
  delete f.meta.referenceAppendix.sources;
  f.save('meta.json', f.meta);
  assert.throws(() => checkEpisode(f.episode, {repoRoot: f.root}), /explicit sources and manifest paths/);
});

test('drafts can be unfinished without becoming publishable', (t) => {
  const f = fixture(t);
  f.meta.draft = true;
  delete f.meta.referenceAppendix;
  f.save('meta.json', f.meta);
  fs.unlinkSync(path.join(f.episode, 'references.json'));
  assert.deepEqual(checkPublished({repoRoot: f.root, legacySlugs: new Set()}).drafts, ['new-video']);
  f.meta.draft = false;
  f.save('meta.json', f.meta);
  assert.throws(() => checkPublished({repoRoot: f.root, legacySlugs: new Set()}));
});

test('source preflight rejects empty, unverified, unsupported and invalid-date sources', async (t) => {
  for (const mutation of ['empty', 'pending', 'no-claim', 'date', 'duplicate']) {
    await t.test(mutation, (t) => {
      const f = fixture(t);
      if (mutation === 'empty') f.refs.sources = [];
      if (mutation === 'pending') f.refs.sources[0].verification.status = 'pending';
      if (mutation === 'no-claim') f.refs.sources[0].supports = [];
      if (mutation === 'date') f.refs.sources[0].verification.checkedAt = '2026-02-31';
      if (mutation === 'duplicate') f.refs.sources.push(structuredClone(f.refs.sources[0]));
      f.save('references.json', f.refs);
      assert.throws(() => checkSources(f.episode, {repoRoot: f.root}));
    });
  }
});

test('manually setting verified without existing evidence fails', (t) => {
  const f = fixture(t);
  fs.unlinkSync(path.join(f.root, 'docs/evidence.md'));
  assert.throws(() => checkSources(f.episode, {repoRoot: f.root}), /ENOENT/);
});

test('article must expose both the original and fixed-source links', (t) => {
  const f = fixture(t);
  fs.writeFileSync(path.join(f.episode, 'article.mdx'), 'https://example.com/reference');
  assert.throws(() => checkSources(f.episode, {repoRoot: f.root}), /complete source link missing/);
});

test('source-only preflight succeeds before rendering, but publication requires output proof', (t) => {
  const f = fixture(t);
  fs.unlinkSync(path.join(f.episode, 'video.mp4'));
  fs.unlinkSync(path.join(f.episode, 'reference-appendix.json'));
  assert.equal(checkSources(f.episode, {repoRoot: f.root}).refs.sources.length, 1);
  assert.throws(() => checkEpisode(f.episode, {repoRoot: f.root}));
});

test('reference edits after rendering and changed media cannot use stale receipts', async (t) => {
  await t.test('reference SHA', (t) => {
    const f = fixture(t);
    f.refs.sources[0].version = 'Changed version after rendering';
    f.save('references.json', f.refs);
    assert.throws(() => checkEpisode(f.episode, {repoRoot: f.root}), /reference input SHA differs/);
  });
  await t.test('final MP4 SHA', (t) => {
    const f = fixture(t);
    fs.appendFileSync(path.join(f.episode, 'video.mp4'), ' changed');
    assert.throws(() => checkEpisode(f.episode, {repoRoot: f.root}), /final video SHA differs/);
  });
});

test('range mismatch and failed original-body preservation proof block publication', async (t) => {
  for (const mutation of ['range', 'source-ids', 'page-range', 'body', 'audio', 'failed-proof']) {
    await t.test(mutation, (t) => {
      const f = fixture(t);
      if (mutation === 'range') f.meta.referenceAppendix.from = 1199;
      if (mutation === 'source-ids') f.receipt.appendix.sourceIds = ['R2'];
      if (mutation === 'page-range') f.receipt.appendix.framesPerPage = 149;
      if (mutation === 'body') f.media.bodyDecodedFramesAndTimestampsEqual = false;
      if (mutation === 'audio') f.media.audioPacketsAndTimingEqual = false;
      if (mutation === 'failed-proof') f.media.passed = false;
      f.save('meta.json', f.meta);
      f.save('reference-appendix.json', f.receipt);
      f.save('reference-appendix-media-check.json', f.media);
      assert.throws(() => checkEpisode(f.episode, {repoRoot: f.root}));
    });
  }
});

test('a historical slug cannot keep a declared summary card under the old exemption', (t) => {
  const f = fixture(t);
  f.refs.presentation = 'summary';
  f.save('references.json', f.refs);
  assert.throws(() => checkPublished({repoRoot: f.root, legacySlugs: new Set(['new-video']),
    legacyVideoSHA256: {'new-video': shaFile(path.join(f.episode, 'video.mp4'))}}), /original-title-quote presentation/);
});

test('original-title mode rejects a missing title or unreconciled translated title', async (t) => {
  await t.test('missing original title', (t) => {
    const f = fixture(t);
    delete f.refs.sources[0].title;
    f.save('references.json', f.refs);
    assert.throws(() => checkSources(f.episode, {repoRoot: f.root}), /missing title/);
  });
  await t.test('translated summary does not match title evidence', (t) => {
    const f = fixture(t);
    f.refs.sources[0].title = '自译概括不能替代原标题';
    f.save('references.json', f.refs);
    assert.throws(() => checkSources(f.episode, {repoRoot: f.root}), /original title: exact original text missing/);
  });
});

test('display overrides are forbidden even when empty and supports remain internal', async (t) => {
  for (const field of ['displayTitle', 'displaySupport']) {
    await t.test(field, (t) => {
      const f = fixture(t);
      f.refs.sources[0][field] = '';
      f.save('references.json', f.refs);
      assert.throws(() => checkSources(f.episode, {repoRoot: f.root}), /cannot replace original titles or quotations/);
    });
  }
  await t.test('internal supported claim alone is not displayed as quotation', (t) => {
    const f = fixture(t);
    assert.equal(checkSources(f.episode, {repoRoot: f.root}).refs.sources[0].supports[0], 'A synthetic supported claim');
    assert.equal(checkEpisode(f.episode, {repoRoot: f.root}).sourceCount, 1);
    assert.deepEqual(f.receipt.quotations, []);
  });
});

test('quotation is optional but requires original text, locator and matching evidence when supplied', async (t) => {
  for (const mutation of ['valid', 'no-text', 'no-locator', 'no-evidence', 'summary-as-quote']) {
    await t.test(mutation, (t) => {
      const f = fixture(t);
      const quotation = {text: originalQuotation, locator: 'Synthetic paragraph 1', evidence: 'docs/evidence.md'};
      if (mutation === 'no-text') delete quotation.text;
      if (mutation === 'no-locator') delete quotation.locator;
      if (mutation === 'no-evidence') delete quotation.evidence;
      if (mutation === 'summary-as-quote') quotation.text = f.refs.sources[0].supports[0];
      f.refs.sources[0].quotation = quotation;
      f.save('references.json', f.refs);
      if (mutation === 'valid') {
        f.receipt.quotations = [{id: 'R1', ...quotation}];
        f.receipt.inputs.referencesSHA256 = shaFile(path.join(f.episode, 'references.json'));
        f.save('reference-appendix.json', f.receipt);
        assert.equal(checkEpisode(f.episode, {repoRoot: f.root}).sourceCount, 1);
      } else {
        assert.throws(() => checkSources(f.episode, {repoRoot: f.root}), /quotation/);
      }
    });
  }
});

test('JSON evidence is decoded before checking exact original title and quotation', (t) => {
  const f = fixture(t);
  write(path.join(f.root, 'docs/original.json'), {documents: [{title: 'Reference fixture',
    paragraphs: ['Leading context. ' + originalQuotation + ' Additional source context.']}]});
  f.refs.sources[0].titleEvidence.evidence = 'docs/original.json';
  f.refs.sources[0].quotation = {text: originalQuotation, locator: 'paragraph 1', evidence: 'docs/original.json'};
  f.save('references.json', f.refs);
  assert.equal(checkSources(f.episode, {repoRoot: f.root}).refs.sources.length, 1);
});

test('receipt must bind original-title presentation and exact title/quotation records', async (t) => {
  for (const mutation of ['presentation', 'title', 'quotation', 'missing-quotations']) {
    await t.test(mutation, (t) => {
      const f = fixture(t);
      if (mutation === 'presentation') delete f.receipt.presentation;
      if (mutation === 'title') f.receipt.sourceTitles[0].title = 'A paraphrase';
      if (mutation === 'quotation') f.receipt.quotations = [{id: 'R1', text: f.refs.sources[0].supports[0], locator: '§1', evidence: 'docs/evidence.md'}];
      if (mutation === 'missing-quotations') delete f.receipt.quotations;
      f.save('reference-appendix.json', f.receipt);
      assert.throws(() => checkEpisode(f.episode, {repoRoot: f.root}), /presentation|source titles|quotations/);
    });
  }
});
