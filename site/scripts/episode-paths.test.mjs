import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {test} from 'node:test';
import {episodeDirectory, episodeSlug, listEpisodes, resolveRepoPath} from './episode-paths.mjs';

function fixture(t) {
  const repoRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'episode-layout-'));
  t.after(() => fs.rmSync(repoRoot, {recursive: true, force: true}));
  const production = path.join(repoRoot, 'episodes/request/example/production');
  const publication = path.join(repoRoot, 'episodes/request/example/publication');
  fs.mkdirSync(production, {recursive: true});
  fs.mkdirSync(publication, {recursive: true});
  fs.writeFileSync(path.join(publication, 'meta.json'), JSON.stringify({slug: 'example', series: 'request'}));
  fs.writeFileSync(path.join(production, 'research.md'), 'Original evidence bytes.');
  fs.writeFileSync(path.join(publication, 'article.mdx'), 'Publication article.');
  fs.mkdirSync(path.join(repoRoot, 'episodes/_shared'), {recursive: true});
  fs.writeFileSync(path.join(repoRoot, 'episodes/_shared/tool.py'), '# shared tool');
  return {repoRoot, production, publication};
}

test('enumerates physical series folders with a unique slug and separate production/publication paths', (t) => {
  const f = fixture(t);
  const records = listEpisodes(f);
  assert.equal(records.length, 1);
  assert.deepEqual(records[0], {slug: 'example', series: 'request', directory: f.publication,
    productionDirectory: f.production, meta: {slug: 'example', series: 'request'}});
  assert.equal(episodeDirectory('example', f), f.publication);
  assert.equal(episodeDirectory('example', {...f, kind: 'production'}), f.production);
  assert.equal(episodeSlug(path.join(f.production, 'revisions/current')), 'example');
});

test('resolves preserved historical evidence paths without rewriting their source bytes', (t) => {
  const f = fixture(t);
  const before = fs.readFileSync(path.join(f.production, 'research.md'));
  for (const relative of ['episodes-codex/example/research.md', 'episodes/request/example/production/research.md'])
    assert.equal(resolveRepoPath(relative, f), path.join(f.production, 'research.md'));
  assert.equal(resolveRepoPath('episodes/example/article.mdx', f), path.join(f.publication, 'article.mdx'));
  assert.equal(resolveRepoPath('episodes-codex/_shared/tool.py', f), path.join(f.repoRoot, 'episodes/_shared/tool.py'));
  assert.deepEqual(fs.readFileSync(path.join(f.production, 'research.md')), before);
  assert.equal(fs.existsSync(path.join(f.repoRoot, 'episodes-codex')), false);
});

test('rejects duplicate slugs across series and contradictory physical classification', (t) => {
  const f = fixture(t);
  const duplicate = path.join(f.repoRoot, 'episodes/peak/example/publication');
  fs.mkdirSync(duplicate, {recursive: true});
  fs.writeFileSync(path.join(duplicate, 'meta.json'), JSON.stringify({slug: 'example', series: 'peak'}));
  assert.throws(() => listEpisodes(f), /Duplicate episode slug/);
  fs.rmSync(path.join(f.repoRoot, 'episodes/peak'), {recursive: true});
  fs.writeFileSync(path.join(f.publication, 'meta.json'), JSON.stringify({series: 'peak'}));
  assert.throws(() => listEpisodes(f), /metadata series differs/);
});

test('historical mapping retains lexical and real filesystem repository boundaries', (t) => {
  const f = fixture(t);
  for (const relative of ['../outside', '/etc/passwd', 'episodes-codex/example/../../outside'])
    assert.throws(() => resolveRepoPath(relative, f), /inside its repository directory/);
  const outside = fs.mkdtempSync(path.join(os.tmpdir(), 'episode-outside-'));
  t.after(() => fs.rmSync(outside, {recursive: true, force: true}));
  fs.writeFileSync(path.join(outside, 'evidence.md'), 'Outside evidence.');
  fs.symlinkSync(path.join(outside, 'evidence.md'), path.join(f.production, 'escape.md'));
  assert.throws(() => resolveRepoPath('episodes-codex/example/escape.md', f), /inside its repository directory/);
});

test('a matching legacy slug and series key does not misinterpret a current physical path', (t) => {
  const f = fixture(t);
  const publication = path.join(f.repoRoot, 'episodes/message-queue/message-queue/publication');
  fs.mkdirSync(publication, {recursive: true});
  fs.writeFileSync(path.join(publication, 'meta.json'), JSON.stringify({series: 'message-queue'}));
  fs.writeFileSync(path.join(publication, 'references.json'), '{}');
  assert.equal(resolveRepoPath('episodes/message-queue/message-queue/publication/references.json', f),
    path.join(publication, 'references.json'));
  assert.equal(resolveRepoPath('episodes/message-queue/references.json', f), path.join(publication, 'references.json'));
});
