// EP.01 v6 RememberScene's note window, extracted as a reusable component.
import React from 'react';
import {MONO, P} from '../theme';
import {Copy, fitSize, textWidth, UIProps} from './ui';
export const NotepadWindow: React.FC<UIProps> = ({e, canvas}) => {
  const compact = e.w < 600;
  const showTitleBar = e.titleBar !== false;
  const padding = compact ? 14 : 32;
  const text = String(e.line ?? e.text ?? '');
  const red = e.highlightColor ?? (e.highlight || e.state === 'handshakeAborted' ? P.danger : undefined);
  const desired = e.fontSize ?? (compact ? 30 : 40);
  const parts = textWidth(text, desired, true) <= e.w - padding * 2 - 20 ? [text] : text.split(' → ');
  const contentStyle: React.CSSProperties = e.contentBounds ? {position: 'absolute', left: e.contentBounds.x - e.x, top: e.contentBounds.y - e.y, width: e.contentBounds.w, height: e.contentBounds.h, padding: 14} : {flex: 1, padding};
  return <div style={{position: 'relative', boxSizing: 'border-box', width: '100%', height: '100%', border: `3px solid ${canvas ? 'transparent' : P.muted}`, borderRadius: canvas ? 0 : 18, background: canvas ? 'transparent' : P.panel, color: P.text, display: 'flex', flexDirection: 'column'}}>
    {/* Hidden title contents retain the exact height, including wrapped cover titles. */}
    {showTitleBar && <div style={{minHeight: compact ? 62 : 86, padding: compact ? '8px 12px' : '0 26px', display: 'flex', alignItems: 'center', gap: compact ? 10 : 18, background: P.panel2, borderBottom: `2px solid ${P.muted}`, borderRadius: '14px 14px 0 0', boxSizing: 'border-box', ...(canvas ? {visibility: 'hidden'} : {})}}>
      {!compact && <svg width={34} height={42} viewBox="0 0 34 42" fill="none" stroke={P.primary} strokeWidth={3} aria-hidden="true"><rect x={3} y={2} width={28} height={38} rx={3} /><path d="M9 13h16M9 21h16M9 29h11" /></svg>}
      <span style={{fontSize: fitSize(e.title ?? '', e.w - (compact ? 30 : 150), 40), fontWeight: 700, flex: 1, whiteSpace: compact ? 'normal' : 'nowrap', lineHeight: 1.2}}>{e.title}</span>
      {!compact && <span style={{color: P.text2, fontSize: 36}} aria-hidden="true">− ×</span>}
    </div>}
    {canvas && e.contentBounds && <div style={{flex: 1, minHeight: 0, background: P.panel, borderRadius: 14}} />}
    <div style={{...contentStyle, boxSizing: 'border-box', minHeight: 0, display: 'flex', justifyContent: 'center', flexDirection: 'column', gap: compact ? 16 : 24, fontFamily: MONO, ...(canvas && !e.contentBounds ? {background: P.panel, borderRadius: 14} : {})}}>
      {parts.map((part, i) => <Copy key={i} size={fitSize((i ? '→ ' : '') + part, e.w - padding * 2 - 24, desired, true)} mono style={{lineHeight: 1.4, color: red ?? (i ? P.success : P.text)}}>{i ? '→ ' : ''}{e.highlight && /qwer1234/.test(part) ? <>{part.split('qwer1234')[0]}<span data-password-highlight="qwer1234" style={{border: `3px solid ${P.danger}`, borderRadius: 6, padding: '4px 6px', color: P.danger, whiteSpace: 'nowrap'}}>qwer1234</span>{part.split('qwer1234')[1]}</> : part}</Copy>)}
    </div>
  </div>;
};
