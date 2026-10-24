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
const {episodesForRelease, parseEpisodeSlugs} = vm.compileFunction(`${releaseCode}\nreturn {episodesForRelease, parseEpisodeSlugs};`, ['fs', 'path'])(fs, path);
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
    // The last mechanism may lead into the first lesson of a later series.
    const series = preview.getSeries();
    const seriesIndex = series.findIndex((s) => s.id === e.series);
    const nextSeries = series[seriesIndex + 1];
    const crossNext = series[seriesIndex].crossSeriesNavigation !== false && nextSeries?.crossSeriesNavigation !== false ? nextSeries : undefined;
    assert.equal(preview.seriesNav(e).next?.slug, chain[i + 1]?.slug ?? crossNext?.episodes[0]?.slug);
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

// LeetCode problem numbers are display labels, not historical EP identifiers.
const algorithmSlug = 'container-most-water';
const algorithm = lessons.find((e) => e.slug === algorithmSlug);
assert.ok(algorithm, 'The first algorithm lesson must be available in preview');
assert.equal(algorithm.ep, 22);
assert.equal(algorithm.problemNumber, 11);
assert.equal(preview.epLabel(algorithm), 'LC.11');
assert.equal(preview.epLabel(11), 'EP.11');
assert.equal(preview.epLabel(preview.getRelated({related: [algorithmSlug]})[0]), 'LC.11');
const nextAlgorithmSlug = 'longest-substring';
const nextAlgorithm = lessons.find((e) => e.slug === nextAlgorithmSlug);
assert.ok(nextAlgorithm, 'The sliding-window lesson must be available in preview');
assert.equal(nextAlgorithm.ep, 23);
assert.equal(nextAlgorithm.problemNumber, 3);
assert.equal(preview.epLabel(nextAlgorithm), 'LC.3');
assert.deepEqual(slugs(preview.getSeries().find((s) => s.id === 'leetcode').episodes), [algorithmSlug, nextAlgorithmSlug]);
assert.equal(preview.seriesNav(nextAlgorithm).prev.slug, algorithmSlug);
assert.deepEqual(slugs(episodesForRelease({tag: nextAlgorithm.firstRelease, kind: '新增', eps: [23]}, lessons)), [nextAlgorithmSlug]);
assert.equal(preview.seriesNav(algorithm).prev, undefined, 'Algorithms have no distributed-systems prerequisite');
assert.notEqual(preview.seriesNav(lessons.find((e) => e.slug === mechanismSlugs.at(-1))).next?.series, 'leetcode', 'System-design learning path must not lead into an unrelated algorithm');
assert.equal(liveLessons.some((e) => e.slug === algorithmSlug), !algorithm.draft);
assert.deepEqual(slugs(episodesForRelease({tag: algorithm.firstRelease, kind: '新增', eps: [22]}, lessons)), [algorithmSlug]);
assert.ok(!slugs(episodesForRelease({tag: 'v0.45.0', kind: '修正', eps: [11]}, lessons)).includes(algorithmSlug),
  'An old EP.11 release must not link to LeetCode problem 11');

// Agent and LeetCode can share ep=22 without a patch linking both courses.
const agentSlug = 'agent-intro';
const agentLesson = lessons.find((e) => e.slug === agentSlug);
assert.ok(agentLesson);
const explicitAgentSlugs = parseEpisodeSlugs('[第22期](https://linhongcun.github.io/video-studio/episodes/agent-intro/)\n[同一页](https://linhongcun.github.io/video-studio/episodes/agent-intro/#ask)');
assert.deepEqual(Array.from(explicitAgentSlugs), [agentSlug]);
assert.deepEqual(Array.from(parseEpisodeSlugs('https://github.com/linhongcun/video-studio/tree/main/episodes/agent-intro/ https://example.com/episodes/agent-intro/ https://linhongcun.github.io/video-studio/episodes/agent-intro/video.mp4')), []);
for (const kind of ['修正', '更新']) {
  assert.deepEqual(slugs(episodesForRelease({tag: 'v0.50.5', kind, eps: [22], episodeSlugs: explicitAgentSlugs}, lessons)), [agentSlug]);
}
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.49.1', kind: '修正', eps: [22], episodeSlugs: explicitAgentSlugs}, lessons)), [], 'An explicit link must retain the first-release gate');
assert.deepEqual(slugs(episodesForRelease({tag: agentLesson.firstRelease, kind: '新增', eps: [22]}, lessons)), [agentSlug]);
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.50.3', kind: '修正', eps: [5], episodeSlugs: parseEpisodeSlugs('https://linhongcun.github.io/video-studio/episodes/cdn/')}, lessons)), ['cdn']);
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.50.4', kind: '修正', eps: [22], episodeSlugs: parseEpisodeSlugs('https://linhongcun.github.io/video-studio/episodes/container-most-water/')}, lessons)), [algorithmSlug]);
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.50.5', kind: '修正', eps: [12]}, lessons)), ['idempotency'], 'Old EP-only releases must retain their fallback');
console.log('Learning paths passed: historical EP.21 sequence and releases preserved; LC.11 has an independent series, display number and release identity.');
console.log('Explicit canonical release links passed: same-EP patches select only the linked course; debut gates and legacy EP fallback preserved.');

