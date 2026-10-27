/**
 * Sparse, deterministic P01–P05 topic diagrams.
 * Returned markup is an inner <g> for viewBox="0 0 600 360".
 * Transparent background; visible geometry x30..570 / y25..335.
 * Examples and rules come from each current episode's script.md and Cover.tsx.
 */
const C = Object.freeze({
  bg: '#171326', surface: '#241D37', edge: '#514166', text: '#F4EEF9',
  muted: '#B6ABC9', violet: '#C7A4FF', coral: '#FF9E8B', teal: '#79D7C6',
});
const FONT = 'Noto Sans CJK SC';
const esc = value => String(value).replace(/[&<>"']/g, ch => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;',
}[ch]));
const attr = object => Object.entries(object)
  .filter(([, value]) => value !== undefined && value !== null)
  .map(([key, value]) => ` ${key}="${esc(value)}"`).join('');
const tag = (name, attributes, content = '') => `<${name}${attr(attributes)}>${content}</${name}>`;
const text = (x, y, value, size = 28, color = C.text, extra = {}) => tag('text', {
  x, y, 'font-size': size, fill: color, 'text-anchor': 'middle',
  'font-weight': 600, ...extra,
}, esc(value));
const rect = (x, y, width, height, fill = C.surface, stroke = C.edge, extra = {}) => tag('rect', {
  x, y, width, height, rx: 10, fill, stroke, 'stroke-width': 2.5, ...extra,
});
const path = (d, color = C.edge, width = 3, extra = {}) => tag('path', {
  d, fill: 'none', stroke: color, 'stroke-width': width,
  'stroke-linecap': 'round', 'stroke-linejoin': 'round', ...extra,
});
const line = (x1, y1, x2, y2, color = C.edge, width = 3, extra = {}) => tag('line', {
  x1, y1, x2, y2, stroke: color, 'stroke-width': width,
  'stroke-linecap': 'round', ...extra,
});
const circle = (cx, cy, r, fill, stroke = 'none', extra = {}) => tag('circle', {
  cx, cy, r, fill, stroke, 'stroke-width': 2.5, ...extra,
});

function horse(x, y, color) {
  // A small flat horse glyph, with four legs, neck, head and tail.
  const body = tag('ellipse', { cx: 0, cy: 0, rx: 25, ry: 11, fill: color });
  return tag('g', { transform: `translate(${x} ${y}) scale(.64)` },
    body
      + path('M 13 -7 L 22 -29 L 34 -25 L 29 -6 Z', color, 2, { fill: color })
      + path('M 30 -25 L 46 -22 L 49 -14 L 38 -10 L 27 -17 Z', color, 2, { fill: color })
      + path('M 25 -27 L 25 -35 L 33 -28 Z', color, 2, { fill: color })
      + path('M -16 6 L -25 23 M -8 8 L -1 23 M 12 7 L 20 22 M 20 4 L 32 16', color, 5)
      + path('M -24 -3 Q -37 -10 -39 3', color, 4)
      + circle(39, -19, 1.8, C.bg));
}

function horseRacing() {
  // Five lanes show ONE representative heat, not the entire set of 25 horses.
  const positions = [185, 265, 320, 235, 375];
  return text(300, 62, '25 匹 · 分 5 组', 30, C.violet)
    + Array.from({ length: 5 }, (_, i) => {
      const y = 107 + i * 39;
      return line(77, y + 20, 535, y + 20, C.edge, 2)
        + text(55, y + 8, i + 1, 25, C.muted)
        + horse(positions[i], y, i === 2 ? C.coral : C.violet);
    }).join('')
    + line(515, 82, 515, 289, C.muted, 2, { 'stroke-dasharray': '8 8' })
    + text(300, 326, '每场最多 5 匹 · 不能计时', 26, C.coral);
}

function person(x, y, color, minutes) {
  return circle(x, y - 18, 9, color)
    + path(`M ${x} ${y - 5} V ${y + 17} M ${x - 13} ${y + 7} L ${x} ${y} L ${x + 13} ${y + 7} M ${x} ${y + 17} L ${x - 11} ${y + 35} M ${x} ${y + 17} L ${x + 11} ${y + 35}`, color, 4)
    + text(x, y + 66, `${minutes}分钟`, 25, color);
}

