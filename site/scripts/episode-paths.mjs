import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

export function findRepoRoot() {
  for (const start of [process.cwd(), path.dirname(fileURLToPath(import.meta.url))]) {
    for (let directory = path.resolve(start); ; directory = path.dirname(directory)) {
      if (fs.existsSync(path.join(directory, 'site/package.json'))
        && fs.existsSync(path.join(directory, 'episodes'))) return fs.realpathSync(directory);
      if (path.dirname(directory) === directory) break;
    }
  }
  throw new Error('Cannot locate video-studio repository inputs');
}

export const REPO_ROOT = findRepoRoot();
const key = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const inside = (parent, file) => file.startsWith(parent + path.sep);

/** Publication metadata is the index; series folders and slugs are physical directories. */
export function listEpisodes({repoRoot = REPO_ROOT} = {}) {
  const root = path.join(repoRoot, 'episodes');
  const records = [];
  const slugs = new Set();
  for (const group of fs.readdirSync(root, {withFileTypes: true}).sort((a, b) => a.name.localeCompare(b.name))) {
    if (group.name.startsWith('_')) continue;
    if (group.isSymbolicLink()) throw new Error(`Series must be a physical directory: ${group.name}`);
    if (!group.isDirectory()) continue;
    if (!key.test(group.name)) throw new Error(`Invalid episode series directory: ${group.name}`);
    for (const entry of fs.readdirSync(path.join(root, group.name), {withFileTypes: true}).sort((a, b) => a.name.localeCompare(b.name))) {
      if (!entry.isDirectory()) continue;
      if (!key.test(entry.name)) throw new Error(`Invalid episode slug: ${entry.name}`);
      const parent = path.join(root, group.name, entry.name);
      const directory = path.join(parent, 'publication');
      const metadata = path.join(directory, 'meta.json');
      if (!fs.existsSync(metadata)) continue;
      if (fs.lstatSync(directory).isSymbolicLink()) throw new Error(`Publication must be a physical directory: ${directory}`);
      const meta = JSON.parse(fs.readFileSync(metadata, 'utf8'));
      if (meta.series !== undefined && meta.series !== group.name) throw new Error(`${entry.name}: metadata series differs from physical directory`);
      if (slugs.has(entry.name)) throw new Error(`Duplicate episode slug: ${entry.name}`);
      slugs.add(entry.name);
      records.push({slug: entry.name, series: group.name, directory,
        productionDirectory: path.join(parent, 'production'), meta});
    }
  }
  return records;
}

export function episodeDirectory(slug, {repoRoot = REPO_ROOT, kind = 'publication'} = {}) {
  if (typeof slug !== 'string' || !key.test(slug)) throw new Error(`Invalid episode slug: ${slug}`);
  if (!['production', 'publication'].includes(kind)) throw new Error(`Invalid episode directory kind: ${kind}`);
  const record = listEpisodes({repoRoot}).find((episode) => episode.slug === slug);
  if (!record) throw new Error(`Unknown episode slug: ${slug}`);
  return kind === 'production' ? record.productionDirectory : record.directory;
}

/** Resolve historical evidence identities without changing frozen reference JSON or receipts. */
export function resolveRepoPath(relative, {repoRoot = REPO_ROOT} = {}) {
  if (typeof relative !== 'string' || !relative || path.isAbsolute(relative)
    || relative.split(/[\\/]/).some((part) => part === '..')) throw new Error('Expected a path inside its repository directory');
  const parent = fs.realpathSync(repoRoot);
  const parts = relative.split('/');
  let mapped = relative;
  if (parts[0] === 'episodes-codex') {
    if (['_shared', '_template'].includes(parts[1])) mapped = ['episodes', ...parts.slice(1)].join('/');
    else if (parts.length === 2 && parts[1].endsWith('.py')) mapped = `scripts/${parts[1]}`;
    else mapped = path.join(episodeDirectory(parts[1], {repoRoot, kind: 'production'}), ...parts.slice(2));
  } else if (parts[0] === 'episodes' && !parts[1]?.startsWith('_')) {
    const episodes = listEpisodes({repoRoot});
    const current = episodes.some((episode) => episode.series === parts[1] && episode.slug === parts[2]
      && ['production', 'publication'].includes(parts[3]));
    if (!current && episodes.some((episode) => episode.slug === parts[1]))
      mapped = path.join(episodeDirectory(parts[1], {repoRoot}), ...parts.slice(2));
  }
  const candidate = path.resolve(parent, mapped);
  if (!inside(parent, candidate)) throw new Error('Path must stay inside its repository directory');
  const real = fs.realpathSync(candidate);
  if (!inside(parent, real)) throw new Error('Path must stay inside its repository directory');
  return real;
}

export function episodeSlug(directory) {
  for (let current = path.resolve(directory); path.dirname(current) !== current; current = path.dirname(current)) {
    if (['production', 'publication'].includes(path.basename(current))) return path.basename(path.dirname(current));
  }
  return path.basename(directory);
}
