/** 更新日志数据：构建时从 GitHub Releases 拉取；网络失败 / 限流时返回 null，页面降级为跳转 Releases 的链接，不让构建失败 */
import fs from 'node:fs';
import path from 'node:path';

export type Release = {tag: string; name: string; date: string; body: string; url: string; kind: '新增' | '修正' | '更新'; eps: number[]};
const API = 'https://api.github.com/repos/linhongcun/video-studio/releases?per_page=100';
let cache: Promise<Release[] | null> | null = null;

/** 各期 meta.json 的 firstRelease → 该 tag 标「新增」并链接这些期 */
function firstReleaseMap(): Map<string, number[]> {
  const dir = path.resolve(process.cwd(), '../episodes');
  const map = new Map<string, number[]>();
  if (!fs.existsSync(dir)) return map;
  for (const slug of fs.readdirSync(dir)) {
    const f = path.join(dir, slug, 'meta.json');
    if (!fs.existsSync(f)) continue;
    try {
      const m = JSON.parse(fs.readFileSync(f, 'utf8'));
      const tag = m.firstRelease != null ? String(m.firstRelease) : '';
      const ep = Number(m.ep);
      if (!tag || !ep) continue;
      const list = map.get(tag) ?? [];
      list.push(ep);
      map.set(tag, list);
    } catch { /* skip bad meta */ }
  }
  for (const [k, v] of map) map.set(k, [...new Set(v)].sort((a, b) => a - b));
  return map;
}

/** 补丁版 → 「修正」；有期数以本 tag 为首发 → 「新增」；其余 → 「更新」 */
const kindOf = (tag: string, debut: number[]): Release['kind'] => {
  const m = tag.match(/^v?(\d+)\.(\d+)\.(\d+)/);
  if (!m) return '更新';
  if (m[3] !== '0') return '修正';
  return debut.length > 0 ? '新增' : '更新';
};

const CN: Record<string, number> = {零: 0, 〇: 0, 一: 1, 二: 2, 两: 2, 三: 3, 四: 4, 五: 5, 六: 6, 七: 7, 八: 8, 九: 9};

/** 中文数字 → 整数（1–99）；阿拉伯数字原样 */
function cnToInt(s: string): number | null {
  if (/^\d{1,3}$/.test(s)) return Number(s);
  if (s === '十') return 10;
  const m = s.match(/^([一二三四五六七八九])?十([一二三四五六七八九])?$/);
  if (m) return (m[1] ? CN[m[1]] : 1) * 10 + (m[2] ? CN[m[2]] : 0);
  if (s.length === 1 && CN[s] != null && CN[s] > 0) return CN[s];
  return null;
}

/** 解析「EP.21」「EP.2/4/5/7/14」「EP1–12」「第十一期」「第二十一期」等，返回全部期号 */
export const parseEps = (text: string): number[] => {
  const out = new Set<number>();
  // 区间：EP1–12 / EP.1-12 / EP.1—12（先于单期，避免只吃到左端）
  for (const m of text.matchAll(/EP\.?\s?(\d{1,3})\s*[–—\-]\s*(\d{1,3})/gi)) {
    let a = Number(m[1]), b = Number(m[2]);
    if (a > b) [a, b] = [b, a];
    if (b - a > 200) continue; // 防误伤
    for (let i = a; i <= b; i++) out.add(i);
  }
  // 列表：EP.21 / EP.2/4/5/7/14 / EP2、3，5
  for (const m of text.matchAll(/EP\.?\s?((?:\d{1,3})(?:\s*[\/、,，]\s*\d{1,3})*)/gi))
    for (const n of m[1].split(/\s*[\/、,，]\s*/)) if (n) out.add(Number(n));
  // 第N期（阿拉伯或中文数字）
  for (const m of text.matchAll(/第\s*([0-9一二三四五六七八九十两〇零]+)\s*期/g)) {
    const n = cnToInt(m[1]);
    if (n && n > 0) out.add(n);
  }
  return [...out].filter((n) => n > 0 && n < 1000).sort((a, b) => a - b);
};

async function load(): Promise<Release[] | null> {
  if (process.env.SKIP_CHANGELOG === '1') return null;
  try {
    const headers: Record<string, string> = {Accept: 'application/vnd.github+json', 'User-Agent': 'video-studio-site'};
    const token = process.env.GITHUB_TOKEN;
    if (token) headers.Authorization = `Bearer ${token}`;
    const res = await fetch(API, {headers, signal: AbortSignal.timeout(8000)});
    if (!res.ok) { console.warn(`[changelog] GitHub Releases ${res.status}，降级为外链`); return null; }
    const list = (await res.json()) as any[];
    const debutByTag = firstReleaseMap();
    const rels: Release[] = list.filter((r) => !r.draft && !r.prerelease).map((r) => {
      const body = String(r.body ?? '').trim();
      const tag = String(r.tag_name);
      const debut = debutByTag.get(tag) ?? [];
      const kind = kindOf(tag, debut);
      // 新增：链首发期；修正/更新：链正文提到的期
      const eps = kind === '新增' ? debut : parseEps(`${r.name ?? ''}\n${body}`);
      return {
        tag, name: r.name || r.tag_name, url: r.html_url, body, kind, eps,
        // 北京时间日期
        date: new Date(Date.parse(r.published_at ?? r.created_at) + 8 * 3600e3).toISOString().slice(0, 16).replace('T', ' '),
      };
    });
    return rels;
  } catch (err) {
    console.warn(`[changelog] 拉取 GitHub Releases 失败（${(err as Error).message}），降级为外链`);
    return null;
  }
}
export const getReleases = () => (cache ??= load());
