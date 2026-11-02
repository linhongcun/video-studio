import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';

// QA only: use the current site parser's frontmatter and {#id} normalization.
const D = path.resolve(process.argv[2]);
let root = D;
while (!fs.existsSync(path.join(root, 'AGENTS.md'))) {
  const parent = path.dirname(root);
  if (parent === root) throw new Error('repository root not found');
  root = parent;
}
const parserFile = path.join(root, 'site/scripts/check-articles.mjs');
const sourceFile = path.join(root, 'site/scripts/article-sources.mjs');
const {parseArticle} = await import(pathToFileURL(parserFile).href);
const {validateArticleSource} = await import(pathToFileURL(sourceFile).href);
const sha = (f) => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const json = (f) => JSON.parse(fs.readFileSync(path.join(D, f), 'utf8'));
const assert = (ok, why) => { if (!ok) throw new Error(why); };
const before = json('qa-editorial/actual-figure-timing/initial-identity.json');
const plan = json('article-figure-plan.json');
const board = json('storyboard.json');
const duration = board.meta.durationInFrames / board.meta.fps;
const tree = parseArticle(fs.readFileSync(path.join(D, 'article.mdx'), 'utf8'));
const nodes = [];
const walk = (node) => {
  if (node.type === 'code' || node.type === 'inlineCode') return;
  if (/mdxJsx(?:Flow|Text)Element/.test(node.type)) nodes.push(node);
  for (const child of node.children ?? []) walk(child);
};
walk(tree);
const attribute = (node, name) => {
  const a = node.attributes?.find((x) => x.type === 'mdxJsxAttribute' && x.name === name);
  if (typeof a?.value === 'string') return a.value;
  const body = a?.value?.data?.estree?.body;
  return body?.length === 1 && body[0].type === 'ExpressionStatement'
    && body[0].expression.type === 'Literal' ? body[0].expression.value : undefined;
};
const sourceMap = new Map();
for (const f of ['references.json', 'article-sources.json']) {
  const data = json(f);
  assert(data.episode === 'kafka-consumer-idempotency', f + ' episode');
  for (const s of data.sources) sourceMap.set(s.id, s);
}
const quotes = nodes.filter((x) => x.name === 'SourceQuote');
const used = new Set();
for (const q of quotes) {
  const id = attribute(q, 'sourceId');
  assert(!used.has(id), 'duplicate source ID');
  assert(typeof attribute(q, 'supports') === 'string', 'missing supports');
  validateArticleSource(sourceMap.get(id), {repoRoot: root});
  used.add(id);
}
const figures = nodes.filter((x) => x.name === 'Figure');
assert(figures.length === 4 && plan.figures.length === 4, 'four real Figure nodes required');
const figureChecks = figures.map((node, index) => {
  const p = plan.figures[index];
  const value = Object.fromEntries(['src', 'alt', 'caption', 'seekTo', 'chapter'].map((k) => [k, attribute(node, k)]));
  assert(Number.isSafeInteger(p.frame), 'integer planned frame');
  assert(p.seconds === p.frame / 30, 'exact frame/30 plan seconds');
  assert(Math.abs(value.seekTo - p.seconds) < 0.000000001, 'Figure timestamp differs from frame');
  assert(value.seekTo >= 0 && value.seekTo < duration, 'timestamp outside actual body');
  assert(value.src === '/video-studio/episodes/kafka-consumer-idempotency/' + p.file, 'Figure URL');
  assert(value.alt === p.alt && value.caption === p.caption && value.chapter === p.chapter, 'Figure descriptions');
  assert(p.file.startsWith('article/consumer-replay-'), 'new image names required');
  return {frame: p.frame, ...value};
});
const protectedChecks = Object.entries(before.protected).map(([file, expected]) => {
  const actual = sha(path.join(D, file));
  assert(actual === expected, 'protected input changed: ' + file);
  return {file, sha256: actual, unchanged: true};
});
const report = {
  kind: 'author-bounded-article-Figure-structure-check-actual-board',
  checkedAtUTC: new Date().toISOString(), pass: true,
  parser: {file: path.relative(root, parserFile), sha256: sha(parserFile), method: 'parseArticle exported normalization; not raw MDX parsing'},
  articleSHA256: sha(path.join(D, 'article.mdx')),
  figurePlanSHA256: sha(path.join(D, 'article-figure-plan.json')),
  figures: figureChecks, exactSourceQuoteCount: quotes.length,
  validatedSourceIds: [...used], protectedChecks,
  scope: 'AST structure, exact saved source quotes, real body timestamps and new URLs; JPEG files intentionally not required yet. No image or independent Main visual approval is claimed.',
};
fs.writeFileSync(path.join(D, 'qa-editorial/actual-figure-timing/structure-check.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({pass: report.pass, figures: figures.length, quotes: quotes.length, articleSHA256: report.articleSHA256}));
