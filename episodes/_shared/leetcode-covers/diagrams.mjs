/**
 * LeetCode cover diagram fragments. Each fragment uses the coordinate system
 * viewBox="0 0 600 400", has a transparent background, and stays inside
 * x=30..570 / y=30..370. Wrap the returned <g> in the caller's SVG.
 * Examples match each current episode's script/Cover; no runtime source reads.
 */
const C = Object.freeze({
  bg: '#0F172A', surface: '#16243A', edge: '#30435E',
  text: '#E5E7EB', gold: '#FFCC70', teal: '#56E4D3',
});
const FONT = 'Noto Sans CJK SC';
const escape = value => String(value).replace(/[&<>"']/g, ch => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;',
}[ch]));
const attrs = object => Object.entries(object)
  .filter(([, value]) => value !== undefined && value !== null)
  .map(([key, value]) => ` ${key}="${escape(value)}"`).join('');
const tag = (name, properties, children = '') => `<${name}${attrs(properties)}>${children}</${name}>`;
const text = (x, y, value, color = C.text, size = 28, extra = {}) => tag('text', {
  x, y, fill: color, 'font-size': size, 'font-weight': 600,
  'text-anchor': 'middle', ...extra,
}, escape(value));
const rect = (x, y, width, height, fill = C.surface, stroke = C.edge, extra = {}) => tag('rect', {
  x, y, width, height, rx: 12, fill, stroke, 'stroke-width': 2, ...extra,
});
const path = (d, color = C.edge, width = 3, extra = {}) => tag('path', {
  d, fill: 'none', stroke: color, 'stroke-width': width,
  'stroke-linecap': 'round', 'stroke-linejoin': 'round', ...extra,
});
const line = (x1, y1, x2, y2, color = C.edge, width = 3, extra = {}) => tag('line', {
  x1, y1, x2, y2, stroke: color, 'stroke-width': width,
  'stroke-linecap': 'round', ...extra,
});
const arrow = (x1, y1, x2, y2, color = C.teal, width = 3) => {
  const angle = Math.atan2(y2 - y1, x2 - x1);
  const back = 11, spread = 6;
  const ax = x2 - back * Math.cos(angle), ay = y2 - back * Math.sin(angle);
  return line(x1, y1, x2, y2, color, width) + path(
    `M ${ax + spread * Math.sin(angle)} ${ay - spread * Math.cos(angle)} L ${x2} ${y2} L ${ax - spread * Math.sin(angle)} ${ay + spread * Math.cos(angle)}`,
    color, width,
  );
};
const circle = (cx, cy, r, fill = C.surface, stroke = C.edge, extra = {}) => tag('circle', {
  cx, cy, r, fill, stroke, 'stroke-width': 3, ...extra,
});

function twoSum() {
  // The episode's second input: [3,8,3], target 6, distinct indices [0,2].
  return text(300, 72, '目标 6', C.gold, 32)
    + [3, 8, 3].map((value, i) => {
      const x = 150 + i * 150, color = i === 0 ? C.teal : i === 2 ? C.gold : C.edge;
      return rect(x - 48, 133, 96, 96, C.surface, color, { 'stroke-width': i === 1 ? 2 : 4 })
        + text(x, 198, value, i === 1 ? C.text : color, 46)
        + text(x, 268, `下标 ${i}`, C.text, 24);
    }).join('')
    + path('M 150 286 V 311 H 450 V 286', C.teal, 3)
    + text(300, 357, '两个 3，两个不同下标', C.teal, 27);
}

function longestSubstring() {
  // abcbadea: the second b at index 3 requires moving left from 0 to 2.
  const chars = [...'abcbadea'];
  return text(300, 65, '旧 b 离开，重复才消失', C.gold, 28)
    + path('M 144 132 Q 208 80 272 132', C.gold, 3)
    + rect(173, 139, 134, 88, 'none', C.teal, { rx: 14, 'stroke-width': 3 })
    + chars.map((char, i) => {
      const x = 80 + i * 64, color = i === 1 || i === 3 ? C.gold : i === 2 ? C.teal : C.edge;
      return tag('g', { opacity: i < 2 ? 0.6 : 1 },
        rect(x - 27, 153, 54, 60, C.surface, color)
        + text(x, 195, char, i === 1 || i === 3 ? C.gold : C.text, 34)
        + text(x, 260, i, C.text, 24));
    }).join('')
    + arrow(80, 294, 208, 294, C.gold, 4)
    + text(300, 350, '左边 0 → 2，保留连续 cb', C.teal, 27);
}

