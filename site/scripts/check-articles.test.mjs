import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {checkArticle, checkArticles} from './check-articles.mjs';
import {readArticleSources, localFile} from './article-sources.mjs';

const quote = '<SourceQuote sourceId="A1" supports="The protocol confirms receipt of the peer’s sequence number." />';
const picture = '<Figure src="/video-studio/episodes/example/article/handshake.jpg" alt="Each peer confirms the other’s sequence number" caption="The final acknowledgment confirms the server’s SYN." seekTo={4.5} />';

function fixture(t, content = `${quote}\n\n${picture}`) {
  const repoRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'article-check-'));
  t.after(() => fs.rmSync(repoRoot, {recursive: true, force: true}));
  const episode = path.join(repoRoot, 'episodes/example');
  fs.mkdirSync(path.join(episode, 'article'), {recursive: true});
  const source = {
    id: 'A1', title: 'Transmission protocol', organization: 'Standards group', version: '2026',
    url: 'https://example.org/protocol', supports: ['Receipt is confirmed.'],
    verification: {status: 'verified', checkedAt: '2026-10-26', evidence: 'evidence.json'},
    quotation: {text: 'The peer sends a "confirming acknowledgment".', locator: 'Section 3, paragraph 2', evidence: 'evidence.json'},
  };
  fs.writeFileSync(path.join(repoRoot, 'evidence.json'), JSON.stringify({original: source.quotation.text}));
  fs.writeFileSync(path.join(episode, 'article-sources.json'), JSON.stringify({schemaVersion: 1, episode: 'example', sources: [source]}));
  fs.writeFileSync(path.join(episode, 'article.mdx'), `---\ntitle: Example\n---\n\n## Handshake {#handshake}\n\n${content}\n`);
  fs.writeFileSync(path.join(episode, 'meta.json'), JSON.stringify({finalVideoFrames: 300, draft: false}));
  fs.writeFileSync(path.join(episode, 'article/handshake.jpg'), Buffer.from([0xff, 0xd8, 0xff, 0xd9]));
  return {repoRoot, episode, source};
}

test('checks rendered article elements and decodes saved JSON evidence', (t) => {
  const {repoRoot} = fixture(t);
  assert.deepEqual(checkArticle('example', {repoRoot}), {slug: 'example', quotes: 1, figures: 1});
});

test('a component sample in a code fence does not satisfy the article requirement', (t) => {
  const {repoRoot} = fixture(t, `\`\`\`mdx\n${quote}\n\`\`\`\n\n${picture}`);
  assert.throws(() => checkArticle('example', {repoRoot}), /missing a verified SourceQuote/);
});

test('hidden wrappers cannot satisfy visible article requirements', (t) => {
  const {repoRoot, episode} = fixture(t);
  for (const attr of ['hidden', 'aria-hidden="true"', 'style={{display: "none"}}', 'style={{visibility: "hidden"}}', 'style="display: none !important"']) {
    fs.writeFileSync(path.join(episode, 'article.mdx'), `<div ${attr}>\n\n${quote}\n\n${picture}\n\n</div>`);
    assert.throws(() => checkArticle('example', {repoRoot}), /missing a verified SourceQuote/);
  }
  fs.writeFileSync(path.join(episode, 'article.mdx'), `<div hidden={false}>\n\n${quote}\n\n${picture}\n\n</div>`);
  assert.equal(checkArticle('example', {repoRoot}).quotes, 1);
});

test('children of components without slots cannot satisfy article requirements', (t) => {
  const {repoRoot, episode} = fixture(t, `${picture.replace('/>', '>')}\n\n${quote}\n\n</Figure>`);
  assert.throws(() => checkArticle('example', {repoRoot}), /Figure does not render child content/);
  fs.writeFileSync(path.join(episode, 'article.mdx'), `${quote.replace('/>', '>')}\n\n${picture}\n\n</SourceQuote>`);
  assert.throws(() => checkArticle('example', {repoRoot}), /SourceQuote does not render child content/);
});

test('rejects an invented excerpt even when its evidence file exists', (t) => {
  const {repoRoot} = fixture(t);
  fs.writeFileSync(path.join(repoRoot, 'evidence.json'), JSON.stringify({summary: 'The source discusses receipt.'}));
  assert.throws(() => checkArticle('example', {repoRoot}), /exact quotation missing/);
});

