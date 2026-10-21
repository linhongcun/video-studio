import React from 'react';
import {FONT, P} from '../theme';
import {Folder} from './Legacy';
import {FileCard} from './FileCard';

export const FileManager: React.FC<{title?: string; canvas?: boolean; children?: React.ReactNode}> = ({title = '缓存', canvas = false, children}) => (
  <div style={{width: '100%', height: '100%', boxSizing: 'border-box', border: `3px solid ${canvas ? 'transparent' : P.muted}`, borderRadius: canvas ? 0 : 18, overflow: 'hidden', background: canvas ? 'transparent' : P.panel, color: P.text, fontFamily: FONT, display: 'flex', flexDirection: 'column'}}>
    {canvas ? <div style={{height: 70, flexShrink: 0}} /> : <div style={{height: 70, flexShrink: 0, padding: '0 28px', display: 'flex', alignItems: 'center', gap: 18, background: P.panel2, fontSize: 32}}>
      <div style={{width: 42, height: 42}}><Folder color={P.accent} /></div>{title}
      <div style={{marginLeft: 'auto', display: 'flex', gap: 12}}>{[0, 1, 2].map((i) => <div key={i} style={{width: 12, height: 12, borderRadius: 6, background: P.muted}} />)}</div>
    </div>}
    <div style={{...(canvas ? {background: P.panel, borderRadius: 14} : {}), flex: 1, minHeight: 0, padding: 28, display: 'flex', gap: 28}}>
      {children === undefined ? <>{['logo.png', 'style.css', 'old.css'].map((filename, i) => <div key={filename} style={{flex: 1, minWidth: 0}}><FileCard filename={filename} date={i === 2 ? '9月18日' : '10月12日'} state={i === 2 ? 'stale' : 'fresh'} /></div>)}</> : children}
    </div>
  </div>
);
