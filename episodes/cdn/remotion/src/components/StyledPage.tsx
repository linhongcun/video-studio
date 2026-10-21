import React from 'react';
import {FONT, P} from '../theme';
import {Copy, stateAt, UIProps} from './ui';
export const StyledPage: React.FC<UIProps> = ({e: original, frame, canvas}) => {
  const e = stateAt(original, frame);
  if (e.variant === 'sessionDemo') {
    const paddingX = Math.min(28, e.w * .052), paddingY = Math.min(20, e.h * .06), gap = Math.min(12, e.h * .035);
    const width = e.w - 6 - paddingX * 2, titleHeight = Math.min(52, e.h * .16), labelHeight = e.sampleLabel ? Math.min(34, e.h * .12) : 0;
    const lines = e.lines ?? [];
    const rowHeight = (e.h - 6 - paddingY * 2 - titleHeight - labelHeight - gap * (lines.length + (e.sampleLabel ? 1 : 0))) / Math.max(1, lines.length);
    return <div data-variant={e.variant} data-sample-data={e.sampleData || undefined} style={{width: '100%', height: '100%', boxSizing: 'border-box', padding: `${paddingY}px ${paddingX}px`, display: 'flex', flexDirection: 'column', gap, border: `3px solid ${canvas ? 'transparent' : P.muted}`, borderRadius: 14, background: P.panel, color: P.text2, fontFamily: FONT}}>
      <Copy size={Math.min(40, e.w * .074)} width={width} height={titleHeight} style={{flexShrink: 0, fontWeight: 800, color: P.text}}>{e.title}</Copy>
      {lines.map((line, i) => {
        // cdn-v1 strikeLine: index (or indices) of lines drawn struck-through and dimmed, e.g. 「源站地址：不返回」.
        // Value-only strike: strikePart 'value' (element/keyframe), a {line, part:'value'} entry in strikeLine, or line.strike === 'value'
        // strikes just the text after the first「：」/「:」(e.g. shot 10 「源站地址：不返回」 keeps the field name readable).
        const strikeEntries: any[] = e.strikeLine === undefined || e.strikeLine === null ? [] : Array.isArray(e.strikeLine) ? e.strikeLine : [e.strikeLine];
        const entry = strikeEntries.find(s => (typeof s === 'object' && s ? s.line : s) === i);
        const struck = entry !== undefined || !!line.strike;
        const part: 'value' | 'line' = (typeof entry === 'object' && entry?.part) || (line.strike === 'value' ? 'value' : undefined) || (line.strikePart ?? e.strikePart) || 'line';
        const sep = part === 'value' ? String(line.text).search(/[：:]/) : -1;
        const strikeStyle = {textDecoration: `line-through ${P.danger} 3px`, color: P.muted};
        return <div key={i} data-session-line={i} data-highlighted={!!line.highlight} data-struck={struck ? part : undefined} style={{flex: 1, minHeight: 0, display: 'flex', alignItems: 'center', padding: '0 8px', borderRadius: 8, background: line.highlight ? `${P.success}18` : undefined, color: line.highlight ? P.success : struck && sep < 0 ? P.muted : P.text2, fontWeight: line.highlight ? 800 : 500}}><Copy text={String(line.text)} size={e.fontSize ?? Math.min(36, e.w * .067)} width={width - 16} height={rowHeight} style={{whiteSpace: 'nowrap', textDecoration: struck && sep < 0 ? `line-through ${P.danger} 3px` : undefined}}>{struck && sep >= 0 ? <><span data-field-name>{String(line.text).slice(0, sep + 1)}</span><span data-struck-value style={strikeStyle}>{String(line.text).slice(sep + 1)}</span></> : line.text}</Copy></div>;
      })}
      {e.sampleLabel && <Copy size={Math.min(28, e.w * .055)} width={width} height={labelHeight} style={{flexShrink: 0, color: P.accent}}>{e.sampleLabel}</Copy>}
    </div>;
  }
  return <div data-variant={e.variant} style={{width: '100%', height: '100%', boxSizing: 'border-box', padding: '20px 28px', display: 'flex', alignItems: 'center', gap: 12, border: `3px solid ${canvas ? 'transparent' : P.muted}`, borderRadius: 14, background: P.panel, color: P.text2, fontFamily: FONT}}>
    {e.cursorBlink && <span data-comment-cursor style={{height: '1.2em', fontSize: e.fontSize ?? 36, width: 3, flexShrink: 0, background: P.primary, opacity: Math.floor(frame / 15) % 2 === 0 ? 1 : 0}} />}
    <Copy size={e.fontSize ?? 36} width={e.w - 80} height={e.h - 46}>{e.variant === 'commentBox' ? e.placeholder : e.text ?? e.title}</Copy>
  </div>;
};
