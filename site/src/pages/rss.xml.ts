import rss from '@astrojs/rss';
import type {APIContext} from 'astro';
import {getEpisodes, epLabel, fmtTime, asset} from '../lib/episodes';

/** 新片订阅：pubDate 取 meta.json publishedAt（北京时间当天 00:00） */
export function GET(ctx: APIContext) {
  const site = new URL(import.meta.env.BASE_URL, ctx.site).href;
  return rss({
    title: 'Video Studio · IT小村',
    description: '用代码拍科普：互联网后端与分布式技术动画短片 + 图文讲解',
    site,
    trailingSlash: true,
    customData: '<language>zh-CN</language>',
    items: getEpisodes().map((e) => ({
      title: `${epLabel(e)} ${e.title}`,
      link: `episodes/${e.slug}/`,
      pubDate: new Date(`${e.date}T00:00:00+08:00`),
      description: `${e.description ?? e.summary}（视频 ${fmtTime(e.duration)}）`,
      categories: e.tags,
    })),
  });
}
