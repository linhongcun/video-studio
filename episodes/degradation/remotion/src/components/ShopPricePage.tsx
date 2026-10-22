import React from 'react';
import {P} from '../theme';
import {browserPageBox} from './browserLayout';
import {Copy, stateAt, UIProps} from './ui';

// EP.14 degradation-v1 (knoll-props 3e5cbce8 §1): one page type, three views (search / checkout / success).
// Every box, string, font size and state frame comes from the storyboard; nothing here is episode copy.
const PAGE_BG = '#FFFFFF';
const INK = P.panel;
const COUPON_GREEN = '#15803D';        // knoll-props §1.1: coupon text colour
const HIGHLIGHT = '#FEF3C7';           // 行底浅黄
const HIGHLIGHT_EDGE = '#F59E0B';
type Ripple = {id: string; bornFrame: number; center: string; r0: number; r1: number; growFrames: number; holdOpacity: number; color: string};
type Coupon = {visible: boolean; applied: boolean; text: string; highlighted: boolean};
type Item = {text: string; button?: string; highlighted?: boolean; background?: boolean};

/** Box keys drawn by each view; a ripple only shows while its centre box is on screen. */
const viewBoxes = (view: string, items: Item[]) => view === 'search'
  ? ['query', ...items.flatMap((_, i) => [`item${i}`, `item${i}Button`])]
  : view === 'checkout' ? ['product', 'address', 'coupon', 'total', 'button'] : view === 'success' ? ['headline', 'paid'] : [];

/** Slight pulse for a highlighted row: background breathes, period 1 s, never below 70 %. */
const pulse = (t: number) => .85 + .15 * Math.sin(2 * Math.PI * t / 30);

export const ShopPricePage: React.FC<UIProps> = ({e: original, frame}) => {
  const t = original.coverStill ? 0 : frame, e = stateAt(original, t), boxes: Record<string, number[]> = e.boxes ?? {};
  const view: string = e.view ?? 'search';
  const search = e.search ?? {}, checkout = e.checkout ?? {}, success = e.success ?? {};
  // Search rows: `item{i}.highlighted` state keys override the authored row flag (knoll-props §1.2).
  const items: Item[] = (search.items ?? []).map((item: Item, i: number) => ({...item, highlighted: e[`item${i}.highlighted`] ?? item.highlighted}));
  // State frames carry coupon/total at top level; the authored defaults live under `checkout`.
  const coupon: Coupon = e.coupon ?? checkout.coupon ?? {visible: false, applied: false, text: '', highlighted: false};
  const total: string = typeof e.total === 'string' ? e.total : checkout.total;
  const lit = (on: boolean | undefined) => on ? {background: HIGHLIGHT, boxShadow: `0 0 0 3px ${HIGHLIGHT_EDGE}`, opacity: original.coverStill ? 1 : pulse(t)} : undefined;

  const text = (key: string, value: string | undefined, size: number, opts: {bold?: boolean; color?: string; highlighted?: boolean; field?: boolean; button?: boolean} = {}) => {
    const b = boxes[key];
    if (!b || value === '' || value == null) return null;
    // Row text always starts at its box x (rows stay aligned whether lit or not); only the search field has an inner inset.
    const pad = opts.field ? 12 : 0;
    return <div key={key} data-shop-box={key} data-highlighted={opts.highlighted || undefined} role={opts.button ? 'button' : opts.field ? 'searchbox' : undefined} aria-pressed={opts.button ? !!e.buttonPressed : undefined}
      style={{...browserPageBox(e, b), boxSizing: 'border-box', display: 'flex', alignItems: 'center', justifyContent: opts.button ? 'center' : 'flex-start', paddingLeft: opts.button ? 0 : pad, paddingRight: opts.button ? 0 : pad, borderRadius: opts.button ? 10 : 8,
        ...(opts.field ? {border: `2px solid ${P.muted}`, background: '#F8FAFC'} : {}),
        ...(opts.button ? {background: P.primary, color: P.bg, filter: e.buttonPressed && key === 'button' ? 'brightness(.8)' : undefined, transform: e.buttonPressed && key === 'button' ? 'translateY(2px)' : undefined} : {color: opts.color ?? INK})}}>
      {opts.highlighted && <div aria-hidden data-row-highlight style={{position: 'absolute', top: 0, bottom: 0, left: -10, right: 0, borderRadius: 8, ...lit(true)}} />}
      <Copy text={value} size={size} width={b[2] - pad * 2 - (opts.field ? 4 : 0)} height={b[3] - (opts.field ? 4 : 0)} style={{position: 'relative', fontWeight: opts.bold ? 700 : 400, whiteSpace: 'nowrap', textAlign: opts.button ? 'center' : 'left'}}>{value}</Copy>
    </div>;
  };

  const shown = new Set(viewBoxes(view, items));
  const ripples: Ripple[] = (e.ripples ?? []).filter((r: Ripple) => shown.has(r.center) && boxes[r.center]);
  return <div data-shop-price-page data-view={view} data-coupon={coupon.visible ? coupon.applied ? 'applied' : 'shown' : 'hidden'} style={{position: 'absolute', inset: 0, background: PAGE_BG, color: INK}}>
    {view === 'search' && <>
      {text('query', search.query, e.rowSize, {field: true})}
      {items.map((item, i) => <React.Fragment key={i}>
        {text(`item${i}`, item.text, e.rowSize, {highlighted: !!item.highlighted})}
        {text(`item${i}Button`, item.button, e.buttonSize, {bold: true, button: true})}
      </React.Fragment>)}
    </>}
    {view === 'checkout' && <>
      {text('product', checkout.product, e.rowSize)}
      {text('address', checkout.address, e.rowSize)}
      {/* §1.1: visible=false keeps the row's place but draws nothing; visible shows the green text; applied is carried by `total`. */}
      {coupon.visible && text('coupon', coupon.text, e.rowSize, {color: COUPON_GREEN, highlighted: !!coupon.highlighted})}
      {text('total', total, e.rowSize, {bold: true})}
      {text('button', checkout.button, e.buttonSize, {bold: true, button: true})}
    </>}
    {view === 'success' && <>
      {text('headline', success.headline, e.headlineSize, {bold: true, color: P.success})}
      {text('paid', success.paid, e.rowSize)}
    </>}
    {/* Rings sit above the page with a page-coloured keyline (visible from the press frame); the pressed button is redrawn on top so they never cross its label. */}
    {ripples.length > 0 && <svg width="100%" height="100%" aria-hidden style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
      {ripples.map(r => {
        const age = t - r.bornFrame;
        if (age < 0) return null;
        const p = r.growFrames > 0 ? Math.min(1, age / r.growFrames) : 1, c = browserPageBox(e, boxes[r.center]);
        const cx = c.left + c.width / 2, cy = c.top + c.height / 2, radius = r.r0 + (r.r1 - r.r0) * p;
        return <g key={r.id} opacity={1 + (r.holdOpacity - 1) * p}><circle cx={cx} cy={cy} r={radius} fill="none" stroke={PAGE_BG} strokeWidth={8} /><circle cx={cx} cy={cy} r={radius} fill="none" stroke={r.color} strokeWidth={4} /></g>;
      })}
    </svg>}
    {ripples.filter(r => /Button$|^button$/.test(r.center) && (r.center !== 'button' || view === 'checkout')).map(r => {
      const label = r.center === 'button' ? checkout.button : items[Number(r.center.slice(4, -6))]?.button;
      return <React.Fragment key={`top-${r.id}`}>{text(r.center, label, e.buttonSize, {bold: true, button: true})}</React.Fragment>;
    })}
  </div>;
};
