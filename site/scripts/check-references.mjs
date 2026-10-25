// New public videos must ship their actual reference appendix. Historical
// episodes remain eligible for the separately tracked, incremental migration.
// This checks recorded inputs/output identity, not whether a paper is true or
// whether someone has watched the final video.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const require = (condition, message) => { if (!condition) throw new Error(message); };
const read = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const nonempty = (value) => typeof value === 'string' && value.trim().length > 0;
const hashPattern = /^[a-f0-9]{64}$/;
const integer = (value) => Number.isSafeInteger(value) && value >= 0;

export function shaFile(file) {
  const hash = crypto.createHash('sha256');
  const handle = fs.openSync(file, 'r');
  const buffer = Buffer.alloc(256 * 1024);
  try {
    let size;
    while ((size = fs.readSync(handle, buffer, 0, buffer.length, null))) hash.update(buffer.subarray(0, size));
  } finally { fs.closeSync(handle); }
  return hash.digest('hex');
}

function within(directory, relative, label) {
  require(nonempty(relative), `${label}: missing path`);
  const file = path.resolve(directory, relative);
  const parent = fs.realpathSync(directory);
  require(fs.statSync(file).isFile(), `${label}: file missing`);
  const real = fs.realpathSync(file);
  require(real.startsWith(parent + path.sep), `${label}: path must stay inside ${directory}`);
  return real;
}

function validDate(value) {
  return typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)
    && !Number.isNaN(Date.parse(value)) && new Date(value).toISOString().slice(0, 10) === value;
}

function https(value) {
  try { return nonempty(value) && new URL(value).protocol === 'https:'; } catch { return false; }
}

function checkTextEvidence(repoRoot, record, text, label) {
  require(record && typeof record === 'object' && !Array.isArray(record)
    && nonempty(record.locator), `${label}: original-text evidence needs a locator`);
  const file = within(repoRoot, record.evidence, `${label} evidence`);
  const raw = fs.readFileSync(file, 'utf8');
  let texts = [raw];
  if (path.extname(file).toLowerCase() === '.json') {
    // JSON evidence may escape quotation marks and newlines. Compare decoded
    // source strings, not their serialization. This does not re-read the URL or
    // independently determine whether the recorded title/quotation is genuine.
    texts = [];
    const visit = (value) => {
      if (typeof value === 'string') texts.push(value);
      else if (Array.isArray(value)) value.forEach(visit);
      else if (value && typeof value === 'object') Object.values(value).forEach(visit);
    };
    visit(JSON.parse(raw));
  }
  require(texts.some((value) => value.includes(text)), `${label}: exact original text missing from evidence record`);
}

export function checkSources(episodeDir, {repoRoot = ROOT, sources = 'references.json', slug = path.basename(episodeDir)} = {}) {
  const refsFile = within(episodeDir, sources, 'references');
  const refs = read(refsFile);
  require(refs.schemaVersion === 1 && refs.episode === slug, 'reference schema/episode differs');
  require(refs.presentation === 'original-title-quote', 'references must use original-title-quote presentation');
  require(validDate(refs.checkedAt), 'reference checkedAt must be a real YYYY-MM-DD date');
  require(Array.isArray(refs.sources) && refs.sources.length > 0, 'reference sources must not be empty');
  const article = fs.readFileSync(within(episodeDir, 'article.mdx', 'article'), 'utf8');
  const ids = new Set();
  for (const source of refs.sources) {
    for (const key of ['id', 'organization', 'title', 'version', 'sections'])
      require(nonempty(source[key]), `source ${source.id ?? '?'} missing ${key}`);
    require(!Object.hasOwn(source, 'displayTitle') && !Object.hasOwn(source, 'displaySupport'),
      `${source.id}: displayTitle/displaySupport cannot replace original titles or quotations`);
    require(!ids.has(source.id), `duplicate source id ${source.id}`);
    ids.add(source.id);
    require(https(source.url), `${source.id}: source URL must use HTTPS`);
    require(Array.isArray(source.supports) && source.supports.length > 0 && source.supports.every(nonempty),
      `${source.id}: source must support a concrete claim`);
    const verification = source.verification;
    require(verification?.status === 'verified' && validDate(verification.checkedAt),
      `${source.id}: source must be verified with a real checkedAt date`);
    within(repoRoot, verification.evidence, `${source.id} verification evidence`);
    checkTextEvidence(repoRoot, source.titleEvidence, source.title, `${source.id} original title`);
    if (Object.hasOwn(source, 'quotation')) {
      require(source.quotation && nonempty(source.quotation.text), `${source.id}: quotation needs original text`);
      checkTextEvidence(repoRoot, source.quotation, source.quotation.text, `${source.id} quotation`);
    }
    for (const url of [source.url, verification.sourceUrl].filter((value) => value !== undefined)) {
      require(https(url) && article.includes(url), `${source.id}: complete source link missing from article: ${url}`);
    }
  }
  return {refs, refsFile};
}

