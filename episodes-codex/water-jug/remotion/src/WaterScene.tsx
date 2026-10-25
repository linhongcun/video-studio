import React from 'react';
import {C} from './theme';
import {T} from './primitives';
import {BAR,CAPACITIES,State,STATES,operationAt,surface,clamp,TRANSFER} from './water-model';
const WATER='#66CFFF';
type View=ReturnType<typeof operationAt>;
export const WaterBars=({volume,view,alpha=1}:{volume:State;view?:View;alpha?:number})=><g opacity={alpha} data-water-bars="true">
 {CAPACITIES.map((capacity,i)=>{
  const x=BAR.centers[i],top=surface(capacity),h=volume[i]*BAR.unit,changed=view&&Math.abs(view.end[i]-view.start[i])>0,moving=changed&&view.phase==='flowing',active=view&&(view.op.from===i||view.op.to===i),color=i?C.blue:C.teal;
  return <g key={i} data-container={i} data-volume={volume[i]} data-capacity={capacity} data-reading-mode={moving?'moving':'stable'}>
   <T x={x} y={top-32} size={29} color={color} anchor="middle">{i?'大':'小'}容器 · 容量{capacity}升</T>
   <rect data-capacity-body="true" x={x-BAR.width/2} y={top} width={BAR.width} height={capacity*BAR.unit} rx={12} fill={C.surface} stroke={active?C.gold:color} strokeWidth={active?3:2}/>
   <clipPath id={'water-clip-'+i}><rect x={x-BAR.width/2+3} y={top+3} width={BAR.width-6} height={capacity*BAR.unit-6} rx={9}/></clipPath>
   <g clipPath={`url(#water-clip-${i})`}><rect data-liquid="true" x={x-BAR.width/2} y={surface(volume[i])} width={BAR.width} height={h} fill={WATER} opacity={.69}/>{h>0&&<path d={`M ${x-BAR.width/2} ${surface(volume[i])} H ${x+BAR.width/2}`} stroke={WATER} strokeWidth={3}/>}</g>
   <T x={x} y={837} size={moving?34:49} color={moving?C.muted:color} mono={!moving} anchor="middle" weight={700} data-reading="true">{moving?(view?.op.kind==='fill'?'装水中':view?.op.kind==='drain'?'倒空中':'转移中'):String(Math.round(volume[i]))+' 升'}</T>
  </g>;
 })}
</g>;
const Route=({path,reveal=1,active=false,progress=0,tip}:any)=><g data-flow-kind="direction-indicator">
 <path d={path} fill="none" stroke={C.edge} strokeWidth={5} strokeLinecap="round"/>
 {active&&<><path d={path} fill="none" stroke={WATER} strokeWidth={6} strokeLinecap="round" pathLength={1} strokeDasharray="1" strokeDashoffset={1-reveal}/>{reveal>.98&&<><path d={path} fill="none" stroke={C.text} strokeWidth={2} strokeLinecap="round" pathLength={1} strokeDasharray=".035 .1" strokeDashoffset={-progress*2} opacity={.65}/><polygon data-flow-tip="true" points={tip.dir==='down'?`${tip.x-8},${tip.y-16} ${tip.x+8},${tip.y-16} ${tip.x},${tip.y}`:`${tip.x+16},${tip.y-8} ${tip.x+16},${tip.y+8} ${tip.x},${tip.y}`} fill={WATER}/></>}</>}
</g>;
export const WaterScene=({state=[0,0],view,completed=0,history=true,utilities=true}:{state?:State;view?:View;completed?:number;history?:boolean;utilities?:boolean})=>{
 const volume=view?.volume??state,active=!!view?.flowVisible,op=view?.op,committed=view?.complete?view.end:view?.start??state,historyCount=view?.historyCount??completed+1;
 const sourceY=surface(volume[1]),targetY=surface(volume[0]);
 const pourPath=`M ${BAR.centers[1]-120} ${sourceY} C 1040 ${sourceY}, 890 ${targetY}, ${BAR.centers[0]+120} ${targetY}`;
 const fillPath=`M 1530 350 H 1240 V ${sourceY}`;
 const drainPath='M 570 754 H 360';
 const audit={volume,capacity:CAPACITIES,pixelsPerLiter:BAR.unit,view:view?{...view,op}:null,historyCount,committed,total:volume[0]+volume[1]};
 return <g data-water-state={JSON.stringify(audit)}>
  {utilities&&<><g opacity={op?.kind==='fill'?1:.28} data-water-source="true"><rect x={1530} y={286} width={220} height={106} rx={18} fill={C.surface} stroke={op?.kind==='fill'?C.gold:C.edge}/><T x={1640} y={332} size={31} color={op?.kind==='fill'?C.gold:C.muted} anchor="middle">水源</T><T x={1640} y={370} size={22} color={C.muted} anchor="middle">只装到容器满</T></g><g opacity={op?.kind==='drain'?1:.28} data-water-outlet="true"><rect x={180} y={712} width={180} height={84} rx={15} fill={C.surface} stroke={op?.kind==='drain'?C.gold:C.edge}/><T x={270} y={764} size={29} color={op?.kind==='drain'?C.gold:C.muted} anchor="middle">倒空出口</T></g></>}
  <WaterBars volume={volume} view={view}/>
  {op?.kind==='fill'&&<Route path={fillPath} active={active} reveal={view!.flowReveal} progress={view!.progress} tip={{x:1240,y:sourceY,dir:'down'}}/>}
  {op?.kind==='drain'&&<Route path={drainPath} active={active} reveal={view!.flowReveal} progress={view!.progress} tip={{x:360,y:754,dir:'left'}}/>}
  {op?.kind==='pour'&&<Route path={pourPath} active={active} reveal={view!.flowReveal} progress={view!.progress} tip={{x:BAR.centers[0]+120,y:targetY,dir:'left'}}/>}
  {view&&<><T x={975} y={809} size={27} color={active?WATER:C.muted} anchor="middle">{op?.kind==='pour'?'大 → 小':op?.kind==='fill'?'水源 → 大容器':'小容器 → 出口'}</T>{view.complete&&<T x={975} y={853} size={28} color={C.gold} anchor="middle">{op?.kind==='pour'?'倒入':op?.kind==='fill'?'装入':'倒出'}{view.amount}升</T>}</>}
  {history&&<g data-history-count={historyCount}>
   <T x={1630} y={487} size={24} color={C.muted} anchor="middle">已完成状态</T><T x={1630} y={526} size={22} color={C.muted} anchor="middle">（小，大）升</T>
   {STATES.slice(Math.max(0,historyCount-3),historyCount).map((s,i,a)=><T key={i} x={1630} y={585+i*64} size={33} mono color={i===a.length-1?C.gold:C.muted} anchor="middle">({s[0]}, {s[1]})</T>)}
  </g>}
 </g>;
};
