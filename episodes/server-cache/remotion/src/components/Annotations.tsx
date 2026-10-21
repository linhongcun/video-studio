import React from 'react';
import {P} from '../theme';
import {Copy, colorToken, emphasisStyle, pulseAt, stateAt, UIProps} from './ui';
import {TextHighlight} from './TextHighlight';
export const CalloutTag: React.FC<UIProps> = ({e: original, frame}) => {
  const e = stateAt(original, frame), pulse = pulseAt(e, frame);
  return <div data-sample-data={e.sampleData || undefined} data-pulse={pulse > 0} data-expiry-mark={e.expiryMark} data-highlighted={e.highlighted} data-escalation={e.escalation || undefined} data-dim={e.dim} style={{width: '100%', height: '100%', boxSizing: 'border-box', display: 'flex', alignItems: 'center', justifyContent: e.align === 'left' ? 'flex-start' : e.align === 'right' ? 'flex-end' : 'center', padding: '8px 16px', overflow: 'hidden', border: `${e.escalation ? 5 : 3}px solid ${colorToken(e.color) ?? P.primary}`, borderRadius: e.radius ?? 14, background: colorToken(e.background) ?? P.panel, color: colorToken(e.color) ?? P.primary, ...emphasisStyle(e), transform: `scale(${1 + pulse * .05})`, boxShadow: pulse || e.escalation ? `0 0 ${(e.escalation ? 14 : 0) + pulse * 24}px ${colorToken(e.color) ?? P.primary}` : undefined}}><Copy size={e.fontSize} width={e.w - 38} height={e.h - 22} style={{fontWeight: e.fontWeight ?? 700, textAlign: e.align ?? 'center'}}>{e.text}</Copy></div>;
};
export const CornerBadge: React.FC<UIProps> = ({e: original, frame}) => {
  const e = stateAt(original, frame), pulse = pulseAt(e, frame);
  return <div data-simulated={e.simulated || undefined} data-sample-data={e.sampleData || undefined} data-expiry-mark={e.expiryMark} data-highlighted={e.highlighted} data-dim={e.dim} data-pulse={pulse > 0} data-conflict={e.conflict || undefined} data-escalation={e.escalation || undefined} style={{width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', boxSizing: 'border-box', padding: '4px 12px', overflow: 'hidden', borderRadius: e.radius ?? 10, background: colorToken(e.background) ?? P.panel2, color: colorToken(e.color) ?? P.text2, ...emphasisStyle(e), transform: `scale(${1 + pulse * .05})`, boxShadow: pulse ? `0 0 ${pulse * 24}px ${colorToken(e.color) ?? P.primary}` : undefined}}><Copy size={e.fontSize} width={e.w - 30} height={e.h - 14} style={{fontWeight: e.fontWeight ?? 700, textAlign: e.align ?? 'center'}}>{e.text}</Copy></div>;
};
export {BlockHighlight} from './AnchorHighlight';
