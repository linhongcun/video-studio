import React from 'react';
import {P, PAGE} from '../theme';
import {browserPageBox} from './browserLayout';
import {ShopImageDrawing} from './shopDrawing';
import {Copy, stateAt, UIProps} from './ui';

/** Checkout and order boxes are authored in absolute scene/cover coordinates. */
export const OrderFlowPage: React.FC<UIProps> = ({e: original, frame}) => {
  const e = stateAt(original, frame), boxes = e.boxes ?? {};
  const checkout = e.checkout ?? {}, order = e.order ?? {};
  const text = (key: string, value: string, size: number, bold = false, anchor?: string) => {
    const box = boxes[key], button = key === 'cButton';
    if (!box || value === '' || value == null) return null;
    return <div key={key} data-anchor={anchor} role={button ? 'button' : undefined} aria-pressed={button ? !!e.buttonPressed : undefined} style={{...browserPageBox(e, box), boxSizing: 'border-box', display: 'flex', alignItems: 'center', justifyContent: button ? 'center' : 'flex-start', overflow: 'hidden', ...(button ? {borderRadius: 10, background: P.primary, color: P.bg, filter: e.buttonPressed ? 'brightness(.8)' : undefined, transform: e.buttonPressed ? 'translateY(2px)' : undefined} : {})}}>
      <Copy size={size} width={box[2]} height={box[3]} style={{fontWeight: bold ? 700 : 400, whiteSpace: 'nowrap', textAlign: button ? 'center' : 'left'}}>{value}</Copy>
    </div>;
  };
  return <div data-order-flow-page data-view={e.view} style={{position: 'absolute', inset: 0, background: PAGE.bg, color: PAGE.ink}}>
    {e.view === 'checkout' && <>
      {text('cTitle', checkout.pageTitle, e.cTitleSize, true)}
      {boxes.cImage && <div style={browserPageBox(e, boxes.cImage)}><ShopImageDrawing id={`${e.id}-checkout`} variant={checkout.pattern} w={boxes.cImage[2]} h={boxes.cImage[3]} frame={frame} /></div>}
      {text('cName', checkout.name, e.cNameSize)}
      {text('cButton', checkout.button, e.cButtonSize, true)}
    </>}
    {e.view === 'order' && <>
      {text('banner', order.banner, e.bannerSize)}
      {text('headline', order.headline, e.headlineSize, true, 'orderHeadline')}
      {text('orderNo', order.orderNo, e.orderNoSize)}
      {e.statusShown && <>
        {text('statusLabel', order.statusLabel, e.statusSize)}
        {text('statusValue', order.statusValue, e.statusSize, true, 'orderStatusValue')}
      </>}
    </>}
  </div>;
};
