/** 更新日志数据：构建时从 GitHub Releases 拉取；网络失败 / 限流时返回 null，页面降级为跳转 Releases 的链接，不让构建失败 */
export type Release = {tag: string; name: string; date: string; body: string; url: string; kind: '新增' | '修正' | '更新'; eps: number[]};
const API = 'https://api.github.com/repos/linhongcun/video-studio/releases?per_page=100';
let cache: Promise<Release[] | null> | null = null;

/** 只有新增了剧集的版本（x.y.0 且首次提到某期）标「新增」；其余 x.y.0 标「更新」，补丁版标「修正」 */
const kindOf = (tag: string, eps: number[]): Release['kind'] => {
  const m = tag.match(/^v?(\d+)\.(\d+)\.(\d+)/);
  if (!m) return '更新';
  if (m[3] !== '0') return '修正';
  return eps.length > 0 ? '新增' : '更新';
};

/** 解析「EP.21」「EP.2/4/5/7/14」「EP2、3，5」等写法，返回全部期号 */
export const parseEps = (text: string): number[] => {
  const out = new Set<number>();
  for (const m of text.matchAll(/EP\.?\s?((?:\d{1,3})(?:\s*[\/、,，]\s*\d{1,3})*)/gi))
    for (const n of m[1].split(/\s*[\/、,，]\s*/)) if (n) out.add(Number(n));
  return [...out].filter((n) => n > 0).sort((a, b) => a - b);
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
    const rels = list.filter((r) => !r.draft && !r.prerelease).map((r) => {
      const body = String(r.body ?? '').trim();
      const eps = parseEps(`${r.name ?? ''}\n${body}`);
      return {
        tag: r.tag_name, name: r.name || r.tag_name, url: r.html_url, body,
        // 北京时间日期
        date: new Date(Date.parse(r.published_at ?? r.created_at) + 8 * 3600e3).toISOString().slice(0, 16).replace('T', ' '),
        kind: '更新' as Release['kind'],
        eps,
      };
    });
    // 按时间从旧到新：某版本首次提到的期号才算「新增剧集」，避免只修旧期的 x.y.0 被标成新增
    const seen = new Set<number>();
    for (const r of [...rels].sort((a, b) => a.date.localeCompare(b.date))) {
      const fresh = r.eps.filter((n) => !seen.has(n));
      r.eps.forEach((n) => seen.add(n));
      r.kind = kindOf(r.tag, fresh);
    }
    return rels;
  } catch (err) {
    console.warn(`[changelog] 拉取 GitHub Releases 失败（${(err as Error).message}），降级为外链`);
    return null;
  }
}
export const getReleases = () => (cache ??= load());