function bridgeTorch() {
  // Rule-establishing initial state: all four people and the ONLY torch left.
  // The labels are individual one-way durations, never person IDs.
  return text(300, 62, '每次最多两人', 30, C.violet)
    + rect(44, 87, 222, 214, C.surface, C.edge, { rx: 18 })
    + rect(468, 87, 88, 214, C.surface, C.edge, { rx: 18 })
    + path('M 266 166 Q 367 192 468 166 M 266 222 Q 367 248 468 222', C.muted, 3)
    + [284, 325, 366, 407, 448].map(x => line(x, 182, x, 235, C.edge, 3)).join('')
    + line(272, 144, 272, 243, C.violet, 3)
    + line(462, 144, 462, 243, C.violet, 3)
    + person(102, 115, C.violet, 1)
    + person(201, 115, C.violet, 2)
    + person(102, 212, C.coral, 5)
    + person(201, 212, C.coral, 10)
    + rect(242, 113, 12, 30, C.coral, C.coral, { rx: 3, 'stroke-width': 1 })
    + path('M 238 109 H 258 L 254 101 H 242 Z', C.coral, 2, { fill: C.coral })
    + path('M 240 96 L 233 86 M 248 95 V 83 M 256 96 L 263 86', C.coral, 2)
    + text(300, 326, '一把手电，往返都要带', 26, C.coral);
}

function waterJug() {
  // Equal-sized abstract object glyphs intentionally encode NO capacity ratio.
  // Initial empty state; no calibrated height, current quantity or 4L stop line.
  const vessel = (cx, capacity, color) => text(cx, 109, `容量 ${capacity} 升`, 28, color)
    + path(`M ${cx - 69} 137 V 249 Q ${cx - 69} 265 ${cx - 53} 265 H ${cx + 53} Q ${cx + 69} 265 ${cx + 69} 249 V 137`, color, 4,
      { fill: C.surface })
    + text(cx, 218, '初始空', 26, C.muted);
  return text(300, 62, '目标：大壶留下 4 升', 30, C.coral)
    + vessel(175, 3, C.violet)
    + vessel(425, 5, C.teal)
    + text(300, 326, '无刻度 · 装满、倒空、互倒', 26, C.muted);
}

function montyHall() {
  // Same pre-decision state as script 03: initially pick 1; host opens empty 3.
  // Current production says EMPTY, not a goat; door 2's prize stays concealed.
  const door = (x, number, label, color, open = false) => rect(x, 120, 130, 129,
    open ? C.bg : C.surface, color, { rx: 8, 'stroke-width': 3 })
    + (open ? path(`M ${x} 120 L ${x + 32} 137 V 235 L ${x} 249 Z`, C.muted, 2, { fill: C.surface }) : '')
    + text(x + (open ? 79 : 65), 205, open ? '空' : number, open ? 31 : 42, color)
    + text(x + 65, 283, label, 25, color);
  return text(300, 58, '主持知情 · 避开奖品', 27, C.violet)
    + text(300, 91, '必开未选空门 · 每局可换', 26, C.muted)
    + door(70, 1, '初选 1', C.violet)
    + door(235, 2, '未开 2', C.coral)
    + door(400, 3, '已开 3', C.muted, true)
    + text(300, 326, '坚持 1，还是换 2？', 25, C.muted);
}

function egg(cx, cy, number) {
  return path(`M ${cx} ${cy - 45} C ${cx - 16} ${cy - 45} ${cx - 31} ${cy - 12} ${cx - 31} ${cy + 8} C ${cx - 31} ${cy + 47} ${cx + 31} ${cy + 47} ${cx + 31} ${cy + 8} C ${cx + 31} ${cy - 12} ${cx + 16} ${cy - 45} ${cx} ${cy - 45} Z`, C.violet, 3,
    { fill: C.surface })
    + text(cx, cy + 83, `蛋 ${number}`, 25, C.muted);
}

function eggDrop() {
  // Abstract 100-storey building, with omitted middle floors made explicit.
  // 14 -> 27 -> 39 is a PLAN; advance only when the previous test did not break.
  return text(300, 62, '没碎，再向上试', 30, C.violet)
    + text(139, 114, '2 枚鸡蛋', 28, C.violet)
    + egg(99, 193, 1) + egg(181, 193, 2)
    + text(423, 114, '100 层', 30, C.coral)
    + rect(351, 132, 144, 159, C.surface, C.edge, { rx: 8, 'stroke-width': 3 })
    + [370, 409, 448].map(x => rect(x, 149, 26, 21, C.edge, 'none', { rx: 3 })).join('')
    + text(423, 225, '⋮', 39, C.muted)
    + [370, 409, 448].map(x => rect(x, 252, 26, 21, C.edge, 'none', { rx: 3 })).join('')
    + text(300, 326, '计划：14 → 27 → 39…', 27, C.coral);
}

const DRAW = new Map([
  ['horse-racing', horseRacing], ['bridge-torch', bridgeTorch],
  ['water-jug', waterJug], ['monty-hall', montyHall], ['egg-drop', eggDrop],
]);
export const SUPPORTED_SLUGS = Object.freeze([...DRAW.keys()]);

/** Return the inner SVG <g>, with no IDs or external references. */
export function diagram(slug) {
  const draw = DRAW.get(slug);
  if (!draw) throw new RangeError(`Unsupported puzzle slug: ${slug}`);
  return tag('g', {
    'data-puzzle-diagram': slug, 'font-family': FONT,
    'shape-rendering': 'geometricPrecision', 'text-rendering': 'optimizeLegibility',
  }, draw());
}
