import React from 'react';
import {BrowserChrome} from './BrowserChrome';
import {StyledPage} from './StyledPage';
import {P} from '../theme';

export const Laptop: React.FC<{canvas?: boolean; width?: number; height?: number; loading?: boolean; loaded?: boolean; children?: React.ReactNode}> = ({width = 860, height = 560, loading = false, loaded = false, children}) => {
  const u = width / 860;
  return <div style={{width, height, position: 'relative'}}>
    <BrowserChrome width={width} height={height - 84 * u} loading={loading} showPadlock={loaded}>
      {children ?? (loaded ? <StyledPage /> : undefined)}
    </BrowserChrome>
    <div style={{height: 32 * u, borderRadius: `0 0 ${14 * u}px ${14 * u}px`, background: P.panel2, borderBottom: `${3 * u}px solid ${P.muted}`, boxSizing: 'border-box'}} />
    <svg width={908 * u} height={54 * u} viewBox="0 0 908 54" style={{display: 'block', marginLeft: -24 * u}} aria-hidden="true">
      <path d="M24 2h860l22 31q-10 17-40 17H42Q12 50 2 33Z" fill={P.panel2} stroke={P.muted} strokeWidth={3} strokeLinejoin="round" />
      <path d="M348 3h212l-12 15H360Z" fill={P.muted} /><path d="M8 34h892" stroke={P.muted} strokeWidth={3} />
    </svg>
  </div>;
};
