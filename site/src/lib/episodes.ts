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
  slug: string; ep: number; problemNumber?: number; episodePart?: string; lessonOrder?: number; firstRelease?: string; title: string; summary: string; duration: number; tags: string[];
  createdAt: string; updatedAt: string; publishedAt?: string; date: string; poster: string; video: string; chapters: Chapter[]; Content: any; fps: number; burnedInCaptions?: boolean;
  draft: boolean; legacy: boolean; archived: boolean; replacedBy?: string[]; related: {slug: string; label?: string}[];
  learningGuide?: {slug: string; label: string}; series?: string; applicationScenario?: string; additionalSeries?: string[]; description?: string; platforms: Platform[]; readMin: number; sourcePath: string;
};
export type Platform = {id: string; label: string; url: string};
/** 平台链接：只渲染 meta.json platforms 里写了真实 URL 的平台，没写的不显示（绝不拼猜） */
const PLATFORMS: [string, string][] = [['bilibili', 'B站'], ['douyin', '抖音'], ['kuaishou', '快手']];
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
/** 相关期数：已发布的给链接，草稿只显示“制作中”。meta.json 的 related 可写 slug 字符串或 {slug, label}；按期号升序显示 */
export function getRelated(e: Episode) {
  const all = new Map(getAllMeta().map((m) => [m.slug, m]));
  return ((e.related ?? []) as (string | {slug: string; label?: string})[]).map((raw) => {
    const r = typeof raw === 'string' ? {slug: raw} : raw;
    const m = all.get(r.slug);
    if (!m || m.archived) return null;
    return {slug: r.slug, ep: Number(m.ep) || 0, problemNumber: m.problemNumber, episodePart: m.episodePart, lessonOrder: m.lessonOrder, label: r.label ?? '', title: m.title, summary: m.summary, legacy: !!m.legacy, published: !m.draft || SHOW_DRAFTS};
  }).filter(Boolean).sort(compareLessons) as {slug: string; ep: number; problemNumber?: number; episodePart?: string; lessonOrder?: number; label: string; title: string; summary: string; legacy: boolean; published: boolean}[];
}
/** 旧版标记：EP.08 起尚未重制的旧期 meta.json 写 legacy: true，卡片和详情页显示这句；重制版上线时删掉该字段 */
export const LEGACY_LABEL = '旧版，重制中';

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

