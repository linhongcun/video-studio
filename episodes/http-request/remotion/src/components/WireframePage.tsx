import React from 'react';
import {FONT, P} from '../theme';

export type WireframePageProps = {highlight?: 'title' | 'text' | 'button' | null; highlightElementId?: string; highlightStyle?: React.CSSProperties};

export const WireframePage: React.FC<WireframePageProps> = ({highlight = null, highlightElementId, highlightStyle}) => {
  const block = (id: NonNullable<WireframePageProps['highlight']>, width: string, height: string): React.CSSProperties => ({
    width, height, borderRadius: 12, position: 'relative', background: !highlightElementId && highlight === id ? P.primary : P.muted,
    boxShadow: !highlightElementId && highlight === id ? `0 0 0 8px ${P.primary}33` : undefined,
  });
  const glow = (id: NonNullable<WireframePageProps['highlight']>, marker = true) => highlightElementId && (highlight === id || (!highlight && id === 'title')) ? <div data-element={marker ? highlightElementId : undefined} data-component={marker ? 'BlockHighlight' : undefined} style={{position: 'absolute', inset: 0, borderRadius: 12, background: P.primary, boxShadow: `0 0 0 8px ${P.primary}33`, ...highlightStyle, opacity: highlight === id ? highlightStyle?.opacity ?? 1 : 0}} /> : null;
  return (
    <div style={{width: '100%', height: '100%', padding: '7%', boxSizing: 'border-box', background: P.panel, border: `3px solid ${P.muted}`, borderRadius: 18, fontFamily: FONT, position: 'relative'}}>
      <div style={{position: 'absolute', right: '6%', top: '4%', color: P.text2, fontSize: 25}}>示意图</div>
      <div style={{...block('title', '70%', '12%'), marginTop: '12%'}}>{glow('title')}</div>
      <div style={{marginTop: '9%', height: '30%', display: 'flex', flexDirection: 'column', gap: '18%'}}>
        {['96%', '90%', '72%'].map((width, i) => <div key={i} style={block('text', width, '13%')}>{glow('text', i === 0)}</div>)}
      </div>
      <div style={{...block('button', '42%', '14%'), marginTop: '9%'}}>{glow('button')}</div>
    </div>
  );
};
