// EP.01 v6 Network panel and row styling, with storyboard-authored columns/cells.
import React from 'react';
import {MONO, P} from '../theme';
import {Copy, fitSize, UIProps} from './ui';
export const networkColumns = (count: number) => `minmax(0, 2fr) repeat(${Math.max(1, count - 1)}, minmax(0, 1fr))`;
export const DevToolsNetwork: React.FC<UIProps> = ({e}) => <div style={{position: 'relative', width: '100%', height: '100%', boxSizing: 'border-box', display: 'flex', flexDirection: 'column', background: P.bg, color: P.text, border: `3px solid ${P.muted}`, borderRadius: 20, fontSize: 40, boxShadow: `0 0 28px ${P.secondary}18`}}>
  <div style={{height: 76, flexShrink: 0, display: 'flex', alignItems: 'center', gap: 18, padding: '0 30px', background: P.panel, borderRadius: '17px 17px 0 0', fontSize: 40, fontWeight: 700}}><div style={{height: 42, width: 10, borderRadius: 5, background: P.primary}} />Network</div>
  <div style={{height: 80, display: 'grid', gridTemplateColumns: networkColumns(e.columns.length), alignItems: 'center', padding: '0 40px', background: P.panel2, color: P.text2, fontSize: Math.max(24, e.fontSize ?? 40), fontWeight: 700}}>{e.columns.map((label: string) => <div key={label}>{label}</div>)}</div>
  {e.note && <div style={{marginTop: 'auto', marginBottom: 32, padding: '0 36px', color: P.text2, fontSize: Math.max(24, e.fontSize ?? 40)}}>{e.note}</div>}
</div>;
export const NetworkRow: React.FC<UIProps> = ({e}) => {
  const innerWidth = e.w - 48;
  const cellUnit = innerWidth / (e.cells.length + 1);
  return <div role="row" style={{position: 'relative', width: '100%', height: '100%', boxSizing: 'border-box', display: 'grid', gridTemplateColumns: networkColumns(e.cells.length), alignItems: 'center', padding: '0 24px', borderBottom: `1px solid ${P.muted}44`, background: P.panel, fontFamily: MONO}}>{e.cells.map((cell: string, i: number) => <div key={i} role="cell" data-cell={i} data-highlighted={e.highlightCell === i || undefined} style={{minWidth: 0, padding: '12px 8px', marginRight: 8, border: `3px solid ${e.highlightCell === i ? P.primary : 'transparent'}`, borderRadius: 10, background: e.highlightCell === i ? `${P.primary}18` : undefined, color: i === 0 ? P.primary : cell === '200' ? P.success : P.text, fontSize: fitSize(cell, cellUnit * (i === 0 ? 2 : 1) - 40, e.fontSize ?? 48, true), overflowWrap: 'anywhere', fontWeight: i === e.cells.length - 1 ? 700 : 400}}>{cell}</div>)}</div>;
};
export const RowHighlight: React.FC<UIProps> = () => <div style={{position: 'absolute', inset: 0, pointerEvents: 'none', boxSizing: 'border-box', border: `4px solid ${P.primary}`, borderRadius: 10, background: `${P.primary}18`}} />;
