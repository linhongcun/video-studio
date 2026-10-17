// Drawings ported from ref-original-Main.tsx.
import React from 'react';
import {P, FONT} from '../theme';

export const ServerRack: React.FC<{color?: string; frame?: number; blinking?: boolean; size?: string}> = ({color = P.secondary, frame = 0, blinking = false, size}) => (
  <div style={{width: '100%', height: '100%', background: P.panel, border: `4px solid ${color}`, borderRadius: 18, padding: size === 'small' ? 12 : 24, boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: size === 'small' ? 12 : 18}}>
    {[0, 1, 2, 3].map((i) => (
      <div key={i} style={{flex: 1, minHeight: 0, background: P.panel2, borderRadius: 8, display: 'flex', alignItems: 'center', padding: size === 'small' ? '0 12px' : '0 20px', gap: size === 'small' ? 8 : 12}}>
        <div style={{width: size === 'small' ? 10 : 16, height: size === 'small' ? 10 : 16, flexShrink: 0, borderRadius: 8, background: P.success, boxShadow: `0 0 10px ${P.success}`, opacity: blinking ? 0.3 + 0.7 * (0.5 + 0.5 * Math.sin(frame / 4 + i * 2)) : 0.8}} />
        <div style={{flex: 1}} />
        {[0, 1, 2].map((j) => <div key={j} style={{width: size === 'small' ? 14 : 22, height: 6, flexShrink: 0, background: '#374151', borderRadius: 3}} />)}
      </div>
    ))}
  </div>
);

export const Gear: React.FC<{color: string}> = ({color}) => (
  <svg viewBox="-50 -50 100 100" width="100%" height="100%">
    {Array.from({length: 8}).map((_, i) => <rect key={i} x={-7} y={-46} width={14} height={20} rx={3} fill={color} transform={`rotate(${i * 45})`} />)}
    <circle r={30} fill={color} /><circle r={12} fill={P.bg} />
  </svg>
);

export const Folder: React.FC<{color: string; fileLift?: number}> = ({color, fileLift = 0}) => (
  <svg viewBox="0 0 200 180" width="100%" height="100%" style={{overflow: 'visible'}}>
    <path d="M10 40 h60 l15 15 h105 v115 h-180z" fill={color} opacity={0.9} />
    <rect x={60} y={10 - fileLift} width={80} height={100} rx={6} fill="#E5E7EB" />
  </svg>
);

export const Check: React.FC<{color: string}> = ({color}) => (
  <svg viewBox="0 0 100 100" width="100%" height="100%"><circle cx={50} cy={50} r={44} fill={color} /><path d="M28 52 L44 68 L73 36" fill="none" stroke={P.bg} strokeWidth={10} strokeLinecap="round" strokeLinejoin="round" /></svg>
);

export const Lock: React.FC<{color: string}> = ({color}) => (
  <svg viewBox="0 0 100 100" width="100%" height="100%"><path d="M30 44 V30 a20 20 0 0 1 40 0 V44" fill="none" stroke={color} strokeWidth={9} /><rect x={20} y={42} width={60} height={50} rx={9} fill={color} /><circle cx={50} cy={64} r={7} fill={P.bg} /><rect x={47} y={64} width={6} height={16} fill={P.bg} /></svg>
);

export const Arrow: React.FC<{e: any; progress: number; endY?: number; target?: any}> = ({e, progress, endY, target}) => {
  const color = e.color;
  if (e.curve !== undefined) {
    // 304 → 缓存抽屉的回折弧线
    const x1 = e.x, y1 = e.y, x2 = e.x - 140, y2 = e.y + e.h;
    const cx = x1 + 40, cy = y2 + 10;
    const d = `M${x1} ${y1} Q${cx} ${cy} ${x2} ${y2}`;
    return (
      <svg style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}} width={1920} height={1080}>
        <path d={d} fill="none" stroke={color} strokeWidth={5} strokeDasharray="1000" strokeDashoffset={1000 * (1 - progress)} pathLength={1000} />
        {progress > 0.95 && <polygon points={`${x2},${y2} ${x2 + 18},${y2 - 14} ${x2 + 20},${y2 + 8}`} fill={color} />}
        <text x={x1 + 30} y={y1 + e.h / 2 + 10} fill={color} fontFamily={FONT} fontSize={28} opacity={progress}>{e.label}</text>
      </svg>
    );
  }
  let x1: number, y1: number, x2: number, y2: number;
  if (e.direction === 'r' || e.direction === 'l') {
    const yy = e.y + e.h - 10;
    [x1, x2] = e.direction === 'r' ? [e.x, e.x + e.w] : [e.x + e.w, e.x];
    y1 = y2 = yy;
  } else {
    x1 = e.x; y1 = e.y; x2 = target ? target.x : e.x + e.w; y2 = endY ?? e.y + e.h;
    if (target) y2 = endY ?? target.y + target.h / 2;
  }
  const xe = x1 + (x2 - x1) * progress, ye = y1 + (y2 - y1) * progress;
  const ang = Math.atan2(y2 - y1, x2 - x1);
  const hl = 18;
  const lab = e.label;
  const small = e.h <= 30;
  return (
    <svg style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}} width={1920} height={1080}>
      <line x1={x1} y1={y1} x2={xe} y2={ye} stroke={color} strokeWidth={small ? 3 : 5} strokeLinecap="round" />
      {progress > 0.02 && (
        <polygon points={`${xe},${ye} ${xe - hl * Math.cos(ang - 0.45)},${ye - hl * Math.sin(ang - 0.45)} ${xe - hl * Math.cos(ang + 0.45)},${ye - hl * Math.sin(ang + 0.45)}`} fill={color} />
      )}
      {lab && (e.direction === 'r' || e.direction === 'l') && (
        <text x={(x1 + x2) / 2} y={y1 - (small ? 6 : 12)} textAnchor="middle" fill={color} fontFamily={FONT} fontSize={small ? 20 : 30} fontWeight={600} opacity={Math.min(1, progress * 2)}>{lab}</text>
      )}
      {lab && !(e.direction === 'r' || e.direction === 'l') && (
        <text x={x1 + (x2 - x1) * 0.45} y={y1 + (y2 - y1) * 0.45 - 14} textAnchor="middle" fill={color} fontFamily={FONT} fontSize={28} fontWeight={600}>{lab}</text>
      )}
    </svg>
  );
};
