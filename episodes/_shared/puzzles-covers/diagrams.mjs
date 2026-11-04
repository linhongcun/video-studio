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

function twelveBalls() {
  // A legal first weighing: 1,2,3,4 versus 5,6,7,8; 9,10,11,12 stay outside.
  // All twelve balls have exactly the same appearance. No answer is revealed.
  const ball = (cx, cy, number) => tag('g', {
    'data-ball-number': number,
  }, circle(cx, cy, 23, C.surface, C.violet)
    + text(cx, cy + 8, number, 24, C.text, {'font-family': 'DejaVu Sans,sans-serif'}));
  return text(300, 43, '第一称：4 球 对 4 球', 29, C.violet)
    + rect(43, 72, 232, 80, C.surface, C.edge, {rx: 16})
    + rect(325, 72, 232, 80, C.surface, C.edge, {rx: 16})
    + [1, 2, 3, 4].map((n, i) => ball(77 + 55 * i, 112, n)).join('')
    + [5, 6, 7, 8].map((n, i) => ball(358 + 55 * i, 112, n)).join('')
    + text(300, 121, '对', 24, C.muted)
    + text(300, 194, '结果？', 29, C.coral)
    + text(300, 234, '左重 / 平衡 / 右重', 26, C.muted)
    + text(117, 293, '盘外', 25, C.muted)
    + [9, 10, 11, 12].map((n, i) => ball(227 + 55 * i, 285, n)).join('')
    + text(300, 338, '恰 1 球异常 · 无外部正常球', 24, C.muted);
}

function birthdayParadox() {
  // Exactly 23 people, in two rows of 12 + 11. The coral pair is an
  // illustrative collision; 50.73% describes the full ideal-model event.
  const glyph = (x, y, color) => circle(x, y - 14, 8, color)
    + path(`M ${x} ${y - 1} V ${y + 19} M ${x - 11} ${y + 7} H ${x + 11} M ${x} ${y + 19} L ${x - 9} ${y + 34} M ${x} ${y + 19} L ${x + 9} ${y + 34}`, color, 4);
  return text(300, 53, '23 人 · 比较月日', 29, C.violet)
    + Array.from({length: 23}, (_, i) => {
      const row = i < 12 ? 0 : 1;
      const col = row === 0 ? i : i - 12;
      return glyph(61 + col * 43 + (row ? 21.5 : 0), 109 + row * 78,
        i === 16 || i === 17 ? C.coral : C.violet);
    }).join('')
    + text(300, 285, '至少两人同生日：50.73%', 29, C.coral)
    + text(300, 326, '365 天 · 独立均匀模型', 24, C.muted);
}

function pirateGold() {
  // Five numbered identities and a shared, as-yet-undivided 100-coin pool.
  // No allocation or proposed vote is shown before the explanation.
  const pirate = (cx, number) => path(`M ${cx - 27} 102 L ${cx} 68 L ${cx + 27} 102 Z`, C.violet, 2, {fill: C.surface})
    + path(`M ${cx - 34} 104 H ${cx + 34}`, C.violet, 4)
    + circle(cx, 121, 17, C.violet)
    + path(`M ${cx} 144 V 170 M ${cx - 19} 156 H ${cx + 19} M ${cx} 170 L ${cx - 14} 192 M ${cx} 170 L ${cx + 14} 192`, C.violet, 5)
    + text(cx, 226, `${number}号`, 25, C.muted);
  return text(300, 44, '5 个海盗 · 100 枚金币', 29, C.violet)
    + [1,2,3,4,5].map((number, i) => pirate(100 + 100 * i, number)).join('')
    + circle(190, 274, 13, C.coral, C.coral)
    + circle(208, 271, 13, C.coral, C.coral)
    + circle(199, 254, 13, C.coral, C.coral)
    + text(331, 281, '待分：100 枚', 28, C.coral)
    + text(300, 329, '全员投票（含提案者） · 至少半数同意', 23, C.muted);
}

