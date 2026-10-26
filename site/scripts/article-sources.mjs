import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

function findRepoRoot() {
  // Astro moves server modules beneath dist/ while prerendering. Locate the
  // repository by its real inputs instead of assuming a source-module depth.
  for (const start of [process.cwd(), path.dirname(fileURLToPath(import.meta.url))]) {
    for (let dir = path.resolve(start); ; dir = path.dirname(dir)) {
      if (fs.existsSync(path.join(dir, 'site/package.json')) && fs.existsSync(path.join(dir, 'episodes'))) return fs.realpathSync(dir);
      if (path.dirname(dir) === dir) break;
    }
  }
  throw new Error('Cannot locate video-studio repository inputs');
}
export const REPO_ROOT = findRepoRoot();
const nonempty = (value) => typeof value === 'string' && value.trim().length > 0;
function require(condition, message) { if (!condition) throw new Error(message); }
const read = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));

export function localFile(root, relative, label = 'file') {
  require(nonempty(relative) && !path.isAbsolute(relative), `${label}: expected a relative path`);
  const parent = fs.realpathSync(root);
  const candidate = path.resolve(parent, relative);
  require(candidate.startsWith(parent + path.sep), `${label}: path leaves its directory`);
  const real = fs.realpathSync(candidate);
  require(real.startsWith(parent + path.sep) && fs.statSync(real).isFile(), `${label}: expected a file inside its directory`);
  return real;
}

export function readArticleSources(slug, {repoRoot = REPO_ROOT} = {}) {
  require(typeof slug === 'string' && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug), 'invalid episode slug');
  const root = path.join(repoRoot, 'episodes', slug);
  const sources = new Map();
  for (const name of ['references.json', 'article-sources.json']) {
    if (!fs.existsSync(path.join(root, name))) continue;
    const record = read(localFile(root, name, name));
    require(record.schemaVersion === 1 && record.episode === slug && Array.isArray(record.sources), `${name}: schema or episode differs`);
    for (const source of record.sources) {
      require(source && nonempty(source.id) && !sources.has(source.id), `${name}: missing or duplicate source id ${source?.id}`);
      sources.set(source.id, source);
    }
  }
  return sources;
}

function validDate(value) {
  return typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)
    && !Number.isNaN(Date.parse(value)) && new Date(value).toISOString().slice(0, 10) === value;
}
function https(value) {
  try { return nonempty(value) && new URL(value).protocol === 'https:'; } catch { return false; }
}

function evidenceIncludes(file, quotation) {
  const raw = fs.readFileSync(file, 'utf8');
  if (path.extname(file).toLowerCase() !== '.json') return raw.includes(quotation);
  const strings = [];
  const commentaryKeys = new Set(['supports', 'support', 'claims', 'claim', 'summary', 'note', 'scope', 'limitations', 'explanation', 'translation']);
  const visit = (value) => {
    if (typeof value === 'string') strings.push(value);
    else if (Array.isArray(value)) value.forEach(visit);
    else if (value && typeof value === 'object') {
      for (const [key, child] of Object.entries(value)) if (!commentaryKeys.has(key)) visit(child);
    }
  };
  visit(JSON.parse(raw));
  return strings.some((value) => value.includes(quotation));
}

// This verifies the saved excerpt and its identity. It cannot establish that
// the source is true or replace an editor reading the surrounding passage.
export function validateArticleSource(source, {repoRoot = REPO_ROOT} = {}) {
  require(source && nonempty(source.id), 'missing source id');
  const label = `source ${source.id}`;
  for (const key of ['title', 'organization', 'version']) require(nonempty(source[key]), `${label}: missing ${key}`);
  if (Object.hasOwn(source, 'author')) require(nonempty(source.author), `${label}: empty author`);
  require(https(source.url), `${label}: source URL must use HTTPS`);
  require(Array.isArray(source.supports) && source.supports.length > 0 && source.supports.every(nonempty), `${label}: missing supported claims`);
  require(source.verification?.status === 'verified' && validDate(source.verification.checkedAt), `${label}: missing verified access date`);
  localFile(repoRoot, source.verification.evidence, `${label} verification`);
  if (source.verification.sourceUrl !== undefined) require(https(source.verification.sourceUrl), `${label}: fixed source URL must use HTTPS`);
  require(nonempty(source.quotation?.text) && nonempty(source.quotation?.locator), `${label}: missing exact quotation or locator`);
  const file = localFile(repoRoot, source.quotation.evidence, `${label} quotation`);
  require(!['article-sources.json', 'references.json', 'article.mdx'].includes(path.basename(file)), `${label}: citation metadata or the article cannot serve as its own original-text evidence`);
  require(evidenceIncludes(file, source.quotation.text), `${label}: exact quotation missing from saved evidence`);
  return source;
}

export function articleImageFile(slug, src, {repoRoot = REPO_ROOT} = {}) {
  const prefix = `/video-studio/episodes/${slug}/`;
  require(nonempty(src) && src.startsWith(`${prefix}article/`), 'article image must use this episode’s article/ directory');
  const relative = src.slice(prefix.length);
  require(!/[?#\\%]/.test(relative) && !relative.split('/').some((part) => part === '..' || part === '.'), 'unsafe article image path');
  require(/\.(?:avif|gif|jpe?g|png|svg|webp)$/i.test(relative), 'unsupported article image type');
  return localFile(path.join(repoRoot, 'episodes', slug), relative, 'article image');
}
