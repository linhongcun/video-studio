import fs from 'node:fs';
import path from 'node:path';
import pkg from '../../package.json';
import tagsMeta from '../content/tags.json';

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
};

/** draft: true 的期数默认不发布；本地预览可用 SHOW_DRAFTS=1 npm run build 查看 */
export const SHOW_DRAFTS = process.env.SHOW_DRAFTS === '1';
const readMeta = (slug: string) => JSON.parse(fs.readFileSync(path.join(EP_DIR, slug, 'meta.json'), 'utf8'));
export function getAllMeta() {
  return fs.readdirSync(EP_DIR).filter((s) => fs.existsSync(path.join(EP_DIR, s, 'meta.json'))).map((s) => ({slug: s, ...readMeta(s)}));
}
/** 相关期数（速览版 ↔ 完整版）：已发布的给链接，草稿只显示“制作中” */
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
  // 优先按 scene.chapterId 与 frontmatter id 显式对应（v2：开场/回顾不在正文里，用 scene 标题）；否则按顺序对齐（速览版）
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
  return {chapters, duration: Math.round((total / fps) * 10) / 10, fps};
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
