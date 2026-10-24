import React from 'react';
import {C, FONT, MONO} from './theme';

export const clamp = (n: number) => Math.max(0, Math.min(1, n));
export const ease = (f: number, at: number, duration = 36) => {
  const p = clamp((f - at) / Math.max(1, duration));
  return p * p * (3 - 2 * p);
};
export const lerp = (a: number, b: number, p: number) => a + (b - a) * p;

export const Txt: React.FC<{
  children: React.ReactNode; x?: number; y?: number; size?: number;
  color?: string; alpha?: number; center?: boolean; width?: number;
  weight?: number; mono?: boolean;
}> = ({children, x = 130, y = 180, size = 44, color = C.text, alpha = 1,
  center = false, width, weight = 600, mono = false}) => <div style={{
  position: 'absolute', left: x, top: y, width, color, opacity: alpha,
  fontSize: size, fontWeight: weight, lineHeight: 1.35,
  fontFamily: mono ? MONO : FONT, whiteSpace: 'pre-line',
  textAlign: center ? 'center' : 'left',
  transform: center ? 'translateX(-50%)' : undefined,
}}>{children}</div>;

export const Ledger: React.FC<{
  label: string; value: React.ReactNode; state: string; detail?: string;
  x?: number; y?: number; color?: string; alpha?: number; width?: number;
  valueSize?: number; mono?: boolean;
}> = ({label, value, state, detail, x = 500, y = 330, color = C.text,
  alpha = 1, width = 470, valueSize = 100, mono = true}) => <div style={{
  position: 'absolute', left: x - width / 2, top: y, width, opacity: alpha,
  textAlign: 'center',
}}>
  <div style={{color: C.muted, fontSize: 25, lineHeight: 1.4}}>{label}</div>
  <div style={{height: 150, display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontFamily: mono ? MONO : FONT, fontSize: valueSize, fontWeight: 650, color}}>{value}</div>
  <div style={{height: 2, margin: '0 25px 19px', background: color, opacity: .7}}/>
  <div style={{fontSize: 30, lineHeight: 1.5, color}}>{state}</div>
  {detail && <div style={{fontSize: 23, lineHeight: 1.55, color: C.muted, marginTop: 13}}>{detail}</div>}
</div>;

export const Chip: React.FC<{
  children: React.ReactNode; x: number; y: number; width?: number;
  color?: string; alpha?: number; size?: number;
}> = ({children, x, y, width = 300, color = C.gold, alpha = 1, size = 27}) => <div style={{
  position: 'absolute', left: x - width / 2, top: y, width, boxSizing: 'border-box',
  padding: '14px 18px', minHeight: 64, border: `1.5px solid ${color}`,
  borderRadius: 12, background: C.bg, color, opacity: alpha,
  textAlign: 'center', fontSize: size, fontWeight: 550, lineHeight: 1.35,
}}>{children}</div>;

export const Line: React.FC<{
  x1: number; y1: number; x2: number; y2: number;
  p?: number; color?: string; alpha?: number; dashed?: boolean;
}> = ({x1, y1, x2, y2, p = 1, color = C.blue, alpha = 1, dashed = false}) => {
  const tx = lerp(x1, x2, clamp(p)), ty = lerp(y1, y2, clamp(p));
  return <svg width={1920} height={1080} style={{position: 'absolute', inset: 0,
    pointerEvents: 'none', opacity: alpha}}>
    <path d={`M${x1} ${y1}L${tx} ${ty}`} stroke={color} strokeWidth={2.5}
      strokeDasharray={dashed ? '9 8' : undefined} fill="none"/>
    {p >= .995 && <circle cx={x2} cy={y2} r={5} fill={color}/>}
  </svg>;
};

export const MovingChip: React.FC<{
  children: React.ReactNode; x1: number; y1: number; x2: number; y2: number;
  p: number; color?: string; alpha?: number; width?: number; arc?: number;
}> = ({children, x1, y1, x2, y2, p, color = C.gold, alpha = 1, width = 240, arc = 0}) =>
  <Chip x={lerp(x1, x2, p)} y={lerp(y1, y2, p) - arc * Math.sin(Math.PI * p)}
    width={width} color={color} alpha={alpha} size={25}>{children}</Chip>;

export const LocalBoundary: React.FC<{
  x: number; y: number; w: number; h: number; p?: number;
  label?: string; color?: string; alpha?: number;
}> = ({x, y, w, h, p = 1, label = '同一笔本地事务', color = C.gold, alpha = 1}) => <>
  <svg width={1920} height={1080} style={{position: 'absolute', inset: 0,
    opacity: alpha, pointerEvents: 'none'}}>
    <path d={`M${x + 120} ${y}H${x + 20}Q${x} ${y} ${x} ${y + 20}V${y + h - 20}Q${x} ${y + h} ${x + 20} ${y + h}H${x + w - 20}Q${x + w} ${y + h} ${x + w} ${y + h - 20}V${y + 20}Q${x + w} ${y} ${x + w - 20} ${y}H${x + w - 120}`}
      fill="none" stroke={color} strokeWidth={2} pathLength={1}
      strokeDasharray={1} strokeDashoffset={1 - clamp(p)}/>
  </svg>
  <Txt x={x + w / 2} y={y - 20} center size={24} color={color} alpha={alpha}>
    {label}
  </Txt>
</>;

export const RuleLine: React.FC<{children: React.ReactNode; alpha?: number; color?: string}> =
  ({children, alpha = 1, color = C.muted}) => <>
    <div style={{position: 'absolute', left: 230, right: 230, top: 797,
      height: 1, background: C.edge, opacity: alpha}}/>
    <Txt x={960} y={822} center width={1600} size={31} color={color} alpha={alpha}>
      {children}
    </Txt>
  </>;

export const SmallLabel: React.FC<{children: React.ReactNode; x?: number; y?: number; alpha?: number; color?: string}> =
  ({children, x = 960, y = 695, alpha = 1, color = C.muted}) =>
    <Txt x={x} y={y} center size={25} color={color} alpha={alpha}>{children}</Txt>;

export const StageDots: React.FC<{current: number; y?: number}> = ({current, y = 126}) =>
  <div style={{position: 'absolute', top: y, left: 100, display: 'flex', gap: 10}}>
    {[1, 2, 3, 4, 5].map(n => <div key={n} style={{width: n === current ? 62 : 25,
      height: 4, borderRadius: 4, background: n === current ? C.teal : C.edge}}/>)}
  </div>;
