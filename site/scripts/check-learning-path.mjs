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
function learningRuntime(episodes) {
  const source = stripImports(fs.readFileSync(path.join(site, 'src/lib/learning.ts'), 'utf8'));
  const {code} = transformSync(source, {loader: 'ts'});
  return vm.compileFunction(`${code}\nreturn {getLearningTracks, getTrackForSeries};`, ['getSeries', 'BASE'])(episodes.getSeries, '/video-studio/');
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
const binaryAlgorithmSlug = 'binary-search';
const binaryAlgorithm = lessons.find((e) => e.slug === binaryAlgorithmSlug);
assert.ok(binaryAlgorithm, 'The binary-search lesson must be available in preview');
assert.equal(binaryAlgorithm.ep, 24);
assert.equal(binaryAlgorithm.problemNumber, 704);
assert.equal(preview.epLabel(binaryAlgorithm), 'LC.704');
const batchAlgorithmSlugs = ['two-sum', 'reverse-linked-list', 'climbing-stairs'];
const algorithmSlugs = [algorithmSlug, nextAlgorithmSlug, binaryAlgorithmSlug, ...batchAlgorithmSlugs];
const algorithmChain = algorithmSlugs.map((slug) => lessons.find((e) => e.slug === slug));
const batchAlgorithms = algorithmChain.slice(3);
const batchRelease = batchAlgorithms[0]?.firstRelease;
assert.ok(batchRelease, 'The algorithm batch needs a shared first release');
for (const [i, e] of algorithmChain.entries()) {
  assert.ok(e, `Missing algorithm metadata for ${algorithmSlugs[i]}`);
  assert.equal(e.series, 'leetcode');
  assert.equal(e.ep, 22 + i);
  assert.equal(e.problemNumber, [11, 3, 704, 1, 206, 70][i]);
  assert.equal(preview.epLabel(e), `LC.${e.problemNumber}`);
  const nav = preview.seriesNav(e);
  assert.equal(nav.prev?.slug, algorithmSlugs[i - 1], `${e.slug}: incorrect previous algorithm`);
  assert.equal(nav.next?.slug, algorithmSlugs[i + 1], `${e.slug}: incorrect next algorithm`);
  assert.equal(liveLessons.some((live) => live.slug === e.slug), !e.draft);
  if (i >= 3) {
    assert.equal(e.firstRelease, batchRelease, 'All three new algorithms debut together');
    if (complete) assert.equal(e.draft, false, `${e.slug} is not published yet`);
  }
}
assert.deepEqual(slugs(preview.getSeries().find((s) => s.id === 'leetcode').episodes), algorithmSlugs);
const liveAlgorithmSlugs = algorithmChain.filter((e) => !e.draft).map((e) => e.slug);
assert.deepEqual(slugs(published.getSeries().find((s) => s.id === 'leetcode').episodes), liveAlgorithmSlugs);
for (const [i, slug] of liveAlgorithmSlugs.entries()) {
  const nav = published.seriesNav(liveLessons.find((e) => e.slug === slug));
  assert.equal(nav.prev?.slug, liveAlgorithmSlugs[i - 1]);
  assert.equal(nav.next?.slug, liveAlgorithmSlugs[i + 1]);
}
// A debut tag can contain several lessons. Explicit links narrow patches or
// updates, while an "新增" entry keeps every lesson associated with that tag.
const batchEps = batchAlgorithms.map((e) => e.ep);
const assertBatchSelection = (release, expected) => assert.deepEqual(
  slugs(episodesForRelease(release, lessons)).sort(), [...expected].sort());
assertBatchSelection({tag: batchRelease, kind: '新增', eps: batchEps}, batchAlgorithmSlugs);
const singleBatchLink = parseEpisodeSlugs('https://linhongcun.github.io/video-studio/episodes/two-sum/');
assertBatchSelection({tag: batchRelease, kind: '新增', eps: batchEps, episodeSlugs: singleBatchLink}, batchAlgorithmSlugs);
const multipleBatchLinks = parseEpisodeSlugs('[链表](https://linhongcun.github.io/video-studio/episodes/reverse-linked-list/)\nhttps://linhongcun.github.io/video-studio/episodes/climbing-stairs/#code\nhttps://linhongcun.github.io/video-studio/episodes/reverse-linked-list/');
assert.deepEqual(Array.from(multipleBatchLinks), ['reverse-linked-list', 'climbing-stairs']);
for (const kind of ['修正', '更新']) {
  assertBatchSelection({tag: batchRelease, kind, eps: batchEps, episodeSlugs: singleBatchLink}, ['two-sum']);
  assertBatchSelection({tag: batchRelease, kind, eps: batchEps, episodeSlugs: multipleBatchLinks}, ['reverse-linked-list', 'climbing-stairs']);
  assertBatchSelection({tag: 'v0.56.3', kind, eps: batchEps, episodeSlugs: multipleBatchLinks}, []);
}
assert.deepEqual(slugs(episodesForRelease({tag: binaryAlgorithm.firstRelease, kind: '新增', eps: [24]}, lessons)), [binaryAlgorithmSlug]);
assert.deepEqual(slugs(episodesForRelease({tag: binaryAlgorithm.firstRelease, kind: '新增', eps: [24], episodeSlugs: parseEpisodeSlugs('https://linhongcun.github.io/video-studio/episodes/binary-search/')}, lessons)), [binaryAlgorithmSlug]);
assert.deepEqual(slugs(episodesForRelease({tag: nextAlgorithm.firstRelease, kind: '新增', eps: [23]}, lessons)), [nextAlgorithmSlug]);
assert.equal(preview.seriesNav(algorithm).prev, undefined, 'Algorithms have no distributed-systems prerequisite');
assert.notEqual(preview.seriesNav(lessons.find((e) => e.slug === mechanismSlugs.at(-1))).next?.series, 'leetcode', 'System-design learning path must not lead into an unrelated algorithm');
assert.equal(liveLessons.some((e) => e.slug === algorithmSlug), !algorithm.draft);
assert.deepEqual(slugs(episodesForRelease({tag: algorithm.firstRelease, kind: '新增', eps: [22]}, lessons)), [algorithmSlug]);
assert.ok(!slugs(episodesForRelease({tag: 'v0.45.0', kind: '修正', eps: [11]}, lessons)).includes(algorithmSlug),
  'An old EP.11 release must not link to LeetCode problem 11');

// Historical URL fixtures are parser inputs, not active lesson links. Keep the
// same-EP release contract covered independently of the retired Agent metadata.
const agentSlug = 'agent-intro';
const retiredAgentSlugs = [agentSlug, 'agent-tool-execution'];
const sameEpFixture = [
  {slug: agentSlug, ep: 22, firstRelease: 'v0.50.0'},
  {slug: 'fixture-independent-course', ep: 22, firstRelease: 'v0.49.0'},
];
for (const slug of retiredAgentSlugs) {
  for (const rows of [lessons, all, liveLessons]) {
    assert.equal(rows.some((e) => e.slug === slug), false, `${slug} must not remain in published, draft or archived metadata`);
  }
}
const explicitAgentSlugs = parseEpisodeSlugs('[第22期](https://linhongcun.github.io/video-studio/episodes/agent-intro/)\n[同一页](https://linhongcun.github.io/video-studio/episodes/agent-intro/#ask)');
assert.deepEqual(Array.from(explicitAgentSlugs), [agentSlug]);
assert.deepEqual(Array.from(parseEpisodeSlugs('https://github.com/linhongcun/video-studio/tree/main/episodes/agent-intro/ https://example.com/episodes/agent-intro/ https://linhongcun.github.io/video-studio/episodes/agent-intro/video.mp4')), []);
for (const kind of ['修正', '更新']) {
  const release = {tag: 'v0.50.5', kind, eps: [22], episodeSlugs: explicitAgentSlugs};
  assert.deepEqual(slugs(episodesForRelease(release, sameEpFixture)), [agentSlug], 'A canonical link must select only its same-EP fixture');
  assert.deepEqual(slugs(episodesForRelease(release, lessons)), [], 'A retired lesson link must not fall back to the same-EP algorithm');
}
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.49.1', kind: '修正', eps: [22], episodeSlugs: explicitAgentSlugs}, sameEpFixture)), [], 'An explicit link must retain the first-release gate');
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.50.0', kind: '新增', eps: [22]}, sameEpFixture)), [agentSlug]);
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.50.0', kind: '新增', eps: [22]}, lessons)), [], 'A retired debut must not acquire another course with the same EP');
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.59.0', kind: '更新', eps: [28], episodeSlugs: ['agent-tool-execution']}, lessons)), []);
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.50.3', kind: '修正', eps: [5], episodeSlugs: parseEpisodeSlugs('https://linhongcun.github.io/video-studio/episodes/cdn/')}, lessons)), ['cdn']);
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.50.4', kind: '修正', eps: [22], episodeSlugs: parseEpisodeSlugs('https://linhongcun.github.io/video-studio/episodes/container-most-water/')}, lessons)), [algorithmSlug]);
assert.deepEqual(slugs(episodesForRelease({tag: 'v0.50.5', kind: '修正', eps: [12]}, lessons)), ['idempotency'], 'Old EP-only releases must retain their fallback');
console.log('Learning paths passed: historical EP.21 sequence and releases preserved; six LeetCode lessons have an independent ordered series, display numbers and release identities.');
console.log('Explicit canonical release links passed: same-EP patches select only the linked course; debut gates and legacy EP fallback preserved.');
console.log('Shared debut release passed: the algorithm tag selects all three new lessons; patch/update URLs select one or several explicit lessons.');

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
    assert.ok(page.includes(`<title>${algorithm.title} · IT小村</title>`), 'Algorithm page title is stale');
    assert.ok(page.includes('LC.11') && !page.includes('EP.22'), 'The algorithm page must display the problem number');
    assert.ok(page.includes('/series/leetcode/'), 'Algorithm page must link its own series');
    assert.equal(page.includes('搜索「IT小村」'), false, 'A site-only lesson must not imply that it was published on other platforms');
    assert.equal(page.includes('aria-label="在其他平台观看"'), false, 'No platform navigation is shown without real episode links');
    assert.ok(text('series/leetcode/index.html').includes(`/episodes/${algorithmSlug}/`));
    const library = text('library/index.html');
    assert.ok(library.includes('data-series="leetcode"') && library.includes(`/episodes/${algorithmSlug}/`), 'The full library must include the independent algorithm series');
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

// Exercise the actual direction loader against published metadata. Every current
// lesson must have one clear home; previous/next may cross chapters within that
// direction, but must never imply that another direction is a prerequisite.
const learning = learningRuntime(published);
const tracks = learning.getLearningTracks();
const hasPublishedAgent = liveLessons.some((lesson) => lesson.series === 'agent');
const puzzle = liveLessons.find((lesson) => lesson.slug === 'horse-racing');
const directionForSeries = {
  request: 'systems', cache: 'systems', peak: 'systems', database: 'systems', distributed: 'systems',
  agent: 'agent', leetcode: 'algorithms', 'design-patterns': 'patterns', puzzles: 'puzzles',
};
const expectedDirections = new Set(liveLessons.map((lesson) => directionForSeries[lesson.series]));
assert.equal(expectedDirections.has(undefined), false, 'Every published series needs a known learning direction');
assert.deepEqual(Array.from(tracks, (track) => track.id).sort(), [...expectedDirections].sort(), 'Only nonempty published learning directions must be available');
assert.ok(learningRuntime(preview).getLearningTracks().every((track) => track.episodes.every((e) => !e.draft && !e.archived)),
  'Draft preview must not advertise unfinished lessons as published direction content');
assert.equal(learning.getTrackForSeries(), undefined);
assert.equal(learning.getTrackForSeries('unknown-series'), undefined);
const assigned = tracks.flatMap((track) => Array.from(track.episodes, (e) => e.slug));
assert.equal(new Set(assigned).size, assigned.length, 'A lesson must not appear in multiple directions');
assert.deepEqual([...assigned].sort(), slugs(liveLessons).sort(), 'Every current lesson must be reachable through a direction');
for (const track of tracks) {
  assert.ok(track.start && track.episodes.some((e) => e.slug === track.start.slug), `${track.title} needs a published starting lesson`);
  assert.ok(track.episodes.every((e) => !e.draft && !e.archived), `${track.title} must not advertise unavailable lessons`);
  for (const series of track.series) {
    assert.equal(learning.getTrackForSeries(series.id)?.id, track.id);
  }
  for (const lesson of track.episodes) {
    const nav = published.seriesNav(lesson);
    for (const neighbor of [nav?.prev, nav?.next].filter(Boolean)) {
      assert.equal(learning.getTrackForSeries(neighbor.series)?.id, track.id, `${lesson.slug} must not lead into unrelated ${neighbor.series}`);
    }
  }
}
assert.equal(tracks.find((t) => t.id === 'systems')?.start.slug, 'http-request', 'System fundamentals should start with the request');
const agentTrack = tracks.find((track) => track.id === 'agent');
if (hasPublishedAgent) {
  assert.ok(agentTrack, 'New published Agent lessons need their own learning direction');
  assert.equal(retiredAgentSlugs.includes(agentTrack.start.slug), false, 'A new Agent direction must not start with a retired lesson');
  assert.equal(learning.getTrackForSeries('agent')?.id, 'agent');
} else {
  assert.equal(agentTrack, undefined, 'An empty Agent direction must not advertise a removed starting lesson');
  assert.equal(learning.getTrackForSeries('agent'), undefined, 'The future Agent series must remain hidden until a new lesson is published');
}
assert.equal(tracks.find((t) => t.id === 'algorithms')?.start.slug, algorithmSlug);
assert.equal(tracks.find((t) => t.id === 'patterns')?.start.slug, 'strategy-pattern', 'Design patterns must start with the published strategy lesson');
assert.equal(learning.getTrackForSeries('design-patterns')?.id, 'patterns', 'Design patterns have their own learning direction');
if (puzzle) {
  assert.equal(puzzle.series, 'puzzles');
  assert.equal(learning.getTrackForSeries('puzzles')?.id, 'puzzles', 'Puzzles have their own learning direction');
  assert.equal(tracks.find((track) => track.id === 'puzzles')?.start.slug, 'horse-racing', 'Puzzles start with the published horse-racing lesson');
  assert.equal(published.seriesNav(puzzle).prev, undefined, 'The first puzzle must not inherit a technical prerequisite');
  const puzzleChain = liveLessons.filter((lesson) => lesson.series === 'puzzles').sort(published.compareLessons);
  for (const [index, lesson] of puzzleChain.entries()) {
    const nav = published.seriesNav(lesson);
    assert.equal(nav.prev?.slug, puzzleChain[index - 1]?.slug, 'Puzzles must follow their own published lesson order');
    assert.equal(nav.next?.slug, puzzleChain[index + 1]?.slug, 'The last puzzle must not lead into another learning direction');
  }
}
console.log(`${tracks.length} learning directions passed: every published lesson has one home; independent directions remain outside the systems path.`);

if (process.argv.includes('--built')) {
  const dist = path.join(site, 'dist');
  const readPage = (rel) => fs.readFileSync(path.join(dist, rel), 'utf8');
  const home = readPage('index.html');
  const learn = readPage('learn/index.html');
  const library = readPage('library/index.html');
  for (const slug of retiredAgentSlugs) {
    assert.equal(fs.existsSync(path.join(dist, `episodes/${slug}`)), false, `${slug} page, captions and copied media must be absent from the build`);
    for (const [name, page] of [['home', home], ['learn', learn], ['library', library], ['rss', readPage('rss.xml')]]) {
      assert.equal(page.includes(`/episodes/${slug}/`), false, `${slug} leaked into ${name}`);
    }
  }
  assert.equal(fs.existsSync(path.join(dist, 'series/agent/index.html')), hasPublishedAgent, 'The Agent catalog page must exist only when new Agent lessons are published');
  assert.equal(learn.includes('id="agent"'), hasPublishedAgent, 'The learning page must expose Agent only when its series has published lessons');
  for (const href of ['/video-studio/learn/', '/video-studio/library/']) {
    assert.ok(home.includes(`href="${href}"`), `Home must expose ${href}`);
  }
  for (const track of tracks) {
    const fragment = new URL(track.href, 'https://linhongcun.github.io').hash.slice(1);
    assert.ok(learn.includes(`id="${fragment}"`), `Missing destination for ${track.href}`);
    assert.ok(home.includes(`href="${track.href}"`), `Home must expose ${track.title}`);
    assert.ok(learn.includes(`href="/video-studio/episodes/${track.start.slug}/"`), `${track.title} must offer its published starting lesson`);
    for (const series of track.series) {
      assert.ok(learn.includes(`href="/video-studio/series/${series.id}/"`), `${track.title} must expose chapter ${series.title}`);
      assert.ok(fs.existsSync(path.join(dist, `series/${series.id}/index.html`)), `Missing preserved series URL: ${series.id}`);
    }
  }
  for (const lesson of liveLessons) {
    assert.ok(library.includes(`href="/video-studio/episodes/${lesson.slug}/"`), `Full library is missing ${lesson.slug}`);
  }
  assert.equal(library.includes(`/episodes/${archiveSlug}/`), false, 'Historical compilation must stay outside the current library');
  console.log('Built navigation passed: home, direction anchors, published starting lessons, all chapter URLs and the complete current library.');
}
