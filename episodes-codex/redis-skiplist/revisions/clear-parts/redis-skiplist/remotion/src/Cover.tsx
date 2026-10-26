import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import rawModel from '../../model.json';
import {C, FONT, MONO} from './theme';
import {useLayoutAudit} from './LayoutAudit';

type CoverSize = '16x9' | '4x3' | '3x4';
const model: any = rawModel;
const T = ({x, y, size = 32, color = C.text, weight = 600, anchor = 'start', mono = false, children}: {
  x: number; y: number; size?: number; color?: string; weight?: number;
  anchor?: 'start' | 'middle' | 'end'; mono?: boolean; children: React.ReactNode;
}) => <text x={x} y={y} fontFamily={mono ? MONO : FONT} fontSize={size}
  fontWeight={weight} fill={color} textAnchor={anchor}>{children}</text>;

/** Both structure and the highlighted single route are read from the teaching model. */
const Diagram = ({x, y, width, height}: {x: number; y: number; width: number; height: number}) => {
  const before = model.before;
  const byId = new Map<string, any>(Object.entries(before.nodes));
  const lower: string[] = before.levels['0'];
  const upper: string[] = before.levels['1'];
  const xpos = (id: string) => id === model.head ? 84 : 186 + lower.indexOf(id) * 98;
  const ypos = (level: number) => level === 1 ? 180 : 352;
  const route: any[] = model.search.events.flatMap((event: any) => event.outcome === 'advance'
    ? [{kind: 'advance', level: event.level, fromNode: event.current, toNode: event.candidate}]
    : event.outcome === 'descend'
      ? [{kind: 'descend', node: event.current, fromLevel: event.level, toLevel: event.level - 1}] : []);
  const routePorts = new Set(route.flatMap((event: any) => event.kind === 'advance'
    ? [`${event.level}:${event.fromNode}`, `${event.level}:${event.toNode}`]
    : [`${event.fromLevel}:${event.node}`, `${event.toLevel}:${event.node}`]));
  const target = model.target;
  const pred = model.search.predecessors[0];
  const successor = model.search.successor;
  const routeD = route.map((event: any, index: number) => {
    const from = event.kind === 'advance' ? [xpos(event.fromNode), ypos(event.level)] : [xpos(event.node), ypos(event.fromLevel)];
    const to = event.kind === 'advance' ? [xpos(event.toNode), ypos(event.level)] : [xpos(event.node), ypos(event.toLevel)];
    return `${index === 0 ? `M${from[0]} ${from[1]}` : ''}L${to[0]} ${to[1]}`;
  }).join('');
  return <svg x={x} y={y} width={width} height={height} viewBox="0 0 1000 560">
    <rect x={22} y={18} width={956} height={524} rx={30} fill={C.surface} stroke={C.edge} strokeWidth={2}/>
    <T x={65} y={81} size={31} color={C.muted}>两层跳表 · 示例</T>
    <rect x={730} y={42} width={192} height={58} rx={13} fill="#463A24" stroke={C.gold} strokeWidth={2}/>
    <T x={826} y={82} size={32} color={C.gold} anchor="middle">找 {target} 的位置</T>
    <T x={63} y={128} size={25} color={C.muted}>上层</T>
    <T x={63} y={302} size={25} color={C.muted}>底层</T>
    {upper.map(id => <line key={'tower-' + id} x1={xpos(id)} y1={ypos(1)} x2={xpos(id)} y2={ypos(0)} stroke={C.edge} strokeWidth={3}/>)}
    {[1, 0].map(level => <g key={'links-' + level}>
      {[model.head, ...(before.levels[String(level)] as string[])].map(id => {
        const next = byId.get(id)?.forward[level];
        if (next == null) return null;
        return <g key={id} data-cover-link-from={id} data-cover-link-to={next} data-cover-link-level={level} data-edge-from={id} data-edge-to={next} data-edge-level={level}>
          <line x1={xpos(id)} y1={ypos(level)} x2={xpos(next) - 35} y2={ypos(level)} stroke={C.edge} strokeWidth={3}/>
          <path d={`M${xpos(next) - 47} ${ypos(level) - 8}L${xpos(next) - 35} ${ypos(level)}L${xpos(next) - 47} ${ypos(level) + 8}`} fill="none" stroke={C.edge} strokeWidth={3}/>
        </g>;
      })}
    </g>)}
    <path data-cover-active-route="true" d={routeD} fill="none" stroke={C.gold} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round"/>
    {route.filter((event: any) => event.kind === 'descend').map((event: any) => <path key={event.node}
      d={`M${xpos(event.node) - 10} ${ypos(event.toLevel) - 52}L${xpos(event.node)} ${ypos(event.toLevel) - 42}L${xpos(event.node) + 10} ${ypos(event.toLevel) - 52}`}
      fill="none" stroke={C.gold} strokeWidth={4}/>)}
    {[1, 0].map(level => <g key={'nodes-' + level}>
      {[model.head, ...(before.levels[String(level)] as string[])].map(id => {
        const isHead = id === model.head;
        const active = routePorts.has(`${level}:${id}`);
        const current = id === pred && level === 0;
        return <g key={id} data-cover-node-id={id} data-cover-node-level={level} data-node-id={id} data-port-level={level} data-node-value={isHead ? '' : byId.get(id)?.value} data-head={isHead ? 'true' : undefined} data-node-height={byId.get(id)?.height} data-node-inserted={isHead ? 'false' : 'true'} data-port-node={id} data-port-value={isHead ? '' : byId.get(id)?.value} data-port-next={byId.get(id)?.forward[level] ?? 'null'} data-cursor-node={current ? id : undefined} data-cursor-level={current ? level : undefined}>
          <rect x={xpos(id) - (isHead ? 37 : 35)} y={ypos(level) - 37} width={isHead ? 74 : 70} height={74} rx={13}
            fill={current ? '#463A24' : C.bg} stroke={active ? C.gold : C.edge} strokeWidth={current ? 4 : 2.5}/>
          <T x={xpos(id)} y={ypos(level) + 13} size={isHead ? 24 : 34} anchor="middle" mono={!isHead}
            color={active ? C.gold : C.text} weight={750}>{isHead ? '起点' : byId.get(id)?.value}</T>
        </g>;
      })}
    </g>)}
    <path d={`M${xpos(pred) + 32} 420H${xpos(successor) - 32}`} fill="none" stroke={C.teal} strokeWidth={3}/>
    <T x={500} y={489} size={34} color={C.teal} anchor="middle" weight={750}>
      {byId.get(pred)?.value} &lt; {target} &lt; {byId.get(successor)?.value}，插入位置找到了
    </T>
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
  <Diagram x={100} y={755} width={880} height={380}/>
  <T x={120} y={1195} size={29} color={C.muted}>{covers.footer}</T>
</svg>;

export const Cover = ({size = '16x9', auditLayout = false}: {size?: CoverSize; auditLayout?: boolean}) => {
  useLayoutAudit(auditLayout, size, 0);
  const spec = covers.sizes[size];
  return <AbsoluteFill data-cover-root="true" data-canvas-width={spec.width} data-canvas-height={spec.height}
    style={{background: C.bg, color: C.text, fontFamily: FONT}}>
    <div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 80% 60%, #173C3D66, transparent 65%)'}}/>
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