function containerMostWater() {
  // Same heights and selected pair as the current original cover: indices 2,6.
  const heights = [2, 3, 10, 5, 7, 8, 9], baseline = 309, unit = 19;
  const x = i => 80 + i * 72;
  return text(300, 65, '宽 4 × 短边 9', C.gold, 30)
    + rect(x(2), baseline - 9 * unit, x(6) - x(2), 9 * unit, C.teal, 'none', { rx: 0, opacity: 0.15 })
    + line(x(2), baseline - 9 * unit, x(6), baseline - 9 * unit, C.teal, 2, { 'stroke-dasharray': '7 7' })
    + line(52, baseline, 541, baseline, C.edge, 2)
    + heights.map((height, i) => {
      const color = i === 2 ? C.teal : i === 6 ? C.gold : C.edge;
      return line(x(i), baseline, x(i), baseline - height * unit, color, i === 2 || i === 6 ? 9 : 6)
        + text(x(i), baseline - height * unit - 20, height, i === 2 || i === 6 ? color : C.text, 25);
    }).join('')
    + path(`M ${x(2)} 326 V 337 H ${x(6)} V 326`, C.edge, 2)
    + text(368, 360, '面积 36', C.gold, 27);
}

function trappingRainWater() {
  // Prefix/suffix maxima solution, NOT a two-pointer illustration.
  // Heights [3,0,2,0,4,0,1]; each cell's water [0,3,1,3,0,1,0].
  const heights = [3, 0, 2, 0, 4, 0, 1], water = [0, 3, 1, 3, 0, 1, 0];
  const x = i => 80 + i * 72, baseline = 309, unit = 41;
  return text(300, 65, 'min(3, 4) − 2 = 1', C.gold, 30)
    + heights.map((height, i) => {
      const column = rect(x(i) - 25, baseline - height * unit, 50, height * unit,
        C.surface, C.edge, { rx: 1, 'stroke-width': height ? 2 : 0 });
      const fill = water[i] ? rect(x(i) - 25, baseline - (height + water[i]) * unit,
        50, water[i] * unit, C.teal, i === 2 ? C.gold : 'none',
        { rx: 0, opacity: i === 2 ? 0.75 : 0.3, 'stroke-width': i === 2 ? 3 : 0 }) : '';
      return column + fill + text(x(i), 350, height, C.text, 25);
    }).join('')
    + line(52, baseline, 541, baseline, C.edge, 2)
    + line(80, 186, 368, 186, C.teal, 2, { opacity: 0.5, 'stroke-dasharray': '6 6' })
    + line(368, 268, 512, 268, C.teal, 2, { opacity: 0.5, 'stroke-dasharray': '6 6' })
    + text(80, 150, '3', C.teal, 26)
    + text(368, 113, '4', C.gold, 26);
}

function permutations() {
  // One prefix's two complete result copies, not an alleged single swap step.
  const row = (cx, y, values, color) => values.map((value, i) => {
    const x = cx + (i - (values.length - 1) / 2) * 52;
    return rect(x - 23, y - 25, 46, 50, C.surface, color, { rx: 9 })
      + text(x, y + 12, value, C.text, 30);
  }).join('');
  return row(300, 70, [1], C.gold)
    + arrow(281, 100, 190, 138, C.edge)
    + arrow(319, 100, 410, 138, C.edge)
    + row(180, 172, [1, 2], C.teal)
    + row(420, 172, [1, 3], C.teal)
    + arrow(180, 207, 180, 244, C.teal)
    + arrow(420, 207, 420, 244, C.teal)
    + row(180, 278, [1, 2, 3], C.teal)
    + row(420, 278, [1, 3, 2], C.gold)
    + text(300, 359, '保存后，撤销再试', C.gold, 28);
}

