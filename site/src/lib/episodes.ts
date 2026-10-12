import fs from 'node:fs';
import path from 'node:path';

export const REPO = 'https://github.com/linhongcun/video-studio';
const EP_DIR = path.resolve(process.cwd(), '../episodes');

const articles = import.meta.glob('../../../episodes/*/article.mdx', {eager: true}) as Record<string, any>;

export type Chapter = {id: string; title: string; start: number; frame: number};

// 章节起点 = 各 scene 之前所有镜头的实际帧数之和（timing.json 的 duration 优先，缺省用 storyboard 的 durationInFrames）
export function computeChapters(slug: string, fmChapters: any[] = []): {chapters: Chapter[]; durationSec: number} {
  const dir = path.join(EP_DIR, slug);
  const sb = JSON.parse(fs.readFileSync(path.join(dir, 'storyboard.json'), 'utf8'));
  const tPath = path.join(dir, 'remotion/src/timing.json');
  const timing = fs.existsSync(tPath) ? JSON.parse(fs.readFileSync(tPath, 'utf8')) : {};
  const fps = sb.meta?.fps ?? 30;
  let acc = 0;
  const scenes = sb.scenes.map((s: any) => {
    const frame = acc;
    for (const sh of s.shots) acc += timing[sh.id]?.duration ?? sh.durationInFrames;
    return {id: s.id, title: s.title, frame};
  });
  if (fmChapters.length && fmChapters.length !== scenes.length)
    console.warn(`[chapters] ${slug}: frontmatter 有 ${fmChapters.length} 章，storyboard 有 ${scenes.length} 个 scene，按顺序对齐`);
  const chapters = scenes.map((s: any, i: number) => {
    const fm = fmChapters[i] ?? {};
    const start = Math.round((s.frame / fps) * 10) / 10;
    if (fm.start !== undefined && Math.abs(fm.start - start) > 0.5)
      console.warn(`[chapters] ${slug}/${fm.id}: frontmatter start=${fm.start}s，按实际帧数校准为 ${start}s`);
    return {id: fm.id ?? s.id, title: fm.title ?? s.title, start, frame: s.frame};
  });
  return {chapters, durationSec: Math.round((acc / fps) * 10) / 10};
}

export function getEpisodes() {
  return fs
    .readdirSync(EP_DIR)
    .filter((slug) => fs.existsSync(path.join(EP_DIR, slug, 'meta.json')))
    .map((slug) => {
      const meta = JSON.parse(fs.readFileSync(path.join(EP_DIR, slug, 'meta.json'), 'utf8'));
      const mod = articles[`../../../episodes/${slug}/article.mdx`];
      const {chapters, durationSec} = computeChapters(slug, mod?.frontmatter?.chapters);
      return {slug, ...meta, title: meta.title ?? mod?.frontmatter?.title, Content: mod?.default, chapters, durationSec};
    })
    .sort((a, b) => String(b.publishedAt).localeCompare(String(a.publishedAt)));
}

export const fmtTime = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
