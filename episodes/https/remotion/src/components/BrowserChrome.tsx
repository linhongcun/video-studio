// Browser chrome ported from EP.01 v6; responsive text never shrinks below 24px.
import React from 'react';
import {FONT, MONO, P} from '../theme';
import {fitSize} from './ui';

export type BrowserChromeProps = {
  canvas?: boolean;
  width?: number; height?: number; chromeHeight?: number;
  title?: string; text?: string; typedChars?: number; loading?: boolean;
  showCursor?: boolean; showPadlock?: boolean; certificateOpen?: boolean;
  frame?: number; addressStyle?: React.CSSProperties; padlockStyle?: React.CSSProperties;
  addressElementId?: string; padlockElementId?: string; children?: React.ReactNode;
  connectionLabel?: string; errorTitle?: string; errorColor?: string;
  highlightText?: string; addressHighlighted?: boolean; lockHighlighted?: boolean;
  titleInset?: number; titleMaxWidth?: number;
  addressContent?: React.ReactNode; toolbarAccessory?: React.ReactNode; toolbarAccessoryWidth?: number;
};
export const Padlock: React.FC<{size: number}> = ({size}) => <svg width={size} height={size} viewBox="0 0 32 36" fill="none" aria-hidden="true"><path d="M8 15V10a8 8 0 0 1 16 0v5" stroke="currentColor" strokeWidth={3} /><rect x={4} y={14} width={24} height={20} rx={5} fill="currentColor" /><path d="M16 22v5" stroke={P.panel} strokeWidth={3} strokeLinecap="round" /></svg>;
export const HighlightedAddress: React.FC<{text: string; highlightText?: string}> = ({text, highlightText}) => {
  if (!highlightText || !text.includes(highlightText)) return <>{text}</>;
  const at = text.indexOf(highlightText);
  return <>{text.slice(0, at)}<span data-url-segment={highlightText} style={{color: P.danger, background: `${P.danger}22`, borderRadius: 4, boxShadow: `0 0 0 2px ${P.danger}`, fontWeight: 700}}>{highlightText}</span>{text.slice(at + highlightText.length)}</>;
};
export const BrowserChrome: React.FC<BrowserChromeProps> = ({width = 860, height = 580, chromeHeight, title = '', text = '', typedChars, loading = false, showCursor = false, showPadlock = false, frame = 0, addressStyle, padlockStyle, addressElementId, padlockElementId, children, connectionLabel, errorTitle, errorColor = P.danger, highlightText, addressHighlighted, lockHighlighted, titleInset = 0, titleMaxWidth, addressContent, toolbarAccessory, toolbarAccessoryWidth = 0, canvas}) => {
  const unit = Math.max(.65, Math.min(1.15, width / 860));
  const compact = width < 600;
  const visibleText = Array.from(text).slice(0, typedChars === undefined ? undefined : Math.max(0, Math.floor(typedChars))).join('');
  const toolbarGap = compact ? 6 : 18 * unit;
  const toolbarPadding = compact ? 4 : 22 * unit;
  const addressPadding = compact ? 2 : 18 * unit;
  const addressWidth = width - 2 * Math.max(2, 4 * unit) - 2 * toolbarPadding - 2 * addressPadding - 4
    - (compact ? 0 : 53 * unit + 2 * toolbarGap)
    - (showPadlock ? Math.max(26, 26 * unit) + 12 : 0)
    - (toolbarAccessory ? toolbarAccessoryWidth + toolbarGap : 0);
  const addressFont = fitSize(visibleText, addressWidth - 12, 29 * Math.max(1, unit), true);
  const lines = Math.max(1, Math.ceil(visibleText.length * addressFont * .61 / Math.max(1, addressWidth)));
  const tabHeight = Math.max(56, 60 * unit);
  const toolbarHeight = Math.max(76 * unit, lines * addressFont * 1.22 + 24);
  const headerHeight = chromeHeight ?? tabHeight + toolbarHeight;
  const tabWidth = Math.min(width - 32, titleMaxWidth ?? Math.max(340 * unit, title.length * 25 + titleInset + 54));
  return <div data-browser-title={title} data-error={errorTitle || undefined} style={{width, height, position: 'relative', display: 'flex', flexDirection: 'column', flexShrink: 0, boxSizing: 'border-box', border: `${Math.max(2, 4 * unit)}px solid ${canvas ? 'transparent' : P.muted}`, borderRadius: canvas ? 0 : 18 * unit, background: canvas ? 'transparent' : P.panel, color: P.text, fontFamily: FONT, boxShadow: canvas ? undefined : `0 0 ${24 * unit}px ${P.secondary}22`}}>
    {/* Separate spacers also preserve fractional flex rounding at every width. */}
    {canvas ? <><div style={{height: tabHeight, flexShrink: 0}} /><div style={{height: headerHeight - tabHeight, flexShrink: 0}} /></> : <><div style={{height: tabHeight, flexShrink: 0, display: 'flex', alignItems: 'flex-end', paddingLeft: 18 * unit, gap: 18 * unit}}>
      <div style={{width: tabWidth, minWidth: 0, minHeight: 44, height: tabHeight - 10, borderRadius: `${12 * unit}px ${12 * unit}px 0 0`, background: P.panel2, display: 'flex', alignItems: 'center', gap: 14 * unit, padding: `0 ${18 * unit}px 0 ${18 * unit + titleInset}px`, boxSizing: 'border-box'}}>
        {loading ? <svg width={26 * unit} height={26 * unit} viewBox="0 0 32 32" style={{flexShrink: 0, transform: `rotate(${frame * 10}deg)`}} aria-label="正在加载"><circle cx={16} cy={16} r={12} fill="none" stroke={P.muted} strokeWidth={4} /><path d="M16 4a12 12 0 0 1 12 12" fill="none" stroke={P.primary} strokeWidth={4} strokeLinecap="round" /></svg> : <div style={{width: 24 * unit, height: 24 * unit, flexShrink: 0, background: P.primary, borderRadius: 6 * unit}} />}
        <span style={{fontSize: fitSize(title, tabWidth - titleInset - 68 * unit, 24 * Math.max(1, unit)), lineHeight: 1, whiteSpace: 'nowrap'}}>{title}</span>
      </div><span style={{fontSize: 30, lineHeight: '44px', color: P.text2}} aria-hidden="true">+</span>
    </div>
    <div style={{height: headerHeight - tabHeight, flexShrink: 0, display: 'flex', alignItems: 'center', gap: toolbarGap, padding: `0 ${toolbarPadding}px`, background: P.panel2}}>
      {!compact && <svg width={30 * unit} height={30 * unit} viewBox="0 0 32 32" fill="none" stroke={P.text2} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m14 7-9 9 9 9M5 16h23" /></svg>}
      <div data-address-box style={{flex: 1, minWidth: 0, minHeight: 48 * unit, display: 'flex', alignItems: 'center', gap: 12, padding: `8px ${addressPadding}px`, background: P.bg, border: `2px solid ${showCursor || addressContent || addressHighlighted ? P.primary : P.muted}`, borderRadius: 10 * unit, boxSizing: 'border-box', boxShadow: addressHighlighted ? `0 0 0 5px ${P.primary}33` : undefined}}>
        {showPadlock && <span data-element={padlockElementId} data-address-icon="lock" style={{display: 'flex', flexShrink: 0, color: P.success, borderRadius: 6, boxShadow: lockHighlighted ? `0 0 0 5px ${P.primary}` : undefined, ...padlockStyle}}><Padlock size={Math.max(26, 26 * unit)} /></span>}
        <div data-element={addressElementId} style={{flex: 1, minWidth: 0, fontFamily: MONO, fontSize: addressFont, lineHeight: 1.22, overflowWrap: compact ? 'normal' : 'anywhere', whiteSpace: compact ? 'pre' : 'pre-wrap', ...addressStyle}}>{addressContent ?? <HighlightedAddress text={visibleText} highlightText={highlightText} />}{showCursor && <span style={{borderRight: `3px solid ${P.primary}`, marginLeft: 3, opacity: Math.floor(frame / 15) % 2 === 0 ? 1 : 0}} />}</div>
      </div>
      {toolbarAccessory && <div style={{width: toolbarAccessoryWidth, flexShrink: 0}}>{toolbarAccessory}</div>}
      {!compact && <div style={{display: 'flex', flexDirection: 'column', gap: 5}} aria-hidden="true">{[0, 1, 2].map(i => <div key={i} style={{width: 23 * unit, height: 3, borderRadius: 2, background: P.text2}} />)}</div>}
    </div>
    </>}
    <div style={{position: 'relative', flex: 1, minHeight: 0, borderRadius: canvas ? 0 : `0 0 ${13 * unit}px ${13 * unit}px`, background: canvas ? 'transparent' : P.bg}}>
      {connectionLabel && <div style={{padding: '12px 16px', fontSize: 24, color: '#FCA5A5'}}>{connectionLabel}</div>}
      {errorTitle ? <div data-page="error" style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24, boxSizing: 'border-box', color: errorColor, fontSize: Math.max(24, Math.min(52, width / 15)), fontWeight: 700}}>{errorTitle}</div> : children}
    </div>
  </div>;
};
