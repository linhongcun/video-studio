import React from 'react';
import {FONT, MONO, P} from '../theme';
import {Copy, colorToken, fitSize, stateAt, UIProps} from './ui';
import {Spinner} from './Spinner';

export const BrowserChrome: React.FC<UIProps> = ({e: original, frame, canvas, source, siblings = []}) => {
  const e = stateAt(original, frame), compact = e.w < 600;
  const docked = siblings.some(originalSibling => {
    const sibling = stateAt(originalSibling, frame);
    return sibling.component === 'DevToolsNetwork' && sibling.layout === 'docked'
      && frame >= (sibling.appearFrame ?? 0) && frame < (sibling.disappearFrame ?? Infinity) && sibling.state !== 'hidden'
      && sibling.x < e.x + e.w && sibling.x + sibling.w > e.x && sibling.y >= e.y && sibling.y < e.y + e.h;
  });
  const headerHeight = compact ? 110 : 80;
  const tabWidth = compact ? e.w - 32 : Math.min(160, e.w * .2);
  const addressWidth = compact ? e.w - 40 : e.w - tabWidth - 72;
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
  return <div data-browser-title={e.title} data-page-blank={!!e.pageBlank} style={{width: '100%', height: '100%', position: 'relative', display: 'flex', flexDirection: 'column', boxSizing: 'border-box', border: `3px solid ${canvas ? 'transparent' : P.muted}`, borderRadius: canvas ? 0 : 18, overflow: 'hidden', background: canvas ? 'transparent' : P.panel, color: P.text, fontFamily: FONT, boxShadow: canvas ? undefined : `0 0 24px ${P.secondary}22`}}>
    {canvas ? <div style={{height: headerHeight, flexShrink: 0}} /> : <div style={{height: headerHeight, flexShrink: 0, display: 'flex', flexDirection: compact ? 'column' : 'row', alignItems: compact ? 'stretch' : 'center', gap: compact ? 6 : 12, padding: compact ? '8px 16px' : '8px 16px 8px 8px', boxSizing: 'border-box', background: P.panel2, borderBottom: `2px solid ${P.muted}`}}>
      <div style={{width: tabWidth, minWidth: 0, height: compact ? 38 : '100%', display: 'flex', alignItems: 'center', gap: 10, padding: '0 8px', boxSizing: 'border-box', background: P.panel, borderRadius: 10, flexShrink: 0}}>
        {e.tabLoading ? <div data-tab-loading data-spinner-speed={e.spinnerSpeed ?? 1} style={{width: 26, height: 26, flexShrink: 0}}><Spinner frame={rotor} /></div> : <div style={{width: 22, height: 22, flexShrink: 0, background: P.primary, borderRadius: 6}} />}
        <Copy size={compact ? 26 : 24} width={tabWidth - 52} style={{whiteSpace: 'nowrap', fontWeight: 700}}>{e.title}</Copy>
      </div>
      <div data-address-box style={{flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', gap: 10, padding: '8px 12px', boxSizing: 'border-box', border: `2px solid ${P.muted}`, borderRadius: 10, background: P.bg}}>
        {e.showPadlock && <svg data-address-icon="lock" width={24} height={28} viewBox="0 0 32 36" style={{flexShrink: 0}} fill="none" stroke={P.success} strokeWidth={3}><path d="M8 15V10a8 8 0 0 1 16 0v5" /><rect x={4} y={14} width={24} height={20} rx={5} /></svg>}
        <Copy mono size={compact ? 26 : 32} width={addressWidth - (e.showPadlock ? 34 : 0)} style={{whiteSpace: 'nowrap'}}>{e.url ?? ''}</Copy>
      </div>
      {!compact && <div aria-hidden style={{display: 'grid', gap: 5}}>{[0, 1, 2].map(i => <div key={i} style={{width: 22, height: 3, borderRadius: 2, background: P.text2}} />)}</div>}
    </div>}
    <div data-page={e.page ?? (e.pageBlank ? 'blank' : undefined)} style={{position: 'relative', flex: 1, minHeight: 0, overflow: 'hidden', background: canvas ? 'transparent' : P.bg}}>
      {e.pageNote && <div data-page-note style={{position: 'absolute', inset: 0, padding: '8%', display: 'flex', alignItems: 'center', justifyContent: 'center', boxSizing: 'border-box', color: colorToken(e.pageNoteColor) ?? P.text2}}><Copy size={compact ? 36 : 52} width={e.w * .8} height={e.h - headerHeight} style={{textAlign: 'center', fontWeight: 700}}>{e.pageNote}</Copy></div>}
      {!e.pageBlank && e.page === 'aboutNetworkingDns' && <div style={{padding: '28px 32px', boxSizing: 'border-box', height: '100%', overflow: 'hidden'}}>
        <div role="searchbox" style={{padding: '12px 18px', border: `2px solid ${P.muted}`, borderRadius: 10, background: P.panel, marginBottom: 24}}><Copy mono size={32} width={e.w - 108}>{e.searchText}</Copy></div>
        <div role="table" style={{border: `2px solid ${P.muted}`, borderRadius: 8, overflow: 'hidden'}}>
          <div role="row" style={{display: 'grid', gridTemplateColumns: '1fr 1fr', background: P.panel2, padding: 16, gap: 16}}>{['hostname', 'addresses'].map(label => <Copy key={label} mono size={30} width={(e.w - 132) / 2} style={{color: P.text2}}>{label}</Copy>)}</div>
          {(e.rows ?? []).map((row, i) => <div role="row" key={i} data-dns-record style={{display: 'grid', gridTemplateColumns: '1fr 1fr', padding: 16, gap: 16, borderTop: `1px solid ${P.muted}`, background: P.panel}}><Copy mono size={34} width={(e.w - 132) / 2} style={{color: P.primary}}>{row.hostname}</Copy><Copy mono size={34} width={(e.w - 132) / 2} style={{color: P.success}}>{row.addresses}</Copy></div>)}
          {!e.rows?.length && <div style={{padding: 28, textAlign: 'center', color: P.text2}}><Copy size={32} width={e.w - 132}>{e.emptyText}</Copy></div>}
        </div>
      </div>}
      {!e.pageBlank && e.page === 'shopDemo' && <div style={{padding: docked ? '12px 36px' : '24px 36px', boxSizing: 'border-box'}}>
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 24, marginBottom: docked ? 8 : 20}}><Copy size={docked ? 36 : 42} width={e.w - (e.loginButton ? 280 : 80)} style={{fontWeight: 800}}>{e.pageTitle}</Copy>{e.loginButton && <div role="button" style={{borderRadius: 12, padding: docked ? '4px 24px' : '10px 28px', background: P.primary, color: P.bg, fontSize: 32, fontWeight: 700}}>登录</div>}</div>
        {cardsVisible && <div data-shop-cards style={{display: 'flex', gap: 24}}>{(e.cards ?? []).map((card, i) => <div key={i} style={{flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', gap: docked ? 16 : 24, padding: docked ? '10px 20px' : 24, height: docked ? 70 : 146, boxSizing: 'border-box', borderRadius: 14, background: P.panel2}}><svg width={docked ? 44 : 76} height={docked ? 44 : 76} viewBox="0 0 80 80" style={{flexShrink: 0}} fill={i % 2 ? P.secondary : P.primary} aria-hidden>{card.icon === 'triangle' ? <path d="M40 8 76 72H4Z" /> : card.icon === 'circle' ? <circle cx={40} cy={40} r={32} /> : null}</svg><Copy size={docked ? 32 : 36} width={(e.w - 96) / Math.max(1, e.cards.length) - (docked ? 100 : 148)} style={{fontWeight: 700, ...(docked ? {whiteSpace: 'nowrap'} : {})}}>{card.title}</Copy></div>)}</div>}
      </div>}
    </div>
  </div>;
};
