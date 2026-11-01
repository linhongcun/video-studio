import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import model from '../../model.json';
import {C, FONT, MONO} from './theme';
import {useLayoutAudit} from './LayoutAudit';

type CoverSize = '16x9' | '4x3' | '3x4';
const T = ({x, y, size = 32, color = C.text, weight = 600, anchor = 'start', mono = false, children}: {
  x: number; y: number; size?: number; color?: string; weight?: number;
  anchor?: 'start' | 'middle' | 'end'; mono?: boolean; children: React.ReactNode;
}) => <text x={x} y={y} fontFamily={mono ? MONO : FONT} fontSize={size}
  fontWeight={weight} fill={color} textAnchor={anchor}>{children}</text>;

const ones = new Set(model.snapshots.after205);
const negative = model.items.find(item => item.role === 'absent-negative')!;
const positive = model.items.find(item => item.role === 'absent-positive')!;

const QueryRow = ({item, y, negativeRow}: {item: typeof negative; y: number; negativeRow: boolean}) => {
  const color = negativeRow ? C.teal : C.gold;
  return <g>
    <T x={72} y={y + 10} size={31} color={C.muted} mono>{item.display}</T>
    <path d={`M156 ${y - 2}h45m-10 -9 10 9-10 9`} fill="none" stroke={C.muted} strokeWidth={3}/>
    {item.positions.map((position, index) => {
      const value = ones.has(position) ? 1 : 0;
      const x = 224 + index * 76;
      return <g key={position}>
        <rect x={x} y={y - 34} width={60} height={60} rx={10}
          fill={value ? '#173C3D' : '#493D25'} stroke={value ? C.teal : C.gold} strokeWidth={2.5}/>
        <T x={x + 30} y={y + 10} size={40} color={value ? C.teal : C.gold} anchor="middle" mono>{value}</T>
      </g>;
    })}
    <path d={`M465 ${y - 2}h41m-10 -9 10 9-10 9`} fill="none" stroke={color} strokeWidth={3}/>
    <T x={535} y={y + 10} size={34} color={color} weight={750}>{negativeRow ? '可排除' : '仍需查'}</T>
  </g>;
};

const Diagram = ({x, y, width, height}: {x: number; y: number; width: number; height: number}) =>
  <svg x={x} y={y} width={width} height={height} viewBox="0 0 800 570">
    <rect x={28} y={16} width={744} height={538} rx={30} fill={C.surface} stroke={C.edge} strokeWidth={2}/>
    <T x={72} y={75} size={31} color={C.muted}>同一份位标记 · 示例</T>
    {Array.from({length: model.bitCount}, (_, position) => {
      const col = position % 8;
      const row = Math.floor(position / 8);
      const bx = 72 + col * 82;
      const by = 102 + row * 112;
      const value = ones.has(position) ? 1 : 0;
      return <g key={position}>
        <rect x={bx} y={by} width={68} height={66} rx={10}
          fill={value ? '#173C3D' : '#0F1B2B'} stroke={value ? C.teal : C.edge} strokeWidth={2}/>
        <T x={bx + 34} y={by + 47} size={42} color={value ? C.teal : C.muted} anchor="middle" mono>{value}</T>
        <T x={bx + 34} y={by + 94} size={24} color={C.muted} anchor="middle" mono>{position}</T>
      </g>;
    })}
    <path d="M72 344H728" stroke={C.edge} strokeWidth={2}/>
    <QueryRow item={negative} y={402} negativeRow/>
    <QueryRow item={positive} y={500} negativeRow={false}/>
  </svg>;

const Title = ({x, y, size}: {x: number; y: number; size: number}) => <g>
  {covers.titleLines.map((line: string, index: number) =>
    <T key={line} x={x} y={y + index * size * 1.42} size={size}
      color={index === 1 ? C.teal : index === 2 ? C.gold : C.text} weight={800}>{line}</T>)}
</g>;

const Portrait = () => <svg width={1080} height={1440} viewBox="0 0 1080 1440">
  <T x={120} y={130} size={27} color={C.muted}>{covers.seriesLabel}</T>
  <T x={120} y={222} size={34} color={C.muted}>{covers.eyebrow}</T>
  <Title x={120} y={365} size={112}/>
  <Diagram x={120} y={735} width={840} height={365}/>
  <T x={120} y={1180} size={29} color={C.muted}>{covers.footer}</T>
</svg>;

export const Cover = ({size = '16x9', auditLayout = false}: {size?: CoverSize; auditLayout?: boolean}) => {
  useLayoutAudit(auditLayout, size, 0);
  const spec = covers.sizes[size];
  return <AbsoluteFill data-cover-root="true" data-canvas-width={spec.width} data-canvas-height={spec.height}
    style={{background: C.bg, color: C.text, fontFamily: FONT}}>
    <div style={{position: 'absolute', inset: 0,
      background: 'radial-gradient(ellipse at 82% 65%, #173C3D66, transparent 65%)'}}/>
    {size === '3x4' ? <Portrait/> : size === '4x3' ?
      <div style={{position: 'absolute', left: 315, top: 0, width: 1080, height: 1440,
        transform: 'scale(.75)', transformOrigin: 'top left'}}><Portrait/></div> :
      <svg width={1920} height={1080} viewBox="0 0 1920 1080">
        <T x={180} y={134} size={30} color={C.muted}>{covers.seriesLabel}</T>
        <T x={180} y={276} size={36} color={C.muted}>{covers.eyebrow}</T>
        <Title x={180} y={430} size={112}/>
        <T x={180} y={852} size={31} color={C.muted}>{covers.footer}</T>
        <Diagram x={1005} y={275} width={785} height={600}/>
      </svg>}
  </AbsoluteFill>;
};
