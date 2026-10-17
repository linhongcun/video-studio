import React from 'react';
import {FONT, P} from '../theme';

export const KeyCap: React.FC<{pressed?: boolean}> = ({pressed = false}) => (
  <div style={{width: '100%', height: '100%', boxSizing: 'border-box', paddingBottom: pressed ? 4 : 20, paddingTop: pressed ? 16 : 0, borderRadius: 24, background: P.muted, fontFamily: FONT}}>
    <div style={{height: '100%', boxSizing: 'border-box', padding: '8% 12%', border: `3px solid ${pressed ? P.primary : P.text2}`, borderRadius: 22, background: pressed ? P.secondary : P.panel2, color: P.text, display: 'flex', flexDirection: 'column', alignItems: 'flex-end', justifyContent: 'center', containerType: 'inline-size'}}>
      <span style={{fontSize: '48cqw', lineHeight: 1}}>↵</span><span style={{fontSize: '18cqw'}}>Enter</span>
    </div>
  </div>
);