/** 章节：chapters.txt 优先；否则合并连续同章的分镜，起点按实际帧数计算。 */
export function computeChapters(slug: string, fm: any[] = []) {
  const storyboardPath = path.join(EP_DIR, slug, 'storyboard.json');
  const chaptersPath = path.join(EP_DIR, slug, 'chapters.txt');
  const hasStoryboard = fs.existsSync(storyboardPath);
  const hasChapters = fs.existsSync(chaptersPath);
  if (!hasStoryboard && !hasChapters) {
    // 草稿期还没有分镜：章节起点暂为 0，仅供 SHOW_DRAFTS 预览
    return {chapters: fm.map((f: any) => ({id: f.id, title: f.title, start: 0, frame: 0, inArticle: true})), duration: 0, fps: 30};
  }
  const {fps, scenes, total} = hasStoryboard ? shotPlan(slug) : {fps: 30, scenes: [], total: 0};
  // 优先按 scene.chapterId 与 frontmatter id 显式对应（v2：开场/回顾不在正文里，用 scene 标题）；否则按顺序对齐
  const byId = scenes.some((s: any) => s.chapterId);
  const fmById = new Map(fm.map((f: any) => [f.id, f]));
  const groups: any[][] = [];
  scenes.forEach((s: any, i: number) => {
    const prev = scenes[i - 1];
    if (prev && ((s.chapterId && s.chapterId === prev.chapterId) || (s.title && s.title === prev.title)))
      groups[groups.length - 1].push(s);
    else groups.push([s]);
  });
  let chapters: Chapter[] = groups.map((group, i) => {
    const s = group[0];
    // 章卡可能有独立 id；正文锚点取同组中能匹配 frontmatter 的分镜。
    const f: any = byId ? group.map((s) => fmById.get(s.chapterId)).find(Boolean) ?? {} : fm[i] ?? {};
    const start = s.from / fps;
    if (!hasChapters && f.start !== undefined && Math.abs(f.start - start) > 0.5)
      console.warn(`[chapters] ${slug}#${f.id}: frontmatter start=${f.start}s → 实际 ${start}s（frame ${s.from}）`);
    return {id: f.id ?? s.chapterId ?? s.id, title: f.title ?? s.title, start, frame: s.from, fmStart: f.start, inArticle: !!f.id};
  });
  if (hasChapters) {
    chapters = fs.readFileSync(chaptersPath, 'utf8').split(/\r?\n/).map((line) => line.trim()).filter(Boolean).map((line, i) => {
      const match = /^(\d{2,}):([0-5]\d)\s+(.+)$/.exec(line);
      if (!match) throw new Error(`[chapters] ${slug}: 无效章节行 ${JSON.stringify(line)}，应为 MM:SS title`);
      const start = Number(match[1]) * 60 + Number(match[2]);
      const title = match[3];
      const chapter = chapters.find((c, j) => c.title === title || groups[j].some((s) => s.title === title));
      const f = fm.find((f) => f.title === title);
      return {id: f?.id ?? chapter?.id ?? `chapter-${i + 1}`, title, start, frame: Math.round(start * fps),
        fmStart: f?.start ?? chapter?.fmStart, inArticle: !!f?.id || !!chapter?.inArticle};
    });
  } else if (!byId && fm.length && fm.length !== groups.length)
    console.warn(`[chapters] ${slug}: frontmatter ${fm.length} 章 vs storyboard ${groups.length} chapter，按顺序对齐`);
  // 成片帧数：storyboard meta.finalVideoFrames 优先（EP.21 起写入；EP.22 起取消全局 60 帧片尾卡，
  // 成片 = 分镜 durationInFrames + 片尾停留 30 帧，见各期 Main.tsx TAIL_HOLD）；
  // 未写 finalVideoFrames 的旧期 = 正片 + 「IT小村 · 原创」片尾卡（episodes/_shared/branding，Remotion Root 同样追加）
  if (!hasStoryboard) return {chapters, duration: 0, fps};
  const sbMeta = readJson(storyboardPath).meta ?? {};
  const brandPath = path.join(EP_DIR, '_shared/branding/spec.json');
  const endCard = fs.existsSync(brandPath) ? readJson(brandPath).endCard?.frames ?? 0 : 0;
  // episode meta.json finalVideoFrames 优先（分镜冻结后不改 storyboard 哈希，如 EP.01 v6）
  const metaPath = path.join(EP_DIR, slug, 'meta.json');
  const epMeta = fs.existsSync(metaPath) ? readJson(metaPath) : {};
  const finalFrames = Number.isFinite(epMeta.finalVideoFrames) ? epMeta.finalVideoFrames
    : Number.isFinite(sbMeta.finalVideoFrames) ? sbMeta.finalVideoFrames : total + endCard;
  if (finalFrames < total) console.warn(`[duration] ${slug}: finalVideoFrames=${finalFrames} < 正片 ${total} 帧`);
  // Preserve frame precision until display formatting; 170.966s must not become 171s.
  return {chapters, duration: finalFrames / fps, fps};
}

