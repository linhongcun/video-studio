import React from 'react';
import {FONT, MONO, P} from '../theme';

const CONTACTS = [
  {name: '妈妈', label: '手机', number: '138 0000 ****', color: P.primary},
  {name: '妈妈 · 家里', label: '家庭', number: '010 0000 ****', color: P.secondary},
  {name: '妈妈 · 备用', label: '手机', number: '139 0000 ****', color: P.accent},
] as const;

/** An intentionally generic contacts app with fictitious example numbers. */
export const PhoneContacts: React.FC<{width?: number; height?: number; query?: string; resultsOpacity?: number; singleResult?: boolean; focusSearch?: boolean; contact?: {name: string; number: string}; searchElementId?: string; resultsElementId?: string; searchStyle?: React.CSSProperties; resultsStyle?: React.CSSProperties}> = ({width, height, query = '妈妈', resultsOpacity = 1, singleResult = false, focusSearch = false, contact, searchElementId, resultsElementId, searchStyle, resultsStyle}) => (
  <div style={{position: 'relative', width: width ?? (focusSearch ? 880 : 560), height: height ?? (focusSearch ? 1250 : 944), boxSizing: 'border-box', border: `5px solid ${P.muted}`, borderRadius: 48, padding: focusSearch ? '64px 40px 36px' : '58px 26px 36px', background: P.panel, color: P.text, fontFamily: FONT, boxShadow: `0 0 28px ${P.secondary}22`}}>
    <div style={{position: 'absolute', top: 22, left: '40%', width: '20%', height: 8, borderRadius: 4, background: P.muted}} />
    <div style={{fontSize: focusSearch ? 52 : 46, fontWeight: 700, marginBottom: 32}}>通讯录</div>
    <div data-element={searchElementId} data-component={searchElementId ? 'SearchBox' : undefined} role="search" aria-label="搜索联系人" style={{height: focusSearch ? 120 : 80, display: 'flex', alignItems: 'center', gap: 24, padding: '0 26px', borderRadius: 14, border: `3px solid ${P.primary}`, background: P.bg, ...searchStyle}}>
      <svg width={32} height={32} viewBox="0 0 32 32" fill="none" stroke={P.primary} strokeWidth={3} strokeLinecap="round" aria-hidden="true"><circle cx={13} cy={13} r={9} /><path d="m20 20 8 8" /></svg>
      <span style={{fontSize: focusSearch ? 72 : 36, fontWeight: 700}}>{query}</span>
    </div>
    <div style={{margin: '32px 0 24px', fontSize: focusSearch ? 34 : 28, color: P.text2, opacity: resultsOpacity}}>找到 {singleResult ? 1 : 3} 位联系人</div>
    <div data-element={resultsElementId} data-component={resultsElementId ? 'ContactRow' : undefined} style={{display: 'flex', flexDirection: 'column', gap: 16, opacity: resultsOpacity, ...resultsStyle}}>
      {(contact ? [{...CONTACTS[0], ...contact}] : CONTACTS.slice(0, singleResult ? 1 : 3)).map((contact, i) => (
        <div key={contact.name} style={{padding: focusSearch ? '32px 26px' : '20px 18px', borderRadius: 16, background: P.panel2, borderLeft: `5px solid ${i === 0 ? P.primary : 'transparent'}`}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 16, marginBottom: 12}}>
            <div style={{width: 52, height: 52, borderRadius: 16, background: contact.color, color: P.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 30, fontWeight: 700}}>妈</div>
            <span style={{fontSize: focusSearch ? 64 : 32, fontWeight: 700}}>{contact.name}</span>
            <span style={{marginLeft: 'auto', color: P.text2, fontSize: focusSearch ? 34 : 28}}>{contact.label}</span>
          </div>
          <div style={{fontFamily: MONO, fontSize: focusSearch ? 62 : 30, whiteSpace: 'nowrap', marginTop: focusSearch ? 26 : 0, color: P.primary}}>{contact.number}</div>
        </div>
      ))}
    </div>
    <div style={{marginTop: 32, textAlign: 'center', color: P.text2, fontSize: focusSearch ? 34 : 28}}>示例联系人 · 虚构号码</div>
    <div style={{position: 'absolute', bottom: 18, left: 210, width: 130, height: 6, borderRadius: 3, background: P.muted}} />
  </div>
);
