import React from 'react';
import {C} from './theme';
import {T} from './primitives';
import {WORLDS,Progress,PICKED,COMPLETE,OFFER,HERO,ROWS,morphLayout,ease,mix,clamp} from './monty-model';
import {DoorRow} from './DoorBoard';
type Props={states:Progress[];focusY?:number;morph?:number;sum?:number;closing?:boolean;alternate?:boolean;emphasis?:number};
export const Overview=({states,focusY=580,morph=1,sum=0,closing=false,alternate=false,emphasis=0}:Props)=>{
 const p=ease(morph),otherAlpha=ease((morph-.8)/.2),math=ease(sum),rowResultAlpha=1-ease(sum/.15),move=ease((sum-.18)/.55),result=ease((sum-.8)/.2);
 return <g data-analysis-board="true" data-prior-total={1} data-analysis-morph={morph}>
  {sum>0&&<rect x={1450} y={445} width={350} height={420} rx={18} fill={C.bg} stroke={C.edge} opacity={ease(sum/.18)}/>}
  {morph===1&&<><T x={960} y={288} size={25} color={C.gold} anchor="middle">分析视图 · 三个初始奖位，各占1/3 · 不是三次抽样</T><rect x={155} y={focusY-78} width={1640} height={184} rx={18} fill={C.teal+'08'} stroke={C.teal+'60'} strokeWidth={2}/></>}
  {WORLDS.map((world,i)=>{
   const layout=i===1?morphLayout(HERO,ROWS[1],p):ROWS[i],alpha=i===1?1:otherAlpha;
   const tokenStart={x:1730,y:ROWS[i].y},target=i===1?{x:1625,y:550}:{x:1625,y:680},token=i===0?tokenStart:{x:mix(tokenStart.x,target.x,move),y:mix(tokenStart.y,target.y,move)};
   return <g key={world.id}>
    <DoorRow world={world} progress={states[i]} layout={layout} alpha={alpha} analysis={morph>.25} showResult={false}/>
    <g opacity={alpha*(i===1?otherAlpha:1)}>
     {i!==1&&morph<1&&<T x={190} y={layout.y+65} size={22} color={C.muted}>另一种初始情景</T>}
     {states[i].reveal===1&&<T x={1530} y={ROWS[i].y+10} size={30} color={i?C.teal:C.red} anchor="middle" alpha={rowResultAlpha}>换门{i?'赢':'输'}</T>}
     {alternate&&i===0&&<T x={1530} y={ROWS[i].y+57} size={22} color={C.muted} anchor="middle" alpha={rowResultAlpha}>若开2，换3也输</T>}
    </g>
    <g opacity={alpha*(i===1?otherAlpha:1)*(closing&&i>0?0:1)} data-case-weight={world.prize} transform={`translate(${token.x} ${token.y})`}>
     <rect x={-50} y={-22} width={100} height={44} rx={11} fill={C.bg} stroke={i===0?C.muted:C.gold}/><T x={0} y={11} size={28} color={i===0?C.muted:C.gold} mono anchor="middle">1/3</T>
    </g>
   </g>;
  })}
  {sum>0&&<g><g opacity={ease((sum-.12)/.1)}><T x={1625} y={487} size={25} color={C.gold} anchor="middle">换门赢的机会相加</T><T x={1625} y={628} size={40} color={C.gold} mono anchor="middle">+</T></g><T x={1625} y={829} size={66} color={C.gold} mono weight={760} anchor="middle" alpha={result}>2/3</T></g>}
  {closing&&<g><rect x={1450} y={445} width={350} height={420} rx={18} fill={C.bg} stroke={C.edge}/><T x={1625} y={510} size={28} color={C.muted} anchor="middle">始终保留原选</T><T x={1625} y={583} size={49} color={C.text} mono anchor="middle">1/3</T><T x={1625} y={688} size={28} color={C.gold} anchor="middle">每次都换门</T><T x={1625} y={791} size={70} color={C.gold} mono weight={760} anchor="middle">2/3</T></g>}
 </g>;
};
