import React from 'react';
import {MONO, P} from '../theme';
import {Copy, fitSize, stateAt, UIProps} from './ui';
import {TextHighlight} from './TextHighlight';
export const networkColumns = (count: number) => `repeat(${Math.max(1, count)}, minmax(0, 1fr))`;
export const DevToolsNetwork: React.FC<UIProps> = ({e}) => {
  const docked = e.layout === 'docked';
  const padding = docked ? 16 : 32;
  return <div data-layout={e.layout} data-panel={e.panel ?? 'network'} style={{position: 'relative', width: '100%', height: '100%', boxSizing: 'border-box', overflow: 'hidden', display: 'flex', flexDirection: 'column', background: P.bg, color: P.text, border: `3px solid ${P.muted}`, borderRadius: docked ? 8 : 20, boxShadow: `0 0 28px ${P.secondary}18`}}>
    <div style={{height: docked ? 44 : 76, flexShrink: 0, display: 'flex', alignItems: 'center', gap: 18, padding: `0 ${padding}px`, background: P.panel, fontSize: docked ? 28 : 40, fontWeight: 700, color: P.primary}}>{e.panel === 'storage' ? '存储 · Cookie' : '网络'}</div>
    <div role="row" style={{height: docked ? 52 : 80, flexShrink: 0, display: 'grid', gridTemplateColumns: networkColumns(e.columns.length), alignItems: 'center', padding: `0 ${padding}px`, background: P.panel2, color: P.text2, fontWeight: 700}}>{e.columns.map((label: string) => <Copy key={label} size={e.fontSize} width={(e.w - padding * 2) / e.columns.length} height={docked ? 48 : 76}>{label}</Copy>)}</div>
    {(e.rows ?? []).map((row, i) => <div key={i} role="row" style={{display: 'grid', gridTemplateColumns: networkColumns(e.columns.length), padding: `12px ${padding}px`}}>{(Array.isArray(row) ? row : Object.values(row)).map((cell, j) => <Copy key={j} mono size={e.fontSize} width={(e.w - padding * 2) / e.columns.length}>{String(cell)}</Copy>)}</div>)}
    {!e.rows?.length && e.emptyText && <div style={{flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24, color: P.text2}}><Copy size={e.fontSize} width={e.w - 48}>{e.emptyText}</Copy></div>}
    {e.note && <Copy size={e.fontSize} width={e.w - 64} style={{marginTop: 'auto', marginBottom: 24, padding: '0 32px', color: P.text2}}>{e.note}</Copy>}
  </div>;
};
export const NetworkRow: React.FC<UIProps> = ({e: original, frame}) => {
  const e = stateAt(original, frame), cellWidth = e.w / e.cells.length;
  return <div role="row" style={{position: 'relative', width: '100%', height: '100%', boxSizing: 'border-box', display: 'grid', gridTemplateColumns: networkColumns(e.cells.length), alignItems: 'center', borderBottom: `1px solid ${P.muted}44`, background: P.panel, fontFamily: MONO}}>{e.cells.map((cell: string, i: number) => <div key={i} role="cell" data-cell={i} style={{minWidth: 0, padding: '8px 12px', boxSizing: 'border-box', color: i === 0 ? P.primary : cell === '200' ? P.success : P.text, fontSize: fitSize(cell, cellWidth - 24, e.fontSize ?? 40, true, e.h - 16), whiteSpace: 'pre', overflow: 'hidden', fontWeight: i === e.cells.length - 1 ? 700 : 400}}>{cell}</div>)}</div>;
};
export const RowHighlight = TextHighlight;
