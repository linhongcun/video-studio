import React from 'react';
import {MONO, P} from '../theme';

export const arcPoint = (x0: number, y0: number, x1: number, y1: number, progress: number, arcHeight = 100) => {
  const p = Math.max(0, Math.min(1, progress));
  return {x: x0 + (x1 - x0) * p, y: y0 + (y1 - y0) * p - Math.sin(Math.PI * p) * arcHeight};
};

export type FlyingLabelProps = {
  text: string; x0: number; y0: number; x1: number; y1: number; progress: number;
  arcHeight?: number; color?: string; width?: number; height?: number; fontSize?: number;
};

export const FlyingLabel: React.FC<FlyingLabelProps> = ({text, x0, y0, x1, y1, progress, arcHeight = 100, color = P.primary, width, height, fontSize = 36}) => {
  const {x, y} = arcPoint(x0, y0, x1, y1, progress, arcHeight);
  return <div style={{position: 'absolute', left: x, top: y, padding: '14px 22px', border: `3px solid ${color}`, borderRadius: 14, background: P.panel, color, fontFamily: MONO, fontSize, width, height, boxSizing: 'border-box', display: 'flex', alignItems: 'center', justifyContent: 'center', whiteSpace: 'nowrap'}}>{text}</div>;
};
