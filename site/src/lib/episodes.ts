import fs from 'node:fs';
import path from 'node:path';
import pkg from '../../package.json';
import tagsMeta from '../content/tags.json';
import seriesMeta from '../content/series.json';

export const REPO = 'https://github.com/linhongcun/video-studio';
export const VERSION = pkg.version;
export const BASE = import.meta.env.BASE_URL;
const EP_DIR = path.resolve(process.cwd(), '../episodes');
const articles = import.meta.glob('../../../episodes/*/article.mdx', {eager: true}) as Record<string, any>;

export type Chapter = {id: string; title: string; start: number; frame: number; fmStart?: number; inArticle?: boolean};
export type Episode = {
  slug: string; ep: number; title: string; summary: string; duration: number; tags: string[];
  date: string; poster: string; video: string; chapters: Chapter[]; Content: any; fps: number;
  draft: boolean; related: {slug: string; label?: string}[];
  series?: string; description?: string; updated?: string; platforms: Platform[]; readMin: number;
};
export type Platform = {id: string; label: string; url: string};
/** 平台链接：只渲染 meta.json platforms 里写了真实 URL 的平台，没写的不显示（绝不拼猜） */
const PLATFORMS: [string, string][] = [['bilibili', 'B站'], ['douyin', '抖音'], ['kuaishou', '快手']];
export const ACCOUNT = 'IT小村';
const platformsOf = (m: any): Platform[] => PLATFORMS
  .map(([id, label]) => ({id, label, url: String(m.platforms?.[id] ?? '').trim()}))
  .filter((p) => /^https:\/\//.test(p.url));

/** 阅读时长：去掉 frontmatter / import / 代码块 / 标签后，中文按字 + 英文按词，约 400 字每分钟 */
function readingMinutes(slug: string) {
  const f = path.join(EP_DIR, slug, 'article.mdx');
  if (!fs.existsSync(f)) return 0;
  const t = fs.readFileSync(f, 'utf8').replace(/^---[\s\S]*?\n---/, '').replace(/```[\s\S]*?```/g, '')
    .replace(/^(import|export) .*$/gm, '').replace(/<[^>]+>/g, '').replace(/\{#[\w-]+\}/g, '');
  const cjk = (t.match(/[\u4e00-\u9fff]/g) ?? []).length;
  const words = (t.replace(/[\u4e00-\u9fff]/g, ' ').match(/[A-Za-z0-9]+/g) ?? []).length;
  return Math.max(1, Math.round((cjk + words) / 400));
}

/** draft: true 的期数默认不发布；本地预览可用 SHOW_DRAFTS=1 npm run build 查看 */
export const SHOW_DRAFTS = process.env.SHOW_DRAFTS === '1';
const readMeta = (slug: string) => JSON.parse(fs.readFileSync(path.join(EP_DIR, slug, 'meta.json'), 'utf8'));
export function getAllMeta() {
  return fs.readdirSync(EP_DIR).filter((s) => fs.existsSync(path.join(EP_DIR, s, 'meta.json'))).map((s) => ({slug: s, ...readMeta(s)}));
}
/** 相关期数：已发布的给链接，草稿只显示“制作中” */
export function getRelated(e: Episode) {
  const all = new Map(getAllMeta().map((m) => [m.slug, m]));
  return (e.related ?? []).map((r) => {
    const m = all.get(r.slug);
    if (!m) return null;
    return {slug: r.slug, label: r.label ?? '', title: m.title, summary: m.summary, published: !m.draft || SHOW_DRAFTS};
  }).filter(Boolean) as {slug: string; label: string; title: string; summary: string; published: boolean}[];
}

const readJson = (p: string) => JSON.parse(fs.readFileSync(p, 'utf8'));

/** 每个 shot 的实际帧数：remotion/src/timing.json 的 duration 优先，否则 storyboard 的 durationInFrames */
function shotPlan(slug: string) {
  const dir = path.join(EP_DIR, slug);
  const sb = readJson(path.join(dir, 'storyboard.json'));
  const tPath = path.join(dir, 'remotion/src/timing.json');
  const timing = fs.existsSync(tPath) ? readJson(tPath) : {};
  const fps = sb.meta?.fps ?? 30;
  let acc = 0;
  const scenes = sb.scenes.map((s: any) => {
    const sceneFrom = acc;
    const shots = s.shots.map((sh: any) => {
      const t = timing[sh.id];
      const o = {sh, from: acc, dur: t?.duration ?? sh.durationInFrames, audioFrames: t?.audioFrames ?? sh.durationInFrames};
      acc += o.dur;
      return o;
    });
    return {id: s.id, chapterId: s.chapterId, title: s.title, from: sceneFrom, shots};
  });
  return {fps, scenes, total: acc};
}

/** 章节：起点按实际帧数计算；id/标题以 article.mdx frontmatter 为准（按顺序与 storyboard scene 一一对应） */
export function computeChapters(slug: string, fm: any[] = []) {
  if (!fs.existsSync(path.join(EP_DIR, slug, 'storyboard.json'))) {
    // 草稿期还没有分镜：章节起点暂为 0，仅供 SHOW_DRAFTS 预览
    return {chapters: fm.map((f: any) => ({id: f.id, title: f.title, start: 0, frame: 0, inArticle: true})), duration: 0, fps: 30};
  }
  const {fps, scenes, total} = shotPlan(slug);
  // 优先按 scene.chapterId 与 frontmatter id 显式对应（v2：开场/回顾不在正文里，用 scene 标题）；否则按顺序对齐
  const byId = scenes.some((s: any) => s.chapterId);
  const fmById = new Map(fm.map((f: any) => [f.id, f]));
  const chapters: Chapter[] = scenes.map((s: any, i: number) => {
    const f: any = byId ? fmById.get(s.chapterId) ?? {} : fm[i] ?? {};
    const start = Math.round((s.from / fps) * 10) / 10;
    if (f.start !== undefined && Math.abs(f.start - start) > 0.5)
      console.warn(`[chapters] ${slug}#${f.id}: frontmatter start=${f.start}s → 实际 ${start}s（frame ${s.from}）`);
    return {id: f.id ?? s.chapterId ?? s.id, title: f.title ?? s.title, start, frame: s.from, fmStart: f.start, inArticle: !!f.id};
  });
  if (!byId && fm.length && fm.length !== scenes.length)
    console.warn(`[chapters] ${slug}: frontmatter ${fm.length} 章 vs storyboard ${scenes.length} scene，按顺序对齐`);
  // 成片帧数：storyboard meta.finalVideoFrames 优先（EP.21 起写入；EP.22 起取消全局 60 帧片尾卡，
  // 成片 = 分镜 durationInFrames + 片尾停留 30 帧，见各期 Main.tsx TAIL_HOLD）；
  // 未写 finalVideoFrames 的旧期 = 正片 + 「IT小村 · 原创」片尾卡（episodes/_shared/branding，Remotion Root 同样追加）
  const sbMeta = readJson(path.join(EP_DIR, slug, 'storyboard.json')).meta ?? {};
  const brandPath = path.join(EP_DIR, '_shared/branding/spec.json');
  const endCard = fs.existsSync(brandPath) ? readJson(brandPath).endCard?.frames ?? 0 : 0;
  const finalFrames = Number.isFinite(sbMeta.finalVideoFrames) ? sbMeta.finalVideoFrames : total + endCard;
  if (finalFrames < total) console.warn(`[duration] ${slug}: finalVideoFrames=${finalFrames} < 正片 ${total} 帧`);
  return {chapters, duration: Math.round((finalFrames / fps) * 10) / 10, fps};
}

/** WebVTT 字幕：与 Remotion Main.tsx 相同的分配规则（v2 的标点集合更全，两套都兼容）（按字数比例铺满真实音频时长） */
export function buildVtt(slug: string) {
  if (!fs.existsSync(path.join(EP_DIR, slug, 'storyboard.json'))) return 'WEBVTT\n';
  const {fps, scenes} = shotPlan(slug);
  const ts = (f: number) => {
    const s = f / fps;
    const hh = Math.floor(s / 3600), mm = Math.floor((s % 3600) / 60), ss = (s % 60).toFixed(3).padStart(6, '0');
    return `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}:${ss}`;
  };
  const v2 = scenes.some((s: any) => s.chapterId);
  const n = (s: string) => s.replace(v2 ? /[\s，。：？！；、,.:?!;—“”"()（）]/g : /[\s，。：？！,.:?!—]/g, '').length || 1;
  const cues: string[] = [];
  for (const sc of scenes) for (const {sh, from, audioFrames} of sc.shots) {
    const subs = sh.subtitles ?? [];
    const total = subs.reduce((a: number, s: any) => a + n(s.text), 0);
    let t = 0;
    subs.forEach((s: any, i: number) => {
      const a = Math.round((t / total) * audioFrames);
      t += n(s.text);
      const b = i === subs.length - 1 ? audioFrames + 6 : Math.round((t / total) * audioFrames) - 1;
      cues.push(`${ts(from + a)} --> ${ts(from + b + 1)}\n${s.text}`);
    });
  }
  return `WEBVTT\n\n${cues.join('\n\n')}\n`;
}

let cache: Episode[] | null = null;
export function getEpisodes(): Episode[] {
  if (cache) return cache;
  cache = fs.readdirSync(EP_DIR)
    .filter((slug) => fs.existsSync(path.join(EP_DIR, slug, 'meta.json')))
    .filter((slug) => SHOW_DRAFTS || !readMeta(slug).draft)
    .map((slug) => {
      const meta = readJson(path.join(EP_DIR, slug, 'meta.json'));
      const mod = articles[`../../../episodes/${slug}/article.mdx`];
      const fm = mod?.frontmatter ?? {};
      const {chapters, duration, fps} = computeChapters(slug, fm.chapters);
      return {
        slug, ep: meta.ep ?? 0, title: meta.title ?? fm.title, summary: meta.summary ?? fm.summary,
        tags: meta.tags ?? [], date: meta.publishedAt, poster: meta.poster, video: meta.video,
        duration, chapters, fps, Content: mod?.default, draft: !!meta.draft, related: meta.related ?? [],
        series: meta.series, description: meta.description, updated: meta.updatedAt && meta.updatedAt > meta.publishedAt ? meta.updatedAt : undefined,
        platforms: platformsOf(meta), readMin: readingMinutes(slug),
      };
    })
    .sort((a, b) => String(b.date).localeCompare(String(a.date)) || b.ep - a.ep);
  return cache;
}

export function getTags() {
  const all = new Map<string, number>();
  for (const e of getEpisodes()) for (const t of e.tags) all.set(t, (all.get(t) ?? 0) + 1);
  const meta = tagsMeta as Record<string, {description?: string; order?: number}>;
  return [...all.entries()]
    .map(([name, count]) => ({name, count, description: meta[name]?.description ?? `关于「${name}」的全部期数。`, order: meta[name]?.order ?? 99}))
    .sort((a, b) => a.order - b.order || b.count - a.count);
}

export const fmtTime = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
export const epLabel = (n: number) => `EP.${String(n).padStart(2, '0')}`;
export const tagHref = (t: string) => `${BASE}tags/${encodeURIComponent(t)}/`;
export const epHref = (slug: string) => `${BASE}episodes/${slug}/`;
export const asset = (slug: string, f: string) => `${BASE}episodes/${slug}/${f}`;

/** 日期：构建时计算（北京时间）。“10月16日”；7 天内（含发布当天）标 NEW */
const BUILD_DAY = new Date(Date.now() + 8 * 3600e3).toISOString().slice(0, 10);
const dayDiff = (d: string) => Math.round((Date.parse(BUILD_DAY) - Date.parse(String(d).slice(0, 10))) / 864e5);
export const fmtDate = (d: string) => { const [y, m, dd] = String(d).slice(0, 10).split('-').map(Number); return `${y}年${m}月${dd}日`; };
export const fmtDateShort = (d: string) => { const [, m, dd] = String(d).slice(0, 10).split('-').map(Number); return `${m}月${dd}日`; };
/** NEW：7 天内发布，且最多标最近 NEW_MAX 期（目前日更，全站都在 7 天内，不加上限会每张卡都是 NEW） */
export const NEW_DAYS = 7, NEW_MAX = 3;
export const isNew = (d: string, slug?: string) => {
  const n = dayDiff(d); if (n < 0 || n >= NEW_DAYS) return false;
  if (!slug) return true;
  return getEpisodes().slice(0, NEW_MAX).some((e) => e.slug === slug);
};
/** ISO 8601 时长，供 JSON-LD 使用 */
export const isoDuration = (s: number) => `PT${Math.floor(s / 60)}M${Math.floor(s % 60)}S`;

/** 系列（篇章）：series.json 定义顺序与简介；每期 meta.json 的 series 指向其 id。系列内按 ep 升序 */
export type Series = {id: string; title: string; description: string; order: number; episodes: Episode[]};
export function getSeries(): Series[] {
  const meta = seriesMeta as Record<string, {title: string; description: string; order: number}>;
  return Object.entries(meta).map(([id, m]) => ({id, ...m, episodes: getEpisodes().filter((e) => e.series === id).sort((a, b) => a.ep - b.ep)}))
    .filter((s) => s.episodes.length).sort((a, b) => a.order - b.order);
}
/** 某期在系列中的位置与系列内上/下一期；系列末尾的“下一期”接下一个系列的第一期 */
export function seriesNav(e: Episode) {
  const all = getSeries();
  const si = all.findIndex((s) => s.id === e.series);
  if (si < 0) return null;
  const s = all[si], i = s.episodes.findIndex((x) => x.slug === e.slug);
  const prevS = all[si - 1], nextS = all[si + 1];
  return {
    series: s, index: i + 1, total: s.episodes.length,
    prev: s.episodes[i - 1] ?? (prevS ? prevS.episodes[prevS.episodes.length - 1] : undefined),
    next: s.episodes[i + 1] ?? (nextS ? nextS.episodes[0] : undefined),
    prevCross: !s.episodes[i - 1] && !!prevS ? prevS : undefined,
    nextCross: !s.episodes[i + 1] && !!nextS ? nextS : undefined,
  };
}
export const seriesHref = (id: string) => `${BASE}series/${id}/`;
