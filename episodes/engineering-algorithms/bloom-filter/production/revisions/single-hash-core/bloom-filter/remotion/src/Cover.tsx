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

const marks = new Set(model.snapshots.afterB);
const collisionQuery = model.items.find(item => item.role === 'absent-positive')!;
const negativeQuery = model.items.find(item => item.role === 'absent-negative')!;
const inserted = model.items.filter(item => model.inserted.includes(item.key));

/** One query, one computation, one arrow path to its sole bit. */
const Diagram = ({x, y, width, height}: {x: number; y: number; width: number; height: number}) => {
  const bitX = (position: number) => 73 + position * 82 + 32;
  const targetX = bitX(collisionQuery.singlePositions[0]);
  return <svg x={x} y={y} width={width} height={height} viewBox="0 0 800 570">
    <rect x={28} y={16} width={744} height={538} rx={30} fill={C.surface} stroke={C.edge} strokeWidth={2}/>
    <T x={72} y={75} size={31} color={C.muted}>一次哈希 · {model.bitCount}个位 · 示例</T>
    <rect x={72} y={108} width={76} height={66} rx={12} fill="#463A24" stroke={C.gold} strokeWidth={2.5}/>
    <T x={110} y={154} size={40} color={C.gold} anchor="middle" mono>{collisionQuery.display}</T>
    <path d="M164 141H258m-12-10 12 10-12 10" stroke={C.gold} fill="none" strokeWidth={3}/>
    <rect x={targetX - 78} y={108} width={156} height={66} rx={12} fill={C.bg} stroke={C.edge} strokeWidth={2.5}/>
    <T x={targetX} y={151} size={32} anchor="middle">哈希一次</T>
    <path d={`M${targetX} 185V238m-10-12 10 12 10-12`} stroke={C.gold} fill="none" strokeWidth={3}/>
    {Array.from({length: model.bitCount}, (_, position) => {
      const bx = 73 + position * 82;
      const isTarget = position === collisionQuery.singlePositions[0];
      const isNegative = position === negativeQuery.singlePositions[0];
      const value = marks.has(position) ? 1 : 0;
      const color = isTarget ? C.gold : isNegative ? C.teal : C.muted;
      return <g key={position} data-bit-index={position} data-bit-value={value}>
        <rect x={bx} y={251} width={64} height={70} rx={10}
          fill={isTarget ? '#463A24' : C.bg} stroke={isTarget || isNegative ? color : C.edge} strokeWidth={isTarget || isNegative ? 3 : 2}/>
        <T x={bx + 32} y={300} size={43} color={color} anchor="middle" mono>{value}</T>
        <T x={bx + 32} y={352} size={25} color={color} anchor="middle" mono>{position}</T>
      </g>;
    })}
    <T x={72} y={405} size={29} color={C.muted}>
      {inserted.map(item => item.display).join('、')}写过{collisionQuery.singlePositions[0]}号位，{collisionQuery.display}从未加入
    </T>
    <path d="M72 433H728" stroke={C.edge} strokeWidth={2}/>
    <T x={75} y={492} size={45} color={C.teal} mono>0</T>
    <T x={125} y={490} size={31} color={C.teal} weight={750}>确定未加入</T>
    <T x={418} y={492} size={45} color={C.gold} mono>1</T>
    <T x={468} y={490} size={31} color={C.gold} weight={750}>仍不确定</T>
  </svg>;
};

const Title = ({x, y, size}: {x: number; y: number; size: number}) => <g>
  {covers.titleLines.map((line: string, index: number) =>
    <T key={line} x={x} y={y + index * size * 1.52} size={size}
      color={index === 1 ? C.teal : index === 2 ? C.gold : C.text} weight={800}>{line}</T>)}
</g>;

const Portrait = () => <svg width={1080} height={1440} viewBox="0 0 1080 1440">
  <T x={120} y={130} size={27} color={C.muted}>{covers.seriesLabel}</T>
  <T x={120} y={222} size={34} color={C.muted}>{covers.eyebrow}</T>
  <Title x={120} y={365} size={112}/>
  <Diagram x={120} y={755} width={840} height={365}/>
  <T x={120} y={1180} size={29} color={C.muted}>{covers.footer}</T>
</svg>;

export const Cover = ({size = '16x9', auditLayout = false}: {size?: CoverSize; auditLayout?: boolean}) => {
  useLayoutAudit(auditLayout, size, 0);
  const spec = covers.sizes[size];
  return <AbsoluteFill data-cover-root="true" data-canvas-width={spec.width} data-canvas-height={spec.height}
    style={{background: C.bg, color: C.text, fontFamily: FONT}}>
    <div style={{position: 'absolute', inset: 0,
      background: 'radial-gradient(ellipse at 80% 60%, #173C3D66, transparent 65%)'}}/>
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
