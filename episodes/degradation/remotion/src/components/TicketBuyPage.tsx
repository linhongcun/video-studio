import React from 'react';
import {P, PAGE} from '../theme';
import {browserPageBox} from './browserLayout';
import {Copy, stateAt, UIProps} from './ui';

/** Ticket purchase page: ready / busy / ok. Boxes are authored in absolute scene/cover coordinates. */
export const TicketBuyPage: React.FC<UIProps> = ({e: original, frame}) => {
  const e = stateAt(original, frame), boxes = e.boxes ?? {}, ticket = e.ticket ?? {};
  const text = (key: string, value: string, size: number, opts: {bold?: boolean; anchor?: string; color?: string; button?: boolean} = {}) => {
    const box = boxes[key];
    if (!box || value === '' || value == null) return null;
    const button = !!opts.button;
    return <div key={key} data-anchor={opts.anchor} role={button ? 'button' : undefined} aria-pressed={button ? !!e.buttonPressed : undefined} style={{...browserPageBox(e, box), boxSizing: 'border-box', display: 'flex', alignItems: 'center', justifyContent: button ? 'center' : 'flex-start', overflow: 'hidden', color: opts.color, ...(button ? {borderRadius: 10, background: P.primary, color: P.bg, filter: e.buttonPressed ? 'brightness(.8)' : undefined, transform: e.buttonPressed ? 'translateY(2px)' : undefined} : {})}}>
      <Copy size={size} width={box[2]} height={box[3]} style={{fontWeight: opts.bold ? 700 : 400, whiteSpace: 'nowrap', textAlign: button ? 'center' : 'left', color: button ? undefined : opts.color}}>{value}</Copy>
    </div>;
  };
  const headlineColor = e.view === 'busy' ? P.danger : e.view === 'ok' ? P.success : PAGE.ink;
  return <div data-ticket-buy-page data-view={e.view} style={{position: 'absolute', inset: 0, background: PAGE.bg, color: PAGE.ink}}>
    {text('title', ticket.title, e.titleSize, {bold: true})}
    {text('headline', ticket.headline, e.headlineSize, {bold: true, anchor: 'ticketHeadline', color: headlineColor})}
    {text('button', ticket.button, e.buttonSize, {bold: true, anchor: 'ticketButton', button: true})}
  </div>;
};
