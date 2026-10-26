import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createProcessor} from '@mdx-js/mdx';
import {REPO_ROOT, readArticleSources, validateArticleSource, articleImageFile} from './article-sources.mjs';

function require(condition, message) { if (!condition) throw new Error(message); }
const nonempty = (value) => typeof value === 'string' && value.trim().length > 0;
const processor = createProcessor({format: 'mdx'});

export function parseArticle(content) {
  // Apply the same authoring syntax preparation as astro.config.mjs. Fenced
  // examples remain code AST nodes, so a sample component never passes a gate.
  const body = content.replace(/^---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)/, '')
    .replace(/^(#{1,6} .*?)\s*\{#([\w-]+)\}[ \t]*$/gm, '$1 \\{#$2\\}');
  return processor.parse(body);
}

function attribute(node, name) {
  const attr = node.attributes?.find((item) => item.type === 'mdxJsxAttribute' && item.name === name);
  if (typeof attr?.value === 'string') return attr.value;
  const body = attr?.value?.data?.estree?.body;
  if (body?.length === 1 && body[0].type === 'ExpressionStatement' && body[0].expression.type === 'Literal') return body[0].expression.value;
  return undefined;
}
function staticallyHidden(node) {
  const hidden = node.attributes?.find((item) => item.type === 'mdxJsxAttribute' && item.name === 'hidden');
  if (hidden && (hidden.value === null || typeof hidden.value === 'string' || attribute(node, 'hidden') === true)) return true;
  if (attribute(node, 'aria-hidden') === 'true' || attribute(node, 'aria-hidden') === true) return true;
  const style = node.attributes?.find((item) => item.type === 'mdxJsxAttribute' && item.name === 'style')?.value;
  if (typeof style === 'string') return /(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden)\s*(?:!important\s*)?(?:;|$)/i.test(style);
  const expression = style?.data?.estree?.body?.[0]?.expression;
  if (expression?.type !== 'ObjectExpression') return false;
  return expression.properties.some((property) => {
    if (property.type !== 'Property' || property.value?.type !== 'Literal') return false;
    const key = property.key.type === 'Identifier' ? property.key.name : property.key.value;
    const value = String(property.value.value).trim().toLowerCase();
    return (key === 'display' && value === 'none') || (key === 'visibility' && value === 'hidden');
  });
}
const text = (node) => node.value ?? (node.children ?? []).map(text).join('');
const jsx = (node, name) => /mdxJsx(?:Flow|Text)Element/.test(node.type) && node.name === name;
function descendants(node, predicate) {
  const matches = [];
  const walk = (n) => { if (staticallyHidden(n)) return; if (predicate(n)) matches.push(n); for (const child of n.children ?? []) walk(child); };
  walk(node);
  return matches;
}

function durationOf(root, meta) {
  const file = path.join(root, 'storyboard.json');
  const sb = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : {};
  const fps = sb.meta?.fps ?? 30;
  const frames = meta.finalVideoFrames ?? sb.meta?.finalVideoFrames
    ?? (sb.scenes ?? []).flatMap((scene) => scene.shots ?? []).reduce((sum, shot) => sum + (shot.durationInFrames ?? 0), 0);
  return frames / fps;
}

export function checkArticle(slug, {repoRoot = REPO_ROOT} = {}) {
  const dir = path.join(repoRoot, 'episodes', slug);
  const meta = JSON.parse(fs.readFileSync(path.join(dir, 'meta.json'), 'utf8'));
  const tree = parseArticle(fs.readFileSync(path.join(dir, 'article.mdx'), 'utf8'));
  const sources = readArticleSources(slug, {repoRoot});
  const duration = durationOf(dir, meta);
  let quotes = 0;
  let figures = 0;
  const used = new Set();
  const walk = (node) => {
    if (staticallyHidden(node) || node.type === 'code' || node.type === 'inlineCode' || jsx(node, 'pre') || jsx(node, 'code') || jsx(node, 'CodeBlock')) return;
    if (jsx(node, 'Figure') || jsx(node, 'SourceQuote')) {
      require(!(node.children ?? []).some((child) => child.type !== 'text' || nonempty(child.value)), `${node.name} does not render child content; use a separate article block`);
    }
    if (jsx(node, 'SourceQuote')) {
      const id = attribute(node, 'sourceId');
      require(nonempty(id), 'SourceQuote needs a literal sourceId');
      require(nonempty(attribute(node, 'supports')), `${id}: SourceQuote needs a concrete supports explanation`);
      require(!used.has(id), `${id}: duplicate SourceQuote; place each excerpt once near its claim`);
      validateArticleSource(sources.get(id), {repoRoot});
      used.add(id);
      quotes++;
    }
    if (jsx(node, 'Figure')) {
      require(nonempty(attribute(node, 'alt')) && nonempty(attribute(node, 'caption')), 'Figure needs descriptive alt and caption');
      articleImageFile(slug, attribute(node, 'src'), {repoRoot});
      const seek = attribute(node, 'seekTo');
      const kind = attribute(node, 'kind') ?? 'video';
      require(kind === 'video' || kind === 'diagram', 'Figure kind must be video or diagram');
      if (kind === 'video') require(typeof seek === 'number' && Number.isFinite(seek) && seek >= 0 && seek < duration, 'Figure needs a real video timestamp inside the episode');
      else require(seek === undefined && /示意图|自制|数据图/.test(attribute(node, 'caption')), 'a diagram needs a caption identifying it as a diagram, without a video timestamp');
      figures++;
    } else if (jsx(node, 'figure')) {
      const caption = descendants(node, (n) => jsx(n, 'figcaption')).some((n) => nonempty(text(n)));
      const svgs = descendants(node, (n) => jsx(n, 'svg'));
      const imgs = descendants(node, (n) => jsx(n, 'img'));
      if (svgs.length || imgs.length) {
        require(caption, 'native figure needs a figcaption');
        for (const svg of svgs) {
          const title = descendants(svg, (n) => jsx(n, 'title')).some((n) => nonempty(text(n)));
          require(title || nonempty(attribute(svg, 'aria-label')) || nonempty(attribute(node, 'aria-label')), 'SVG figure needs an accessible description');
        }
        for (const img of imgs) {
          require(nonempty(attribute(img, 'alt')), 'native image needs descriptive alt');
          articleImageFile(slug, attribute(img, 'src'), {repoRoot});
        }
        figures++;
      }
    } else if (node.type === 'image') {
      require(nonempty(node.alt) && nonempty(node.title), 'Markdown image needs alt and a caption in its title');
      articleImageFile(slug, node.url, {repoRoot});
      figures++;
    }
    for (const child of node.children ?? []) walk(child);
  };
  walk(tree);
  require(quotes > 0, 'missing a verified SourceQuote in the article body');
  require(figures > 0, 'missing an informative captioned figure in the article body');
  return {slug, quotes, figures};
}

export function checkArticles({repoRoot = REPO_ROOT} = {}) {
  const results = [];
  const failures = [];
  for (const slug of fs.readdirSync(path.join(repoRoot, 'episodes')).sort()) {
    const metaFile = path.join(repoRoot, 'episodes', slug, 'meta.json');
    if (!fs.existsSync(metaFile)) continue;
    const meta = JSON.parse(fs.readFileSync(metaFile, 'utf8'));
    if (meta.draft || meta.archived) continue;
    try { results.push(checkArticle(slug, {repoRoot})); }
    catch (error) { failures.push(`${slug}: ${error.message}`); }
  }
  return {results, failures};
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const {results, failures} = checkArticles();
  for (const failure of failures) console.error(`[articles] ${failure}`);
  if (failures.length) process.exitCode = 1;
  else console.log(`Article checks passed: ${results.length} published articles, ${results.reduce((n, r) => n + r.quotes, 0)} verified excerpts, ${results.reduce((n, r) => n + r.figures, 0)} captioned figures. Editorial and visual review remain required.`);
}