function hatParity() {
  // 1 is the first speaker at the queue tail, facing all 99 people ahead.
  // Representatives 2, 3 and 100 plus an explicit ellipsis are NOT all 100 people.
  // The first hat is unknown to its wearer; no spoken colour is assigned here.
  const wearer = (cx, number, hatColor, first = false) => {
    const ink = first ? C.coral : C.violet;
    const hat = first ? C.surface : hatColor;
    return circle(cx, 189, 18, C.surface, ink)
      + path(`M ${cx + 17} 185 L ${cx + 25} 192 L ${cx + 17} 196`, ink, 2.5)
      + path(`M ${cx} 211 V 244 M ${cx - 18} 223 H ${cx + 18} M ${cx} 244 L ${cx - 13} 265 M ${cx} 244 L ${cx + 13} 265`, ink, 4.5)
      + rect(cx - 24, 142, 48, 29, hat, first ? C.coral : C.muted,
        {rx: 5, 'stroke-width': 2.5, ...(first ? {'stroke-dasharray': '5 4'} : {})})
      + line(cx - 32, 173, cx + 32, 173, first ? C.coral : C.muted, 5)
      + (first ? text(cx, 166, '?', 24, C.coral, {'font-family': 'DejaVu Sans,sans-serif'}) : '')
      + text(cx, 298, `${number}号`, 23, first ? C.coral : C.muted);
  };
  return text(300, 43, '每人只说「黑」或「白」', 28, C.violet)
    + text(108, 93, '队尾 · 先答', 23, C.coral)
    + text(383, 93, '前方 99 人（省略示意）', 24, C.violet)
    + path('M 213 121 V 111 H 552 V 121', C.edge, 2.5)
    + wearer(108, 1, null, true)
    + wearer(248, 2, '#111018')
    + wearer(343, 3, C.text)
    + text(420, 208, '…', 43, C.muted)
    + wearer(517, 100, '#111018')
    + line(167, 192, 197, 192, C.coral, 3)
    + path('M 188 185 L 197 192 L 188 199', C.coral, 3)
    + text(300, 338, '只能看前方 · 能听见已答', 24, C.muted);
}

function prisonersLight() {
  // Only three representative identities are drawn; the ellipsis denotes the others.
  // Initial known-OFF state only: no counter assignment or signaling answer is shown.
  const prisoner = (cx, number) => tag('g', {
    'data-person-number': number, 'data-representative': 'true',
  }, circle(cx, 91, 10, C.violet)
    + path(`M ${cx} 106 V 132 M ${cx - 15} 116 H ${cx + 15} M ${cx} 132 L ${cx - 12} 151 M ${cx} 132 L ${cx + 12} 151`, C.violet, 4)
    + text(cx, 181, `${number}号`, 24, C.muted));
  return text(300, 43, '100人 · 每次仅1人', 29, C.violet)
    + prisoner(120, 1)
    + prisoner(240, 2)
    + tag('g', {'data-people-ellipsis': 'true'}, text(360, 125, '…', 43, C.muted))
    + prisoner(480, 100)
    + text(105, 260, '初始', 24, C.muted)
    + tag('g', {'data-light-state': 'off'},
      rect(190, 204, 220, 96, C.surface, C.violet, {rx: 16})
      + text(300, 232, '共享灯', 22, C.muted)
      + text(300, 280, '0 · 灭', 35, C.violet))
    + text(500, 260, '状态保留', 24, C.coral)
    + text(300, 338, '只靠开关灯 · 可保留个人记忆', 23, C.muted);
}

const DRAW = new Map([
  ['horse-racing', horseRacing], ['bridge-torch', bridgeTorch],
  ['water-jug', waterJug], ['monty-hall', montyHall], ['egg-drop', eggDrop],
  ['twelve-balls', twelveBalls],
  ['birthday-paradox', birthdayParadox],
  ['hat-parity', hatParity],
  ['pirate-gold', pirateGold],
  ['prisoners-light', prisonersLight],
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
