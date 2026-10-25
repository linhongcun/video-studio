'use strict';
// Only the two frozen articles below may receive these exact site-only edits.
const assert = require('node:assert/strict'), fs = require('node:fs'), path = require('node:path');
const crypto = require('node:crypto'), cp = require('node:child_process');
const root = path.resolve(__dirname, '../../..');
const hash = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');
const relative = (file) => path.relative(root, file);
const plans = {
  permutations: {
    ids: ['problem', 'derive', 'walk', 'code'],
    headings: ['先把题目说清楚', '为什么需要选择和撤销', '同一组数字怎样走出六种顺序', '为什么保存副本'],
    remove: '阶段1只完成代码、文稿和动画源码；配音、实际媒体与网站检查尚未执行。',
  },
  'trapping-rain-water': {
    ids: ['problem', 'derive', 'scan', 'code'],
    headings: ['给了什么，要返回什么', '先从一列推导水位', '定义与计算', '完整Python程序'],
    oldChapters: 'chapters:\n  - title: "先看哪里能留水"\n    start: 0.0\n  - title: "为什么要记住左右高点"\n    start: 24.0\n  - title: "两遍准备，再逐列加水"\n    start: 61.0\n  - title: "把水深写成程序"\n    start: 146.8\n',
    remove: '当前章节起点为文稿开发估计，正式站点由真实分镜刷新；',
  },
};
function transform(slug, source, sb) {
  const plan = plans[slug]; assert.ok(plan, 'No approved derivation for ' + slug);
  const chapters = sb.scenes.reduce((all, scene) => {
    if (all.at(-1)?.id !== scene.chapterId) all.push({id: scene.chapterId, title: scene.title, frame: scene.from});
    return all;
  }, []);
  assert.deepEqual(chapters.map((chapter) => chapter.id), plan.ids);
  const edits = []; let text = source;
  function replace(before, after, reason) {
    assert.equal(text.split(before).length - 1, 1, `${slug}: expected exactly one ${reason}`);
    text = text.replace(before, after); edits.push({reason, before, after});
  }
  if (plan.oldChapters) {
    const next = 'chapters:\n' + chapters.map((chapter) => `  - id: ${chapter.id}\n    title: ${JSON.stringify(chapter.title)}\n`).join('');
    replace(plan.oldChapters, next, 'Give existing chapters real storyboard IDs; omit obsolete estimated starts');
  } else {
    assert.ok(source.includes('chapters:\n' + chapters.map((chapter) => `  - id: ${chapter.id}\n    title: ${chapter.title}\n`).join('')));
  }
  plan.headings.forEach((heading, i) => replace(`\n## ${heading}\n`, `\n## ${heading} {#${plan.ids[i]}}\n`, `Connect ${plan.ids[i]} to the existing section`));
  if (slug === 'permutations') {
    replace('<!-- SOLUTION:START solution.py -->', '{/* SOLUTION:START solution.py */}', 'Convert the invisible generated-code start marker to valid MDX comment syntax');
    replace('<!-- SOLUTION:END -->', '{/* SOLUTION:END */}', 'Convert the invisible generated-code end marker to valid MDX comment syntax');
  }
  replace(plan.remove, '', 'Remove an obsolete production-stage statement');
  assert.deepEqual(text.match(/^```[\s\S]*?^```/gm), source.match(/^```[\s\S]*?^```/gm), 'Code fences must be byte-identical');
  return {text, chapters, edits};
}
function paths(slug) {
  return {
    source: path.join(root, 'episodes-codex', slug, 'article.mdx'),
    snapshot: path.join(__dirname, slug + '.source.mdx'),
    derived: path.join(__dirname, slug + '.mdx'),
    diff: path.join(__dirname, slug + '.diff'),
    proof: path.join(__dirname, slug + '.proof.json'),
  };
}
function difference(files, derived) {
  const result = cp.spawnSync('diff', ['-u', '--label', relative(files.source), '--label', relative(files.derived), files.snapshot, '-'], {input: derived, encoding: 'utf8'});
  assert.equal(result.status, 1, result.stderr || 'An approved derivation must have a precise diff');
  return result.stdout;
}
function proofFor(slug, files, source, derived, diff, result) {
  const freezePath = path.join(root, 'episodes-codex', slug, 'source-sha256.json');
  const frozenArticleSHA256 = JSON.parse(fs.readFileSync(freezePath, 'utf8'))['article.mdx'];
  assert.equal(hash(source), frozenArticleSHA256, 'Production article must retain the frozen SHA');
  return {
    purpose: 'Reproducible site-only chapter/anchor derivation; not a movie or website QA result',
    slug,
    sourcePath: relative(files.source), sourceSHA256: hash(source),
    sourceFreezePath: relative(freezePath), frozenArticleSHA256,
    sourceSnapshotPath: relative(files.snapshot), derivedPath: relative(files.derived), derivedSHA256: hash(derived),
    diffPath: relative(files.diff), diffSHA256: hash(diff),
    transformPath: relative(__filename),
    chapters: result.chapters,
    exactEdits: result.edits,
    scope: ['Only the listed chapter frontmatter, four existing H2 anchors, invisible MDX comment syntax and obsolete production-stage text change.', 'All explanation, examples, Python code, remaining headings and production source bytes are preserved.', 'Times come from actual storyboard frames; the derived frontmatter contains no estimated start values.'],
  };
}
function prepare(slug) {
  const files = paths(slug), source = fs.readFileSync(files.source);
  const sb = JSON.parse(fs.readFileSync(path.join(root, 'episodes-codex', slug, 'storyboard.json'), 'utf8'));
  const result = transform(slug, source.toString(), sb), derived = Buffer.from(result.text);
  fs.writeFileSync(files.snapshot, source); fs.writeFileSync(files.derived, derived);
  const diff = difference(files, derived); fs.writeFileSync(files.diff, diff);
  const proof = proofFor(slug, files, source, derived, diff, result);
  fs.writeFileSync(files.proof, JSON.stringify(proof, null, 2) + '\n');
  return proof;
}
function verifyArticle(slug, canonicalFile) {
  if (!plans[slug]) {
    assert.equal(slug, 'daily-temperatures');
    const source = fs.readFileSync(path.join(root, 'episodes-codex', slug, 'article.mdx'));
    if (canonicalFile) assert.deepEqual(fs.readFileSync(canonicalFile), source);
    return {slug, mode: 'byte-identical', sourceSHA256: hash(source), derivedSHA256: hash(source)};
  }
  const files = paths(slug), source = fs.readFileSync(files.source);
  assert.deepEqual(fs.readFileSync(files.snapshot), source, 'The frozen production article changed');
  const sb = JSON.parse(fs.readFileSync(path.join(root, 'episodes-codex', slug, 'storyboard.json'), 'utf8'));
  const result = transform(slug, source.toString(), sb), derived = Buffer.from(result.text), diff = difference(files, derived);
  assert.deepEqual(fs.readFileSync(files.derived), derived);
  assert.equal(fs.readFileSync(files.diff, 'utf8'), diff);
  const proof = proofFor(slug, files, source, derived, diff, result);
  assert.deepEqual(JSON.parse(fs.readFileSync(files.proof, 'utf8')), proof);
  if (canonicalFile) assert.deepEqual(fs.readFileSync(canonicalFile), derived, 'Canonical article must equal the exact approved transform');
  return {slug, mode: 'explicit-site-derivative', ...proof, artifacts: [__filename, files.snapshot, files.derived, files.diff, files.proof].map(relative)};
}
module.exports = {transform, verifyArticle};
if (require.main === module) {
  const [flag, slug] = process.argv.slice(2);
  if (flag === '--write' && plans[slug]) {prepare(slug); console.log(JSON.stringify(verifyArticle(slug), null, 2));}
  else if (flag === '--check' && (plans[slug] || slug === 'daily-temperatures')) console.log(JSON.stringify(verifyArticle(slug, process.argv[4]), null, 2));
  else throw new Error('Use --write <approved-slug> or --check <slug> [canonical-file]. No canonical files are written.');
}