export function checkEpisode(episodeDir, {repoRoot = ROOT} = {}) {
  const meta = read(path.join(episodeDir, 'meta.json'));
  const slug = path.basename(episodeDir);
  require(meta.slug === slug, 'published slug differs from folder');
  const appendix = meta.referenceAppendix;
  require(appendix?.kind === 'references', 'missing referenceAppendix declaration');
  require(integer(appendix.from) && integer(appendix.durationInFrames) && appendix.durationInFrames > 0,
    'reference appendix requires an explicit positive frame range');
  require(nonempty(appendix.sources) && nonempty(appendix.manifest),
    'reference appendix requires explicit sources and manifest paths');
  const {refs, refsFile} = checkSources(episodeDir, {repoRoot, sources: appendix.sources, slug});
  const receipt = read(within(episodeDir, appendix.manifest, 'appendix receipt'));
  const media = read(within(episodeDir, 'reference-appendix-media-check.json', 'appendix media check'));
  require(receipt.schemaVersion === 1 && receipt.episode === slug && receipt.appendix?.kind === 'references',
    'appendix receipt schema/episode differs');
  require(receipt.presentation === refs.presentation, 'rendered appendix presentation differs from original-title mode');
  require(Array.isArray(receipt.sourceTitles) && receipt.sourceTitles.length === refs.sources.length
    && receipt.sourceTitles.every((entry, index) => entry.id === refs.sources[index].id
      && entry.title === refs.sources[index].title), 'rendered appendix original source titles differ');
  const quotations = refs.sources.filter((source) => Object.hasOwn(source, 'quotation'))
    .map((source) => ({id: source.id, ...source.quotation}));
  require(Array.isArray(receipt.quotations) && receipt.quotations.length === quotations.length
    && receipt.quotations.every((entry, index) => ['id', 'text', 'locator', 'evidence']
      .every((key) => entry[key] === quotations[index][key])), 'rendered appendix original quotations differ');
  const end = appendix.from + appendix.durationInFrames;
  require(integer(meta.finalVideoFrames) && meta.finalVideoFrames === end
    && receipt.bodyFrames === appendix.from && receipt.finalVideoFrames === end
    && receipt.appendix.from === appendix.from && receipt.appendix.durationInFrames === appendix.durationInFrames,
  'final video/receipt/metadata appendix frame ranges differ');
  require(JSON.stringify(receipt.appendix.sourceIds) === JSON.stringify(refs.sources.map((source) => source.id)),
    'appendix receipt source IDs differ');
  require(Array.isArray(receipt.appendix.pages) && receipt.appendix.pages.length > 0
    && integer(receipt.appendix.framesPerPage) && receipt.appendix.framesPerPage > 0
    && receipt.appendix.pages.length * receipt.appendix.framesPerPage === appendix.durationInFrames,
  'appendix page count/duration differs');
  require(receipt.inputs?.referencesSHA256 === shaFile(refsFile), 'reference input SHA differs from rendered appendix');
  require(hashPattern.test(receipt.inputs?.bodySHA256 ?? '') && hashPattern.test(receipt.inputs?.generatorSHA256 ?? ''),
    'appendix receipt lacks body/generator SHA');
  const videoSHA = shaFile(within(episodeDir, meta.video, 'final video'));
  require(receipt.outputSHA256 === videoSHA, 'final video SHA differs from appendix receipt');
  require(media.passed === true && media.outputSHA256 === videoSHA
    && media.bodySHA256 === receipt.inputs.bodySHA256 && media.bodyFrames === appendix.from
    && media.appendedFrames === appendix.durationInFrames && media.finalFrames === end,
  'appendix media check is missing, failed or belongs to another output');
  for (const field of ['bodyDecodedFramesAndTimestampsEqual', 'outputVideoTimelineContinuous', 'audioPacketsAndTimingEqual'])
    require(media[field] === true, `appendix media check did not verify ${field}`);
  require(hashPattern.test(media.bodyFrameMD5RowsSHA256 ?? '')
    && hashPattern.test(media.audioPacketPayloadAndTimingSHA256 ?? '')
    && /^SHA256=[a-f0-9]{64}$/.test(media.decodedAudioPCM ?? ''), 'appendix media check lacks body/audio fingerprints');
  return {slug, sourceCount: refs.sources.length};
}

