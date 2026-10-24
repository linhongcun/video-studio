import type {APIRoute} from 'astro';
import {getEpisodes, buildVtt} from '../../../lib/episodes';
export function getStaticPaths() {
  return getEpisodes({includeArchived: true}).map((e) => ({params: {slug: e.slug}}));
}
export const GET: APIRoute = ({params}) => new Response(buildVtt(params.slug!), {headers: {'Content-Type': 'text/vtt; charset=utf-8'}});
