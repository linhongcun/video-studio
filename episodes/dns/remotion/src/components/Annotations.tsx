import React from 'react';
import {P} from '../theme';
import {Copy, colorToken, UIProps} from './ui';
import {TextHighlight} from './TextHighlight';
export const CalloutTag: React.FC<UIProps> = ({e}) => <div style={{width: '100%', height: '100%', boxSizing: 'border-box', display: 'flex', alignItems: 'center', justifyContent: e.align === 'left' ? 'flex-start' : 'center', padding: '8px 16px', overflow: 'hidden', border: `3px solid ${colorToken(e.color) ?? P.primary}`, borderRadius: e.radius ?? 14, background: colorToken(e.background) ?? P.panel, color: colorToken(e.color) ?? P.primary}}><Copy size={e.fontSize} width={e.w - 38} height={e.h - 22} style={{fontWeight: e.fontWeight ?? 700, textAlign: e.align ?? 'center'}}>{e.text}</Copy></div>;
export const CornerBadge: React.FC<UIProps> = ({e}) => <div data-simulated={e.simulated || undefined} style={{width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', boxSizing: 'border-box', padding: '4px 12px', overflow: 'hidden', borderRadius: 10, background: colorToken(e.background) ?? P.panel2, color: colorToken(e.color) ?? P.text2}}><Copy size={e.fontSize} width={e.w - 24} height={e.h - 8} style={{fontWeight: e.fontWeight ?? 700, textAlign: e.align ?? 'center'}}>{e.text}</Copy></div>;
export const BlockHighlight = TextHighlight;
