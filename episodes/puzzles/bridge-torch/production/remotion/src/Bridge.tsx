import React from 'react';
import {C} from './theme';
import {T} from './primitives';
import {Move,State,PEOPLE,Person,personPosition,torchPosition,stages} from './crossings';
export const personColor=(p:Person)=>({1:C.teal,2:C.blue,5:C.gold,10:C.red}[p]);
export const PersonNode=({person,x,y,active=false,alpha=1}:any)=><g data-person={person} data-active={active?'true':'false'} transform={`translate(${x} ${y})`} opacity={alpha}>
 <rect data-person-body="true" x={-74} y={-39} width={148} height={78} rx={19} fill={C.surface} stroke={personColor(person)} strokeWidth={active?4:2}/>
 <T x={-10} y={13} size={36} mono color={personColor(person)} weight={760} anchor="end">{person}</T><T x={-3} y={11} size={23} color={personColor(person)}>分钟</T>
</g>;
export const Torch=({x,y,holder}:any)=><g data-torch="unique" data-carried-by={holder} transform={`translate(${x} ${y})`}>
 <rect x={-24} y={-23} width={48} height={46} rx={10} fill={C.gold+'22'} stroke={C.gold} strokeWidth={2}/>
 <path d="M -12 -8 L 5 -8 L 12 -16 L 17 -16 L 17 8 L 12 8 L 5 0 L -12 0 Z" fill={C.gold}/>
 <path d="M 21 -11 L 32 -17 M 23 -4 L 36 -4 M 21 3 L 32 9" stroke={C.gold} strokeWidth={2}/>
 <T x={0} y={45} size={20} color={C.gold} anchor="middle">手电</T>
</g>;
export const Bridge=({state,move,progress=0,alpha=1,labels=true}: {state:State;move?:Move;progress?:number;alpha?:number;labels?:boolean})=>{
 const arrived=!!move&&progress>=stages.arrive,total=state.total+(arrived?move.minutes:0);
 const direction=move?(move.to?'左岸 → 右岸':'右岸 → 左岸'):null;
 const sides={...state.sides};if(arrived&&move)for(const p of move.people)sides[p]=move.to;
 const holder=move&&progress>=stages.handoff?move.people[0]:state.holder;
 return <g opacity={alpha} data-bridge-state={JSON.stringify({sides,torchSide:arrived&&move?move.to:state.torchSide,holder,move,progress,total,arrived,phase:!move?'settled':progress<stages.handoff?'handoff':progress<stages.depart?'departure':progress<stages.cross?'crossing':progress<stages.arrive?'arrival':'settled'})}>
  <rect x={120} y={293} width={360} height={492} rx={25} fill={C.surface} stroke={C.edge}/><rect x={1440} y={293} width={360} height={492} rx={25} fill={C.surface} stroke={C.edge}/>
  <T x={300} y={315} size={25} color={C.muted} anchor="middle">左岸 · 起点</T><T x={1620} y={315} size={25} color={C.muted} anchor="middle">右岸 · 终点</T>
  <rect x={500} y={405} width={920} height={310} rx={20} fill="#18273C" stroke={C.edge} strokeWidth={3}/>
  <path d="M 520 560 H 1400" stroke={C.edge} strokeWidth={2} strokeDasharray="10 14"/>
  <T x={960} y={300} size={26} color={C.muted} anchor="middle">窄桥 · 最多两人同行</T>
  {PEOPLE.map(p=>{const position=personPosition(p,state,move,progress);return <PersonNode key={p} person={p} {...position} active={move?.people.includes(p)&&progress<stages.arrive}/>;})}
  <Torch {...torchPosition(state,move,progress)} holder={holder}/>
  {move&&move.people[0]!==state.holder&&progress<stages.handoff&&<T x={960} y={557} size={35} color={C.gold} anchor="middle">同岸交接手电</T>}
  {labels&&<g>
   {move&&<><T x={960} y={786} size={30} color={C.muted} anchor="middle">{move.people.map(p=>p+'分钟').join(' 和 ')} · {direction}</T><T x={810} y={855} size={38} color={arrived?C.gold:C.muted} anchor="middle">{arrived?'本次 +':'本次需 '}{move.minutes} 分钟</T></>}
   <T x={move?1200:960} y={855} size={42} color={arrived?C.gold:C.text} anchor="middle" weight={760}>累计 {total} 分钟</T>
  </g>}
 </g>;
};
