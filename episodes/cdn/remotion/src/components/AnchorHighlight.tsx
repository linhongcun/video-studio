// cdn-v1: BlockHighlight `anchor` — fit the box to a named region rendered by a sibling BrowserChrome
// ('shopLogo' | 'cardButtons' | 'shopPage' → [data-anchor] nodes). Storyboard x/y/w/h stay as the fallback.
import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {flushSync} from 'react-dom';
import {cancelRender, continueRender, delayRender} from 'remotion';
import {P} from '../theme';
import {colorToken, stateAt, UIProps} from './ui';
import {TextHighlight} from './TextHighlight';

const useBrowserLayoutEffect = typeof document === 'undefined' ? useEffect : useLayoutEffect;
export const ANCHOR_SELECTORS: Record<string, string> = {shopLogo: '[data-anchor="shopLogo"]', cardButtons: '[data-anchor="cardButton"]', shopPage: '[data-anchor="shopPage"]'};
const PAD = 8;

export const AnchorHighlight: React.FC<UIProps> = ({e: original, frame, siblings = []}) => {
  const e = stateAt(original, frame);
  const ref = useRef<HTMLDivElement>(null);
  type Box = {left: number; top: number; width: number; height: number};
  const [boxes, setBox] = useState<Box[] | null>(null);
  useBrowserLayoutEffect(() => {
    const layer = ref.current?.parentElement ?? null, scene = layer?.closest<HTMLElement>('[data-storyboard-scene]') ?? layer?.parentElement ?? null;
    const selector = ANCHOR_SELECTORS[e.anchor];
    if (!layer || !scene || !selector) {setBox(null); return;}
    const handle = delayRender(`Anchor highlight ${e.id}`);
    let cancelled = false;
    const measure = async () => {
      await document.fonts.ready;
      if (cancelled) return;
      const authored = layer.getBoundingClientRect(), scale = authored.width / parseFloat(getComputedStyle(layer).width);
      // Prefer browsers that overlap the authored fallback box (a scene can hold more than one BrowserChrome).
      const browsers = siblings.filter(s => s.component === 'BrowserChrome').map(s => scene.querySelector<HTMLElement>(`[data-element="${s.id}"]`)).filter(Boolean) as HTMLElement[];
      const overlaps = (r: DOMRect) => r.left < authored.right && r.right > authored.left && r.top < authored.bottom && r.bottom > authored.top;
      const pool = browsers.filter(b => overlaps(b.getBoundingClientRect()));
      const nodes = (pool.length ? pool : browsers).flatMap(b => Array.from(b.querySelectorAll<HTMLElement>(selector))).filter(n => n.getClientRects().length);
      if (!nodes.length || !(scale > 0)) {flushSync(() => setBox(null)); return;}
      // One box per anchored node (e.g. each card button), each padded outside the node.
      // Clip each node to the visible page viewport (a node can overflow a short browser), then keep the padded box inside the browser window.
      const clip = (n: HTMLElement) => {
        const r = n.getBoundingClientRect(), page = n.closest<HTMLElement>('[data-page]')?.getBoundingClientRect(), win = n.closest<HTMLElement>('[data-element]')?.getBoundingClientRect();
        const left = Math.max(r.left, page?.left ?? -Infinity), top = Math.max(r.top, page?.top ?? -Infinity), right = Math.min(r.right, page?.right ?? Infinity), bottom = Math.min(r.bottom, page?.bottom ?? Infinity);
        const box = {left: left - PAD * scale, top: top - PAD * scale, right: right + PAD * scale, bottom: bottom + PAD * scale};
        if (win && (r.bottom > bottom || r.right > right)) {box.right = Math.min(box.right, win.right); box.bottom = Math.min(box.bottom, win.bottom);}
        return {left: (box.left - authored.left) / scale, top: (box.top - authored.top) / scale, width: (box.right - box.left) / scale, height: (box.bottom - box.top) / scale};
      };
      flushSync(() => setBox(nodes.map(clip)));
    };
    void measure().catch(cancelRender).finally(() => continueRender(handle));
    return () => {cancelled = true; continueRender(handle);};
  }, [e.anchor, e.id, frame, siblings]);
  const color = colorToken(e.color) ?? P.primary;
  const style = (b?: Box): React.CSSProperties => ({position: 'absolute', left: b?.left ?? 0, top: b?.top ?? 0, width: b?.width ?? '100%', height: b?.height ?? '100%', pointerEvents: 'none', boxSizing: 'border-box', border: `4px solid ${color}`, borderRadius: 12, background: `${color}14`});
  return <div ref={ref} data-anchor-highlight={e.anchor} data-anchor-fitted={!!boxes?.length} style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
    {boxes?.length ? boxes.map((b, i) => <div key={i} data-anchor-box={i} style={style(b)} />) : <div data-anchor-fallback style={style()} />}
  </div>;
};
/** BlockHighlight: anchor-fitted when `anchor` is set, otherwise the EP.04 text-measured highlight. */
export const BlockHighlight: React.FC<UIProps> = props => props.e.anchor ? <AnchorHighlight {...props} /> : <TextHighlight {...props} />;