test('supported claims and citation metadata cannot serve as their own source evidence', (t) => {
  const {repoRoot, episode, source} = fixture(t);
  fs.writeFileSync(path.join(repoRoot, 'evidence.json'), JSON.stringify({supports: [source.quotation.text]}));
  assert.throws(() => checkArticle('example', {repoRoot}), /exact quotation missing/);
  source.quotation.evidence = 'episodes/example/article-sources.json';
  fs.writeFileSync(path.join(episode, 'article-sources.json'), JSON.stringify({schemaVersion: 1, episode: 'example', sources: [source]}));
  assert.throws(() => checkArticle('example', {repoRoot}), /cannot serve as its own original-text evidence/);
});

test('a symlink alias cannot disguise citation metadata as original evidence', (t) => {
  const {repoRoot, episode, source} = fixture(t);
  fs.symlinkSync(path.join(episode, 'article-sources.json'), path.join(repoRoot, 'alias.json'));
  source.quotation.evidence = 'alias.json';
  fs.writeFileSync(path.join(episode, 'article-sources.json'), JSON.stringify({schemaVersion: 1, episode: 'example', sources: [source]}));
  assert.throws(() => checkArticle('example', {repoRoot}), /cannot serve as its own original-text evidence/);
});

test('source supplements cannot silently replace video reference identities', (t) => {
  const {repoRoot, episode, source} = fixture(t);
  fs.writeFileSync(path.join(episode, 'references.json'), JSON.stringify({schemaVersion: 1, episode: 'example', sources: [source]}));
  assert.throws(() => readArticleSources('example', {repoRoot}), /duplicate source id/);
});

test('rejects misleading video timestamps, poster images and foreign image paths', (t) => {
  const {repoRoot, episode} = fixture(t);
  for (const [changed, message] of [
    [picture.replace('4.5', '10'), /real video timestamp/],
    [picture.replace('article/handshake.jpg', 'cover-16x9.jpg'), /article\/ directory/],
    [picture.replace('/episodes/example/', '/episodes/another/'), /article\/ directory/],
  ]) {
    fs.writeFileSync(path.join(episode, 'article.mdx'), `${quote}\n\n${changed}`);
    assert.throws(() => checkArticle('example', {repoRoot}), message);
  }
});

test('rejects a symlink escaping the evidence directory', (t) => {
  const {repoRoot, episode} = fixture(t);
  fs.symlinkSync(path.join(repoRoot, 'evidence.json'), path.join(episode, 'escape.json'));
  assert.throws(() => localFile(episode, 'escape.json'), /inside its directory/);
});

test('a captioned accessible SVG counts, and a decorative SVG does not', (t) => {
  const diagram = '<figure><svg role="img"><title>Three messages exchange and confirm initial sequence numbers</title></svg><figcaption>示意图：交换序号后，各自确认对方的起始序号。</figcaption></figure>';
  const {repoRoot, episode} = fixture(t, `${quote}\n\n${diagram}`);
  assert.equal(checkArticle('example', {repoRoot}).figures, 1);
  fs.writeFileSync(path.join(episode, 'article.mdx'), `${quote}\n\n${diagram.replace(/<figcaption>.*?<\/figcaption>/, '')}`);
  assert.throws(() => checkArticle('example', {repoRoot}), /needs a figcaption/);
});

test('a locally authored diagram is explicit and does not need a video timestamp', (t) => {
  const {repoRoot} = fixture(t, `${quote}\n\n${picture.replace('seekTo={4.5}', 'kind="diagram"').replace('The final acknowledgment confirms the server’s SYN.', '自制示意图：双方交换并确认初始序号。')}`);
  assert.equal(checkArticle('example', {repoRoot}).figures, 1);
});

test('archived articles are kept out of the current-content requirement', (t) => {
  const {repoRoot, episode} = fixture(t, 'A historical article.');
  fs.writeFileSync(path.join(episode, 'meta.json'), JSON.stringify({archived: true}));
  assert.deepEqual(checkArticles({repoRoot}), {results: [], failures: []});
});