if (process.argv.includes('--built')) {
  const dist = path.join(site, 'dist');
  const text = (rel) => fs.readFileSync(path.join(dist, rel), 'utf8');
  const route = `episodes/${algorithmSlug}/`;
  const publishedIndex = text('index.html');
  if (algorithm.draft) {
    assert.equal(fs.existsSync(path.join(dist, route, 'index.html')), false, 'Draft algorithm must not have a public page');
    assert.equal(publishedIndex.includes(`/episodes/${algorithmSlug}/`), false, 'Draft algorithm leaked into home');
    assert.equal(text('rss.xml').includes(`/episodes/${algorithmSlug}/`), false, 'Draft algorithm leaked into RSS');
  } else {
    const page = text(`${route}index.html`);
    assert.ok(page.includes(`<title>${algorithm.title} · Video Studio</title>`), 'Algorithm page title is stale');
    assert.ok(page.includes('LC.11') && !page.includes('EP.22'), 'The algorithm page must display the problem number');
    assert.ok(page.includes('/series/leetcode/'), 'Algorithm page must link its own series');
    assert.equal(page.includes('搜索「IT小村」'), false, 'A site-only lesson must not imply that it was published on other platforms');
    assert.equal(page.includes('aria-label="在其他平台观看"'), false, 'No platform navigation is shown without real episode links');
    assert.ok(text('series/leetcode/index.html').includes(`/episodes/${algorithmSlug}/`));
    assert.ok(publishedIndex.includes('data-series="leetcode"') && publishedIndex.includes(`/episodes/${algorithmSlug}/`));
    assert.ok(text('rss.xml').includes('LC.11') && text('rss.xml').includes(`/episodes/${algorithmSlug}/`));
    assert.deepEqual(Array.from(algorithm.chapters, (c) => c.id), ['area', 'proof', 'scan', 'code']);
    for (const chapter of algorithm.chapters) {
      assert.ok(page.includes(`id="${chapter.id}"`), `Missing article anchor ${chapter.id}`);
      assert.ok(page.includes(`data-id="${chapter.id}" data-start="${chapter.start}"`), `Missing timed chapter ${chapter.id}`);
    }
    const storyboard = readJson(path.join(site, '../episodes', algorithmSlug, 'storyboard.json'));
    const narration = storyboard.scenes.flatMap((s) => s.shots.flatMap((sh) => sh.subtitles.map((sub) => sub.text)));
    const captions = text(`${route}captions.vtt`).trim().split(/\r?\n\s*\r?\n/).slice(1)
      .map((cue) => cue.split(/\r?\n/).slice(1).join('\n'));
    assert.equal(narration.length, 44, 'The frozen lesson must contain all 44 narration sentences');
    assert.deepEqual(captions, narration, 'Published subtitles must match every frozen narration sentence in order');
    for (const file of [algorithm.video, algorithm.poster]) {
      const source = fs.readFileSync(path.join(site, '../episodes', algorithmSlug, file));
      const built = fs.readFileSync(path.join(dist, route, file));
      assert.equal(createHash('sha256').update(built).digest('hex'), createHash('sha256').update(source).digest('hex'),
        `Built ${file} differs from the approved source`);
    }
    console.log('Built LC.11 passed: title, independent series, four chapter anchors, 44 exact subtitles, copied video and poster.');
  }
}
