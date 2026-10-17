import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {FONT, MONO, P} from '../theme';

export type BrowserChromeProps = {
  width?: number;
  height?: number;
  /** Fit the chrome to short storyboard windows without overflowing the shell. */
  chromeHeight?: number;
  title?: string;
  text?: string;
  /** Number of visible characters. Omit to show the whole address. */
  typedChars?: number;
  loading?: boolean;
  showCursor?: boolean;
  showPadlock?: boolean;
  certificateOpen?: boolean;
  addressStyle?: React.CSSProperties;
  padlockStyle?: React.CSSProperties;
  addressElementId?: string;
  padlockElementId?: string;
  children?: React.ReactNode;
};

const Padlock: React.FC<{size: number}> = ({size}) => (
  <svg width={size} height={size} viewBox="0 0 32 36" fill="none" aria-hidden="true">
    <path d="M8 15V10a8 8 0 0 1 16 0v5" stroke="currentColor" strokeWidth={3} />
    <rect x={4} y={14} width={24} height={20} rx={5} fill="currentColor" />
    <path d="M16 22v5" stroke={P.panel} strokeWidth={3} strokeLinecap="round" />
  </svg>
);

/** Generic browser shell. Animation is tied to Remotion frames, never wall time. */
export const BrowserChrome: React.FC<BrowserChromeProps> = ({
  width = 860,
  height = 580,
  chromeHeight,
  title = 'example.com',
  text = 'example.com',
  typedChars,
  loading = false,
  showCursor = false,
  showPadlock = false,
  certificateOpen = false,
  addressStyle,
  padlockStyle,
  addressElementId,
  padlockElementId,
  children,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const unit = chromeHeight === undefined ? width / 860 : chromeHeight / 136;
  const visibleText = Array.from(text)
    .slice(0, typedChars === undefined ? undefined : Math.max(0, Math.floor(typedChars)))
    .join('');
  const cursorOn = Math.floor((frame / fps) * 2) % 2 === 0;

  return (
    <div
      style={{
        width,
        height,
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        flexShrink: 0,
        boxSizing: 'border-box',
        border: `${4 * unit}px solid ${P.muted}`,
        borderRadius: 18 * unit,
        background: P.panel,
        color: P.text,
        fontFamily: FONT,
        boxShadow: `0 0 ${24 * unit}px ${P.secondary}22`,
      }}
    >
      <div style={{height: 60 * unit, flexShrink: 0, display: 'flex', alignItems: 'flex-end', paddingLeft: 18 * unit, gap: 18 * unit}}>
        <div style={{width: 340 * unit, height: 48 * unit, borderRadius: `${12 * unit}px ${12 * unit}px 0 0`, background: P.panel2, display: 'flex', alignItems: 'center', gap: 14 * unit, padding: `0 ${18 * unit}px`, boxSizing: 'border-box'}}>
          {loading ? (
            <svg width={26 * unit} height={26 * unit} viewBox="0 0 32 32" style={{flexShrink: 0, transform: `rotate(${(frame / fps) * 300}deg)`}} aria-label="正在加载">
              <circle cx={16} cy={16} r={12} fill="none" stroke={P.muted} strokeWidth={4} />
              <path d="M16 4a12 12 0 0 1 12 12" fill="none" stroke={P.primary} strokeWidth={4} strokeLinecap="round" />
            </svg>
          ) : (
            <div style={{width: 24 * unit, height: 24 * unit, flexShrink: 0, background: P.primary, borderRadius: 6 * unit}} />
          )}
          <span style={{fontSize: 24 * unit, overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis'}}>{title}</span>
        </div>
        <span style={{fontSize: 30 * unit, lineHeight: `${48 * unit}px`, color: P.text2}} aria-hidden="true">+</span>
      </div>

      <div style={{height: 76 * unit, flexShrink: 0, display: 'flex', alignItems: 'center', gap: 18 * unit, padding: `0 ${22 * unit}px`, background: P.panel2}}>
        <svg width={30 * unit} height={30 * unit} viewBox="0 0 32 32" fill="none" stroke={P.text2} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="m14 7-9 9 9 9M5 16h23" />
        </svg>
        <div style={{flex: 1, minWidth: 0, height: 48 * unit, display: 'flex', alignItems: 'center', gap: 16 * unit, padding: `0 ${18 * unit}px`, background: P.bg, border: `${2 * unit}px solid ${showCursor ? P.primary : P.muted}`, borderRadius: 10 * unit, boxSizing: 'border-box'}}>
          {showPadlock && <span data-element={padlockElementId} data-component={padlockElementId ? 'LockIcon' : undefined} style={{display: 'flex', color: P.success, ...padlockStyle}}><Padlock size={26 * unit} /></span>}
          <div data-element={addressElementId} data-component={addressElementId ? 'AddressBarTyping' : undefined} style={{display: 'flex', alignItems: 'center', overflow: 'hidden', whiteSpace: 'pre', fontFamily: MONO, fontSize: 29 * unit, lineHeight: 1.2, ...addressStyle}}>
            <span>{visibleText}</span>
            {showCursor && <span style={{height: 31 * unit, width: 3 * unit, marginLeft: 3 * unit, flexShrink: 0, background: P.primary, opacity: cursorOn ? 1 : 0}} />}
          </div>
        </div>
        <div style={{display: 'flex', flexDirection: 'column', gap: 5 * unit}} aria-hidden="true">
          {[0, 1, 2].map((i) => <div key={i} style={{width: 23 * unit, height: 3 * unit, borderRadius: 2 * unit, background: P.text2}} />)}
        </div>
      </div>

      <div style={{position: 'relative', flex: 1, minHeight: 0, overflow: 'hidden', borderRadius: `0 0 ${13 * unit}px ${13 * unit}px`, background: P.bg}}>
        {children}
      </div>

      {certificateOpen && (
        <div role="status" style={{position: 'absolute', zIndex: 2, top: 128 * unit, left: 62 * unit, width: 540 * unit, boxSizing: 'border-box', padding: 28 * unit, background: P.panel, border: `${3 * unit}px solid ${P.success}`, borderRadius: 16 * unit, boxShadow: `0 ${12 * unit}px ${32 * unit}px ${P.bg}`}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 18 * unit, color: P.success, fontSize: 34 * unit, fontWeight: 700}}>
            <Padlock size={36 * unit} />连接是安全的
          </div>
          <div style={{height: 2 * unit, margin: `${22 * unit}px 0`, background: P.panel2}} />
          <div style={{fontSize: 28 * unit, color: P.text}}>证书有效</div>
          <div style={{fontFamily: MONO, fontSize: 28 * unit, color: P.text2, marginTop: 12 * unit}}>example.com</div>
        </div>
      )}
    </div>
  );
};