export function checkPublished({repoRoot = ROOT, legacySlugs, legacyVideoSHA256 = {}} = {}) {
  if (!legacySlugs) {
    const policy = read(path.join(repoRoot, 'site/scripts/reference-legacy.json'));
    require(policy.schemaVersion === 1 && /^[a-f0-9]{40}$/.test(policy.baselineCommit), 'invalid reference legacy policy');
    require(Array.isArray(policy.publishedSlugs) && policy.publishedSlugs.every(nonempty)
      && new Set(policy.publishedSlugs).size === policy.publishedSlugs.length, 'invalid reference legacy slug list');
    legacySlugs = new Set(policy.publishedSlugs);
    legacyVideoSHA256 = policy.publishedVideoSHA256;
    require(legacyVideoSHA256 && Object.keys(legacyVideoSHA256).length === legacySlugs.size
      && [...legacySlugs].every((slug) => hashPattern.test(legacyVideoSHA256[slug] ?? '')),
    'invalid reference legacy media hashes');
  }
  const summary = {validated: [], legacyDeferred: [], drafts: []};
  const problems = [];
  const episodes = path.join(repoRoot, 'episodes');
  for (const slug of fs.readdirSync(episodes).sort()) {
    const directory = path.join(episodes, slug);
    const metaFile = path.join(directory, 'meta.json');
    if (!fs.existsSync(metaFile)) continue;
    try {
      const meta = read(metaFile);
      if (meta.draft === true) { summary.drafts.push(slug); continue; }
      const declared = Object.hasOwn(meta, 'referenceAppendix')
        || ['references.json', 'reference-appendix.json', 'reference-appendix-media-check.json']
          .some((name) => fs.existsSync(path.join(directory, name)));
      if (legacySlugs.has(slug) && !declared) {
        require(hashPattern.test(legacyVideoSHA256[slug] ?? ''), 'historical exemption requires its fixed original media SHA');
        require(shaFile(within(directory, meta.video, 'historical video')) === legacyVideoSHA256[slug],
          'remade public video requires reference sources and an actual encoded appendix');
        summary.legacyDeferred.push(slug);
        continue;
      }
      require(declared, 'new public video requires reference sources and an actual encoded appendix');
      summary.validated.push(checkEpisode(directory, {repoRoot}));
    } catch (error) { problems.push(`${slug}: ${error.message}`); }
  }
  require(!problems.length, `Reference appendix check failed:\n${problems.join('\n')}`);
  return summary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    if (process.argv.length === 4 && process.argv[2] === '--sources') {
      const directory = path.resolve(process.argv[3]);
      const {refs} = checkSources(directory);
      console.log(`Reference source preflight passed: ${refs.episode}, ${refs.sources.length} source(s). Recorded evidence and article links checked; original-source review remains required.`);
    } else {
      require(process.argv.length === 2, 'Usage: check-references.mjs [--sources EPISODE_DIRECTORY]');
      const summary = checkPublished();
      console.log(`Reference appendices passed: ${summary.validated.length} verified outputs; ${summary.legacyDeferred.length} historical episodes deferred; ${summary.drafts.length} drafts skipped.`);
    }
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
