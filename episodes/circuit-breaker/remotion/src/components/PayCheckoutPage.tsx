import React from 'react';
import {P} from '../theme';
import {browserPageBox} from './browserLayout';
import {Spinner} from './Spinner';
import {Copy, stateAt, UIProps} from './ui';

const PAGE_BG = '#F8FAFC';
type Ripple = {id: string; bornFrame: number; center: 'button'; r0: number; r1: number; growFrames: number; holdOpacity: number; color: string};

/** Payment boxes are authored in absolute scene/cover coordinates. */
export const PayCheckoutPage: React.FC<UIProps> = ({e: original, frame}) => {
  const t = original.coverStill ? 0 : frame, e = stateAt(original, t), boxes = e.boxes ?? {}, pay = e.pay ?? {};
  const text = (key: string, value: string, size: number, opts: {bold?: boolean; anchor?: string; color?: string; button?: boolean; labelOnly?: boolean} = {}) => {
    const box = boxes[key];
    if (!box || value === '' || value == null) return null;
    const button = !!opts.button;
    return <div key={key} data-anchor={opts.anchor} role={button ? 'button' : undefined} aria-pressed={button ? !!e.buttonPressed : undefined} style={{...browserPageBox(e, box), boxSizing: 'border-box', display: 'flex', alignItems: 'center', justifyContent: button ? 'center' : 'flex-start', overflow: 'hidden', color: opts.color, ...(button ? {borderRadius: 10, background: opts.labelOnly ? 'transparent' : P.primary, color: P.bg, filter: e.buttonPressed ? 'brightness(.8)' : undefined, transform: e.buttonPressed ? 'translateY(2px)' : undefined} : {})}}>
      <Copy size={size} width={box[2]} height={box[3]} style={{fontWeight: opts.bold ? 700 : 400, whiteSpace: 'nowrap', textAlign: button ? 'center' : 'left', color: button ? undefined : opts.color}}><span style={{background: opts.labelOnly ? P.primary : button ? undefined : PAGE_BG, boxShadow: opts.labelOnly ? `0 0 0 2px ${P.primary}` : button ? undefined : `0 0 0 6px ${PAGE_BG}`, borderRadius: 4}}>{value}</span></Copy>
    </div>;
  };
  const button = boxes.button && browserPageBox(e, boxes.button);
  return <div data-pay-checkout-page data-view={e.view} style={{position: 'absolute', inset: 0, background: PAGE_BG, color: P.panel}}>
    {(e.view === 'ready' || e.view === 'paying') && text('button', pay.button, e.buttonSize, {bold: true, button: true})}
    {/* Knoll: rings above the button (a ring still inside it stays visible) but under the copy; copy glyphs carry a page-coloured halo so a settled ring passes behind the amount line instead of through it. */}
    {button && <svg width="100%" height="100%" aria-hidden style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
      {(e.ripples ?? []).map((ripple: Ripple) => {
        const age = t - ripple.bornFrame;
        if (age < 0) return null;
        const progress = ripple.growFrames > 0 ? Math.min(1, age / ripple.growFrames) : 1;
        // Knoll: rings sharing the button centre would settle on the same circle; nest each later click slightly inside
        // (15 % of its growth per earlier ring) so both clicks stay distinguishable after they settle.
        const nest = (e.ripples ?? []).filter((other: Ripple) => other.center === ripple.center && other.bornFrame < ripple.bornFrame).length;
        const target = ripple.r1 - nest * (ripple.r1 - ripple.r0) * .15;
        const radius = ripple.r0 + (target - ripple.r0) * progress, lit = e.litRipple === ripple.id;
        // Knoll: a page-coloured keyline under each ring keeps a ring that is still inside the (same-cyan) button readable.
        return <g key={ripple.id} opacity={lit ? 1 : 1 + (ripple.holdOpacity - 1) * progress}><circle cx={button.left + button.width / 2} cy={button.top + button.height / 2} r={radius} fill="none" stroke={PAGE_BG} strokeWidth={(lit ? 8 : 4) + 4} /><circle cx={button.left + button.width / 2} cy={button.top + button.height / 2} r={radius} fill="none" stroke={ripple.color} strokeWidth={lit ? 8 : 4} /></g>;
      })}
    </svg>}
    {/* Knoll: the button label is drawn again above the rings (with a button-coloured halo), so a ring inside the button never crosses 「支付」. */}
    {(e.view === 'ready' || e.view === 'paying') && text('button', pay.button, e.buttonSize, {bold: true, button: true, labelOnly: true})}
    {text('amount', pay.amount, e.amountSize, {anchor: 'payAmount'})}
    {e.view === 'paying' && <>
      {e.spinning && boxes.spinner && <div style={browserPageBox(e, boxes.spinner)}><Spinner frame={t} /></div>}
      {text('status', pay.status, e.statusSize, {color: P.muted})}
    </>}
    {e.view === 'success' && text('headline', pay.headline, e.headlineSize, {bold: true, color: P.success})}
  </div>;
};
