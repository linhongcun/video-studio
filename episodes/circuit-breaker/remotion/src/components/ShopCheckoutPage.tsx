import React from 'react';
import covers from '@covers';
import {ShotElement, storyboard} from '../storyboard';
import {P, PAGE} from '../theme';
import {browserPageBox} from './browserLayout';
import {Spinner} from './Spinner';
import {Copy, stateAt, UIProps} from './ui';

type Ripple = {id: string; bornFrame: number; center: 'button'; r0: number; r1: number; growFrames: number; holdOpacity: number; color: string};
type Insurance = {state: string; text?: string; checkbox?: boolean | null; spinning?: boolean};
const shopElements = (value: any): ShotElement[] => {
  if (!value || typeof value !== 'object') return [];
  if (value.component === 'BrowserChrome' && value.page === 'shopCheckout') return [value];
  return Object.values(value).flatMap(shopElements);
};
const insuranceRows = (e: ShotElement): Insurance[] => [e, ...(e.stateKeyframes ?? [])].map(s => s.checkout?.insurance).filter(Boolean);
const authoredInsurance = [...shopElements(storyboard), ...shopElements(covers)].flatMap(insuranceRows);
const warnedStates = new Set<string>();
const insuranceText = (e: ShotElement, state: string): string | undefined => {
  if (state === 'pending') return '';
  const rows = [...insuranceRows(e), ...authoredInsurance];
  const find = (name: string) => rows.find(row => row.state === name && typeof row.text === 'string')?.text;
  const text = find(state) ?? (state === 'available' ? find('ticked') : state === 'ticked' ? find('available') : undefined);
  if (text === undefined && !warnedStates.has(state)) {
    warnedStates.add(state);
    console.warn(`ShopCheckoutPage: no authored insurance text for state "${state}"`);
  }
  return text;
};

/** Checkout boxes are authored in absolute scene/cover coordinates. */
export const ShopCheckoutPage: React.FC<UIProps> = ({e: original, frame}) => {
  const t = original.coverStill ? 0 : frame, e = stateAt(original, t), boxes = e.boxes ?? {}, checkout = e.checkout ?? {}, success = e.success ?? {};
  const state = typeof e.insurance === 'string' ? e.insurance : checkout.insurance?.state;
  const rowText = e.view === 'checkout' ? insuranceText(e, state) : undefined;
  const checkbox = state === 'available' || state === 'ticked', ticked = state === 'ticked';
  const rowVisible = !!rowText && !!boxes.insurance;
  const offset = rowVisible && checkbox && boxes.insuranceCheckbox ? boxes.insuranceCheckbox[2] + 12 : 0;
  const text = (key: string, value: string, size: number, opts: {bold?: boolean; color?: string; button?: boolean; labelOnly?: boolean; offset?: number} = {}) => {
    const box = boxes[key];
    if (!box || value === '' || value == null) return null;
    const button = !!opts.button, shift = opts.offset ?? 0;
    return <div key={key} role={button ? 'button' : undefined} aria-pressed={button ? !!e.buttonPressed : undefined} style={{...browserPageBox(e, [box[0] + shift, box[1], box[2] - shift, box[3]]), boxSizing: 'border-box', display: 'flex', alignItems: 'center', justifyContent: button ? 'center' : 'flex-start', overflow: 'hidden', color: opts.color, ...(button ? {borderRadius: 10, background: opts.labelOnly ? 'transparent' : P.primary, color: P.bg, filter: e.buttonPressed ? 'brightness(.8)' : undefined, transform: e.buttonPressed ? 'translateY(2px)' : undefined} : {})}}>
      <Copy text={value} size={size} width={box[2] - shift} height={box[3]} style={{fontWeight: opts.bold ? 700 : 400, whiteSpace: 'nowrap', textAlign: button ? 'center' : 'left', color: button ? undefined : opts.color}}><span style={{background: opts.labelOnly ? P.primary : button ? undefined : PAGE.bg, boxShadow: opts.labelOnly ? `0 0 0 2px ${P.primary}` : button ? undefined : `0 0 0 6px ${PAGE.bg}`, borderRadius: 4}}>{value}</span></Copy>
    </div>;
  };
  const button = e.view === 'checkout' && checkout.button && boxes.button && browserPageBox(e, boxes.button);
  return <div data-shop-checkout-page data-view={e.view} data-insurance-state={state} style={{position: 'absolute', inset: 0, background: PAGE.bg, color: PAGE.ink}}>
    {e.view === 'checkout' && <>
      {text('button', checkout.button, e.buttonSize, {bold: true, button: true})}
      {/* Rings sit above the button and below the copy, with nested radii and a page-coloured keyline. */}
      {button && <svg width="100%" height="100%" aria-hidden style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
        {(e.ripples ?? []).map((ripple: Ripple) => {
          const age = t - ripple.bornFrame;
          if (age < 0) return null;
          const progress = ripple.growFrames > 0 ? Math.min(1, age / ripple.growFrames) : 1;
          const nest = (e.ripples ?? []).filter((other: Ripple) => other.center === ripple.center && other.bornFrame < ripple.bornFrame).length;
          const target = ripple.r1 - nest * (ripple.r1 - ripple.r0) * .15;
          const radius = ripple.r0 + (target - ripple.r0) * progress, lit = e.litRipple === ripple.id;
          return <g key={ripple.id} opacity={lit ? 1 : 1 + (ripple.holdOpacity - 1) * progress}><circle cx={button.left + button.width / 2} cy={button.top + button.height / 2} r={radius} fill="none" stroke={PAGE.bg} strokeWidth={(lit ? 8 : 4) + 4} /><circle cx={button.left + button.width / 2} cy={button.top + button.height / 2} r={radius} fill="none" stroke={ripple.color} strokeWidth={lit ? 8 : 4} /></g>;
        })}
      </svg>}
      {/* Redraw the label with its button-coloured halo above the rings. */}
      {text('button', checkout.button, e.buttonSize, {bold: true, button: true, labelOnly: true})}
      {text('product', checkout.product, e.rowSize)}
      {text('address', checkout.address, e.rowSize)}
      {rowVisible && <>
        {text('insurance', rowText, e.rowSize, {color: state === 'loading' || state === 'unavailable' ? P.muted : PAGE.ink, offset})}
        {checkbox && boxes.insuranceCheckbox && <div role="checkbox" aria-checked={ticked} style={{...browserPageBox(e, boxes.insuranceCheckbox), boxSizing: 'border-box', border: `2px solid ${PAGE.ink}`, borderRadius: 4, background: ticked ? P.primary : PAGE.field}}>{ticked && <svg width="100%" height="100%" viewBox="0 0 24 24" aria-hidden><path d="M5 12l4 4L19 6" fill="none" stroke="white" strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" /></svg>}</div>}
        {state === 'loading' && boxes.insuranceSpinner && <div style={browserPageBox(e, boxes.insuranceSpinner)}><Spinner frame={t} /></div>}
      </>}
      {text('total', typeof e.total === 'string' ? e.total : checkout.total, e.rowSize)}
    </>}
    {e.view === 'success' && <>
      {text('headline', success.headline, e.headlineSize, {bold: true, color: P.success})}
      {text('paid', success.paid, e.rowSize)}
    </>}
  </div>;
};
