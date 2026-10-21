import React from 'react';
import {MONO, P} from '../theme';
import {Copy, stateAt, UIProps} from './ui';
import {TextHighlight} from './TextHighlight';
export const networkColumns = (count: number) => `repeat(${Math.max(1, count)}, minmax(0, 1fr))`;
export const DevToolsNetwork: React.FC<UIProps> = ({e: original, frame}) => {
  const e = stateAt(original, frame), panel = e.panel ?? 'network';
  const headerMode = panel === 'headers' || Array.isArray(e.headers);
  const hideOthers = e.hideOthers || (headerMode && !(e.headers ?? []).length);
  const docked = e.layout === 'docked', compact = e.w < 600;
  const padding = docked || compact ? 16 : 32;
  const authoredLines = headerMode ? e.headers ?? [] : panel === 'console' ? e.consoleLines ?? [] : [];
  const titleHeight = Math.min(docked ? 44 : compact ? 48 : 76, ...authoredLines.map(line => Math.max(1, line.y - e.y - 6)));
  const columnHeight = docked ? 52 : compact ? 44 : 80;
  const fontSize = e.fontSize ?? (compact ? 26 : 40);
  const columns: string[] = e.columns ?? [];
  const rows = (e.rows ?? []).slice(0, Math.max(0, e.visibleRows ?? Infinity));
  const originHeight = e.storageOrigin ? (docked ? 28 : compact ? 36 : 44) : 0;
  const rowHeight = Math.min(docked ? 64 : compact ? 52 : 72, Math.max(1, (e.h - 6 - titleHeight - columnHeight - originHeight - (e.sampleLabel ? 42 : 0)) / Math.max(1, rows.length)));
  const title = e.title ?? (panel === 'storage' ? '存储 · Cookie' : panel === 'headers' ? e.headerSection : panel === 'console' ? '控制台' : '网络');
  // Header and console coordinates are authored in scene space, not panel space.
  const lineBox = (line: any, all: any[]) => {
    const left = line.x - e.x - 3, top = line.y - e.y - 3;
    if (e.singleLine) return {left, top, width: Math.max(1, e.w - 6 - left - padding), height: Math.max(1, Math.min(e.h - 6 - top, (line.fontSize ?? fontSize) * 1.2))};
    const next = all.filter(other => other.y > line.y).map(other => other.y - line.y);
    return {left, top, width: Math.max(1, e.w - 6 - left - padding), height: Math.max(1, Math.min(e.h - 6 - top, ...next))};
  };
  return <div data-layout={e.layout} data-panel={panel} data-hide-others={e.hideOthers || undefined} data-single-line={e.singleLine || undefined} data-sample-data={e.sampleData || undefined} style={{position: 'relative', width: '100%', height: '100%', boxSizing: 'border-box', overflow: 'hidden', display: 'flex', flexDirection: 'column', background: P.bg, color: P.text, border: `3px solid ${P.muted}`, borderRadius: docked ? 8 : 20, boxShadow: `0 0 28px ${P.secondary}18`}}>
    {!hideOthers && <div data-panel-title style={{height: titleHeight, flexShrink: 0, display: 'flex', alignItems: 'center', gap: 18, padding: `0 ${padding}px`, boxSizing: 'border-box', background: P.panel, fontWeight: 700, color: P.primary}}>
      <Copy size={docked ? 28 : compact ? 30 : 40} width={(e.w - padding * 2 - 6) * (e.request ? .4 : 1)} height={titleHeight}>{title}</Copy>
      {e.request && <Copy mono size={fontSize} width={(e.w - padding * 2 - 24) * .6} height={titleHeight} style={{marginLeft: 'auto', color: P.text2}}>{e.request}</Copy>}
    </div>}
    {headerMode ? (e.headers ?? []).map((header, i, all) => {
      const geometry = lineBox(header, all);
      const separator = typeof header.separator === 'string' ? header.separator : /^(HTTP\/|GET$|POST$|PUT$|DELETE$|PATCH$|HEAD$|OPTIONS$)/.test(header.name) ? ' ' : ': ';
      const prefix = `${header.name}${separator}${header.value ?? ''}`;
      const fullText = prefix + (header.attrs ?? []).map(attr => `; ${attr.text}`).join('');
      const dimmed = header.role === 'dim' || (e.dimOthers && header.role !== 'hi' && header.role !== 'other');
      return <div key={i} data-header-line={i} data-role={header.role} style={{position: 'absolute', ...geometry, display: 'flex', alignItems: e.singleLine ? 'center' : 'flex-start', color: header.role === 'hi' ? P.primary : P.text, opacity: dimmed ? e.dimOpacity ?? .35 : 1}}><Copy mono text={fullText} size={header.fontSize ?? fontSize} width={geometry.width} height={geometry.height} style={{whiteSpace: 'pre'}}>
        <span data-header-value>{prefix}</span>{(header.attrs ?? []).map((attr, j) => <span key={j} data-header-attr={attr.text} data-note-ref={attr.note} style={{opacity: attr.dim ? e.dimOpacity ?? .35 : 1}}>{`; ${attr.text}`}</span>)}
      </Copy></div>;
    }) : !hideOthers && (panel === 'console' ? (e.consoleLines ?? []).map((line, i, all) => {
      const geometry = lineBox(line, all), text = `> ${line.input}\n${line.output}`;
      return <div key={i} data-console-line={i} style={{position: 'absolute', ...geometry}}><Copy mono size={line.fontSize ?? fontSize} width={geometry.width} height={geometry.height} style={{color: P.primary}}>{text}</Copy></div>;
    }) : <>
      {e.storageOrigin && <div data-storage-origin style={{height: originHeight, flexShrink: 0, padding: `0 ${padding}px`, display: 'flex', alignItems: 'center', background: P.panel, color: P.text2}}><Copy mono size={fontSize} width={e.w - padding * 2 - 6} height={originHeight}>{e.storageOrigin}</Copy></div>}
      {!!columns.length && <div role="row" style={{height: columnHeight, flexShrink: 0, display: 'grid', gridTemplateColumns: networkColumns(columns.length), alignItems: 'center', padding: `0 ${padding}px`, background: P.panel2, color: P.text2, fontWeight: 700}}>{columns.map((label, i) => <Copy key={i} size={fontSize} width={(e.w - padding * 2 - 6) / columns.length - 8} height={columnHeight}>{label}</Copy>)}</div>}
      {rows.map((row, i) => <div key={i} data-storage-row={panel === 'storage' ? i : undefined} data-highlighted={e.highlightRows?.includes(i) || false} role="row" style={{height: rowHeight, flexShrink: 0, boxSizing: 'border-box', display: 'grid', gridTemplateColumns: networkColumns(columns.length), alignItems: 'center', padding: `0 ${padding}px`, border: `2px solid ${e.highlightRows?.includes(i) ? P.primary : 'transparent'}`, background: e.highlightRows?.includes(i) ? `${P.primary}18` : undefined}}>{(Array.isArray(row) ? row : Object.values(row)).map((cell, j) => <Copy key={j} mono size={fontSize} width={(e.w - padding * 2 - 10) / Math.max(1, columns.length) - 8} height={rowHeight - 4}>{String(cell)}</Copy>)}</div>)}
      {!rows.length && e.emptyText && <div data-empty-storage style={{flex: 1, minHeight: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 24px', color: P.text2}}><Copy size={fontSize} width={e.w - 54} height={e.h - titleHeight - columnHeight - originHeight - 6}>{e.emptyText}</Copy></div>}
    </>)}
    {!hideOthers && (e.sampleLabel || e.note) && <div style={{marginTop: 'auto', flexShrink: 0, padding: `4px ${padding}px`, color: e.sampleLabel ? P.accent : P.text2}}><Copy size={fontSize} width={e.w - padding * 2 - 6} height={34}>{e.sampleLabel ?? e.note}</Copy></div>}
  </div>;
};
export const NetworkRow: React.FC<UIProps> = ({e: original, frame}) => {
  const e = stateAt(original, frame), cellWidth = e.w / e.cells.length;
  return <div role="row" style={{position: 'relative', width: '100%', height: '100%', boxSizing: 'border-box', display: 'grid', gridTemplateColumns: networkColumns(e.cells.length), alignItems: 'center', borderBottom: `1px solid ${P.muted}44`, background: P.panel, fontFamily: MONO}}>{e.cells.map((cell: string, i: number) => <div key={i} role="cell" data-cell={i} style={{minWidth: 0, padding: '8px 12px', boxSizing: 'border-box', color: i === 0 ? P.primary : cell === '200' ? P.success : P.text, whiteSpace: 'pre', overflow: 'hidden', fontWeight: i === e.cells.length - 1 ? 700 : 400}}><Copy mono size={e.fontSize ?? 40} width={cellWidth - 24} height={e.h - 16}>{cell}</Copy></div>)}</div>;
};
export const RowHighlight = TextHighlight;
