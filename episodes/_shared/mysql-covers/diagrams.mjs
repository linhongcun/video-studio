/**
 * MySQL-series cover diagrams: inner SVG <g> fragments.
 * viewBox="0 0 600 360"; visible geometry x30..570 / y25..330.
 * Generic database cylinders are original geometry, not a product logo.
 * Internal records, requests and transaction modifications remain separate.
 * Current script.md / Cover.tsx examples are fixed here; no runtime I/O.
 */
const C = Object.freeze({
  bg: '#10211F', surface: '#172E2A', edge: '#34564F',
  text: '#EBF6F0', muted: '#9CB7AE', mint: '#78DFC0',
  amber: '#D8B778', cyan: '#7CCDDD',
});
const FONT = 'Noto Sans CJK SC';
const esc = value => String(value).replace(/[&<>"']/g, ch => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;',
}[ch]));
const attrs = object => Object.entries(object)
  .filter(([, value]) => value !== undefined && value !== null)
  .map(([key, value]) => ` ${key}="${esc(value)}"`).join('');
const tag = (name, properties, content = '') => `<${name}${attrs(properties)}>${content}</${name}>`;
const text = (x, y, value, size = 28, color = C.text, extra = {}) => tag('text', {
  x, y, 'font-size': size, fill: color, 'font-weight': 600,
  'text-anchor': 'middle', ...extra,
}, esc(value));
const rect = (x, y, width, height, fill = C.surface, stroke = C.edge, extra = {}) => tag('rect', {
  x, y, width, height, rx: 12, fill, stroke, 'stroke-width': 2.5, ...extra,
});
const path = (d, color = C.edge, width = 3, extra = {}) => tag('path', {
  d, fill: 'none', stroke: color, 'stroke-width': width,
  'stroke-linecap': 'round', 'stroke-linejoin': 'round', ...extra,
});
const line = (x1, y1, x2, y2, color = C.edge, width = 3, extra = {}) => tag('line', {
  x1, y1, x2, y2, stroke: color, 'stroke-width': width,
  'stroke-linecap': 'round', ...extra,
});
const arrow = (x1, y1, x2, y2, color = C.mint, width = 3, extra = {}) => {
  const angle = Math.atan2(y2 - y1, x2 - x1), back = 10, spread = 6;
  const ax = x2 - back * Math.cos(angle), ay = y2 - back * Math.sin(angle);
  return line(x1, y1, x2, y2, color, width, extra)
    + path(`M ${ax + spread * Math.sin(angle)} ${ay - spread * Math.cos(angle)} L ${x2} ${y2} L ${ax - spread * Math.sin(angle)} ${ay + spread * Math.cos(angle)}`,
      color, width);
};

function database(cx, top, width, height) {
  // Stable neutral identity. State is encoded in record text and request paths.
  const left = cx - width / 2, right = cx + width / 2, ry = 18;
  const bottom = top + height, topCenter = top + ry, bottomCenter = bottom - ry;
  return path(`M ${left} ${topCenter} V ${bottomCenter} C ${left} ${bottom} ${right} ${bottom} ${right} ${bottomCenter} V ${topCenter}`,
    C.edge, 3, { fill: C.surface })
    + tag('ellipse', { cx, cy: topCenter, rx: width / 2, ry,
      fill: C.surface, stroke: C.edge, 'stroke-width': 3 })
    + path(`M ${left} ${bottomCenter - 17} C ${left} ${bottomCenter + 1} ${right} ${bottomCenter + 1} ${right} ${bottomCenter - 17}`,
      C.edge, 2);
}

function dbIndex() {
  // The actual order 7042 remains in the same order table. The index-to-record
  // link is logical locating information, not a physical row/disk address.
  // No tree, fixed comparison count, uniqueness or performance claim is added.
  return text(300, 62, '先定位，再读取', 30, C.mint)
    + text(139, 143, '索引', 28, C.muted)
    + rect(60, 166, 158, 71, C.surface, C.mint, { 'stroke-width': 3 })
    + text(139, 214, '7042', 38, C.mint)
    + arrow(231, 203, 307, 203, C.mint, 3)
    + text(435, 110, 'MySQL', 28, C.muted)
    + database(435, 128, 230, 160)
    + text(435, 202, '订单记录', 26, C.text)
    + text(435, 261, '7042', 34, C.mint)
    + text(300, 321, '逻辑定位信息 → 对应记录', 26, C.muted);
}