/** WebVTT 字幕优先使用冻结的镜内 from/to；旧稿没有完整时序时按字数分配。 */
export function buildVtt(slug: string) {
  if (!fs.existsSync(path.join(EP_DIR, slug, 'storyboard.json'))) return 'WEBVTT\n';
  const {fps, scenes} = shotPlan(slug);
  const meta = readJson(path.join(EP_DIR, slug, 'storyboard.json')).meta;
  const metaPath = path.join(EP_DIR, slug, 'meta.json');
  const epMeta = fs.existsSync(metaPath) ? readJson(metaPath) : {};
  const card = meta?.unvoicedEndCard ?? meta?.javaEndCard ?? epMeta.referenceAppendix;
  const cardFrom = Number.isInteger(card?.from) && card.from >= 0
    && Number.isInteger(card?.durationInFrames) && card.durationInFrames > 0 ? card.from : undefined;
  const ts = (f: number, cueEnd = false) => {
    // Native cues can remain active when their end equals the first card frame.
    // Only that exact end uses the greatest millisecond strictly before it.
    // Multiply integer frames first; rounding seconds first can cross an exact millisecond boundary.
    const s = cueEnd && f === cardFrom ? (Math.ceil(f * 1000 / fps) - 1) / 1000 : f / fps;
    const hh = Math.floor(s / 3600), mm = Math.floor((s % 3600) / 60), ss = (s % 60).toFixed(3).padStart(6, '0');
    return `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}:${ss}`;
  };
  const v2 = scenes.some((s: any) => s.chapterId);
  const n = (s: string) => s.replace(v2 ? /[\s，。：？！；、,.:?!;—“”"()（）]/g : /[\s，。：？！,.:?!—]/g, '').length || 1;
  const cues: string[] = [];
  for (const sc of scenes) for (const {sh, from, dur, audioFrames} of sc.shots) {
    const subs = sh.subtitles ?? [];
    const timed = subs.length > 0 && subs.every((s: any, i: number) =>
      Number.isInteger(s.from) && Number.isInteger(s.to) && s.from >= 0 && s.to >= s.from && s.to < dur
      && (i === 0 || s.from > subs[i - 1].to));
    if (timed) {
      subs.forEach((s: any) => cues.push(`${ts(from + s.from)} --> ${ts(from + s.to + 1, true)}\n${s.text}`));
      continue;
    }
    const total = subs.reduce((a: number, s: any) => a + n(s.text), 0);
    let t = 0;
    subs.forEach((s: any, i: number) => {
      const a = Math.round((t / total) * audioFrames);
      t += n(s.text);
      const b = i === subs.length - 1 ? audioFrames + 6 : Math.round((t / total) * audioFrames) - 1;
      cues.push(`${ts(from + a)} --> ${ts(from + b + 1, true)}\n${s.text}`);
    });
  }
  return `WEBVTT\n\n${cues.join('\n\n')}\n`;
}

let cache: Episode[] | null = null;
export function getEpisodes({includeArchived = false}: {includeArchived?: boolean} = {}): Episode[] {
  if (!cache) cache = fs.readdirSync(EP_DIR)
    .filter((slug) => fs.existsSync(path.join(EP_DIR, slug, 'meta.json')))
    .filter((slug) => SHOW_DRAFTS || !readMeta(slug).draft)
    .map((slug) => {
      const meta = readJson(path.join(EP_DIR, slug, 'meta.json'));
      const dates = episodeDates(meta);
      const mod = articles[`../../../episodes/${slug}/article.mdx`];
      const fm = mod?.frontmatter ?? {};
      const {chapters, duration, fps} = computeChapters(slug, fm.chapters);
      return {
        slug, ep: meta.ep ?? 0, problemNumber: meta.problemNumber, episodePart: meta.episodePart, lessonOrder: meta.lessonOrder, firstRelease: meta.firstRelease, learningGuide: meta.learningGuide, replacedBy: meta.replacedBy, title: meta.title ?? fm.title, summary: meta.summary ?? fm.summary,
        tags: meta.tags ?? [], ...dates, date: dates.publishedAt ?? dates.createdAt, poster: meta.poster, video: meta.video,
        duration, chapters, fps, Content: mod?.default, draft: !!meta.draft, legacy: !!meta.legacy, archived: !!meta.archived, related: meta.related ?? [],
        series: meta.series,
        applicationScenario: meta.applicationScenario,
        additionalSeries: Array.isArray(meta.additionalSeries) ? meta.additionalSeries.filter((id: unknown) => typeof id === 'string' && id !== meta.series) : [],
        description: meta.description,
        platforms: platformsOf(meta), readMin: readingMinutes(slug),
        sourcePath: meta.sourcePath ?? `episodes/${slug}/remotion`,
        burnedInCaptions: meta.burnedInCaptions === true,
      };
    })
    .sort((a, b) => Date.parse(dateIso(b.date)) - Date.parse(dateIso(a.date)) || compareLessons(b, a));
  return includeArchived ? cache : cache.filter((e) => !e.archived);
}

export function getTags() {
  const all = new Map<string, number>();
  for (const e of getEpisodes()) for (const t of e.tags) all.set(t, (all.get(t) ?? 0) + 1);
  const meta = tagsMeta as Record<string, {description?: string; order?: number}>;
  return [...all.entries()]
    .map(([name, count]) => ({name, count, description: meta[name]?.description ?? `与「${name}」相关的视频与图文。`, order: meta[name]?.order ?? 99}))
    .sort((a, b) => a.order - b.order || b.count - a.count);
}

export const fmtTime = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
/** 教学顺序与历史期号分开：同一期可有入门、方案详解，不改旧链接与整数期号。 */
export const compareLessons = (a: {ep: number; lessonOrder?: number}, b: {ep: number; lessonOrder?: number}) =>
  a.ep - b.ep || (a.lessonOrder ?? 0) - (b.lessonOrder ?? 0);
/** 题号用于算法系列展示；整数 ep 继续用于历史排序和 Release 关联。 */
export const epLabel = (item: number | {ep: number; problemNumber?: number; episodePart?: string}) => {
  if (typeof item !== 'number' && Number.isInteger(item.problemNumber) && item.problemNumber! > 0)
    return `LC.${item.problemNumber}`;
  const ep = typeof item === 'number' ? item : item.ep;
  const part = typeof item === 'number' ? '' : item.episodePart;
  return `EP.${String(ep).padStart(2, '0')}${part ? ` · ${part}` : ''}`;
};
/** 引导目标必须已发布（或显式预览草稿），避免展示尚未上线的教学链接。 */
export const learningGuideFor = (e: Episode) => e.learningGuide
  ? getEpisodes().find((x) => x.slug === e.learningGuide!.slug) : undefined;
/** 归档页只链接已发布的替代课程；制作中的课程保留可识别名称，不产生死链接。 */
export const archiveReplacementsFor = (e: Episode) => getRelated({...e, related: (e.replacedBy ?? []).map((slug) => ({slug}))});
export const tagHref = (t: string) => `${BASE}tags/${encodeURIComponent(t)}/`;
export const epHref = (slug: string) => `${BASE}episodes/${slug}/`;
export const asset = (slug: string, f: string) => `${BASE}episodes/${slug}/${f}`;

/** 历史日期保留日精度；新时间必须明确时区，避免构建机器改变内容版本。 */
export function dateIso(d: string): string {
  if (typeof d === 'string') {
    const day = d.slice(0, 10);
    const parsed = new Date(`${day}T00:00:00Z`);
    const validDay = Number.isFinite(parsed.getTime()) && parsed.toISOString().slice(0, 10) === day;
    if (validDay && /^\d{4}-\d{2}-\d{2}$/.test(d)) return `${d}T00:00:00+08:00`;
    if (validDay && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?(?:Z|[+-]\d{2}:\d{2})$/.test(d) && Number.isFinite(Date.parse(d))) return d;
  }
  throw new Error(`无效的剧集时间：${d}；请使用 YYYY-MM-DD 或含时区的 ISO 8601 时间`);
}

export function episodeDates(meta: {createdAt?: string; updatedAt?: string; publishedAt?: string; draft?: boolean}) {
  // 兼容尚未迁移的历史元数据；显式字段写入后不在构建时刷新。
  const createdAt = meta.createdAt ?? meta.publishedAt;
  const updatedAt = meta.updatedAt ?? createdAt;
  if (!createdAt || !updatedAt) throw new Error('剧集缺少创建或修改时间');
  if (meta.publishedAt) dateIso(meta.publishedAt);
  else if (!meta.draft) throw new Error('已发布剧集缺少首次公开时间 publishedAt');
  if (Date.parse(dateIso(updatedAt)) < Date.parse(dateIso(createdAt)))
    throw new Error(`剧集修改时间 ${updatedAt} 早于创建时间 ${createdAt}`);
  return {createdAt, updatedAt, publishedAt: meta.publishedAt};
}

const shanghaiDate = new Intl.DateTimeFormat('en-GB', {
  timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23',
});
const dateParts = (d: string) => Object.fromEntries(shanghaiDate.formatToParts(new Date(dateIso(d))).map((p) => [p.type, p.value]));
export const fmtVersion = (d: string) => {
  const p = dateParts(d);
  return `${p.year}-${p.month}-${p.day}${d.length > 10 ? ` ${p.hour}:${p.minute}:${p.second}` : ''} 版`;
};
export const fmtDate = (d: string) => {
  const p = dateParts(d);
  return `${p.year}年${Number(p.month)}月${Number(p.day)}日${d.length > 10 ? ` ${p.hour}:${p.minute}:${p.second}` : ''}`;
};
export const fmtDay = (d: string) => {const p = dateParts(d); return `${p.year}-${p.month}-${p.day}`;};
export const fmtDateShort = (d: string) => {const p = dateParts(d); return `${Number(p.month)}月${Number(p.day)}日`;};

/** NEW 根据首发日期计算，内容修改不会变成新一期。 */
const BUILD_DAY = new Date(Date.now() + 8 * 3600e3).toISOString().slice(0, 10);
const dayDiff = (d: string) => {const p = dateParts(d); return Math.round((Date.parse(BUILD_DAY) - Date.parse(`${p.year}-${p.month}-${p.day}`)) / 864e5);};
/** NEW：7 天内发布，且最多标最近 NEW_MAX 期（目前日更，全站都在 7 天内，不加上限会每张卡都是 NEW） */
export const NEW_DAYS = 7, NEW_MAX = 3;
export const isNew = (d: string, slug?: string) => {
  const n = dayDiff(d); if (n < 0 || n >= NEW_DAYS) return false;
  if (!slug) return true;
  return getEpisodes().slice(0, NEW_MAX).some((e) => e.slug === slug);
};
/** ISO 8601 时长，供 JSON-LD 使用 */
export const isoDuration = (s: number) => `PT${Math.floor(s / 60)}M${Math.floor(s % 60)}S`;

/** 一期可额外收录进多个目录，仍使用同一slug、媒体与首发身份；series保留主学习路径。 */
export type Series = {id: string; title: string; description: string; order: number; crossSeriesNavigation?: boolean; independentLessons?: boolean; episodes: Episode[]};
/** 归档内容仍保留系列归属；这不把它重新加入现行课程或前后课导航。 */
export function seriesFor(e: Pick<Episode, 'series'>): Omit<Series, 'episodes'> | undefined {
  const meta = seriesMeta as Record<string, Omit<Series, 'id' | 'episodes'>>;
  return e.series && meta[e.series] ? {id: e.series, ...meta[e.series]} : undefined;
}
export function getSeries(): Series[] {
  const meta = seriesMeta as Record<string, {title: string; description: string; order: number; crossSeriesNavigation?: boolean; independentLessons?: boolean}>;
  return Object.entries(meta).map(([id, m]) => ({id, ...m, episodes: getEpisodes().filter((e) => e.series === id || e.additionalSeries?.includes(id)).sort(compareLessons)}))
    .filter((s) => s.episodes.length).sort((a, b) => a.order - b.order);
}
export const additionalSeriesFor = (e: Episode) => e.archived ? [] : getSeries()
  .filter((series) => series.id !== e.series && e.additionalSeries?.includes(series.id));
/** 某期在系列中的位置与系列内上/下一期；独立系列不与相邻系列组成学习路径。 */
export function seriesNav(e: Episode) {
  if (e.archived) return null;
  // 额外目录不能改变原有上/下一课，也不作为跨系列导航的中间章节。
  const all = getSeries().map((series) => ({...series, episodes: series.episodes.filter((episode) => episode.series === series.id)}))
    .filter((series) => series.episodes.length);
  const si = all.findIndex((s) => s.id === e.series);
  if (si < 0) return null;
  const s = all[si], i = s.episodes.findIndex((x) => x.slug === e.slug);
  const adjacent = (neighbor: Series | undefined) =>
    s.crossSeriesNavigation !== false && neighbor?.crossSeriesNavigation !== false ? neighbor : undefined;
  const prevS = adjacent(all[si - 1]), nextS = adjacent(all[si + 1]);
  return {
    series: s, index: i + 1, total: s.episodes.length,
    prev: s.episodes[i - 1] ?? (prevS ? prevS.episodes[prevS.episodes.length - 1] : undefined),
    next: s.episodes[i + 1] ?? (nextS ? nextS.episodes[0] : undefined),
    prevCross: !s.episodes[i - 1] && !!prevS ? prevS : undefined,
    nextCross: !s.episodes[i + 1] && !!nextS ? nextS : undefined,
  };
}
export const seriesHref = (id: string) => `${BASE}series/${id}/`;
