// node scripts/check-chapters.mjs [path/to/episodes-before.ts] (run from site/)
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {transformSync} from 'esbuild';
import {load} from 'js-yaml';

const root = path.resolve(import.meta.dirname, '../../episodes');
const source = path.resolve(import.meta.dirname, '../src/lib/episodes.ts');
function readCompute(file, fileSystem = fs) {
  const text = fs.readFileSync(file, 'utf8');
  // Run the actual chapter code without Astro's unrelated import.meta.glob imports.
  const chapterCode = text.slice(text.indexOf('const readJson ='), text.indexOf('/** WebVTT'));
  const {code} = transformSync(chapterCode.replace(/^export /gm, ''), {loader: 'ts'});
  return vm.compileFunction(`${code}\nreturn computeChapters;`, ['fs', 'path', 'EP_DIR'])(fileSystem, path, root);
}
const before = readCompute(process.argv[2] ?? source);
const after = readCompute(source);
const fallback = readCompute(source, {
  ...fs,
  existsSync: (file) => path.basename(file) !== 'chapters.txt' && fs.existsSync(file),
});

console.log('Episode                 Before  After');
for (const slug of fs.readdirSync(root).filter((s) => fs.existsSync(path.join(root, s, 'meta.json')))) {
  const article = path.join(root, slug, 'article.mdx');
  const frontmatter = fs.existsSync(article) ? fs.readFileSync(article, 'utf8').match(/^---\r?\n([\s\S]*?)\r?\n---/)?.[1] : '';
  const fm = (load(frontmatter ?? '') ?? {}).chapters ?? [];
  const old = before(slug, fm);
  const current = after(slug, fm);
  console.log(`${slug.padEnd(24)}${String(old.chapters.length).padStart(6)}${String(current.chapters.length).padStart(7)}`);
  assert.equal(current.duration, old.duration, `${slug}: duration`);
  assert.equal(current.fps, old.fps, `${slug}: fps`);
  assert.ok(current.chapters.length, `${slug}: empty TOC`);
  current.chapters.forEach((c, i) => {
    assert.ok(c.id && c.title, `${slug}: missing id/title`);
    assert.ok(Number.isFinite(c.start) && c.start >= 0 && (!current.duration || c.start < current.duration), `${slug}: invalid start`);
    assert.ok(i === 0 || c.start >= current.chapters[i - 1].start, `${slug}: unordered TOC`);
    assert.equal(c.frame, Math.round(c.frame), `${slug}: noninteger frame`);
  });
  assert.equal(new Set(current.chapters.map((c) => c.id)).size, current.chapters.length, `${slug}: duplicate ids`);
  assert.deepEqual(current, old, `${slug}: unexpected TOC change`);
}

const actual = after('cache-consistency');
const formatted = actual.chapters.map((c) => `${String(Math.floor(c.start / 60)).padStart(2, '0')}:${String(c.start % 60).padStart(2, '0')} ${c.title}`);
const chapterFile = path.join(root, 'cache-consistency/chapters.txt');
if (fs.existsSync(chapterFile)) {
  const lines = fs.readFileSync(chapterFile, 'utf8').trim().split(/\r?\n/);
  assert.deepEqual(formatted, lines);
}
assert.deepEqual(fallback('cache-consistency').chapters.map((c) => c.title), actual.chapters.map((c) => c.title));
console.log('\ncache-consistency:\n' + formatted.join('\n'));
console.log('\nAll episode comparisons and cache-consistency fallback checks passed.');
