import React from 'react';
import {FONT, P} from '../theme';
import {Copy, colorToken, stateAt, UIProps} from './ui';
import {Spinner} from './Spinner';
import {browserHeaderHeight, compactBrowserHeaderHeight, fitLayout} from './browserLayout';
import {SaleDemoPage} from './SaleDemoPage';
import {ItemShopPage} from './ItemShopPage';
import {AdminItemPage} from './AdminItemPage';
import {OrderFlowPage} from './OrderFlowPage';
import {TicketBuyPage} from './TicketBuyPage';
import {PayCheckoutPage} from './PayCheckoutPage';
import {PayBillsPage} from './PayBillsPage';

export const BrowserChrome: React.FC<UIProps & {children?: React.ReactNode}> = ({e: original, frame, canvas, source, siblings = [], browserContentLayout: layout, children}) => {
  const e = stateAt(original, frame), compact = e.w < 600;
  const dockedPanels = siblings.map(sibling => stateAt(sibling, frame)).filter(sibling => {
    return sibling.component === 'DevToolsNetwork' && sibling.layout === 'docked'
      && frame >= (sibling.appearFrame ?? 0) && frame < (sibling.disappearFrame ?? Infinity) && sibling.state !== 'hidden'
      && sibling.x < e.x + e.w && sibling.x + sibling.w > e.x && sibling.y >= e.y && sibling.y < e.y + e.h;
  });
  const docked = dockedPanels.length > 0;
  const headerHeight = browserHeaderHeight(e);
  const fitCompactChrome = compact && headerHeight < compactBrowserHeaderHeight(e);
  // Fit both rows, their padding and gap inside the header's bottom border.
  const compactAddressHeight = 26 * 1.2 + 16 + 4;
  const chromeScale = fitCompactChrome ? (headerHeight - 2) / (16 + (38 + 6) * (1 + (e.backTabs?.length ?? 0) + (e.afterTabs?.length ?? 0)) + compactAddressHeight) : 1;
  const tabHeight = 38 * chromeScale;
  // cdn-v1 pageLayout 'topHalf': shop content fits above the WorldMap sibling inside this browser (else above the page midline).
  const topHalf = e.pageLayout === 'topHalf';
  const mapSibling = siblings.map(sibling => stateAt(sibling, frame)).find(s => s.component === 'WorldMap' && s.y > e.y && s.y < e.y + e.h && s.x < e.x + e.w && s.x + s.w > e.x);
  const topHalfHeight = Math.max(60, (mapSibling ? mapSibling.y : e.y + 3 + headerHeight + (e.h - headerHeight) / 2) - (e.y + 3 + headerHeight) - 12);
  // Compact windows without a precomputed layout (covers) fit the shop content above the page note.
  const compactHeight = e.h - headerHeight - 6 - (e.pageNote ? 64 : 0) - 8;
  const shop = topHalf ? fitLayout(topHalfHeight, false, !!e.loginButton || !!e.ordersEntry, !!e.userBadge) : layout?.shop ?? (compact && e.page === 'shopDemo' ? fitLayout(compactHeight, false, false, !!e.userBadge) : undefined), login = layout?.login;
  const shopAvail = topHalf ? topHalfHeight : layout?.height ?? (compact ? compactHeight : Infinity);
  // Hide the card row when the reserved page height cannot hold it (e.g. shot 21: page sits behind the next-episode title).
  const cardsFit = !shop || shopAvail >= shop.padding + shop.titleHeight + shop.gap + shop.rowHeight * .8;
  // Card buttons only when a card is wide enough to keep title + button legible.
  const cardWidth = (e.w - 96) / Math.max(1, e.cards?.length ?? 1);
  const showCardButtons = cardWidth >= 240;
  // Narrow cards (cover windows): stack a small button under the title instead of dropping it.
  const stackedButtonSize = Math.max(14, Math.min(20, Math.round((shop?.fontSize ?? 30) * .55)));
  // Stacked cards grow (up to the free page height under the row) so the title keeps its fitted size above the button.
  const stackedNeed = (shop?.fontSize ?? 30) * 1.2 + stackedButtonSize * 1.25 + 6 + 2 * Math.min(shop?.rowPadding ?? 10, 8);
  const stackedSpare = shop ? Math.max(0, shopAvail - (shop.padding + shop.titleHeight + shop.gap + shop.rowHeight) - (e.pageNote ? 8 : 0)) : 0;
  const stackedRowHeight = Math.max(shop?.rowHeight ?? 70, Math.min(stackedNeed, (shop?.rowHeight ?? 70) + stackedSpare));
  const stackedPad = Math.min(shop?.rowPadding ?? 10, 8);
  const stackedTitleHeight = Math.max(16, stackedRowHeight - 2 * stackedPad - stackedButtonSize * 1.25 - 6);
  // Title auto-fit: shrink the page title so it ends before any tag that starts to its right on the title row.
  const pageTopY = e.y + 3 + headerHeight, titleLeftX = e.x + 3 + (compact ? 20 : 36) + (e.shopLogo ? Math.round((shop?.titleHeight ?? (compact ? 36 : 50)) * (compact ? 1 : 1.3)) + 24 : 0);
  const titleRowBottom = pageTopY + (shop?.padding ?? 24) + Math.max(shop?.titleHeight ?? 50, 50) + 8;
  const blockers = siblings.filter(s => s.id !== e.id && (s.component === 'CalloutTag' || s.component === 'CornerBadge' || (s.type === 'text' && s.role !== 'subtitle')) && s.y < titleRowBottom && s.y + s.h > pageTopY && s.x > titleLeftX + 120 && s.x < e.x + e.w);
  const titleMaxWidth = blockers.length ? Math.min(...blockers.map(s => s.x)) - 16 - titleLeftX : Infinity;
  const logoSize = e.shopLogo ? Math.round((shop?.titleHeight ?? (compact ? 36 : 50)) * (compact ? 1 : 1.3)) : 0;
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
  const backTabs: string[] = e.backTabs ?? [];
  const afterTabs: string[] = e.afterTabs ?? [];
  const addressWidth = compact ? e.w - 44 : e.w - tabWidth * (backTabs.length + afterTabs.length + 1) - 132;
  const fittedTabWidth = fitCompactChrome ? e.w - 6 - 32 * chromeScale : tabWidth;
  const fittedAddressWidth = fitCompactChrome
    ? e.w - 6 - (32 + 28 + 8 + 24 + 4 + (e.showPadlock && e.url ? 34 : 0)) * chromeScale
    : addressWidth - (e.showPadlock && e.url ? 34 : 0);
  const inactiveTab = (title: string, key: string) => <div key={key} data-inactive-tab style={{width: fittedTabWidth, minWidth: 0, height: compact ? tabHeight : '100%', display: 'flex', alignItems: 'center', padding: `0 ${8 * chromeScale}px`, boxSizing: 'border-box', background: P.bg, color: P.text2, borderRadius: 10, flexShrink: 0}}><Copy size={compact ? 26 * chromeScale : 24} width={fittedTabWidth - 16 * chromeScale} height={fitCompactChrome ? tabHeight : undefined} style={{whiteSpace: 'nowrap'}}>{title}</Copy></div>;
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
  return <div data-browser-title={e.title} data-reloading={reloading} data-conflict={e.conflict || undefined} data-sample-data={e.sampleData || undefined} data-page-blank={!!e.pageBlank} style={{width: '100%', height: '100%', position: 'relative', display: 'flex', flexDirection: 'column', boxSizing: 'border-box', border: `3px solid ${canvas ? 'transparent' : P.muted}`, borderRadius: canvas ? 0 : 18, overflow: 'hidden', background: canvas ? 'transparent' : P.panel, color: P.text, fontFamily: FONT, boxShadow: canvas ? undefined : `0 0 24px ${P.secondary}22`}}>
    {/* Keep the header and border inset so authored page coordinates never move. */}
    {canvas ? <div style={{height: headerHeight, flexShrink: 0}} /> : <div style={{height: headerHeight, flexShrink: 0, display: 'flex', flexDirection: compact ? 'column' : 'row', alignItems: compact ? 'stretch' : 'center', gap: compact ? 6 * chromeScale : 12, padding: compact ? `${8 * chromeScale}px ${16 * chromeScale}px` : '8px 16px 8px 8px', boxSizing: 'border-box', background: P.panel2, borderBottom: `2px solid ${P.muted}`}}>
      {backTabs.map((title, i) => inactiveTab(title, `back-${i}`))}
      <div style={{width: fittedTabWidth, minWidth: 0, height: compact ? tabHeight : '100%', display: 'flex', alignItems: 'center', gap: 10 * chromeScale, padding: `0 ${8 * chromeScale}px`, boxSizing: 'border-box', background: P.panel, borderRadius: 10, flexShrink: 0}}>
        {e.tabLoading || reloading ? <div data-tab-loading data-spinner-speed={e.spinnerSpeed ?? 1} style={{width: 26 * chromeScale, height: 26 * chromeScale, flexShrink: 0}}><Spinner frame={rotor} /></div> : <div style={{width: 22 * chromeScale, height: 22 * chromeScale, flexShrink: 0, background: P.primary, borderRadius: 6}} />}
        <Copy size={compact ? 26 * chromeScale : 24} width={fittedTabWidth - 52 * chromeScale} height={fitCompactChrome ? tabHeight : undefined} style={{whiteSpace: 'nowrap', fontWeight: 700}}>{e.title}</Copy>
      </div>
      {afterTabs.map((title, i) => inactiveTab(title, `after-${i}`))}
      <div style={{display: 'flex', flex: 1, minWidth: 0, alignItems: 'center', gap: 8 * chromeScale}}>
      <div role="button" aria-label="reload" aria-pressed={reloading} data-refresh-pressed={reloading} style={{width: compact ? 28 * chromeScale : 36, height: compact ? 28 * chromeScale : 36, flexShrink: 0, padding: 3 * chromeScale, boxSizing: 'border-box', borderRadius: 6, background: reloading ? P.secondary : 'transparent', transform: reloading ? 'scale(.9)' : undefined, boxShadow: reloading ? `inset 0 2px 5px ${P.bg}` : undefined}}><svg width="100%" height="100%" viewBox="0 0 32 32" fill="none" stroke={P.text} strokeWidth={3}><path d="M25 12a10 10 0 1 0 0 10M25 4v8h-8" /></svg></div>
      <div data-address-box style={{flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', gap: 10 * chromeScale, padding: `${8 * chromeScale}px ${12 * chromeScale}px`, boxSizing: 'border-box', border: `${2 * chromeScale}px solid ${P.muted}`, borderRadius: 10, background: P.bg}}>
        {e.showPadlock && !!e.url && <svg data-address-icon="lock" width={24 * chromeScale} height={28 * chromeScale} viewBox="0 0 32 36" style={{flexShrink: 0}} fill="none" stroke={P.success} strokeWidth={3}><path d="M8 15V10a8 8 0 0 1 16 0v5" /><rect x={4} y={14} width={24} height={20} rx={5} /></svg>}
        <Copy mono size={compact ? 26 * chromeScale : 32} width={fittedAddressWidth} height={fitCompactChrome ? 26 * 1.2 * chromeScale : undefined} style={{whiteSpace: 'nowrap'}}>{e.url ?? ''}</Copy>
      </div>
      </div>
      {!compact && <div aria-hidden style={{display: 'grid', gap: 5}}>{[0, 1, 2].map(i => <div key={i} style={{width: 22, height: 3, borderRadius: 2, background: P.text2}} />)}</div>}
    </div>}
    <div data-page={e.page ?? (e.pageBlank ? 'blank' : undefined)} style={{position: 'relative', flex: 1, minHeight: 0, overflow: 'hidden', background: canvas ? 'transparent' : P.bg}}>
      {!canvas && reloading && <div data-reload-indicator style={{position: 'absolute', left: 0, top: 0, width: `${25 + (frame % 30) / 30 * 75}%`, height: 3, background: P.primary, zIndex: 2}} />}
      {children}
      {!e.pageBlank && (e.page === 'itemShop' || e.page === 'ordersPage') && <ItemShopPage e={e} frame={frame} rotor={rotor} />}
      {!e.pageBlank && e.page === 'adminItem' && <AdminItemPage e={e} frame={frame} />}
      {!e.pageBlank && e.page === 'orderFlow' && <OrderFlowPage e={e} frame={frame} />}
      {!e.pageBlank && e.page === 'ticketBuy' && <TicketBuyPage e={e} frame={frame} />}
      {!e.pageBlank && e.page === 'payCheckout' && <PayCheckoutPage e={e} frame={frame} />}
      {!e.pageBlank && e.page === 'payBills' && <PayBillsPage e={e} frame={frame} />}
      {!e.pageBlank && e.page === 'saleDemo' && <SaleDemoPage e={e} source={source ?? original} frame={frame} canvas={canvas} rotor={rotor} />}
      {!e.pageBlank && pageNote && <div data-page-note style={{position: 'absolute', left: '8%', right: '8%', bottom: Math.max(12, pageHeight - availableHeight + 12), display: 'flex', justifyContent: 'center', color: colorToken(pageNoteColor) ?? P.text2}}><Copy size={compact ? 24 : 40} width={e.w * .84} height={Math.min(52, pageHeight * .25)} style={{textAlign: 'center', fontWeight: 700}}>{pageNote}</Copy></div>}
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
      {!e.pageBlank && e.page === 'shopDemo' && <div data-shop-page data-anchor="shopPage" data-page-layout={e.pageLayout} data-content-height={layout?.height} style={{padding: shop ? `${shop.padding}px ${compact ? 20 : 36}px` : compact ? '10px 20px' : docked ? '12px 36px' : '24px 36px', boxSizing: 'border-box'}}>
        <div style={{display: 'flex', alignItems: 'center', justifyContent: e.loginButton ? 'space-between' : 'flex-start', gap: 24, height: Math.max(shop?.titleHeight ?? 0, logoSize) || undefined, marginBottom: shop?.gap ?? (docked ? 8 : 20)}}>{e.shopLogo && <div data-anchor="shopLogo" data-logo-loading={e.logoLoading || undefined} aria-label="商店标志" style={{width: logoSize, height: logoSize, flexShrink: 0, borderRadius: logoSize * .22, overflow: 'hidden', position: 'relative', background: e.logoLoading ? '#334155' : `linear-gradient(135deg, ${P.primary}, ${P.secondary})`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{e.logoLoading ? <div data-logo-shimmer style={{position: 'absolute', top: 0, bottom: 0, width: '45%', left: `${((frame % 40) / 40) * 160 - 50}%`, background: 'linear-gradient(90deg, transparent, #94A3B855, transparent)'}} /> : <svg width="64%" height="64%" viewBox="0 0 40 40" aria-hidden><path d="M8 14h24l-2.5 20h-19Z" fill={P.bg} /><path d="M14 14v-3a6 6 0 0 1 12 0v3" fill="none" stroke={P.bg} strokeWidth={3.2} /></svg>}</div>}<Copy size={shop?.titleSize ?? (compact ? 30 : docked ? 36 : 42)} width={Math.min(titleMaxWidth, e.w - logoSize - (e.shopLogo ? 24 : 0) - (e.loginButton ? 280 : e.ordersEntry ? 300 : e.userBadge || siblings.some(s => s.id === 'user-badge') ? e.w * .48 : 80))} height={shop?.titleHeight} style={{fontWeight: 800, ...(shop ? {whiteSpace: 'nowrap'} : {})}}>{e.pageTitle}</Copy>{e.loginButton && <div role="button" aria-pressed={loginPressed} data-login-pressed={loginPressed} style={{borderRadius: 12, padding: shop ? `${shop.buttonPadding}px 24px` : docked ? '4px 24px' : '10px 28px', background: P.primary, color: P.bg, fontWeight: 700, ...loginPressStyle}}><Copy size={shop ? shop.buttonSize : 32} width={100} height={shop ? shop.buttonSize * 1.2 : 48} style={shop ? {whiteSpace: 'nowrap'} : undefined}>登录</Copy></div>}{e.ordersEntry && <div data-orders-entry data-disabled={e.ordersEntry.disabled || undefined} style={{marginLeft: 'auto', flexShrink: 0, borderRadius: 12, padding: shop ? `${shop.buttonPadding}px 24px` : '8px 24px', border: `2px solid ${P.muted}`, color: e.ordersEntry.disabled ? P.muted : P.text, background: e.ordersEntry.disabled ? 'transparent' : P.panel2, opacity: e.ordersEntry.disabled ? .75 : 1, fontWeight: 700}}><Copy size={shop ? shop.buttonSize : 32} width={220} height={shop ? shop.buttonSize * 1.2 : 48} style={{whiteSpace: 'nowrap'}}>{e.ordersEntry.text}</Copy></div>}</div>
        {userBadge}
        {cardsVisible && cardsFit && !!e.cards?.length && <div data-shop-cards style={{display: 'flex', gap: 24, marginRight: layout?.cardsRightInset ? Math.max(0, layout.cardsRightInset - (compact ? 20 : 36)) : undefined}}>{(e.cards ?? []).map((card, i) => <div key={i} style={{flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', gap: shop?.rowPadding ?? (docked ? 16 : 24), padding: shop ? `${card.button && !showCardButtons ? stackedPad : Math.min(shop.rowPadding, (shop.rowHeight - shop.fontSize * 1.2) / 2)}px ${shop.rowPadding}px` : docked ? '10px 20px' : 24, height: card.button && !showCardButtons && shop ? stackedRowHeight : shop?.rowHeight ?? (docked ? 70 : 146), boxSizing: 'border-box', borderRadius: 14, background: P.panel2}}><svg width={shop?.iconSize ?? (docked ? 44 : 76)} height={shop?.iconSize ?? (docked ? 44 : 76)} viewBox="0 0 80 80" style={{flexShrink: 0}} fill={i % 2 ? P.secondary : P.primary} aria-hidden>{card.icon === 'triangle' ? <path d="M40 8 76 72H4Z" /> : card.icon === 'circle' ? <circle cx={40} cy={40} r={32} /> : null}</svg><div data-card-text style={card.button && !showCardButtons ? {display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4, minWidth: 0, flex: 1} : {display: 'contents'}}><Copy size={shop?.fontSize ?? (docked ? 32 : 36)} width={(e.w - 96) / Math.max(1, e.cards.length) - (shop ? shop.iconSize + shop.rowPadding * 3 : docked ? 100 : 148) - (card.button && showCardButtons ? (shop?.buttonSize ?? (compact ? 20 : 28)) * 4.6 + 36 : 0)} height={card.button && !showCardButtons ? stackedTitleHeight : undefined} style={{fontWeight: 700, ...(shop || docked ? {whiteSpace: 'nowrap'} : {})}}>{card.title}</Copy>{card.button && !showCardButtons && <div data-anchor="cardButton" data-stacked role="button" style={{borderRadius: 8, padding: '1px 8px', background: P.secondary, color: '#FFFFFF', fontWeight: 700}}><Copy size={stackedButtonSize} width={stackedButtonSize * 4.4} height={stackedButtonSize * 1.25} style={{whiteSpace: 'nowrap'}}>{card.button}</Copy></div>}</div>{card.button && showCardButtons && <div data-anchor="cardButton" role="button" style={{marginLeft: 'auto', flexShrink: 0, borderRadius: 10, padding: compact ? '2px 8px' : '6px 16px', background: P.secondary, color: '#FFFFFF', fontWeight: 700}}><Copy size={compact ? Math.min(20, shop?.buttonSize ?? 20) : shop?.buttonSize ?? 28} width={(compact ? 20 : shop?.buttonSize ?? 28) * 4.4} height={(compact ? 20 : shop?.buttonSize ?? 28) * 1.25} style={{whiteSpace: 'nowrap'}}>{card.button}</Copy></div>}</div>)}</div>}
      </div>}
      {!e.pageBlank && e.page !== 'shopDemo' && userBadge && <div style={{position: 'absolute', right: 36, top: 12, maxWidth: '48%'}}>{userBadge}</div>}
      {e.dimPage > 0 && (e.pageBlank || (e.page !== 'itemShop' && e.page !== 'ordersPage')) && <div data-page-dim style={{position: 'absolute', inset: 0, background: P.bg, opacity: e.dimPage, pointerEvents: 'none', zIndex: 10}} />}
    </div>
  </div>;
};
