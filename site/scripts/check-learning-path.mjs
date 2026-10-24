// Run from site/: node scripts/check-learning-path.mjs
// Exercise the actual metadata + loaders without Astro's MDX import.meta.glob.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {transformSync} from 'esbuild';

const site = path.resolve(import.meta.dirname, '..');
const readJson = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const introSlug = 'distributed-tx-intro', advancedSlug = 'distributed-tx';
const stripImports = (text) => text.replace(/^import .*;\r?\n/gm, '').replace(/^export /gm, '');
function episodeRuntime(showDrafts) {
  const source = stripImports(fs.readFileSync(path.join(site, 'src/lib/episodes.ts'), 'utf8'))
    .replace('import.meta.env.BASE_URL', "'/video-studio/'")
    .replace(/^const articles = .*;$/m, 'const articles = {};');
  const {code} = transformSync(source, {loader: 'ts'});
  return vm.compileFunction(`${code}\nreturn {getEpisodes, getSeries, getRelated, seriesNav, epLabel, learningGuideFor};`,
    ['fs', 'path', 'pkg', 'tagsMeta', 'seriesMeta', 'process'])(fs, path,
    readJson(path.join(site, 'package.json')),
    readJson(path.join(site, 'src/content/tags.json')),
    readJson(path.join(site, 'src/content/series.json')),
    {cwd: () => site, env: {SHOW_DRAFTS: showDrafts ? '1' : '0'}});
}
const releasesSource = stripImports(fs.readFileSync(path.join(site, 'src/lib/releases.ts'), 'utf8'));
const releaseCode = transformSync(releasesSource, {loader: 'ts'}).code;
const {episodesForRelease} = vm.compileFunction(`${releaseCode}\nreturn {episodesForRelease};`, ['fs', 'path'])(fs, path);
const slugs = (rows) => Array.from(rows, (e) => e.slug);

const preview = episodeRuntime(true);
const lessons = preview.getEpisodes();
const intro = lessons.find((e) => e.slug === introSlug);
const advanced = lessons.find((e) => e.slug === advancedSlug);
assert.ok(intro && advanced, 'Both independent EP.21 lessons must exist');
assert.equal(intro.ep, 21);
assert.equal(advanced.ep, 21);
assert.equal(preview.epLabel(20), 'EP.20');
assert.equal(preview.epLabel(intro), 'EP.21 · 入门');
assert.equal(preview.epLabel(advanced), 'EP.21 · 方案详解');
assert.equal(new Set(slugs(lessons)).size, lessons.length, 'No slug may replace another lesson');
assert.deepEqual(slugs(preview.getSeries().find((s) => s.id === 'distributed').episodes),
  ['db-sharding', 'global-id', introSlug, advancedSlug]);
assert.equal(preview.seriesNav(lessons.find((e) => e.slug === 'global-id')).next.slug, introSlug);
assert.equal(preview.seriesNav(intro).prev.slug, 'global-id');
assert.equal(preview.seriesNav(intro).next.slug, advancedSlug);
assert.equal(preview.seriesNav(advanced).prev.slug, introSlug);
assert.equal(preview.learningGuideFor(intro).slug, advancedSlug);
assert.equal(preview.learningGuideFor(advanced).slug, introSlug);
assert.ok(preview.getRelated(advanced).some((e) => e.slug === introSlug && e.episodePart === '入门'));

// The live loader must hide draft lessons AND their learning-guide links.
const published = episodeRuntime(false);
const liveLessons = published.getEpisodes();
assert.equal(liveLessons.some((e) => e.slug === introSlug), !intro.draft);
const liveAdvanced = liveLessons.find((e) => e.slug === advancedSlug);
assert.equal(published.learningGuideFor(liveAdvanced)?.slug, intro.draft ? undefined : introSlug);

// A shared integer EP number must neither overwrite the existing episode nor
// retroactively insert the new prelude into the old release history.
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.45.5', kind: '修正', eps: [21]}, lessons)), [advancedSlug]);
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.26.0', kind: '新增', eps: [21]}, lessons)), [advancedSlug]);
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.46.0', kind: '新增', eps: [21]}, lessons)), [introSlug]);
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.46.1', kind: '修正', eps: [21]}, lessons)).sort(),
  [advancedSlug, introSlug].sort());
console.log('Learning path passed: EP.20 → EP.21 · 入门 → EP.21 · 方案详解; draft visibility, reciprocal guides and release history preserved.');
