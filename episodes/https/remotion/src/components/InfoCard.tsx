import React from 'react';
import {progress} from '../animation';
import {FONT, P} from '../theme';
import {colorToken, Copy, stateAt, textWidth, UIProps} from './ui';

/** Fit this new card in both dimensions without changing the episode's Copy. */
const CardCopy: React.FC<{children?: React.ReactNode; text?: string; size: number; width: number; height: number; mono?: boolean; style?: React.CSSProperties}> = ({children, text, size, width, height, mono, style}) => {
  const lines = (text ?? String(children ?? '')).split('\n');
  const widest = Math.max(1, ...lines.map(line => textWidth(line, 1, mono)));
  const fitted = Math.max(1, Math.min(size, width / (widest * 1.03), height / (lines.length * 1.2)));
  return <Copy mono={mono} size={fitted} style={{width, maxWidth: '100%', maxHeight: '100%', flexShrink: 1, overflow: 'hidden', ...style, fontSize: fitted}}>{children}</Copy>;
};

/** Plain storyboard-authored copy and counters, without a window shell. */
export const InfoCard: React.FC<UIProps> = ({e: original, frame}) => {
  const e = stateAt(original, frame), color = colorToken(e.color ?? 'primary');
  const align = e.align === 'center' ? 'center' : 'left';
  const titleSize = e.titleSize ?? 32, valueSize = e.valueSize ?? 72, lineSize = e.lineSize ?? 30;
  const lines: string[] = e.lines ?? [];
  const hasTitle = e.title != null, hasValue = e.value != null || e.unit != null;
  const numeric = typeof e.value === 'number' || (typeof e.value === 'string' && e.value.trim() !== '' && Number.isFinite(Number(e.value)));
  let value = e.value ?? '';
  if (numeric && typeof e.countFrom === 'number' && e.countFrames > 0) {
    const p = progress(frame, e.appearFrame ?? 0, e.countFrames);
    value = p === 1 ? e.value : Math.round(e.countFrom + (Number(e.value) - e.countFrom) * p);
  }
  const valueText = `${value}${e.unit ? ` ${e.unit}` : ''}`;
  const width = Math.max(1, e.w - 54), height = Math.max(1, e.h - 54);
  const groups = Number(hasTitle) + Number(hasValue) + Number(lines.length > 0);
  const desiredHeight = (hasTitle ? titleSize * 1.2 : 0) + (hasValue ? valueSize * 1.2 : 0)
    + lines.length * lineSize * 1.2 + Math.max(0, groups - 1) * 12;
  const scale = Math.min(1, height / Math.max(1, desiredHeight));
  return <div data-info-card style={{width: '100%', height: '100%', boxSizing: 'border-box', borderRadius: 14, border: `3px solid ${color}`, background: colorToken(e.background ?? 'panel'), color: P.text, fontFamily: FONT, padding: 24, overflow: 'hidden', display: 'flex', flexDirection: 'column', gap: 12 * scale, alignItems: align === 'center' ? 'center' : 'flex-start'}}>
    {hasTitle && <CardCopy size={titleSize * scale} width={width} height={titleSize * 1.2 * scale} style={{color: P.text2, textAlign: align}}>{e.title}</CardCopy>}
    {hasValue && <CardCopy text={valueText} mono={numeric} size={valueSize * scale} width={width} height={valueSize * 1.2 * scale} style={{color, fontWeight: 800, textAlign: align, whiteSpace: 'nowrap'}}>{value}{e.unit && <span style={{fontFamily: FONT, fontSize: '.5em', fontWeight: 500}}> {e.unit}</span>}</CardCopy>}
    {lines.length > 0 && <CardCopy size={lineSize * scale} width={width} height={lines.length * lineSize * 1.2 * scale} style={{textAlign: align}}>{lines.join('\n')}</CardCopy>}
  </div>;
};