function climbingStairs() {
  // The actual 4th/5th/6th stair counts. The routes are the last 1 or 2 steps.
  return path('M 80 330 V 270 H 230 V 220 H 380 V 170 H 530 V 330 Z', C.edge, 3,
      { fill: C.surface })
    + text(155, 246, '5 种', C.teal, 33)
    + text(305, 196, '8 种', C.teal, 33)
    + text(455, 146, '13 种', C.gold, 33)
    + text(155, 310, '第 4 阶', C.text, 24)
    + text(305, 260, '第 5 阶', C.text, 24)
    + text(455, 210, '第 6 阶', C.text, 24)
    + path('M 155 215 C 182 82 354 62 431 112', C.teal, 3)
    + path('M 421 102 L 431 112 L 417 114', C.teal, 3)
    + text(241, 74, '2 阶', C.teal, 25)
    + path('M 305 162 Q 351 127 417 126', C.gold, 3)
    + path('M 406 120 L 417 126 L 406 132', C.gold, 3)
    + text(352, 115, '1 阶', C.gold, 24)
    + text(300, 360, '5 + 8 = 13', C.gold, 30);
}

function numberOfIslands() {
  // Immutable grid and components from number-of-islands/src/lesson.json.
  const grid = [[1, 1, 0, 0, 0], [1, 1, 0, 0, 0], [0, 0, 2, 0, 0], [0, 0, 0, 3, 3]];
  const colors = ['', C.teal, C.gold, C.text], size = 64, sx = 140, sy = 63;
  const land = grid.flatMap((row, r) => row.map((id, c) => {
    if (!id) return '';
    const x = sx + c * size, y = sy + r * size, color = colors[id];
    let shape = rect(x + 5, y + 5, size - 10, size - 10, color, 'none', { rx: 12, opacity: 0.82 });
    if (row[c + 1] === id) shape += rect(x + size / 2, y + 5, size / 2 + 1, size - 10, color, 'none', { rx: 0, opacity: 0.82 });
    if (row[c - 1] === id) shape += rect(x - 1, y + 5, size / 2 + 1, size - 10, color, 'none', { rx: 0, opacity: 0.82 });
    if (grid[r + 1]?.[c] === id) shape += rect(x + 5, y + size / 2, size - 10, size / 2 + 1, color, 'none', { rx: 0, opacity: 0.82 });
    if (grid[r - 1]?.[c] === id) shape += rect(x + 5, y - 1, size - 10, size / 2 + 1, color, 'none', { rx: 0, opacity: 0.82 });
    return shape;
  })).join('');
  return rect(113, 43, 374, 300, C.surface, C.edge, { rx: 24 })
    + grid.flatMap((row, r) => row.map((id, c) => !id ? path(
      `M ${sx + c * size + 15} ${sy + r * size + 31} q 8 5 16 0 t 16 0`, C.edge, 2,
    ) : '')).join('')
    + land
    + text(300, 360, '四邻相连 · 3 座岛', C.teal, 26);
}

function reverseLinkedList() {
  // First reversal completed: node 1 -> None, saved nxt -> 2, 2 -> 3 -> None.
  const nodes = [160, 300, 440];
  return text(300, 73, '先保存 nxt → 2', C.teal, 29)
    + arrow(300, 100, 300, 170, C.teal, 3)
    + text(58, 230, '空', C.text, 25)
    + text(541, 230, '空', C.text, 25)
    + nodes.map((x, i) => rect(x - 42, 177, 84, 84, C.surface,
      i === 0 ? C.gold : i === 1 ? C.teal : C.edge, { 'stroke-width': 3 })
      + text(x, 234, i + 1, C.text, 40)).join('')
    + arrow(112, 219, 86, 219, C.gold, 3)
    + arrow(348, 219, 391, 219, C.teal, 3)
    + arrow(488, 219, 515, 219, C.teal, 3)
    + text(300, 346, '改掉连接，下一步入口还在', C.gold, 27);
}

