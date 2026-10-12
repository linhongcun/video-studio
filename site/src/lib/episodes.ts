import fs from 'node:fs';
import path from 'node:path';
import pkg from '../../package.json';
import tagsMeta from '../content/tags.json';

export const REPO = 'https://github.com/linhongcun/video-studio';
export const VERSION = pkg.version;
export const BASE = import.meta.env.BASE_URL;
const EP_DIR = path.resolve(process.cwd(), '../episodes');
const articles = import.meta.glob('../../../episodes/*/article.mdx', {eager: true}) as Record<string, any>;

export type Chapter = {id: string; title: string; start: number; frame: number; fmStart?: number};
export type Episode = {
  slug: string; ep: number; title: string; summary: string; duration: number; tags: string[];
  date: string; poster: string; video: string; chapters: Chapter[]; Content: any; fps: number;
};

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
    return {id: s.id, title: s.title, from: sceneFrom, shots};
  });
  return {fps, scenes, total: acc};
}

/** 章节：起点按实际帧数计算；id/标题以 article.mdx frontmatter 为准（按顺序与 storyboard scene 一一对应） */
export function computeChapters(slug: string, fm: any[] = []) {
  const {fps, scenes, total} = shotPlan(slug);
  if (fm.length && fm.length !== scenes.length)
    console.warn(`[chapters] ${slug}: frontmatter ${fm.length} 章 vs storyboard ${scenes.length} scene，按顺序对齐`);
  const chapters: Chapter[] = scenes.map((s: any, i: number) => {
    const f = fm[i] ?? {};
    const start = Math.round((s.from / fps) * 10) / 10;
    if (f.start !== undefined && Math.abs(f.start - start) > 0.5)
      console.warn(`[chapters] ${slug}#${f.id}: frontmatter start=${f.start}s → 实际 ${start}s（frame ${s.from}）`);
    return {id: f.id ?? s.id, title: f.title ?? s.title, start, frame: s.from, fmStart: f.start};
  });
  return {chapters, duration: Math.round((total / fps) * 10) / 10, fps};
}

/** WebVTT 字幕：与 Remotion Main.tsx 相同的分配规则（按字数比例铺满真实音频时长） */
export function buildVtt(slug: string) {
  const {fps, scenes} = shotPlan(slug);
  const ts = (f: number) => {
    const s = f / fps;
    const hh = Math.floor(s / 3600), mm = Math.floor((s % 3600) / 60), ss = (s % 60).toFixed(3).padStart(6, '0');
    return `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}:${ss}`;
  };
  const n = (s: string) => s.replace(/[\s，。：？！,.:?!—]/g, '').length || 1;
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
    .map((slug) => {
      const meta = readJson(path.join(EP_DIR, slug, 'meta.json'));
      const mod = articles[`../../../episodes/${slug}/article.mdx`];
      const fm = mod?.frontmatter ?? {};
      const {chapters, duration, fps} = computeChapters(slug, fm.chapters);
      return {
        slug, ep: meta.ep ?? 0, title: meta.title ?? fm.title, summary: meta.summary ?? fm.summary,
        tags: meta.tags ?? [], date: meta.publishedAt, poster: meta.poster, video: meta.video,
        duration, chapters, fps, Content: mod?.default,
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
