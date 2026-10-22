// cdn-v1: BlockHighlight `anchor` — fit the box to a named region rendered by a sibling BrowserChrome or DevToolsNetwork
// ('shopLogo' | 'cardButtons' | 'shopPage' → [data-anchor] nodes). Storyboard x/y/w/h stay as the fallback.
import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {flushSync} from 'react-dom';
import {cancelRender, continueRender, delayRender} from 'remotion';
import {P} from '../theme';
import {colorToken, stateAt, UIProps} from './ui';
import {TextHighlight} from './TextHighlight';
import {clipHighlightBox} from './highlightClip';

const useBrowserLayoutEffect = typeof document === 'undefined' ? useEffect : useLayoutEffect;
export const ANCHOR_SELECTORS: Record<string, string> = {shopLogo: '[data-anchor="shopLogo"]', cardButtons: '[data-anchor="cardButton"]', shopPage: '[data-anchor="shopPage"]', itemName: '[data-anchor="itemName"]', itemPrice: '[data-anchor="itemPrice"]', itemStock: '[data-anchor="itemStock"]', orderRow: '[data-anchor="orderRow"]', adminInput: '[data-anchor="adminInput"]', adminSaved: '[data-anchor="adminSaved"]', orderHeadline: '[data-anchor="orderHeadline"]', orderStatusValue: '[data-anchor="orderStatusValue"]', ticketHeadline: '[data-anchor="ticketHeadline"]', ticketButton: '[data-anchor="ticketButton"]', payAmount: '[data-anchor="payAmount"]', billRow: '[data-anchor="billRow"]', billAmount: '[data-anchor="billAmount"]', devtoolsRow: '[data-anchor="devtoolsRow"]'};
const PAD = 8;

export const AnchorHighlight: React.FC<UIProps> = ({e: original, frame, siblings = []}) => {
  const e = stateAt(original, frame);
  const ref = useRef<HTMLDivElement>(null);
  type Box = {left: number; top: number; width: number; height: number};
  const [fallback, setFallback] = useState<Box | null>(null);
  const [boxes, setBox] = useState<Box[] | null>(null);
  useBrowserLayoutEffect(() => {
    const layer = ref.current?.parentElement ?? null, scene = layer?.closest<HTMLElement>('[data-storyboard-scene], [data-cover-scene]') ?? layer?.parentElement ?? null;
    const selector = ANCHOR_SELECTORS[e.anchor];
    if (!layer || !scene) {setBox(null); return;}
    const handle = delayRender(`Anchor highlight ${e.id}`);
    let cancelled = false;
    const measure = async () => {
      await document.fonts.ready;
      if (cancelled) return;
      const authored = layer.getBoundingClientRect(), scale = authored.width / parseFloat(getComputedStyle(layer).width), scaleY = authored.height / parseFloat(getComputedStyle(layer).height);
      flushSync(() => setFallback(clipHighlightBox(scene, layer, {left: 0, top: 0, width: parseFloat(getComputedStyle(layer).width), height: parseFloat(getComputedStyle(layer).height)}, siblings, frame)));
      if (!selector) {flushSync(() => setBox(null)); return;}
      // Prefer containers that overlap the fallback box; network rows live in a sibling panel.
      const containers = siblings.map(s => stateAt(s, frame)).filter(s => s.component === (e.anchor === 'devtoolsRow' ? 'DevToolsNetwork' : 'BrowserChrome') && frame >= (s.appearFrame ?? 0) && frame < (s.disappearFrame ?? Infinity) && s.state !== 'hidden').map(s => scene.querySelector<HTMLElement>(`[data-element="${s.id}"]`)).filter(Boolean) as HTMLElement[];
      const overlaps = (r: DOMRect) => r.left < authored.right && r.right > authored.left && r.top < authored.bottom && r.bottom > authored.top;
      const pool = containers.filter(b => overlaps(b.getBoundingClientRect()));
      const nodes = (pool.length ? pool : containers).flatMap(b => Array.from(b.querySelectorAll<HTMLElement>(selector))).filter(n => n.getClientRects().length);
      if (!nodes.length || !(scale > 0 && scaleY > 0)) {flushSync(() => setBox(null)); return;}
      // One box per anchored node (e.g. each card button), each padded outside the node.
      flushSync(() => setBox(nodes.map(n => {
        const r = n.getBoundingClientRect();
        return clipHighlightBox(scene, layer, {left: (r.left - authored.left) / scale - PAD, top: (r.top - authored.top) / scaleY - PAD, width: r.width / scale + PAD * 2, height: r.height / scaleY + PAD * 2}, siblings, frame, n);
      })));
    };
    void measure().catch(cancelRender).finally(() => continueRender(handle));
    return () => {cancelled = true; continueRender(handle);};
  }, [e.anchor, e.id, frame, siblings]);
  const color = colorToken(e.color) ?? P.primary;
  const style = (b?: Box): React.CSSProperties => ({display: b && (b.width <= 0 || b.height <= 0) ? 'none' : undefined, position: 'absolute', left: b?.left ?? 0, top: b?.top ?? 0, width: b?.width ?? '100%', height: b?.height ?? '100%', pointerEvents: 'none', boxSizing: 'border-box', border: `4px solid ${color}`, borderRadius: 12, background: `${color}14`});
  return <div ref={ref} data-anchor-highlight={e.anchor} data-anchor-fitted={!!boxes?.length} style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
    {boxes?.length ? boxes.map((b, i) => <div key={i} data-anchor-box={i} style={style(b)} />) : <div data-anchor-fallback style={style(fallback ?? undefined)} />}
  </div>;
};
/** BlockHighlight: anchor-fitted when `anchor` is set, otherwise the EP.04 text-measured highlight. */
export const BlockHighlight: React.FC<UIProps> = props => props.e.anchor ? <AnchorHighlight {...props} /> : <TextHighlight {...props} />;
