import rss from '@astrojs/rss';
import type {APIContext} from 'astro';
import {getEpisodes, epLabel, fmtTime, dateIso} from '../lib/episodes';

/** 新片订阅：pubDate 取 meta.json publishedAt（北京时间当天 00:00） */
export function GET(ctx: APIContext) {
  const site = new URL(import.meta.env.BASE_URL, ctx.site).href;
  return rss({
    title: 'IT小村 · 技术可视化',
    description: '用技术动画短片与图文讲解，理解高并发、高可用、高性能、计算机网络、分布式、MySQL、消息队列、Agent 开发、算法与设计模式。',
    site,
    trailingSlash: true,
    customData: '<language>zh-CN</language>',
    items: getEpisodes().filter((e) => !!e.publishedAt).map((e) => ({
      title: `${epLabel(e)} ${e.title}`,
      link: `episodes/${e.slug}/`,
      pubDate: new Date(dateIso(e.publishedAt!)),
      description: `${e.description ?? e.summary}（视频 ${fmtTime(e.duration)}）`,
      categories: e.tags,
    })),
  });
}
