// Check a perceptual invariant independently of the camera interpolation:
// the subject being enlarged must remain visible and approach the viewport
// center without first moving in the opposite direction.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {actualNavState, BRANCH_COLORS} from './branch-map/index.ts';
import {pageBg, pageInk} from '../../episodes/_shared/theme/pageTheme.ts';

assert.equal(BRANCH_COLORS.bg, pageBg);
assert.equal(BRANCH_COLORS.ink, pageInk);

const cases = [];
for (const x of [200, 960, 1720]) for (const y of [300, 450, 760]) {
  const spec = {title: 'Camera invariant', nodes: [{id: 'subject', label: 'Subject', x, y, w: 240}],
    edges: [], shots: {'in': {focus: 'subject', enter: {hold: 10, zoom: 60}},
      'out': {focus: 'subject', exit: {hold: 10, zoom: 60}}}};
  for (const shotId of ['in', 'out']) {
    let distance = shotId === 'in' ? Infinity : -Infinity;
    const samples = [];
    for (let frame = 0; frame < 120; frame++) {
      const state = actualNavState(spec, shotId, frame, 120);
      const {scale, tx, ty} = state.camera;
      const screenX = x * scale + tx, screenY = y * scale + ty;
      assert(screenX >= 0 && screenX <= 1920 && screenY >= 160 && screenY <= 900,
        `Subject left the visible canvas: ${x},${y} ${shotId} frame ${frame}`);
      const nextDistance = Math.hypot(screenX - 960, screenY - 450);
      assert(shotId === 'in' ? nextDistance <= distance + 1e-8 : nextDistance >= distance - 1e-8,
        `Subject reversed direction: ${x},${y} ${shotId} frame ${frame}`);
      distance = nextDistance;
      if ([0, 10, 25, 40, 55, 70, 119].includes(frame)) samples.push({frame, screenX, screenY, scale});
    }
    const first = actualNavState(spec, shotId, 0, 120);
    const last = actualNavState(spec, shotId, 119, 120);
    assert.equal(first.progress, shotId === 'in' ? 0 : 1);
    assert.equal(last.progress, shotId === 'in' ? 1 : 0);
    cases.push({x, y, shotId, framesChecked: 120, samples});
  }
}
console.log(JSON.stringify({scope: 'Subject visibility and monotonic approach/return; not visual quality scoring',
  navigatorSha256: createHash('sha256').update(readFileSync(new URL('./branch-map/index.ts', import.meta.url))).digest('hex'),
  canonicalPagePaletteMatches: true,
  cases: cases.length, framesChecked: cases.length * 120, passed: true, records: cases}, null, 2));