function dbTransaction() {
  // Two changes INSIDE ONE database and ONE transaction: transfer 200.
  // Initial 1000/500, successful committed result 800/700. The arrows describe
  // pending modifications, not another-session visibility or physical layers.
  return text(300, 62, '同一 MySQL 实例 · 一笔事务', 29, C.mint)
    + database(300, 88, 480, 188)
    + rect(94, 139, 180, 106, C.bg, C.edge, { rx: 10 })
    + rect(326, 139, 180, 106, C.bg, C.edge, { rx: 10 })
    + text(184, 171, '你的账户', 26, C.muted)
    + text(416, 171, '对方账户', 26, C.muted)
    + text(184, 228, '1000 → 800', 29, C.amber)
    + text(416, 228, '500 → 700', 29, C.amber)
    + text(300, 209, '+', 30, C.mint)
    + path('M 184 251 V 259 H 416 V 251', C.mint, 2.5)
    + text(300, 321, '两处修改，一起提交或回滚', 26, C.mint);
}

function dbLock() {
  // Same existing goods record 7042, stock 1, both requests buy one.
  // This example has A acquire first; it makes no FIFO/first-arrival promise.
  // B has NO result while waiting and must re-check the fresh 0 after A commits.
  return text(300, 62, '商品 7042 · 已存在主键记录', 28, C.muted)
    + text(300, 113, 'MySQL', 27, C.muted)
    + database(300, 128, 180, 147)
    + text(300, 198, '库存', 26, C.text)
    + text(300, 250, '1 → 0', 35, C.mint)
    + rect(34, 161, 140, 66, C.surface, C.mint, { rx: 11 })
    + text(104, 205, '甲先加锁', 28, C.mint)
    + arrow(181, 194, 205, 194, C.mint, 3)
    + rect(426, 161, 140, 66, C.surface, C.amber, { rx: 11 })
    + text(496, 205, '乙先等待', 28, C.amber)
    + line(420, 194, 402, 194, C.amber, 3)
    + line(399, 179, 399, 211, C.amber, 3)
    + text(300, 321, '甲提交后：乙读 0，再检查 → 缺货', 26, C.muted);
}

function dbReplication() {
  // Single-primary ASYNCHRONOUS teaching example, same user 7042.
  // Primary has committed 青禾 while replica still exposes 阿青.
  // One forward pending-copy route only: no replica ACK or synchronous barrier.
  return text(300, 62, 'MySQL 异步复制 · 用户7042', 29, C.muted)
    + text(155, 111, '主库', 28, C.text)
    + text(445, 111, '从库', 28, C.text)
    + database(155, 133, 180, 137)
    + database(445, 133, 180, 137)
    + text(155, 224, '青禾', 38, C.mint)
    + text(445, 224, '阿青', 38, C.amber)
    + text(300, 173, '待应用', 26, C.cyan)
    + arrow(254, 224, 346, 224, C.cyan, 3, { 'stroke-dasharray': '6 7' })
    + text(300, 321, '主库已提交 · 从库尚未应用', 26, C.muted);
}

const DRAW = new Map([
  ['db-index', dbIndex], ['db-transaction', dbTransaction],
  ['db-lock', dbLock], ['db-replication', dbReplication],
]);
export const SUPPORTED_SLUGS = Object.freeze([...DRAW.keys()]);

/** Return an inner <g> for a caller-supplied SVG, with no IDs/external assets. */
export function diagram(slug) {
  const draw = DRAW.get(slug);
  if (!draw) throw new RangeError(`Unsupported database slug: ${slug}`);
  return tag('g', {
    'data-database-diagram': slug, 'font-family': FONT,
    'shape-rendering': 'geometricPrecision', 'text-rendering': 'optimizeLegibility',
  }, draw());
}
