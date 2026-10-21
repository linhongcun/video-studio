import {ShotElement} from '../storyboard';
import {stateAt} from './ui';

export type HighlightBox = {left: number; top: number; width: number; height: number};
type Rect = {left: number; top: number; right: number; bottom: number};
const overlaps = (a: Rect, b: Rect) => a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
const intersection = (a: Rect, b: Rect): Rect => ({left: Math.max(a.left, b.left), top: Math.max(a.top, b.top), right: Math.min(a.right, b.right), bottom: Math.min(a.bottom, b.bottom)});

/** Clamp padded boxes in screen space so camera and entrance scales are respected. */
export function clipHighlightBox(scene: HTMLElement, layer: HTMLElement, box: HighlightBox, siblings: ShotElement[], frame: number, target?: HTMLElement): HighlightBox {
  const authored = layer.getBoundingClientRect();
  const sx = authored.width / parseFloat(getComputedStyle(layer).width), sy = authored.height / parseFloat(getComputedStyle(layer).height);
  if (!(sx > 0 && sy > 0)) return box;
  const rect = {left: authored.left + box.left * sx, top: authored.top + box.top * sy, right: authored.left + (box.left + box.width) * sx, bottom: authored.top + (box.top + box.height) * sy};
  const active = siblings.map(s => stateAt(s, frame)).filter(s => frame >= (s.appearFrame ?? 0) && frame < (s.disappearFrame ?? Infinity) && s.state !== 'hidden');
  const node = (s: ShotElement) => Array.from(scene.querySelectorAll<HTMLElement>('[data-element]')).find(n => n.dataset.element === s.id);
  const panels = active.filter(s => s.component === 'DevToolsNetwork').map(s => ({e: s, node: node(s)})).filter(p => p.node);
  const center = target?.getBoundingClientRect() ?? rect;
  const cx = (center.left + center.right) / 2, cy = (center.top + center.bottom) / 2;
  const panel = panels.find(p => {const r = p.node!.getBoundingClientRect(); return cx >= r.left && cx <= r.right && cy >= r.top && cy <= r.bottom;});
  let viewport: Rect | undefined;
  if (panel) {
    const root = panel.node!.firstElementChild as HTMLElement;
    const r = root.getBoundingClientRect(), px = r.width / root.offsetWidth, py = r.height / root.offsetHeight;
    viewport = {left: r.left + root.clientLeft * px, top: r.top + root.clientTop * py, right: r.right - root.clientLeft * px, bottom: r.bottom - root.clientTop * py};
  } else {
    const browsers = active.filter(s => s.component === 'BrowserChrome').map(s => ({e: s, node: node(s)})).filter(b => b.node);
    const browser = browsers.find(b => target && b.node!.contains(target)) ?? browsers.find(b => overlaps(rect, b.node!.getBoundingClientRect()));
    const page = browser?.node!.querySelector<HTMLElement>('[data-page]');
    if (page) {
      viewport = page.getBoundingClientRect();
      for (const p of panels) {
        const r = p.node!.getBoundingClientRect();
        if (p.e.layout === 'docked' && overlaps(r, viewport) && cy < r.top) viewport = {left: viewport.left, top: viewport.top, right: viewport.right, bottom: Math.min(viewport.bottom, r.top)};
      }
    }
  }
  const clipped = viewport ? intersection(rect, viewport) : rect;
  return {left: (clipped.left - authored.left) / sx, top: (clipped.top - authored.top) / sy, width: Math.max(0, clipped.right - clipped.left) / sx, height: Math.max(0, clipped.bottom - clipped.top) / sy};
}
