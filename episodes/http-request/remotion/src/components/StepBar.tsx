import React from 'react';
import {FONT, P} from '../theme';
import {Lock} from './Legacy';

const LABELS = ['查缓存', '找地址', '建连接', '发请求', '画页面'];

const StepIcon: React.FC<{index: number; color: string}> = ({index, color}) => {
  if (index === 0) return <svg width="100%" height="100%" viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth={6} strokeLinejoin="round"><path d="M20 8h44l17 17v66H20Z" /><path d="M64 8v19h17M30 71l16-22 12 13 12-18 10 27Z" /><circle cx={39} cy={35} r={6} fill={color} stroke="none" /></svg>;
  if (index === 2) return <Lock color={color} />;
  return <svg width="100%" height="100%" viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {index === 1 ? <><rect x={15} y={12} width={70} height={78} rx={9} /><path d="M32 6v16M50 6v16M68 6v16M30 42h40M30 58h40M30 74h25" /></> : index === 3 ? <><rect x={7} y={22} width={86} height={57} rx={6} /><path d="M7 40h86M46 40v39M70 40v39M17 59h19M54 59h8" /><circle cx={81} cy={59} r={4} fill={color} stroke="none" /></> : <><rect x={8} y={14} width={84} height={74} rx={8} /><path d="M8 33h84M25 50h50M25 63h28" /><rect x={25} y={72} width={25} height={6} fill={color} stroke="none" /></>}
  </svg>;
};

export const StepBar: React.FC<{activeCount?: number; labels?: readonly string[]}> = ({activeCount = 0, labels = LABELS}) => (
  <div style={{width: '100%', height: '100%', display: 'flex', alignItems: 'center', fontFamily: FONT}}>
    {labels.map((label, i) => {
      const color = i < activeCount ? P.primary : P.muted;
      return <React.Fragment key={label}>
        {i > 0 && <div style={{height: 5, flex: 0.35, background: color, marginBottom: 48, borderRadius: 3}} />}
        <div style={{flex: 1, display: 'flex', alignItems: 'center', flexDirection: 'column', gap: 18, color}}>
          <div style={{width: 100, height: 100, padding: 18, border: `3px solid ${color}`, borderRadius: 22, background: i < activeCount ? `${P.primary}12` : P.panel}}><StepIcon index={i} color={color} /></div>
          <div style={{fontSize: 36, fontWeight: 700, whiteSpace: 'nowrap'}}>{label}</div>
        </div>
      </React.Fragment>;
    })}
  </div>
);
