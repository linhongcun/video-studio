import React from 'react';
import {FONT, P} from '../theme';
import {Copy, UIProps} from './ui';
export const StyledPage: React.FC<UIProps> = ({e, frame}) => <div data-variant={e.variant} style={{width: '100%', height: '100%', boxSizing: 'border-box', padding: '20px 28px', display: 'flex', alignItems: 'center', gap: 12, border: `3px solid ${P.muted}`, borderRadius: 14, background: P.panel, color: P.text2, fontFamily: FONT}}>
  {e.cursorBlink && <span data-comment-cursor style={{height: '1.2em', fontSize: e.fontSize ?? 36, width: 3, flexShrink: 0, background: P.primary, opacity: Math.floor(frame / 15) % 2 === 0 ? 1 : 0}} />}
  <Copy size={e.fontSize ?? 36} width={e.w - 80} height={e.h - 46}>{e.variant === 'commentBox' ? e.placeholder : e.text ?? e.title}</Copy>
</div>;
