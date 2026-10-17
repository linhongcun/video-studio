import React from 'react';
import {FONT, P} from '../theme';
import {Copy, colorToken, stateAt, UIProps} from './ui';
import {Spinner} from './Spinner';
import {browserHeaderHeight} from './browserLayout';

export const BrowserChrome: React.FC<UIProps> = ({e: original, frame, source, siblings = [], browserContentLayout: layout}) => {
  const e = stateAt(original, frame), compact = e.w < 600;
  const dockedPanels = siblings.map(sibling => stateAt(sibling, frame)).filter(sibling => {
    return sibling.component === 'DevToolsNetwork' && sibling.layout === 'docked'
      && frame >= (sibling.appearFrame ?? 0) && frame < (sibling.disappearFrame ?? Infinity) && sibling.state !== 'hidden'
      && sibling.x < e.x + e.w && sibling.x + sibling.w > e.x && sibling.y >= e.y && sibling.y < e.y + e.h;
  });
  const docked = dockedPanels.length > 0;
  const headerHeight = browserHeaderHeight(e);
  const shop = layout?.shop, login = layout?.login;
  const pageHeight = e.h - headerHeight - 6;
  const panelTop = Math.min(e.y + e.h, ...dockedPanels.map(s => s.y));
  const availableHeight = panelTop - e.y - headerHeight - 6;
  const siblingNote = siblings.map(s => stateAt(s, frame)).find(s => s.pageNote && frame >= (s.appearFrame ?? 0) && frame < (s.disappearFrame ?? Infinity) && s.state !== 'hidden');
  const pageNote = e.pageNote ?? siblingNote?.pageNote;
  const pageNoteColor = e.pageNoteColor ?? siblingNote?.pageNoteColor;
  const reloading = e.state === 'reloaded' ? false : !!e.reloading;
  // A press belongs to its authored state and releases at the next state cue.
  const currentState = [...(e.stateKeyframes ?? [])].filter(key => key.frame <= frame).sort((a, b) => b.frame - a.frame)[0];
  const loginPressed = e.pressed === 'login' && (!currentState || currentState.pressed === 'login');
  const loginPressStyle: React.CSSProperties = loginPressed ? {transform: 'translateY(3px) scale(.96)', boxShadow: `inset 0 3px 8px ${P.bg}`, filter: 'brightness(.85)'} : {};
  const tabWidth = compact ? e.w - 32 : Math.min(160, e.w * .2);
  const addressWidth = compact ? e.w - 44 : e.w - tabWidth - 132;
  // Integrate speed over the authored states so slowing down never jumps the rotor.
  let rotor = 0, previousFrame = 0, speed = (source ?? original).spinnerSpeed ?? 1;
  for (const key of [...(original.stateKeyframes ?? [])].sort((a, b) => a.frame - b.frame)) {
    if (key.frame > frame) break;
    rotor += Math.max(0, key.frame - previousFrame) * speed;
    previousFrame = key.frame;
    speed = key.spinnerSpeed ?? speed;
  }
  rotor += (frame - previousFrame) * speed;
  const cardsVisible = !e.stateKeyframes?.some(key => key.state === 'cardsShown') || e.state === 'cardsShown';
  const userBadge = e.userBadge && <div data-user-badge style={{marginBottom: shop?.gap ?? (compact ? 8 : 16), padding: '4px 8px', borderRadius: 8, background: P.panel2, color: P.success}}><Copy mono size={shop?.fontSize ?? (compact ? 24 : 36)} width={e.w - 94} height={shop ? shop.badgeHeight - 8 : Math.min(48, pageHeight * .24)} style={shop ? {whiteSpace: 'nowrap'} : undefined}>{e.userBadge}</Copy></div>;
  return <div data-browser-title={e.title} data-reloading={reloading} data-conflict={e.conflict || undefined} data-sample-data={e.sampleData || undefined} data-page-blank={!!e.pageBlank} style={{width: '100%', height: '100%', position: 'relative', display: 'flex', flexDirection: 'column', boxSizing: 'border-box', border: `3px solid ${P.muted}`, borderRadius: 18, overflow: 'hidden', background: P.panel, color: P.text, fontFamily: FONT, boxShadow: `0 0 24px ${P.secondary}22`}}>
    <div style={{height: headerHeight, flexShrink: 0, display: 'flex', flexDirection: compact ? 'column' : 'row', alignItems: compact ? 'stretch' : 'center', gap: compact ? 6 : 12, padding: compact ? '8px 16px' : '8px 16px 8px 8px', boxSizing: 'border-box', background: P.panel2, borderBottom: `2px solid ${P.muted}`}}>
      <div style={{width: tabWidth, minWidth: 0, height: compact ? 38 : '100%', display: 'flex', alignItems: 'center', gap: 10, padding: '0 8px', boxSizing: 'border-box', background: P.panel, borderRadius: 10, flexShrink: 0}}>
        {e.tabLoading || reloading ? <div data-tab-loading data-spinner-speed={e.spinnerSpeed ?? 1} style={{width: 26, height: 26, flexShrink: 0}}><Spinner frame={rotor} /></div> : <div style={{width: 22, height: 22, flexShrink: 0, background: P.primary, borderRadius: 6}} />}
        <Copy size={compact ? 26 : 24} width={tabWidth - 52} style={{whiteSpace: 'nowrap', fontWeight: 700}}>{e.title}</Copy>
      </div>
      <div style={{display: 'flex', flex: 1, minWidth: 0, alignItems: 'center', gap: 8}}>
      <div role="button" aria-label="reload" aria-pressed={reloading} data-refresh-pressed={reloading} style={{width: compact ? 28 : 36, height: compact ? 28 : 36, flexShrink: 0, padding: 3, boxSizing: 'border-box', borderRadius: 6, background: reloading ? P.secondary : 'transparent', transform: reloading ? 'scale(.9)' : undefined, boxShadow: reloading ? `inset 0 2px 5px ${P.bg}` : undefined}}><svg width="100%" height="100%" viewBox="0 0 32 32" fill="none" stroke={P.text} strokeWidth={3}><path d="M25 12a10 10 0 1 0 0 10M25 4v8h-8" /></svg></div>
      <div data-address-box style={{flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', gap: 10, padding: '8px 12px', boxSizing: 'border-box', border: `2px solid ${P.muted}`, borderRadius: 10, background: P.bg}}>
        {e.showPadlock && <svg data-address-icon="lock" width={24} height={28} viewBox="0 0 32 36" style={{flexShrink: 0}} fill="none" stroke={P.success} strokeWidth={3}><path d="M8 15V10a8 8 0 0 1 16 0v5" /><rect x={4} y={14} width={24} height={20} rx={5} /></svg>}
        <Copy mono size={compact ? 26 : 32} width={addressWidth - (e.showPadlock ? 34 : 0)} style={{whiteSpace: 'nowrap'}}>{e.url ?? ''}</Copy>
      </div>
      </div>
      {!compact && <div aria-hidden style={{display: 'grid', gap: 5}}>{[0, 1, 2].map(i => <div key={i} style={{width: 22, height: 3, borderRadius: 2, background: P.text2}} />)}</div>}
    </div>
    <div data-page={e.page ?? (e.pageBlank ? 'blank' : undefined)} style={{position: 'relative', flex: 1, minHeight: 0, overflow: 'hidden', background: P.bg}}>
      {reloading && <div data-reload-indicator style={{position: 'absolute', left: 0, top: 0, width: `${25 + (frame % 30) / 30 * 75}%`, height: 3, background: P.primary, zIndex: 2}} />}
      {pageNote && <div data-page-note style={{position: 'absolute', left: '8%', right: '8%', bottom: Math.max(12, pageHeight - availableHeight + 12), display: 'flex', justifyContent: 'center', color: colorToken(pageNoteColor) ?? P.text2}}><Copy size={compact ? 24 : 40} width={e.w * .84} height={Math.min(52, pageHeight * .25)} style={{textAlign: 'center', fontWeight: 700}}>{pageNote}</Copy></div>}
      {!e.pageBlank && e.page === 'loginForm' && <div data-login-form data-content-height={layout?.height} style={{padding: `${login?.padding ?? 20}px 36px`, boxSizing: 'border-box', height: layout?.height ?? availableHeight, display: 'flex', flexDirection: 'column', gap: login?.gap ?? 20}}>
        <div style={login ? {height: login.titleHeight, flexShrink: 0, display: 'flex', alignItems: 'center'} : {display: 'contents'}}><Copy size={login?.titleSize ?? 42} width={e.w - 78} height={login?.titleHeight ?? Math.min(52, availableHeight * .2)} style={{fontWeight: 800, ...(login ? {whiteSpace: 'nowrap'} : {})}}>{e.pageTitle}</Copy></div>
        <div style={{display: 'flex', alignItems: 'center', gap: 24, flex: login ? undefined : 1, height: login ? login.rowHeight * 2 + login.rowGap : undefined, flexShrink: login ? 0 : undefined, minHeight: 0}}>
          <div style={{display: 'grid', gap: login?.rowGap ?? 12, flex: 1, minWidth: 0}}>{['account', 'password'].map(field => {
            const value = String(e.loginFields?.[field] ?? '');
            const masked = field === 'password' ? '•'.repeat(Array.from(value).length) : value;
            const height = login?.rowHeight ?? Math.min(64, Math.max(24, (availableHeight - 104) / 2));
            return <div key={field} role="textbox" aria-label={field} aria-readonly="true" data-login-field={field} style={{height, display: 'flex', alignItems: 'center', padding: '0 20px', boxSizing: 'border-box', border: `2px solid ${P.muted}`, borderRadius: 10, background: P.panel}}><Copy mono size={login?.fontSize ?? 36} width={e.w - 300} height={height - 4} style={login ? {whiteSpace: 'nowrap'} : undefined}>{masked}</Copy></div>;
          })}</div>
          <div role="button" aria-pressed={loginPressed} data-login-pressed={loginPressed} style={{padding: `${login?.buttonPadding ?? 12}px 28px`, borderRadius: 12, background: P.primary, color: P.bg, ...loginPressStyle}}><Copy size={login ? login.buttonSize : 32} width={100} height={login ? login.buttonSize * 1.2 : 48} style={login ? {whiteSpace: 'nowrap'} : undefined}>登录</Copy></div>
        </div>
      </div>}
      {!e.pageBlank && e.page === 'aboutNetworkingDns' && <div style={{padding: '28px 32px', boxSizing: 'border-box', height: '100%', overflow: 'hidden'}}>
        <div role="searchbox" style={{padding: '12px 18px', border: `2px solid ${P.muted}`, borderRadius: 10, background: P.panel, marginBottom: 24}}><Copy mono size={32} width={e.w - 108}>{e.searchText}</Copy></div>
        <div role="table" style={{border: `2px solid ${P.muted}`, borderRadius: 8, overflow: 'hidden'}}>
          <div role="row" style={{display: 'grid', gridTemplateColumns: '1fr 1fr', background: P.panel2, padding: 16, gap: 16}}>{['hostname', 'addresses'].map(label => <Copy key={label} mono size={30} width={(e.w - 132) / 2} style={{color: P.text2}}>{label}</Copy>)}</div>
          {(e.rows ?? []).map((row, i) => <div role="row" key={i} data-dns-record style={{display: 'grid', gridTemplateColumns: '1fr 1fr', padding: 16, gap: 16, borderTop: `1px solid ${P.muted}`, background: P.panel}}><Copy mono size={34} width={(e.w - 132) / 2} style={{color: P.primary}}>{row.hostname}</Copy><Copy mono size={34} width={(e.w - 132) / 2} style={{color: P.success}}>{row.addresses}</Copy></div>)}
          {!e.rows?.length && <div style={{padding: 28, textAlign: 'center', color: P.text2}}><Copy size={32} width={e.w - 132}>{e.emptyText}</Copy></div>}
        </div>
      </div>}
      {!e.pageBlank && e.page === 'shopDemo' && <div data-shop-page data-content-height={layout?.height} style={{padding: shop ? `${shop.padding}px ${compact ? 20 : 36}px` : compact ? '10px 20px' : docked ? '12px 36px' : '24px 36px', boxSizing: 'border-box'}}>
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 24, height: shop?.titleHeight, marginBottom: shop?.gap ?? (docked ? 8 : 20)}}><Copy size={shop?.titleSize ?? (compact ? 30 : docked ? 36 : 42)} width={e.w - (e.loginButton ? 280 : e.userBadge || siblings.some(s => s.id === 'user-badge') ? e.w * .48 : 80)} height={shop?.titleHeight} style={{fontWeight: 800, ...(shop ? {whiteSpace: 'nowrap'} : {})}}>{e.pageTitle}</Copy>{e.loginButton && <div role="button" aria-pressed={loginPressed} data-login-pressed={loginPressed} style={{borderRadius: 12, padding: shop ? `${shop.buttonPadding}px 24px` : docked ? '4px 24px' : '10px 28px', background: P.primary, color: P.bg, fontWeight: 700, ...loginPressStyle}}><Copy size={shop ? shop.buttonSize : 32} width={100} height={shop ? shop.buttonSize * 1.2 : 48} style={shop ? {whiteSpace: 'nowrap'} : undefined}>登录</Copy></div>}</div>
        {userBadge}
        {cardsVisible && !!e.cards?.length && <div data-shop-cards style={{display: 'flex', gap: 24, marginRight: layout?.cardsRightInset ? Math.max(0, layout.cardsRightInset - (compact ? 20 : 36)) : undefined}}>{(e.cards ?? []).map((card, i) => <div key={i} style={{flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', gap: shop?.rowPadding ?? (docked ? 16 : 24), padding: shop ? `${Math.min(shop.rowPadding, (shop.rowHeight - shop.fontSize * 1.2) / 2)}px ${shop.rowPadding}px` : docked ? '10px 20px' : 24, height: shop?.rowHeight ?? (docked ? 70 : 146), boxSizing: 'border-box', borderRadius: 14, background: P.panel2}}><svg width={shop?.iconSize ?? (docked ? 44 : 76)} height={shop?.iconSize ?? (docked ? 44 : 76)} viewBox="0 0 80 80" style={{flexShrink: 0}} fill={i % 2 ? P.secondary : P.primary} aria-hidden>{card.icon === 'triangle' ? <path d="M40 8 76 72H4Z" /> : card.icon === 'circle' ? <circle cx={40} cy={40} r={32} /> : null}</svg><Copy size={shop?.fontSize ?? (docked ? 32 : 36)} width={(e.w - 96) / Math.max(1, e.cards.length) - (shop ? shop.iconSize + shop.rowPadding * 3 : docked ? 100 : 148)} style={{fontWeight: 700, ...(shop || docked ? {whiteSpace: 'nowrap'} : {})}}>{card.title}</Copy></div>)}</div>}
      </div>}
      {!e.pageBlank && e.page !== 'shopDemo' && userBadge && <div style={{position: 'absolute', right: 36, top: 12, maxWidth: '48%'}}>{userBadge}</div>}
    </div>
  </div>;
};
