import React from 'react';
import {FONT, MONO, P} from '../theme';
import {Check} from './Legacy';
import {ImagePlaceholder} from './ImagePlaceholder';

export type FileCardProps = {
  filename?: string;
  date?: string;
  state?: 'fresh' | 'check' | 'stale';
  showExpiredBadge?: boolean;
};

export const FileCard: React.FC<FileCardProps> = ({filename = 'logo.png', date = '10月12日', state = 'fresh', showExpiredBadge = true}) => (
  <div style={{position: 'relative', width: '100%', height: '100%', boxSizing: 'border-box', padding: '7%', display: 'flex', flexDirection: 'column', gap: '7%', borderRadius: 18, border: `3px solid ${state === 'check' ? P.success : P.muted}`, background: P.panel2, color: state === 'stale' ? P.text2 : P.text, fontFamily: FONT, containerType: 'inline-size'}}>
    <div style={{flex: 1, minHeight: 0, filter: state === 'stale' ? 'grayscale(1)' : undefined, opacity: state === 'stale' ? 0.4 : 1}}><ImagePlaceholder progress={1} variant={filename.endsWith('.css') ? 'right' : 'left'} /></div>
    <div style={{fontFamily: MONO, fontSize: '9cqw', lineHeight: 1.2}}>{filename}</div>
    <div style={{fontSize: '7.5cqw', color: P.text2}}>{date}</div>
    {state === 'check' && <div style={{position: 'absolute', width: '18%', aspectRatio: '1', right: '3%', top: '3%'}}><Check color={P.success} /></div>}
    {state === 'stale' && <svg aria-label="旧文件" width="18%" height="18%" viewBox="0 0 60 60" style={{position: 'absolute', left: '5%', top: '5%'}}><circle cx={30} cy={30} r={26} fill={P.panel} stroke={P.text2} strokeWidth={5} /><path d="M30 13v18l12 8" fill="none" stroke={P.text2} strokeWidth={5} strokeLinecap="round" /></svg>}
    {state === 'stale' && showExpiredBadge && <div role="status" style={{position: 'absolute', right: '5%', top: '5%', padding: '4% 6%', borderRadius: 10, border: `3px solid ${P.danger}`, background: P.accent, color: P.bg, fontSize: '12cqw', lineHeight: 1.1, fontWeight: 900, boxShadow: `0 4px 16px ${P.bg}`}}>已过期</div>}
  </div>
);
