/** Reader-facing notes are plain text and explicit links, never release-body HTML. */
const SITE = 'https://linhongcun.github.io';
const BASE = '/video-studio/';
const INTERNAL = /(?:\bsha(?:-?256)?\b|冻结|质检|预检|校验|构建|验收|清单|资产|保真|回执|声学|帧数|\b(?:QA|PTS|AAC|PCM|LUFS|COPYFIT|Remotion)\b|[a-f0-9]{16,}|\bPR\s*#\d+)/i;
const MARKDOWN_LINK = /\[([^\]\n]+)\]\(\s*<?(https:\/\/[^\s)>]+)>?(?:\s+["'][^\n]*?["'])?\s*\)/g;

const plain = (text) => text.replace(MARKDOWN_LINK, '$1').replace(/[`*_]/g, '').replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();

/** Keep the opening description, not subsequent production/deployment reports. */
export function readerSummary(body) {
  const lines = body.split(/\r?\n/).map((line) => line.trim());
  const first = lines.find((line) => line && !/^(?:#{1,6}\s|```|---)/.test(line) && !/^[-*]\s*\[/.test(line)
    && !/^(?:版本[：:]\s*v?\d+\.\d+\.\d+|(?:观看视频|观看视频与配套文章|观看视频与配套图文)[：:]\s*(?:https?:\/\/|\[))/.test(plain(line)));
  if (!first) return '';
  // Bare URL clauses are navigation metadata; related pages are linked below the summary.
  const text = plain(first.replace(/^[-*]\s+/, ''))
    .replace(/(?:[，,；;]\s*)?[^，,；;。！？]*https?:\/\/[^\s。！？]+[^。！？]*/g, '');
  const sentences = text.match(/[^。]+(?:。|$)/g) ?? [];
  const selected = [];
  for (const sentence of sentences) {
    if (INTERNAL.test(sentence) || !sentence.replace(/[。！？\s]/g, '')) continue;
    if (selected.join('').length + sentence.length > 220) break;
    selected.push(sentence);
    if (selected.length === 2) break;
  }
  return selected.join('').trim();
}

/** Only current site pages and public cover resources belong in the short log. */
export function readerLinks(body) {
  const links = new Map();
  for (const match of body.matchAll(MARKDOWN_LINK)) {
    let url;
    try { url = new URL(match[2]); } catch { continue; }
    if (url.protocol !== 'https:' || url.username || url.password) continue;
    const label = plain(match[1]);
    if (!label || INTERNAL.test(label)) continue;
    const sitePage = url.origin === SITE && url.pathname.startsWith(BASE)
      && /^(?:episodes\/[a-z0-9-]+\/|series\/[a-z0-9-]+\/|learn\/|library\/)$/.test(url.pathname.slice(BASE.length));
    const coverResource = ['github.com', 'raw.githubusercontent.com'].includes(url.hostname)
      && url.pathname.startsWith('/linhongcun/video-studio/') && url.pathname.includes('/design/')
      && /\.(?:zip|png|jpe?g|svg)$/i.test(url.pathname);
    if (!sitePage && !coverResource) continue;
    const href = sitePage ? `${url.pathname}${url.search}${url.hash}` : url.href;
    if (!links.has(href)) links.set(href, {label, href, external: !sitePage});
  }
  return [...links.values()];
}

export function readerNotes(release) {
  const heading = plain(release.name).replace(/^v?\d+\.\d+\.\d+\s*[:：·—-]?\s*/, '')
    .replace(/[（(]只上站点[）)]|[，,、]?\s*只上站点/g, '').trim();
  return {
    heading: heading && !INTERNAL.test(heading) ? heading : `${release.kind}记录`,
    summary: readerSummary(release.body),
    links: readerLinks(release.body),
  };
}
