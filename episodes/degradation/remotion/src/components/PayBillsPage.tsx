import React from 'react';
import {P} from '../theme';
import {browserPageBox} from './browserLayout';
import {Copy, stateAt, UIProps} from './ui';

export const PayBillsPage: React.FC<UIProps> = ({e: original, frame}) => {
  const e = stateAt(original, frame), boxes = e.boxes ?? {}, bills = e.bills ?? {}, row = bills.rows?.[0];
  const rowText = row?.text ?? '', amountIndex = row?.amount ? rowText.indexOf(row.amount) : -1;
  return <div data-pay-bills-page style={{position: 'absolute', inset: 0, background: '#F8FAFC', color: P.panel}}>
    {boxes.billsTitle && bills.title && <div style={{...browserPageBox(e, boxes.billsTitle), display: 'flex', alignItems: 'center'}}>
      <Copy size={e.billsTitleSize} width={boxes.billsTitle[2]} height={boxes.billsTitle[3]} style={{fontWeight: 700, whiteSpace: 'nowrap'}}>{bills.title}</Copy>
    </div>}
    {boxes.billRow0 && row && <div data-anchor="billRow" style={{...browserPageBox(e, boxes.billRow0), boxSizing: 'border-box', display: 'flex', alignItems: 'center', padding: '0 16px', background: '#F1F5F9', border: '1px solid #E2E8F0', borderRadius: 10, overflow: 'hidden'}}>
      <Copy text={rowText} size={e.billRowSize} width={boxes.billRow0[2] - 34} height={boxes.billRow0[3] - 2} style={{whiteSpace: 'nowrap'}}>{amountIndex < 0 ? rowText : <><span>{rowText.slice(0, amountIndex)}</span><span data-anchor="billAmount">{row.amount}</span><span>{rowText.slice(amountIndex + row.amount.length)}</span></>}</Copy>
    </div>}
    {/* Knoll: the billAmount anchor is the rendered amount span itself (fits the glyphs); boxes.billAmount0 is the fallback when the amount is not in the row text. */}
    {boxes.billAmount0 && amountIndex < 0 && <div data-anchor="billAmount" aria-hidden style={{...browserPageBox(e, boxes.billAmount0), opacity: 0, pointerEvents: 'none'}} />}
  </div>;
};
