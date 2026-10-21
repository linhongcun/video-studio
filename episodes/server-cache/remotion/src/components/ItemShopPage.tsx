import React from 'react';
import {P} from '../theme';
import {browserPageBox} from './browserLayout';
import {ShopImageDrawing} from './shopDrawing';
import {Spinner} from './Spinner';
import {Copy, stateAt, UIProps} from './ui';

/** Page boxes remain in scene (or cover canvas) coordinates. */
export const ItemShopPage: React.FC<UIProps & {rotor?: number}> = ({e: original, frame, rotor = frame}) => {
  const e = stateAt(original, frame), boxes = e.boxes ?? {}, item = e.item ?? {};
  const placeholder = e.info === 'placeholder';
  const text = (key: string, value: string, size: number, color: string, bold = false, anchor?: string, background?: string) => {
    const box = boxes[key];
    if (!box) return null;
    return <div key={key} data-anchor={anchor} style={{...browserPageBox(e, box), display: 'flex', alignItems: 'center', justifyContent: key === 'button' ? 'center' : 'flex-start', borderRadius: background ? 10 : undefined, background, color}}>
      <Copy size={size} width={box[2]} height={box[3]} style={{fontWeight: bold ? 700 : 400, whiteSpace: 'nowrap', textAlign: key === 'button' ? 'center' : 'left'}}>{value}</Copy>
    </div>;
  };
  const field = (key: string, size: number, color: string, bold = false) => placeholder && boxes[key]
    ? <div key={key} data-anchor={`item${key[0].toUpperCase()}${key.slice(1)}`} style={{...browserPageBox(e, boxes[key]), borderRadius: 10, background: '#334155'}} />
    : text(key, item[key], size, color, bold, `item${key[0].toUpperCase()}${key.slice(1)}`);
  return <>
    {e.page === 'ordersPage' ? <>
      {text('title', e.order?.pageTitle, e.shopNameSize, P.text, true)}
      {text('order', e.order?.orderText, e.orderSize, P.text, false, 'orderRow', P.panel2)}
    </> : <>
      {!e.compact && text('title', item.shopName, e.shopNameSize, P.text, true)}
      {!e.compact && e.viewers && text('viewers', item.viewersText, e.viewersSize, P.accent)}
      {boxes.image && <div style={browserPageBox(e, boxes.image)}><ShopImageDrawing id={`${e.id}-item`} variant={item.pattern} state={placeholder ? 'placeholder' : 'shown'} w={boxes.image[2]} h={boxes.image[3]} frame={rotor} /></div>}
      {!e.compact && field('name', e.nameSize, P.text, true)}
      {field('price', e.priceSize, P.accent, true)}
      {field('stock', e.stockSize, P.text2)}
      {!e.compact && text('button', item.button, e.buttonSize, P.bg, true, undefined, P.primary)}
      {placeholder && boxes.spinner && <div data-item-spinner style={{...browserPageBox(e, boxes.spinner), display: 'flex', alignItems: 'center', justifyContent: 'center'}}><div style={{width: e.spinnerSize, height: e.spinnerSize, flexShrink: 0}}><Spinner frame={rotor} /></div></div>}
    </>}
    {e.dimPage > 0 && <div data-item-dim style={{position: 'absolute', inset: 0, background: P.bg, opacity: e.dimPage}} />}
  </>;
};
