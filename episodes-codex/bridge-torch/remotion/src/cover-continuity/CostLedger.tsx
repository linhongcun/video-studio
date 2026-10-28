import React from 'react';
import {C} from './theme';
import {T} from './primitives';
import {clamp} from '../crossings';
const costs=[[2,1,5,1,10],[2,1,10,2,2]];
export const CostLedger=({focus='slow',reveal=1}:{focus?:'slow'|'remaining';reveal?:number})=> <g data-cost-ledger={focus}>
 <rect x={510} y={336} width={900} height={424} rx={20} fill={C.bg} stroke={C.edge}/>
 {costs.map((row,r)=>{
  const slow=r===0?[2,4]:[2],active=row.map((_,i)=>focus==='slow'?slow.includes(i):!slow.includes(i));
  const selected=row.filter((_,i)=>active[i]),sum=selected.reduce((a,b)=>a+b,0),y=r?585:407;
  return <g key={r} opacity={r?clamp(reveal*2-.55):1}>
   <T x={550} y={y-28} size={27} color={C.muted}>方案{r?'二':'一'} · {r?17:19}分钟</T>
   {row.map((cost,i)=><g key={i} opacity={active[i]?1:.22}>
    <rect x={590+i*153} y={y} width={125} height={64} rx={12} fill={active[i]?C.gold+'17':C.surface} stroke={active[i]?C.gold:C.edge} strokeWidth={active[i]?2:1}/>
    <T x={652+i*153} y={y+44} size={34} color={active[i]?C.gold:C.muted} mono anchor="middle">{i%2===0?`${cost} →`:`← ${cost}`}</T>
   </g>)}
   <T x={960} y={y+110} size={30} color={C.gold} anchor="middle">{focus==='slow'?(r?'慢者同行：':'慢者分开：'):'其余各趟：'}{selected.join(' + ')} = {sum} 分钟</T>
  </g>;
 })}
</g>;