function numberOfProvinces() {
  // Only AB, BC, DE are direct input edges. F is an isolated sixth city.
  const city = (x, y, label, color) => path(
    `M ${x - 24} ${y + 10} V ${y - 17} H ${x - 10} V ${y - 32} H ${x + 8} V ${y - 10} H ${x + 24} V ${y + 10} Z`,
    color, 2.5, { fill: C.surface },
  ) + line(x - 17, y - 7, x - 13, y - 7, color, 3)
    + line(x - 3, y - 20, x + 1, y - 20, color, 3)
    + text(x, y + 45, label, color, 28);
  return rect(65, 57, 354, 137, 'none', C.teal, { rx: 28, 'stroke-width': 2 })
    + rect(65, 227, 254, 105, 'none', C.gold, { rx: 28, 'stroke-width': 2 })
    + rect(430, 227, 114, 105, 'none', C.text, { rx: 28, 'stroke-width': 2 })
    + line(111, 130, 240, 101, C.teal, 3)
    + line(240, 101, 371, 130, C.teal, 3)
    + line(120, 268, 267, 268, C.gold, 3)
    + city(111, 130, 'A', C.teal) + city(240, 101, 'B', C.teal)
    + city(371, 130, 'C', C.teal) + city(120, 268, 'D', C.gold)
    + city(267, 268, 'E', C.gold) + city(487, 268, 'F', C.text)
    + text(489, 136, '3 组', C.gold, 35)
    + text(300, 360, '间接相连，也在同一组', C.teal, 26);
}

function binarySearch() {
  const values = [1, 3, 5, 7, 9, 11, 13, 15], x = i => 82 + i * 62;
  return text(300, 70, '目标 13', C.gold, 32)
    + rect(298, 145, 250, 95, 'none', C.teal, { rx: 13, 'stroke-width': 3 })
    + values.map((value, i) => tag('g', { opacity: i < 4 ? 0.5 : 1 },
      rect(x(i) - 25, 162, 50, 63, C.surface, i === 3 ? C.gold : C.edge)
      + text(x(i), 205, value, i === 3 ? C.gold : C.text, 28)
      + text(x(i), 269, i, C.text, 24))).join('')
    + path('M 57 285 V 300 H 293 V 285', C.gold, 3)
    + text(300, 352, '1 ≤ 3 ≤ 5 ≤ 7 < 13', C.gold, 29);
}

function dailyTemperatures() {
  // Original cover excerpt: days 3..7; no temperature scale is asserted.
  const values = [35, 31, 30, 32, 36], x = i => 90 + i * 105;
  const y = value => 150 + (36 - value) * 22;
  return text(300, 70, '等 4 天', C.teal, 32)
    + path('M 90 139 V 88 H 510 V 118', C.teal, 3)
    + path(values.map((value, i) => `${i ? 'L' : 'M'} ${x(i)} ${y(value)}`).join(' '), C.text, 3)
    + values.map((value, i) => {
      const color = i === 0 ? C.gold : i === 4 ? C.teal : C.text;
      return line(x(i), y(value) + 10, x(i), 309, C.edge, 12, { opacity: 0.45 })
        + circle(x(i), y(value), 8, C.surface, color)
        + text(x(i), y(value) - 21, value, color, 29)
        + text(x(i), 352, `第${i + 3}天`, C.text, 24);
    }).join('');
}

const DRAW = new Map([
  [1, twoSum], [3, longestSubstring], [11, containerMostWater],
  [42, trappingRainWater], [46, permutations], [70, climbingStairs],
  [200, numberOfIslands], [206, reverseLinkedList], [547, numberOfProvinces],
  [704, binarySearch], [739, dailyTemperatures],
]);

export const SUPPORTED_PROBLEMS = Object.freeze([...DRAW.keys()]);

/** Return an inner SVG <g>; caller supplies <svg viewBox="0 0 600 400">. */
export function diagram(problemNumber) {
  const number = Number(problemNumber), draw = DRAW.get(number);
  if (!draw) throw new RangeError(`Unsupported LeetCode problem: ${problemNumber}`);
  return tag('g', {
    'data-leetcode-diagram': number,
    'font-family': FONT,
    'shape-rendering': 'geometricPrecision',
    'text-rendering': 'optimizeLegibility',
  }, draw());
}
