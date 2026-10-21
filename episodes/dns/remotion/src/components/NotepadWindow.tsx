import React from 'react';
import {MONO, P} from '../theme';
import {Copy, colorToken, fitSize, stateAt, UIProps} from './ui';
export const NotepadWindow: React.FC<UIProps> = ({e: original, frame, canvas}) => {
  const e = stateAt(original, frame);
  const compact = e.w < 600, padding = compact ? 20 : 32;
  const titleHeight = compact ? 62 : 86;
  const lines = [...(e.lines ?? [{text: e.line ?? e.text ?? ''}]), ...e.appendedLines];
  const autoLines = lines.filter(line => line.y === undefined).length;
  const autoHeight = (e.h - titleHeight - padding * 2) / Math.max(1, autoLines);
  const highlights: number[] = e.highlightLines ?? [];
  let autoIndex = 0;
  return <div data-variant={e.variant} style={{position: 'relative', boxSizing: 'border-box', width: '100%', height: '100%', overflow: 'hidden', border: `3px solid ${canvas ? 'transparent' : P.muted}`, borderRadius: canvas ? 0 : 18, background: canvas ? 'transparent' : e.variant === 'terminal' ? P.bg : P.panel, color: P.text}}>
    {canvas && <div style={{position: 'absolute', inset: `${e.titleBar === false ? 0 : titleHeight}px 0 0`, borderRadius: 14, background: e.variant === 'terminal' && !e.coverCard ? P.bg : P.panel}} />}
    {!canvas && e.titleBar !== false && <div style={{height: titleHeight, padding: compact ? '8px 16px' : '0 26px', display: 'flex', alignItems: 'center', gap: 18, background: P.panel2, borderBottom: `2px solid ${P.muted}`, boxSizing: 'border-box'}}>
      <span style={{fontSize: fitSize(e.title ?? '', e.w - padding * 2, compact ? 32 : 40, false, titleHeight - 16), fontWeight: 700, whiteSpace: 'nowrap', lineHeight: 1.2}}>{e.title}</span>
    </div>}
    {lines.map((line, i) => {
      const left = line.x === undefined ? padding : line.x - e.x;
      const top = line.y === undefined ? titleHeight + padding + autoIndex++ * autoHeight : line.y - e.y;
      const width = Math.max(1, e.w - left - padding);
      const nextTop = lines.filter(other => other.y !== undefined && other.y - e.y > top).map(other => other.y - e.y);
      const height = line.y === undefined ? autoHeight : Math.min(e.h - top - padding, ...nextTop.map(y => y - top));
      const lit = highlights.includes(i);
      return <div key={i} data-terminal-line={i} data-role={line.role} data-highlighted={lit} data-annotation={line.annotation ?? undefined} style={{position: 'absolute', left, top, width, height, display: i < (e.visibleLines ?? Infinity) ? 'flex' : 'none', alignItems: line.y === undefined ? 'center' : 'flex-start', opacity: e.dimOthers && !lit ? e.dimOpacity ?? .35 : 1, fontFamily: e.fontFamily ?? MONO}}>
        <Copy mono size={line.fontSize ?? e.fontSize ?? (compact ? 32 : 36)} width={width} height={height} style={{whiteSpace: 'pre', color: colorToken(line.color) ?? (line.role === 'answer' ? P.success : line.role === 'cmd' ? P.primary : P.text)}}>{line.text}</Copy>
      </div>;
    })}
  </div>;
};
