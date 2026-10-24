// Run from repository root or site/: node site/scripts/check-learning-path.mjs
// Exercise real metadata and real loaders without Astro's MDX import.meta.glob.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {transformSync} from 'esbuild';

const site = path.resolve(import.meta.dirname, '..');
const readJson = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const introSlug = 'distributed-tx-intro', archiveSlug = 'distributed-tx';
const mechanismSlugs = ['tx-2pc', 'tx-tcc', 'tx-saga', 'tx-outbox'];
const complete = process.argv.includes('--complete');
const existingOnly = process.argv.includes('--existing-only');
const stripImports = (text) => text.replace(/^import .*;\r?\n/gm, '').replace(/^export /gm, '');
function episodeRuntime(showDrafts) {
  const source = stripImports(fs.readFileSync(path.join(site, 'src/lib/episodes.ts'), 'utf8'))
    .replace('import.meta.env.BASE_URL', "'/video-studio/'")
    .replace(/^const articles = .*;$/m, 'const articles = {};');
  const {code} = transformSync(source, {loader: 'ts'});
  return vm.compileFunction(`${code}\nreturn {getEpisodes, getSeries, getRelated, seriesNav, epLabel, learningGuideFor, archiveReplacementsFor, compareLessons};`,
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
const introArticle = fs.readFileSync(path.join(site, '../episodes', introSlug, 'article.mdx'), 'utf8');
assert.equal(introArticle.includes('../distributed-tx/'), false, 'Published intro article must not lead back to the compilation');
for (const slug of mechanismSlugs) {
  assert.ok(introArticle.includes(`../${slug}/`), `Missing independent lesson link: ${slug}`);
  const config = readJson(path.join(site, '../episodes-codex', slug, 'episode-config.json'));
  assert.ok(introArticle.includes(config.title), `Intro article title is stale for ${slug}`);
}
const linkedOrder = mechanismSlugs.map((slug) => introArticle.lastIndexOf(`../${slug}/`));
assert.deepEqual(linkedOrder, [...linkedOrder].sort((a, b) => a - b));


const preview = episodeRuntime(true);
const lessons = preview.getEpisodes();
const all = preview.getEpisodes({includeArchived: true});
const intro = lessons.find((e) => e.slug === introSlug);
const archive = all.find((e) => e.slug === archiveSlug);
const history = [...all].sort(preview.compareLessons);
assert.ok(intro && archive, 'The intro and historical compilation must remain addressable');
assert.ok(archive.archived);
assert.equal(preview.epLabel(20), 'EP.20');
assert.equal(preview.epLabel(intro), 'EP.21 · 入门');
assert.equal(lessons.some((e) => e.slug === archiveSlug), false, 'Archive must not appear in the catalog');
assert.equal(preview.seriesNav(archive), null, 'Archive must not receive an invalid series position');
assert.equal(new Set(slugs(all)).size, all.length, 'No new slug may overwrite a previous lesson');
assert.equal(preview.getRelated({...intro, related: [{slug: archiveSlug}]}).length, 0, 'Archive must not leak through related recommendations');
assert.equal(preview.learningGuideFor({...intro, learningGuide: {slug: archiveSlug, label: 'old'}}), undefined);

const published = episodeRuntime(false);
const liveLessons = published.getEpisodes();
assert.ok(published.getEpisodes({includeArchived: true}).some((e) => e.slug === archiveSlug));
assert.equal(liveLessons.some((e) => e.slug === archiveSlug), false);
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.45.5', kind: '修正', eps: [21]}, history)), [archiveSlug]);
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.26.0', kind: '新增', eps: [21]}, history)), [archiveSlug]);
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.46.0', kind: '新增', eps: [21]}, history)), [introSlug]);

if (!existingOnly) {
  const mechanisms = mechanismSlugs.map((slug) => lessons.find((e) => e.slug === slug));
  mechanisms.forEach((e, i) => assert.ok(e, `Missing production metadata for ${mechanismSlugs[i]}`));
  const expected = ['db-sharding', 'global-id', introSlug, ...mechanismSlugs];
  assert.deepEqual(slugs(preview.getSeries().find((s) => s.id === 'distributed').episodes), expected);
  const chain = [intro, ...mechanisms];
  for (let i = 0; i < chain.length; i++) {
    const e = chain[i];
    assert.equal(e.ep, 21);
    assert.equal(e.lessonOrder, i);
    assert.equal(preview.seriesNav(e).prev.slug, i ? chain[i - 1].slug : 'global-id');
    assert.equal(preview.seriesNav(e).next?.slug, chain[i + 1]?.slug);
    if (i < chain.length - 1) {
      assert.equal(preview.learningGuideFor(e)?.slug, chain[i + 1].slug);
      const actual = published.learningGuideFor(e);
      assert.equal(actual?.slug, chain[i + 1].draft ? undefined : chain[i + 1].slug);
    }
    if (i > 0) {
      assert.equal(e.firstRelease, 'v0.47.0');
      assert.ok(preview.getRelated(e).some((r) => r.slug === introSlug), `${e.slug} must offer the prerequisite`);
      if (complete) assert.equal(e.draft, false, `${e.slug} is not published yet`);
    }
  }
  assert.equal(preview.learningGuideFor(mechanisms.at(-1))?.slug, introSlug);
  assert.equal(preview.seriesNav(lessons.find((e) => e.slug === 'global-id')).next.slug, introSlug);
  const liveExpected = expected.filter((slug) => !lessons.find((e) => e.slug === slug).draft);
  assert.deepEqual(slugs(published.getSeries().find((s) => s.id === 'distributed').episodes), liveExpected);
  assert.deepEqual(slugs(preview.archiveReplacementsFor(archive)), mechanismSlugs);
  for (const replacement of published.archiveReplacementsFor(archive)) {
    assert.equal(replacement.published, !mechanisms.find((e) => e.slug === replacement.slug).draft);
  }
  assert.deepEqual(slugs(episodesForRelease({tag: 'v0.47.0', kind: '新增', eps: [21]}, history)), mechanismSlugs);
}
if (process.argv.includes('--built')) {
  const dist = path.join(site, 'dist');
  const text = (rel) => fs.readFileSync(path.join(dist, rel), 'utf8');
  const archivePage = text(`episodes/${archiveSlug}/index.html`);
  const introPage = text(`episodes/${introSlug}/index.html`);
  assert.equal(introPage.includes(`/episodes/${archiveSlug}/`), false, 'Intro page still links the old compilation');
  assert.equal(introPage.includes(`href="../${archiveSlug}/"`), false);
  for (const slug of mechanismSlugs) assert.ok(introPage.includes(`href="../${slug}/"`), `Built intro article lacks ${slug}`);
  assert.ok(archivePage.includes('data-archived') && archivePage.includes('此合集已拆为独立短片'));
  assert.ok(archivePage.includes('name="robots" content="noindex,follow"'));
  assert.match(archivePage, /<html[^>]*data-pagefind-ignore="all"/);
  assert.equal(archivePage.includes('第 0/'), false);
  assert.equal(archivePage.includes('class="pager"'), false);
  assert.equal((text(`episodes/${archiveSlug}/captions.vtt`).match(/-->/g) ?? []).length, 76);
  const movie = fs.readFileSync(path.join(dist, `episodes/${archiveSlug}/video.mp4`));
  assert.equal(createHash('sha256').update(movie).digest('hex'), 'ef17294435f00901ffcdc7c3711501102ffea9db8e7c0160b5001cbb6b19eb91');
  for (const rel of ['index.html', 'series/distributed/index.html', 'tags/分布式事务/index.html', 'rss.xml']) {
    assert.equal(text(rel).includes(`/episodes/${archiveSlug}/`), false, `Archive leaked into ${rel}`);
  }
  const fragmentDir = path.join(dist, 'pagefind/fragment');
  const fragments = fs.readdirSync(fragmentDir).filter((f) => f.endsWith('.pf_fragment')).map((f) => {
    const raw = gunzipSync(fs.readFileSync(path.join(fragmentDir, f))).toString('utf8');
    assert.ok(raw.startsWith('pagefind_dcd'));
    return JSON.parse(raw.slice('pagefind_dcd'.length));
  });
  assert.equal(fragments.some((f) => f.url === `/episodes/${archiveSlug}/`), false, 'Archive remains in actual search index');
  assert.ok(fragments.some((f) => f.url === `/episodes/${introSlug}/`));
  for (const slug of mechanismSlugs) {
    const lesson = lessons.find((e) => e.slug === slug);
    if (lesson?.draft) {
      assert.equal(archivePage.includes(`href="/video-studio/episodes/${slug}/"`), false);
      assert.ok(archivePage.includes(lesson.title), `Draft replacement ${slug} needs a visible title`);
    } else if (lesson) {
      assert.ok(archivePage.includes(`href="/video-studio/episodes/${slug}/"`));
      assert.ok(fs.existsSync(path.join(dist, `episodes/${slug}/index.html`)));
    }
  }
  console.log(`Built routes, original media/VTT and archive search exclusion passed (${fragments.length} indexed pages).`);
}
console.log(existingOnly
  ? 'Archive/catalog separation passed; original page and release history remain addressable. New-course checks intentionally skipped.'
  : `Learning path passed: EP.20 → 入门 → 2PC → TCC → Saga → 可靠消息; archive excluded from catalog, draft links safe, original release history preserved${complete ? '; all four shorts published' : ''}.`);
