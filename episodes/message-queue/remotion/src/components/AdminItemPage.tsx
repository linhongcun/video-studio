import React from 'react';
import {P} from '../theme';
import {browserPageBox} from './browserLayout';
import {Copy, stateAt, UIProps} from './ui';

/** Admin fields use the same absolute scene/cover boxes as ItemShopPage. */
export const AdminItemPage: React.FC<UIProps> = ({e: original, frame}) => {
  const e = stateAt(original, frame), boxes = e.boxes ?? {}, admin = e.admin ?? {};
  const text = (key: string, value: string, size: number, style: React.CSSProperties = {}, anchor?: string) => {
    const box = boxes[key];
    if (!box) return null;
    const input = key === 'input', button = key === 'button';
    const padding = input ? 8 : 0, border = input ? 1 : 0;
    return <div key={key} data-anchor={anchor} role={input ? 'textbox' : button ? 'button' : undefined} aria-readonly={input ? true : undefined} aria-pressed={button ? !!e.buttonPressed : undefined} style={{...browserPageBox(e, box), boxSizing: 'border-box', display: 'flex', alignItems: 'center', justifyContent: button ? 'center' : 'flex-start', overflow: 'hidden', ...style}}>
      <Copy text={value} size={size} width={box[2] - (padding + border) * 2} height={box[3] - border * 2} style={{whiteSpace: 'nowrap', textAlign: button ? 'center' : 'left'}}>{value}</Copy>
    </div>;
  };
  return <div data-admin-item-page style={{position: 'absolute', inset: 0, background: '#F8FAFC', color: P.panel}}>
    {text('title', admin.pageTitle, e.adminTitleSize, {fontWeight: 700})}
    {text('name', admin.name, e.adminNameSize)}
    {text('priceLabel', admin.priceLabel, e.priceLabelSize)}
    {text('input', e.priceValue, e.inputSize, {border: `1px solid ${P.muted}`, background: '#FFFFFF', color: P.panel, padding: '0 8px'}, 'adminInput')}
    {text('button', admin.button, e.buttonSize, {borderRadius: 10, background: e.buttonPressed ? P.secondary : P.primary, color: P.bg, fontWeight: 700, transform: e.buttonPressed ? 'translateY(2px)' : undefined})}
    {e.saved && text('saved', `✓ ${admin.savedText}`, e.savedSize, {color: '#15803D'}, 'adminSaved')}
  </div>;
};
